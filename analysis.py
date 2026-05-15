import os

import matplotlib.pyplot as plt
import pandas as pd


LOG_FILE = "transfer_logs.csv"


def analyze_logs():
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} was not found. Run client.py first.")
        return

    df = pd.read_csv(LOG_FILE)

    print("--- TRANSFER ANALYSIS SUMMARY ---")
    print(f"Total network events: {len(df)}")

    timeout_count = len(df[df["event"] == "TIMEOUT"])
    failed_count = len(df[df["event"] == "TRANSFER_FAILED"])
    print(f"Total timeouts: {timeout_count}")
    print(f"Failed packets: {failed_count}")

    send_events = df[df["event"] == "SEND"]
    retry_counts = send_events.groupby("seq_num").size()

    plt.figure(figsize=(10, 5))
    retry_counts.plot(kind="bar", color="coral", edgecolor="black")
    plt.title("Send Attempts per Packet")
    plt.xlabel("Sequence Number")
    plt.ylabel("Send Count")
    plt.tight_layout()

    print("Rendering chart...")
    plt.show()


if __name__ == "__main__":
    analyze_logs()
