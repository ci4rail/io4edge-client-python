import io4edge_client.core as core
import argparse

def main():
    parser = argparse.ArgumentParser(description="set value of persistent parameter")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    parser.add_argument(
        "name", help="Name of persistent parameter", type=str
    )
    parser.add_argument(
        "value", help="Value of persistent parameter", type=str
    )
    args = parser.parse_args()

    core_client = core.new_core_client(args.addr)
    core_client.set_persistent_parameter(args.name, args.value)


if __name__ == "__main__":
    main()
