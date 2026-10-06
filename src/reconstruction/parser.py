"""
Evidence Parser and Validator for Reconstruction Engine (Person 3).
"""
from typing import Tuple
from src.core.schemas import EvidencePackage
from src.acquisition.dump_format import NFDSerializer
from src.acquisition.integrity import ChainOfCustodyVerifier


class EvidenceParser:
    """Loads, validates, and unpacks .nfd forensic containers for timeline reconstruction."""

    @staticmethod
    def parse_and_validate(file_path: str) -> Tuple[EvidencePackage, bool]:
        """Loads a dump file and verifies cryptographic integrity."""
        package = NFDSerializer.load_dump(file_path)
        is_valid = ChainOfCustodyVerifier.verify_integrity(package.model_dump())
        return package, is_valid
