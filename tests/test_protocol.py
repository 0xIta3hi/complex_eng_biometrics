import unittest

from src.protocol import PRIME, make_beaver_triples, reconstruct, split_secret, split_vector


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


if __name__ == "__main__":
    unittest.main()