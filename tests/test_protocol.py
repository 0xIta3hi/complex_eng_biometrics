import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

from src.enrollment import (
    EnrollmentError,
    EnrollmentStore,
    reconstruct_shamir_secret,
    split_shamir_secret,
)
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


class EnrollmentTests(unittest.TestCase):
    def make_store(self, temporary_directory: str) -> EnrollmentStore:
        return EnrollmentStore([
            Path(temporary_directory) / "party-0.json",
            Path(temporary_directory) / "party-1.json",
            Path(temporary_directory) / "party-2.json",
        ])

    def test_shamir_secret_reconstructs_from_any_two_points(self):
        points = split_shamir_secret(123)
        self.assertEqual(reconstruct_shamir_secret(points[:2]), 123)
        self.assertEqual(reconstruct_shamir_secret(points[::2]), 123)
        self.assertEqual(reconstruct_shamir_secret(points[1:]), 123)

    def test_enrollment_persists_one_json_file_per_party(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            store.enroll("alice", [12, 5, 9])

            for party_path in store.party_paths:
                self.assertTrue(party_path.exists())
            self.assertEqual(store.load_template("alice"), [12, 5, 9])

    def test_template_load_survives_one_missing_party_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            store.enroll("alice", [12, 5, 9])
            store.party_paths[1].unlink()

            self.assertEqual(store.load_template("alice"), [12, 5, 9])

    def test_enrollment_rejects_duplicate_and_supports_replacement(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            store.enroll("alice", [1, 2])
            with self.assertRaises(EnrollmentError):
                store.enroll("alice", [3, 4])

            store.enroll("alice", [3, 4], replace=True)
            self.assertEqual(store.load_template("alice"), [3, 4])

    def test_delete_removes_enrolled_user(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            store.enroll("alice", [1, 2])
            store.delete("alice")

            with self.assertRaises(EnrollmentError):
                store.load_template("alice")

    def test_authentication_uses_stored_template_and_returns_decision_only(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            store.enroll("alice", [10, 20])
            with patch("src.enrollment.run_mpc_authentication", return_value={"accepted": True, "distance": 0}) as mocked:
                result = store.authenticate("alice", [10, 20], threshold=0)

            self.assertEqual(result, {"user_id": "alice", "accepted": True})
            mocked.assert_called_once_with([10, 20], [10, 20], 0)

    def test_invalid_enrollment_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = self.make_store(temporary_directory)
            with self.assertRaises(EnrollmentError):
                store.enroll("bad user", [1, 2])
            with self.assertRaises(EnrollmentError):
                store.enroll("alice", [])
            with self.assertRaises(EnrollmentError):
                store.enroll("alice", [1, True])


if __name__ == "__main__":
    unittest.main()