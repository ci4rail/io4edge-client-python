import io4edge_client.core as core
import argparse

def main():
    parser = argparse.ArgumentParser(description="get reset reason of io4edge device")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    args = parser.parse_args()

    core_client = core.new_core_client(args.addr)
    print(core_client.get_reset_reason())


if __name__ == "__main__":
    main()
