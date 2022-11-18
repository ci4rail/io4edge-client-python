import io4edge_client


def main():
    fb_client = io4edge_client.functionblock.Client("S101-IOU07-USB-EXT-1-binio._io4edge_binaryIoTypeC._tcp")
    fb_client.Command()

if __name__ == "__main__":
    main()
