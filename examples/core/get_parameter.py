import io4edge_client.core as core
import argparse

def main():
    parser = argparse.ArgumentParser(description="get value of persistent parameter")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    parser.add_argument(
        "name", help="Name of persistent parameter", type=str
    )
    args = parser.parse_args()

    core_client = core.new_core_client(args.addr)
    print(f"{args.name}={core_client.get_persistent_parameter(args.name)}")


if __name__ == "__main__":
    main()
