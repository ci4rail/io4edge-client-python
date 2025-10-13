import io4edge_client
import argparse

def progress_callback(progress):
    print(f"Progress: {progress:.1f}%")

def main():
    parser = argparse.ArgumentParser(description="load io4edge firmware")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the core function block", type=str
    )
    parser.add_argument(
        "file", help="raw firmware binary file", type=str
    )
    args = parser.parse_args()

    core_client = io4edge_client.CoreClient(args.addr)

    # Read in file
    with open(args.file, "rb") as f:
        firmware_data = f.read()
        core_client.load_firmware(firmware_data, progress_cb=progress_callback)


if __name__ == "__main__":
    main()
