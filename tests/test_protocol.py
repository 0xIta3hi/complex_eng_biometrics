import unittest
from unittest.mock import patch

from src.protocol import PRIME, authenticate, make_beaver_triples, mod, reconstruct, split_secret, split_vector


class FakePartyConnection:
    def __init__(self, party_id: int) -> None:
        self.party_id = party_id
        self.sent_bytes = 0
        self.received_bytes = 0

    def request(self, message: dict[str, object]) -> dict[str, object]:
        operation = message["op"]
        if operation == "load":
            return {"status": "ready"}
        if operation == "mask":
            return {
                "d": mod(int(message["value"]) - int(message["a"])),
                "e": mod(int(message["value"]) - int(message["b"])),
            }
        if operation == "multiply":
            share = mod(
                int(message["c"])
                + int(message["d"]) * int(message["b"])
                + int(message["e"]) * int(message["a"])
                + int(message["correction"])
            )
            return {"share": share}
        if operation == "reset":
            return {"status": "reset"}
        raise AssertionError(f"unexpected operation: {operation}")


class ProtocolTests(unittest.TestCase):
    def test_secret_reconstruction(self):
        self.assertEqual(reconstruct(split_secret(123)), 123)

    def test_vector_reconstruction(self):
        shares = split_vector([12, 5, 9])
        self.assertEqual([sum(coordinate) % PRIME for coordinate in zip(*shares)], [12, 5, 9])

    def test_beaver_triple_relation(self):
        triple = make_beaver_triples(1)[0]
        a = sum(triple["a"]) % PRIME
        b = sum(triple["b"]) % PRIME
        c = sum(triple["c"]) % PRIME
        self.assertEqual(c, a * b % PRIME)

    def test_vector_share_dimensions_match_input(self):
        shares = split_vector([12, 5, 9, 3])
        self.assertEqual(len(shares), 3)
        self.assertEqual([len(share) for share in shares], [4, 4, 4])

    def test_authenticate_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            authenticate([], [], threshold=0)

    def test_authenticate_rejects_mismatched_dimensions(self):
        with self.assertRaises(ValueError):
            authenticate([1, 2], [1], threshold=1)

    @patch("src.protocol.PartyConnection", FakePartyConnection)
    def test_authenticate_accepts_distance_at_threshold(self):
        result = authenticate([2, 4], [1, 2], threshold=5)
        self.assertEqual(result["distance"], 5)
        self.assertTrue(result["accepted"])

    @patch("src.protocol.PartyConnection", FakePartyConnection)
    def test_authenticate_rejects_distance_above_threshold(self):
        result = authenticate([2, 4], [1, 2], threshold=4)
        self.assertEqual(result["distance"], 5)
        self.assertFalse(result["accepted"])


if __name__ == "__main__":
    unittest.main()