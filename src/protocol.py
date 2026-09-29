"""Protocol primitives for additive sharing and Beaver multiplication."""

from __future__ import annotations

import json
import secrets
import socket
import time
from dataclasses import dataclass
from typing import Any

PRIME = 2**61 - 1
PARTY_COUNT = 3
PARTY_HOST = "127.0.0.1"
PARTY_PORTS = (8001, 8002, 8003)


def mod(value: int) -> int:
    return value % PRIME


def split_secret(value: int, rng: Any = secrets) -> list[int]:
    first = rng.randbelow(PRIME)
    second = rng.randbelow(PRIME)
    return [first, second, mod(value - first - second)]


def split_vector(vector: list[int], rng: Any = secrets) -> list[list[int]]:
    shares = [[] for _ in range(PARTY_COUNT)]
    for value in vector:
        for party_id, share in enumerate(split_secret(value, rng)):
            shares[party_id].append(share)
    return shares


def reconstruct(shares: list[int]) -> int:
    return sum(shares) % PRIME


def make_beaver_triples(size: int, rng: Any = secrets) -> list[dict[str, list[int]]]:
    triples = []
    for _ in range(size):
        a = rng.randbelow(PRIME)
        b = rng.randbelow(PRIME)
        triples.append({"a": split_secret(a, rng), "b": split_secret(b, rng), "c": split_secret(a * b, rng)})
    return triples


def encode_message(message: dict[str, Any]) -> bytes:
    return (json.dumps(message, separators=(",", ":")) + "\n").encode()


@dataclass
class PartyConnection:
    party_id: int
    host: str = PARTY_HOST
    port: int = 0
    sent_bytes: int = 0
    received_bytes: int = 0

    def __post_init__(self) -> None:
        if not self.port:
            self.port = PARTY_PORTS[self.party_id]

    def request(self, message: dict[str, Any]) -> dict[str, Any]:
        payload = encode_message(message)
        with socket.create_connection((self.host, self.port), timeout=10) as connection:
            connection.sendall(payload)
            self.sent_bytes += len(payload)
            response = bytearray()
            while not response.endswith(b"\n"):
                chunk = connection.recv(65536)
                if not chunk:
                    raise ConnectionError(f"party {self.party_id} closed the connection")
                response.extend(chunk)
            self.received_bytes += len(response)
        result = json.loads(response)
        if "error" in result:
            raise RuntimeError(f"party {self.party_id}: {result['error']}")
        return result


def run_multiplication(connections: list[PartyConnection], value_shares: list[int], triple: dict[str, list[int]]) -> list[int]:
    masked = []
    for party_id, connection in enumerate(connections):
        masked.append(connection.request({
            "op": "mask", "value": value_shares[party_id],
            "a": triple["a"][party_id], "b": triple["b"][party_id],
        }))
    opened_d = reconstruct([item["d"] for item in masked])
    opened_e = reconstruct([item["e"] for item in masked])
    outputs = []
    for party_id, connection in enumerate(connections):
        response = connection.request({
            "op": "multiply", "c": triple["c"][party_id],
            "a": triple["a"][party_id], "b": triple["b"][party_id],
            "d": opened_d, "e": opened_e,
            "correction": opened_d * opened_e if party_id == 0 else 0,
        })
        outputs.append(response["share"])
    return outputs


def authenticate(query: list[int], template: list[int], threshold: int) -> dict[str, Any]:
    if len(query) != len(template) or not query:
        raise ValueError("query and template must have the same non-zero dimension")
    connections = [PartyConnection(party_id) for party_id in range(PARTY_COUNT)]
    query_shares = split_vector(query)
    template_shares = split_vector(template)
    triples = make_beaver_triples(len(query))
    started = time.perf_counter()
    for party_id, connection in enumerate(connections):
        response = connection.request({"op": "load", "query": query_shares[party_id], "template": template_shares[party_id]})
        if response.get("status") != "ready":
            raise RuntimeError(f"party {party_id} rejected load")
    distance_shares = [0] * PARTY_COUNT
    for index in range(len(query)):
        difference_shares = [mod(query_shares[party_id][index] - template_shares[party_id][index]) for party_id in range(PARTY_COUNT)]
        product_shares = run_multiplication(connections, difference_shares, triples[index])
        distance_shares = [mod(distance_shares[party_id] + product_shares[party_id]) for party_id in range(PARTY_COUNT)]
    opened_distance = reconstruct(distance_shares)
    elapsed_ms = (time.perf_counter() - started) * 1000
    for connection in connections:
        connection.request({"op": "reset"})
    return {
        "distance": opened_distance, "accepted": opened_distance <= threshold,
        "threshold": threshold, "dimension": len(query),
        "rounds": 2 + 2 * len(query),
        "sent_bytes": sum(connection.sent_bytes for connection in connections),
        "received_bytes": sum(connection.received_bytes for connection in connections),
        "latency_ms": elapsed_ms,
    }