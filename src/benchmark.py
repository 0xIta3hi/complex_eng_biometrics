"""Small dimension/latency benchmark for the prototype."""

from __future__ import annotations

import argparse
import random
import statistics

from .protocol import authenticate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimensions", nargs="+", type=int, default=[8, 32, 64, 128])
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    for dimension in args.dimensions:
        latencies = []
        sent = received = 0
        for _ in range(args.runs):
            query = [random.randrange(100) for _ in range(dimension)]
            template = [random.randrange(100) for _ in range(dimension)]
            result = authenticate(query, template, threshold=dimension * 10000)
            latencies.append(result["latency_ms"])
            sent += result["sent_bytes"]
            received += result["received_bytes"]
        print(f"dimension={dimension} median_latency_ms={statistics.median(latencies):.2f} avg_sent_bytes={sent / args.runs:.0f} avg_received_bytes={received / args.runs:.0f}")


if __name__ == "__main__":
    main()