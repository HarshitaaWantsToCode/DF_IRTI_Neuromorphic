"""
Serializer and Deserializer for Neuromorphic Forensic Dump (.nfd) files (Person 2).
"""
import json
import gzip
import os
from typing import Dict, Any
from src.core.schemas import EvidencePackage


class NFDSerializer:
    """Manages the disk persistence and schema compliance of .nfd files."""

    @staticmethod
    def save_dump(evidence: EvidencePackage, file_path: str, compress: bool = True) -> str:
        """Saves an EvidencePackage to disk as a .nfd container."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        dump_data = evidence.model_dump()

        if compress:
            if not file_path.endswith(".nfd.gz") and not file_path.endswith(".nfd"):
                file_path += ".nfd.gz"
            with gzip.open(file_path, "wt", encoding="utf-8") as f:
                json.dump(dump_data, f, indent=2)
        else:
            if not file_path.endswith(".nfd"):
                file_path += ".nfd"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dump_data, f, indent=2)

        return file_path

    @staticmethod
    def load_dump(file_path: str) -> EvidencePackage:
        """Loads a .nfd or .nfd.gz dump file and deserializes into EvidencePackage."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"NFD dump file not found: {file_path}")

        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        return EvidencePackage(**data)
