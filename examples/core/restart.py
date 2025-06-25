import io4edge_client.core as core
import argparse

def main():
    parser = argparse.ArgumentParser(description="restart io4edge device")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    args = parser.parse_args()

    core_client = core.new_core_client(args.addr)
    core_client.restart()


if __name__ == "__main__":
    main()
