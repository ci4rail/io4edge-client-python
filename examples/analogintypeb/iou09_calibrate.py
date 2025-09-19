#!/usr/bin/env python3
# SPDX-License-Identifer: Apache-2.0
import io4edge_client.core as core
import io4edge_client.analogintypeb as ana
import io4edge_client.functionblock as fb
import argparse
import time

NUM_CHANNELS = 8
SAMPLE_RATE = 1000  # Hz
GAIN_SETTING = 1  # x1


def sample_for_calibration(ana_client, channel: int) -> float:
    config = ana.Pb.ConfigurationSet()
    config.channelConfig.add(
        channel=channel, sample_rate=SAMPLE_RATE, gain=GAIN_SETTING
    )
    ana_client.upload_configuration(config)
    ana_client.start_stream(
        1 << channel,
        fb.Pb.StreamControlStart(
            bucketSamples=400,
            keepaliveInterval=1000,
            bufferedSamples=1000,
            low_latency_mode=False,
        ),
    )
    n_samples = 0
    all_samples = []
    while n_samples < SAMPLE_RATE:
        generic_stream_data, stream_data = ana_client.read_stream()
        n_samples += len(stream_data.samples)
        all_samples.extend([sample.value[0] for sample in stream_data.samples])
    ana_client.stop_stream()

    avg = sum(all_samples) / len(all_samples)
    print(f"Channel {channel+1} average sample value is {avg}")
    return avg


def offset_param_name(channel: int) -> str:
    return f"ch{channel +1 }_offset"


def gain_param_name(channel: int) -> str:
    return f"ch{channel+1 }_gain"


def write_calibration(core_client, channel: int, offset: float, gain: float):
    print(
        f"Writing calibration parameters for channel {channel+1}: offset={offset}, gain={gain}"
    )
    core_client.set_persistent_parameter(offset_param_name(channel), f"{offset: .6f}")
    core_client.set_persistent_parameter(gain_param_name(channel), f"{gain: .6f}")



def create_clients(addr: str):
    ana_client = ana.Client(addr + "-anain")
    core_client = core.new_core_client(addr)
    return ana_client, core_client


def purge_parameters(core_client):
    for channel in range(NUM_CHANNELS):
        core_client.set_persistent_parameter(offset_param_name(channel), "")
        core_client.set_persistent_parameter(gain_param_name(channel), "")


def prompt(msg: str):
    input(msg)

def main():
    parser = argparse.ArgumentParser(
        description="Calibrate IOU09 or MIO09 analog input channels"
    )
    parser.add_argument("addr", help="MDNS address of device", type=str)

    args = parser.parse_args()

    # ana_client, core_client = create_clients(args.addr)
    # purge_parameters(core_client)
    # core_client.restart()
    # print("Purged device parameters. Restarting device to apply changes...")
    # time.sleep(10)

    print("Offset calibration...")
    offset = [0.0] * NUM_CHANNELS
    gain = [1.0] * NUM_CHANNELS
    ana_client, core_client = create_clients(args.addr)

    for channel in range(1,2):
        prompt(f"Connect channel {channel+1} to 0.0V and press Enter")
        raw_value = sample_for_calibration(ana_client, channel)
        if abs(raw_value) > 0.2:
            raise ValueError("measured value too far from 0.0V")
        
        offset[channel] = raw_value
        write_calibration(core_client, channel, offset[channel], gain[channel])
    
    core_client.restart()
    time.sleep(10)
    ana_client, core_client = create_clients(args.addr)

    for channel in range(1,2):
        prompt(f"Connect channel {channel+1} to 10.0V and press Enter")
        raw_value = sample_for_calibration(ana_client, channel)
        if abs(raw_value) < 0.9 or abs(raw_value) > 1.1:
            raise ValueError("measured value too far from 10.0V after offset calibration")
        gain[channel] = 1.0 / raw_value
        write_calibration(core_client, channel, offset[channel], gain[channel])
        core_client.restart()
        
        
if __name__ == "__main__":
    main()
