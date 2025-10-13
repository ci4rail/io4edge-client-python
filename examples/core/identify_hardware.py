import io4edge_client
import argparse

def main():
    parser = argparse.ArgumentParser(description="identify io4edge hardware")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    args = parser.parse_args()

    core_client = io4edge_client.CoreClient(args.addr)
    print(core_client.identify_hardware())


if __name__ == "__main__":
    main()
