"""
Unit Tests for Forensic Acquisition, Cryptographic Chain of Custody, and Tamper Detection (Person 2).
"""
import os
import pytest
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.acquisition.collector import ForensicCollector
from src.acquisition.integrity import ChainOfCustodyVerifier
from src.acquisition.dump_format import NFDSerializer


def test_acquisition_and_merkle_verification(tmp_path):
    sim = NeuromorphicSimulator(num_cores=2, neurons_per_core=8)
    collector = ForensicCollector(num_cores=2, neurons_per_core=8)

    for i in range(5):
        snap, spikes = sim.step(i)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence({"experiment": "test"})
    assert evidence.header.total_steps == 5
    assert len(evidence.block_hashes) == 5

    # Check Merkle verification
    is_valid = ChainOfCustodyVerifier.verify_integrity(evidence.model_dump())
    assert is_valid is True

    # Test serialization to .nfd
    dump_file = os.path.join(tmp_path, "test_dump.nfd")
    saved_path = collector.export_dump(dump_file, compress=False)
    assert os.path.exists(saved_path)

    # Load back
    loaded_pkg = NFDSerializer.load_dump(saved_path)
    assert loaded_pkg.header.root_merkle_hash == evidence.header.root_merkle_hash


def test_evidence_tamper_detection():
    """Verifies that altering any acquired snapshot breaks the Merkle tree verification."""
    sim = NeuromorphicSimulator(num_cores=2, neurons_per_core=8)
    collector = ForensicCollector(num_cores=2, neurons_per_core=8)

    for i in range(5):
        snap, spikes = sim.step(i)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()
    evidence_dict = evidence.model_dump()

    # Tamper with membrane potential in snapshot 2, Core 0
    evidence_dict["snapshots"][2]["cores"][0]["membrane_potentials"][0] += 0.99

    # Re-verify integrity
    is_valid = ChainOfCustodyVerifier.verify_integrity(evidence_dict)
    assert is_valid is False, "Tampered evidence should fail cryptographic verification!"
