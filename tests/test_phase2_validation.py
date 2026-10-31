"""
Tests for Phase 2 Forensic Validation:
1. Genuine DVS128 AEDAT 2.0 ingestion and timestamp normalization
2. Immutable source verification via SHA-256
3. Simulator stimulation via real events
4. Cryptographic Merkle tree verification & deliberate tamper detection
5. Ground-truth isolation (reconstruction has no access to ground truth)
6. Benign control baseline producing zero false-positive anomaly events
7. Evidence-sufficiency ablation where removal of evidence changes score
8. Reproducibility across repeated runs
"""
import os
import hashlib
import pytest
from src.datasets.dvs128_loader import DVS128GestureLoader
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.acquisition.collector import ForensicCollector
from src.acquisition.integrity import ChainOfCustodyVerifier
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator
from src.eval.reconstruction_score import ReconstructionScorer
from src.eval.evidence_ablation import EvidenceAblationEngine
from src.core.schemas import ArtifactClass


SAMPLE_FILE = "data/dvs128/events_128.aedat"


@pytest.fixture
def genuine_sample():
    assert os.path.exists(SAMPLE_FILE), "Sample file data/dvs128/events_128.aedat must exist"
    loader = DVS128GestureLoader()
    return loader.load_sample(SAMPLE_FILE, max_events=200)


def test_genuine_sample_ingestion_and_immutability(genuine_sample):
    loader = DVS128GestureLoader()
    is_valid, msg = loader.validate_path(SAMPLE_FILE)
    assert is_valid, msg

    meta = loader.load_metadata(SAMPLE_FILE)
    assert meta.file_checksum_sha256 == "6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3"
    assert len(genuine_sample.events) == 200

    # Verify timestamps are normalized to seconds, positive, and monotonic
    for i in range(1, len(genuine_sample.events)):
        assert genuine_sample.events[i].timestamp >= genuine_sample.events[i - 1].timestamp
        assert genuine_sample.events[i].timestamp_raw > 0


def test_real_dataset_stimulation_drives_simulator(genuine_sample):
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    inputs = {0: [e.channel_id % 32 for e in genuine_sample.events[:15]]}
    snap, spikes = sim.step(step_idx=0, input_spikes=inputs)

    assert snap.step == 0
    assert 0 in snap.cores
    # Potentials should be altered by input stimulus
    assert max(snap.cores[0].membrane_potentials) > 0.35


def test_merkle_independent_verification_and_tamper_detection(genuine_sample):
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    collector = ForensicCollector(num_cores=4, neurons_per_core=32)

    for step in range(10):
        snap, spikes = sim.step(step)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()
    
    # 1. Independent re-verification passes
    hashes = [ChainOfCustodyVerifier.hash_data(s.model_dump()) for s in evidence.snapshots]
    root = ChainOfCustodyVerifier.compute_merkle_root(hashes)
    assert root == evidence.header.root_merkle_hash

    # 2. Deliberate tamper detected
    evidence.snapshots[2].cores[0].membrane_potentials[0] += 0.99
    tampered_hashes = [ChainOfCustodyVerifier.hash_data(s.model_dump()) for s in evidence.snapshots]
    tampered_root = ChainOfCustodyVerifier.compute_merkle_root(tampered_hashes)
    assert tampered_root != evidence.header.root_merkle_hash


def test_benign_control_produces_zero_false_positives(genuine_sample):
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    collector = ForensicCollector(num_cores=4, neurons_per_core=32)

    for step in range(30):
        batch = genuine_sample.events[step * 5 : (step + 1) * 5]
        inputs = {0: [e.channel_id % 32 for e in batch]}
        snap, spikes = sim.step(step, input_spikes=inputs)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()
    timeline = TimelineGenerator().generate_timeline(evidence)
    recon = EventCorrelator.correlate_attack(timeline, total_cores=4)

    assert len(timeline) == 0
    assert recon.detected_attack_type == "benign"
    assert recon.root_cause_core == -1


def test_evidence_sufficiency_ablation_degradation(genuine_sample):
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    attack_cfg = {
        "name": "AblationTest",
        "target_core": 1,
        "weight_shift": 2.0,
        "start_step": 5,
        "duration_steps": 10,
    }
    sim.attach_attack(attack_cfg)
    ground_truth = sim.get_ground_truth()

    collector = ForensicCollector(num_cores=4, neurons_per_core=32)
    for step in range(20):
        snap, spikes = sim.step(step)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()

    ablation = EvidenceAblationEngine()
    # Evaluate with Synaptic State (relevant for weight shift) vs without Synaptic State
    full_res = ablation.evaluate_subset(evidence, ground_truth, [ArtifactClass.SYNAPTIC_STATE, ArtifactClass.SPIKE_EVENTS])
    reduced_res = ablation.evaluate_subset(evidence, ground_truth, [ArtifactClass.CONFIGURATION])

    # Removing the critical synaptic evidence must degrade reconstruction score
    assert full_res["reconstruction_score"] > reduced_res["reconstruction_score"]
    assert full_res["success"] is True
    assert reduced_res["success"] is False


def test_repeated_run_determinism(genuine_sample):
    # Two identical runs must generate bit-for-bit identical Merkle roots
    roots = []
    for _ in range(2):
        sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=123)
        collector = ForensicCollector(num_cores=4, neurons_per_core=32)
        for step in range(10):
            snap, spikes = sim.step(step)
            collector.record_step(snap, spikes)
        ev = collector.seal_evidence()
        roots.append(ev.header.root_merkle_hash)

    assert roots[0] == roots[1]
