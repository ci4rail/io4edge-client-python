import io4edge_client.core
import argparse

def main():
    parser = argparse.ArgumentParser(description="restart io4edge device")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    args = parser.parse_args()

    core_client = io4edge_client.CoreClient(args.addr)
    core_client.restart()


if __name__ == "__main__":
    main()
