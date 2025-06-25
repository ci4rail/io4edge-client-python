import io4edge_client.core as core
import argparse

def main():
    parser = argparse.ArgumentParser(description="identify io4edge hardware")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    args = parser.parse_args()

    core_client = core.new_core_client(args.addr)
    print(core_client.identify_hardware())


if __name__ == "__main__":
    main()
