"""Synthetic enrollment and 2-of-3 Shamir share storage."""

from __future__ import annotations

import json
import re
import secrets
from pathlib import Path
from typing import Any, Sequence

from .protocol import PARTY_COUNT, PRIME, authenticate as run_mpc_authentication, mod

SHAMIR_THRESHOLD = 2
STORAGE_VERSION = 1
USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


class EnrollmentError(ValueError):
    """Raised when enrollment storage or input validation fails."""


def validate_user_id(user_id: str) -> None:
    if not isinstance(user_id, str) or not USER_ID_PATTERN.fullmatch(user_id):
        raise EnrollmentError("user_id must be 1-64 characters: letters, digits, _, ., or -")


def validate_vector(vector: Sequence[int]) -> list[int]:
    if isinstance(vector, (str, bytes)) or not vector:
        raise EnrollmentError("feature vector must be a non-empty sequence of integers")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in vector):
        raise EnrollmentError("feature vector values must be integers")
    return [mod(value) for value in vector]


def split_shamir_secret(value: int, rng: Any = secrets) -> list[dict[str, int]]:
    """Create three points from a degree-one polynomial with f(0) == value."""
    slope = rng.randbelow(PRIME)
    return [
        {"x": party_id, "y": mod(value + slope * party_id)}
        for party_id in range(1, PARTY_COUNT + 1)
    ]


def split_shamir_vector(vector: Sequence[int], rng: Any = secrets) -> list[list[dict[str, int]]]:
    normalized_vector = validate_vector(vector)
    shares = [[] for _ in range(PARTY_COUNT)]
    for value in normalized_vector:
        for party_index, point in enumerate(split_shamir_secret(value, rng)):
            shares[party_index].append(point)
    return shares


def reconstruct_shamir_secret(points: Sequence[dict[str, int]]) -> int:
    if len(points) < SHAMIR_THRESHOLD:
        raise EnrollmentError("at least two Shamir points are required")
    selected_points = points[:SHAMIR_THRESHOLD]
    result = 0
    for index, point in enumerate(selected_points):
        numerator = 1
        denominator = 1
        for other_index, other_point in enumerate(selected_points):
            if index == other_index:
                continue
            numerator = mod(numerator * (-other_point["x"]))
            denominator = mod(denominator * (point["x"] - other_point["x"]))
        result = mod(result + point["y"] * numerator * pow(denominator, PRIME - 2, PRIME))
    return result


def reconstruct_shamir_vector(share_vectors: Sequence[Sequence[dict[str, int]]]) -> list[int]:
    if len(share_vectors) < SHAMIR_THRESHOLD:
        raise EnrollmentError("at least two party share vectors are required")
    dimensions = {len(vector) for vector in share_vectors}
    if len(dimensions) != 1 or not dimensions.pop():
        raise EnrollmentError("share vectors must have the same non-zero dimension")
    return [
        reconstruct_shamir_secret([vector[index] for vector in share_vectors[:SHAMIR_THRESHOLD]])
        for index in range(len(share_vectors[0]))
    ]


