import csv
import os
from collections import Counter


LOG_FILE = "transfer_logs.csv"


def load_events(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def total_duration(events):
    # Prefer the elapsed value reported on TRANSFER_COMPLETE, fall back to the
    # span between the first and last logged event.
    for event in events:
        if event["event"] == "TRANSFER_COMPLETE" and "elapsed=" in event["details"]:
            try:
                return float(event["details"].split("elapsed=")[1].rstrip("s"))
            except ValueError:
                break

    timestamps = [float(event["timestamp"]) for event in events if event["timestamp"]]
    return max(timestamps) - min(timestamps) if timestamps else 0.0


def summarize(events):
    counts = Counter(event["event"] for event in events)

    send_events = [event for event in events if event["event"] == "SEND"]
    unique_packets = len({event["seq_num"] for event in send_events})

    # A retransmission is any send attempt beyond the first one for a packet.
    retransmissions = len(send_events) - unique_packets

    return {
        "Unique packets sent": unique_packets,
        "Total send attempts": len(send_events),
        "Retransmissions": retransmissions,
        "ACKs received": counts.get("ACK_RECEIVED", 0),
        "Timeouts": counts.get("TIMEOUT", 0),
        "Simulated drops": counts.get("SIMULATED_DROP", 0),
        "Failed transfers": counts.get("TRANSFER_FAILED", 0),
        "Total transfer time (s)": round(total_duration(events), 3),
    }


def plot_send_attempts(events):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib not installed; chart skipped. Install with: pip install matplotlib)")
        return

    attempts = Counter(event["seq_num"] for event in events if event["event"] == "SEND")
    seqs = sorted(attempts, key=int)
    values = [attempts[seq] for seq in seqs]

    plt.figure(figsize=(10, 5))
    plt.bar(seqs, values, color="coral", edgecolor="black")
    plt.title("Send Attempts per Packet")
    plt.xlabel("Sequence Number")
    plt.ylabel("Send Count")
    plt.tight_layout()
    print("Rendering chart...")
    plt.show()


def analyze_logs():
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} was not found. Run client.py first.")
        return

    events = load_events(LOG_FILE)

    print("--- TRANSFER ANALYSIS SUMMARY ---")
    print(f"Total network events: {len(events)}")
    for label, value in summarize(events).items():
        print(f"{label}: {value}")

    plot_send_attempts(events)


if __name__ == "__main__":
    analyze_logs()
