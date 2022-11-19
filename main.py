import io4edge_client.binaryiotypec as binio


def main():
    binio_client = binio.client.Client(
        "S101-IOU07-USB-EXT-1-binio._io4edge_binaryIoTypeC._tcp"
    )
    binio_client.set_output(1, True)


if __name__ == "__main__":
    main()
