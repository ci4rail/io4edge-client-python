import io4edge_client.binaryiotyped as binio
import io4edge_client.functionblock as fb
import argparse

def main():
    parser = argparse.ArgumentParser(description="Get binary i/o type D configuration client")
    parser.add_argument(
        "addr", help="MDNS address or IP:Port of the function block", type=str
    )

    args = parser.parse_args()

    binio_client = binio.Client(args.addr)

    config = binio_client.download_configuration()
    print("Downloaded config is :")
    print(config)
    # for c in config :
    #     print("Channel:", c.channel)
    #     print("Mode:", c.mode)
    #     print("Current Value:", c.initialValue)
    #     print("Overload Recovery Timeout ms:", c.overloadRecoveryTimeoutMs)
    #     print("Watchdog Timeout ms:", c.watchdogTimeoutMs)
    #     print("fritting Enable:", c.frittingEnable)

if __name__ == "__main__":
    main()
