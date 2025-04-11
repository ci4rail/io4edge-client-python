#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.digiwave as dw
import io4edge_client.functionblock as fb
import argparse
import csv

def parse_csv_to_dict(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        next(csv_reader)  # Skip header
        next(csv_reader)  # Skip header
        
        line = 0
        for row in csv_reader:
            if len(row) == 0:
                break
            
            entry = {
                'time_s': row[0],
                'ch2_bitbus': row[1],
                'time_250ns_tics': row[2],
                'delta_tics': row[3],
                'time_ns': row[4] if len(row) > 4 else None,
                'delta_ps': row[5] if len(row) > 5 else None,
                'comment': row[6] if len(row) > 6 else None
            }
            # if int(entry['delta_tics']) > 100:
            #     print(f"line {line}: delta_tics > 100: {entry['delta_tics']}")
            line += 1
            data.append(entry)
    
    return data

def entries_to_vcd(data):
    vcd = """$timescale
1 ns
$end
$var wire 1 ! bitbus $end
$upscope $end
$enddefinitions $end
"""
    for entry in data:
        time_ns = int(entry['time_ns'])
        if time_ns is not None:
            vcd += f"#{round(time_ns)}\n{entry['ch2_bitbus']}!\n"
    vcd += """
$dumpoff
$end
"""
    return vcd

def entries_to_edr(data):
    edr = []
    for entry in data:
        dt = int(entry['delta_tics'])
        level = 1 if entry['ch2_bitbus'] == '1' else 0
        #print(f"dt: {dt}, level: {level}")
        while True:
            if dt >= 0x80:
                v = 0
                dt -= 0x80
            else: 
                v = dt & 0x7f
                dt -= v
            if not level:
                v |= 0x80
            #print(f" v: {v}")
            edr.append(v)
            if dt == 0:
                break
    return edr


def main():
    parser = argparse.ArgumentParser(description="send digiwave stream")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the bbsniffer function block", type=str
    )
    parser.add_argument(
        "wavecsv", help="CSV file with waveform", type=str
    )

    args = parser.parse_args()

    dw_client = dw.Client(args.addr)
    
    dw_client.upload_configuration(
        dw.Pb.ConfigurationSet(
            full_duplex = True,
            claim_rx = False,
            
        )
    )
    
    data = parse_csv_to_dict(args.wavecsv)
    edr = entries_to_edr(data)    
    vcd = entries_to_vcd(data)
    with open(args.wavecsv + '.vcd', 'w') as vcd_file:
        vcd_file.write(vcd)
    
    print(len(edr))
    
    # while True:    
    dw_client.send_wave(bytes(edr[:3000]))
        
if __name__ == "__main__":
    main()
