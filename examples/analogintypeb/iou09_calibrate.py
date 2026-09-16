#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import io4edge_client.core as core
import io4edge_client.analogintypeb as ana
import io4edge_client.functionblock as fb
import argparse
import time
import math
import statistics

NUM_CHANNELS = 8
SAMPLE_RATE = 1000  # Hz
GAIN_SETTING = 1  # x1
REF_VOLTAGE = 9.994
NOISE_SAMPLE_RATE = 2000  # Hz
NOISE_DURATION = 5  # seconds
NOISE_PEAK_LIMIT = 0.005  # V
FULL_SCALE_VOLTAGE = 10.0  # V at gain 1

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
        _, stream_data = ana_client.read_stream(timeout=5)
        n_samples += len(stream_data.samples)
        all_samples.extend([sample.value[0] for sample in stream_data.samples])
    ana_client.stop_stream()
    time.sleep(1) # wait for stream stop

    avg = sum(all_samples) / len(all_samples)
    print(f"Channel {channel+1} average sample value is {avg}")
    return avg


def verify_noise(ana_client):
    prompt("Apply 0.0V to all channels and press Enter for the noise check")
    config = ana.Pb.ConfigurationSet()
    for channel in range(NUM_CHANNELS):
        config.channelConfig.add(
            channel=channel, sample_rate=NOISE_SAMPLE_RATE, gain=GAIN_SETTING
        )
    ana_client.upload_configuration(config)
    ana_client.start_stream(
        (1 << NUM_CHANNELS) - 1,
        fb.Pb.StreamControlStart(
            bucketSamples=400,
            keepaliveInterval=1000,
            bufferedSamples=1000,
            low_latency_mode=False,
        ),
    )
    samples = [[] for _ in range(NUM_CHANNELS)]
    target_samples = NOISE_SAMPLE_RATE * NOISE_DURATION
    try:
        while any(len(values) < target_samples for values in samples):
            _, stream_data = ana_client.read_stream(timeout=5)
            for sample in stream_data.samples:
                for channel, value in enumerate(sample.value, sample.baseChannel):
                    if not 0 <= channel < NUM_CHANNELS:
                        raise ValueError(f"Unexpected sample channel {channel}")
                    if not math.isfinite(value):
                        raise ValueError(f"Non-finite sample on channel {channel + 1}")
                    if len(samples[channel]) < target_samples:
                        samples[channel].append(value * FULL_SCALE_VOLTAGE)
    finally:
        ana_client.stop_stream()

    failed_channels = []
    for channel, values in enumerate(samples):
        noise = statistics.pstdev(values)
        peak = max(abs(value) for value in values)
        print(
            f"Channel {channel + 1}: noise (standard deviation)={noise * 1000:.3f} mV, "
            f"peak deviation from 0V={peak * 1000:.3f} mV"
        )
        if peak > NOISE_PEAK_LIMIT:
            failed_channels.append(str(channel + 1))
    if failed_channels:
        raise SystemExit(
            "Noise check failed: peak deviation exceeds 5 mV on channel(s) "
            + ", ".join(failed_channels)
        )


def offset_param_name(channel: int) -> str:
    return f"ch{channel +1 }_offset"


def gain_param_name(channel: int) -> str:
    return f"ch{channel+1 }_gain"


def write_calibration(core_client, channel: int, offset: float, gain: float):
    print(
        f"Writing calibration parameters for channel {channel+1}: offset={offset: .6f}, gain={gain: .6f}"
    )
    core_client.set_persistent_parameter(offset_param_name(channel), f"{offset: .6f}")
    core_client.set_persistent_parameter(gain_param_name(channel), f"{gain: .6f}")


def create_clients(addr: str):
    ana_client = ana.Client(addr + "-anain")
    core_client = core.CoreClient(addr)
    return ana_client, core_client


def purge_parameters(core_client):
    for channel in range(NUM_CHANNELS):
        core_client.set_persistent_parameter(offset_param_name(channel), "")
        core_client.set_persistent_parameter(gain_param_name(channel), "")


def prompt(msg: str):
    input(msg)


def restart_device(core_client, msg: str):
    print(msg)
    core_client.restart()
    time.sleep(10)

def main():
    parser = argparse.ArgumentParser(
        description="Calibrate IOU09 or MIO09 analog input channels"
    )
    parser.add_argument("addr", help="MDNS address of device", type=str)

    args = parser.parse_args()

    ana_client, core_client = create_clients(args.addr)
    purge_parameters(core_client)
    restart_device(core_client, "Purged device parameters. Restarting device to apply changes...")

    print("Offset calibration...")
    offset = [0.0] * NUM_CHANNELS
    gain = [1.0] * NUM_CHANNELS
    ana_client, core_client = create_clients(args.addr)

    prompt(f"Apply 0.0V to all channels and press Enter")
    for channel in range(0, NUM_CHANNELS):
        raw_value = sample_for_calibration(ana_client, channel)
        if abs(raw_value) > 0.2:
            raise ValueError("measured value too far from 0.0V")

        offset[channel] = raw_value
        write_calibration(core_client, channel, offset[channel], gain[channel])

    restart_device(core_client, "Restarting device to apply changes...")
    ana_client, core_client = create_clients(args.addr)

    prompt(f"Apply {REF_VOLTAGE} V to all channels and press Enter")
    for channel in range(0, NUM_CHANNELS):
        raw_value = sample_for_calibration(ana_client, channel)
        if abs(raw_value) < 0.9*(REF_VOLTAGE/10) or abs(raw_value) > 1.1*(REF_VOLTAGE/10):
            raise ValueError(
                f"measured value too far from {REF_VOLTAGE} V"
            )
        gain[channel] = REF_VOLTAGE/10 / raw_value
        write_calibration(core_client, channel, offset[channel], gain[channel])


    restart_device(core_client, "Restarting device to apply changes...")
    ana_client, core_client = create_clients(args.addr)

    print("Verifying calibration...")
    for channel in range(0, NUM_CHANNELS):
        raw_value = sample_for_calibration(ana_client, channel)
        if abs(raw_value) < 0.995*(REF_VOLTAGE/10) or abs(raw_value) > 1.005*(REF_VOLTAGE/10):
            raise ValueError(
                f"measured value too far from {REF_VOLTAGE} V"
            )

    verify_noise(ana_client)


if __name__ == "__main__":
    main()