class EnrollmentStore:
    """Stores one JSON share file per party for synthetic templates."""

    def __init__(self, party_paths: Sequence[str | Path]) -> None:
        if len(party_paths) != PARTY_COUNT:
            raise EnrollmentError(f"exactly {PARTY_COUNT} party paths are required")
        self.party_paths = [Path(path) for path in party_paths]

    def enroll(self, user_id: str, vector: Sequence[int], replace: bool = False) -> None:
        validate_user_id(user_id)
        normalized_vector = validate_vector(vector)
        documents = self._load_documents()
        existing = any(user_id in document["users"] for document in documents)
        if existing and not replace:
            raise EnrollmentError(f"user already enrolled: {user_id}")
        shares = split_shamir_vector(normalized_vector)
        updated_documents = []
        for party_index, document in enumerate(documents):
            document["users"][user_id] = {
                "dimension": len(normalized_vector),
                "shares": shares[party_index],
            }
            updated_documents.append(document)
        self._write_documents(updated_documents)

    def authenticate(self, user_id: str, query: Sequence[int], threshold: int) -> dict[str, Any]:
        validate_user_id(user_id)
        normalized_query = validate_vector(query)
        template = self.load_template(user_id)
        if len(normalized_query) != len(template):
            raise EnrollmentError("query dimension does not match enrolled template")
        result = run_mpc_authentication(normalized_query, template, threshold)
        return {"user_id": user_id, "accepted": bool(result["accepted"])}

    def load_template(self, user_id: str) -> list[int]:
        validate_user_id(user_id)
        available_shares = []
        for party_index, document in enumerate(self._load_documents()):
            record = document["users"].get(user_id)
            if record is None:
                continue
            available_shares.append((party_index, record))
        if len(available_shares) < SHAMIR_THRESHOLD:
            raise EnrollmentError(f"not enough shares available for user: {user_id}")
        selected = available_shares[:SHAMIR_THRESHOLD]
        dimensions = {record["dimension"] for _, record in selected}
        if len(dimensions) != 1 or not dimensions.pop():
            raise EnrollmentError("stored share dimensions do not match")
        share_vectors = []
        for party_index, record in selected:
            share_vectors.append([
                {"x": party_index + 1, "y": int(point["y"])}
                for point in record["shares"]
            ])
        return reconstruct_shamir_vector(share_vectors)

    def delete(self, user_id: str) -> None:
        validate_user_id(user_id)
        documents = self._load_documents()
        if not any(user_id in document["users"] for document in documents):
            raise EnrollmentError(f"user is not enrolled: {user_id}")
        for document in documents:
            document["users"].pop(user_id, None)
        self._write_documents(documents)

    def _load_documents(self) -> list[dict[str, Any]]:
        documents = []
        for party_index, path in enumerate(self.party_paths):
            if not path.exists():
                documents.append(self._empty_document(party_index))
                continue
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise EnrollmentError(f"cannot read party {party_index} share file") from error
            self._validate_document(document, party_index)
            documents.append(document)
        return documents

    def _write_documents(self, documents: Sequence[dict[str, Any]]) -> None:
        temporary_paths = []
        try:
            for path, document in zip(self.party_paths, documents):
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary_path = path.with_suffix(path.suffix + ".tmp")
                temporary_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                temporary_paths.append((temporary_path, path))
            for temporary_path, path in temporary_paths:
                temporary_path.replace(path)
        except OSError as error:
            for temporary_path, _ in temporary_paths:
                temporary_path.unlink(missing_ok=True)
            raise EnrollmentError("could not persist party share files") from error

    @staticmethod
    def _empty_document(party_index: int) -> dict[str, Any]:
        return {
            "version": STORAGE_VERSION,
            "threshold": SHAMIR_THRESHOLD,
            "party_id": party_index,
            "users": {},
        }

    @staticmethod
    def _validate_document(document: Any, party_index: int) -> None:
        if not isinstance(document, dict):
            raise EnrollmentError("party share file must contain a JSON object")
        if document.get("version") != STORAGE_VERSION or document.get("threshold") != SHAMIR_THRESHOLD:
            raise EnrollmentError("unsupported party share file format")
        if document.get("party_id") != party_index or not isinstance(document.get("users"), dict):
            raise EnrollmentError("invalid party share file metadata")
        for user_id, record in document["users"].items():
            validate_user_id(user_id)
            if not isinstance(record, dict) or not isinstance(record.get("shares"), list):
                raise EnrollmentError("invalid stored user share record")
            if record.get("dimension") != len(record["shares"]) or not record["shares"]:
                raise EnrollmentError("invalid stored share dimension")
            for point in record["shares"]:
                if not isinstance(point, dict) or not isinstance(point.get("y"), int):
                    raise EnrollmentError("invalid stored share point")
