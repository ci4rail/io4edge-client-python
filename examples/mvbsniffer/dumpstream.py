# SPDX-License-Identifer: Apache-2.0
import io4edge_client.mvbsniffer as mvb
import io4edge_client.functionblock as fb


def main():
    mvb_client = mvb.Client("S101-IOU03-USB-EXT-4-binio")

    stream_start = mvb.Pb.StreamControlStart()
    stream_start.filter.add(
        mvb.Pb.FilterMask(f_code_mask=0x0FFF, include_timedout_frames=False)
    )

    mvb_client.start_stream(
        stream_start,
        fb.Pb.StreamControlStart(
            bucketSamples=25,
            keepaliveInterval=1000,
            bufferedSamples=50,
            low_latency_mode=True,
        ),
    )

    for i in range(10):
        try:
            generic_stream_data, telegrams = mvb_client.read_stream(timeout=3)
        except TimeoutError:
            print("Timeout")
            continue

        for telegram in telegrams.entries:
            if telegram.State != mvb.TelegramPb.State.kSuccessful:
                if telegram.State & mvb.TelegramPb.State.kTimedOut:
                    print("No slave frame has been received to a master frame")
                if telegram.State & mvb.TelegramPb.State.kMissedMvbFrames:
                    print(
                        "one or more MVB frames are lost in the device since the last telegram"
                    )
                if telegram.State & mvb.TelegramPb.State.kMissedTelegrams:
                    print("one or more telegrams are lost")
            print(telegram_to_str(telegram))


def telegram_to_str(telegram):
    ret_val = "addr=%03x, " % telegram.addr
    ret_val += (
        "%s" % mvb.TelegramPb._TELEGRAM_TYPE.values_by_number[telegram.f_code].name
    )
    if len(telegram.data) > 0:
        ret_val += ", data="
        for b in telegram.data:
            ret_val += "%02x " % b
    return ret_val


if __name__ == "__main__":
    main()
