"""
Cryptographic Integrity and Chain-of-Custody for Neuromorphic Evidence (Person 2).
"""
import hashlib
import json
from typing import List, Any


class ChainOfCustodyVerifier:
    """Computes cryptographic hashes and Merkle roots to ensure evidence cannot be tampered with post-acquisition."""

    @staticmethod
    def hash_data(data: Any) -> str:
        """Computes SHA-256 hash of a python dict or string data."""
        if isinstance(data, (dict, list)):
            encoded = json.dumps(data, sort_keys=True).encode("utf-8")
        else:
            encoded = str(data).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def compute_merkle_root(cls, hashes: List[str]) -> str:
        """Constructs a Merkle Tree from a list of snapshot hashes and returns the root hash."""
        if not hashes:
            return hashlib.sha256(b"empty").hexdigest()
        
        current_layer = list(hashes)
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                if i + 1 < len(current_layer):
                    combined = (current_layer[i] + current_layer[i + 1]).encode("utf-8")
                else:
                    combined = (current_layer[i] + current_layer[i]).encode("utf-8")
                next_layer.append(hashlib.sha256(combined).hexdigest())
            current_layer = next_layer
        
        return current_layer[0]

    @classmethod
    def verify_integrity(cls, evidence_dict: dict) -> bool:
        """Verifies whether the Merkle root matches the re-computed hashes of all snapshot blocks."""
        stored_root = evidence_dict.get("header", {}).get("root_merkle_hash")
        snapshots = evidence_dict.get("snapshots", [])
        computed_hashes = [cls.hash_data(s) for s in snapshots]
        computed_root = cls.compute_merkle_root(computed_hashes)
        return stored_root == computed_root
