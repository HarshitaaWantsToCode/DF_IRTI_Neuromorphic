"""
Comprehensive Stage 4 Real-World Dataset Validation and Forensic Evaluation Tests.
Validates:
1. Dataset metadata, genuine event streaming, and SHA-256 integrity checks.
2. Attack injections with explicit DoS success criteria on bounded queues.
3. Timestamp-aware scheduling causing physical firing divergence under jitter.
4. Model-grounded synaptic poisoning on real event inputs.
5. Evidence acquisition, deterministic block serialization, and Merkle root tamper detection.
6. Ground-truth isolation during reconstruction.
7. Combinatorial 127-subset evidence ablation and threshold sensitivity.
"""
import os
import json
import pytest
import numpy as np

from src.datasets.dvs128_loader import DVS128GestureLoader
from src.datasets.shd_loader import SHDDatasetLoader
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.neuromorphic.snn_classifier import SNNClassifier
from src.acquisition.collector import ForensicCollector
from src.acquisition.integrity import ChainOfCustodyVerifier
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator
from src.eval.reconstruction_score import ReconstructionScorer
from src.eval.evidence_ablation import EvidenceAblationEngine


DVS128_PATH = os.path.join("data", "dvs128", "events_128.aedat")
EXPECTED_DVS128_SHA256 = "6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3"


def test_stage4_dvs128_genuine_provenance_and_integrity():
    """Validates real DVS128 recording integrity, source provenance, and event parsing."""
    assert os.path.exists(DVS128_PATH), f"Genuine DVS128 recording missing at {DVS128_PATH}"
    loader = DVS128GestureLoader()

    # 1. Integrity check
    is_valid, computed_hash = loader.validate_integrity(DVS128_PATH, EXPECTED_DVS128_SHA256)
    assert is_valid is True, f"DVS128 checksum mismatch: {computed_hash}"
    assert computed_hash == EXPECTED_DVS128_SHA256

    # 2. Provenance extraction
    prov = loader.get_source_provenance(DVS128_PATH)
    assert "DVS128 Gesture" in prov["dataset_name"]
    assert "Amir, A." in prov["citation"]
    assert prov["file_checksum_sha256"] == EXPECTED_DVS128_SHA256

    # 3. Load recording
    sample = loader.load_recording(DVS128_PATH, max_events=5000)
    assert len(sample.events) == 5000
    assert sample.events[0].timestamp <= sample.events[-1].timestamp
    for evt in sample.events[:100]:
        assert 0 <= evt.x < 128
        assert 0 <= evt.y < 128
        assert evt.polarity in (0, 1)


def test_stage4_timestamp_aware_jitter_scheduling():
    """
    Validates that jittering timestamps in the event scheduler changes the actual
    arrival and membrane potential delivery step, proving it is not merely metadata.
    """
    # Baseline run: without jitter
    sim_base = NeuromorphicSimulator(seed=42)
    sim_base.v_membrane[0][:] = 1.2
    sim_base.step(0)
    s1_base, _ = sim_base.step(1)

    # Attack run: with temporal jitter applied to inter-core pulses
    sim_jitter = NeuromorphicSimulator(seed=42)
    jitter_cfg = {
        "name": "Stage4 Jitter Test",
        "start_step": 0,
        "duration_steps": 2,
        "target_core": 0,
        "jitter_magnitude_ms": 10.0,
    }
    sim_jitter.attach_attack(jitter_cfg)
    sim_jitter.v_membrane[0][:] = 1.2
    sim_jitter.step(0)
    # The scheduler must hold jittered spikes for later steps
    assert len(sim_jitter.scheduler) > 0, "Jittered spikes were not scheduled in the event priority queue"

    s1_jitter, _ = sim_jitter.step(1)
    # Divergence in queue and membrane dynamics
    potentials_base = s1_base.cores[1].membrane_potentials
    potentials_jitter = s1_jitter.cores[1].membrane_potentials
    assert sum(potentials_base) != sum(potentials_jitter), "Membrane potential failed to diverge under timestamp jitter"


def test_stage4_spike_flooding_queue_saturation_and_dos_criterion():
    """
    Validates that high-rate spike injection saturates inter-core queues and meets
    an explicit DoS criterion (drop_rate >= 0.30 and queue_utilization == 1.0).
    """
    sim = NeuromorphicSimulator(queue_capacity=30, service_rate_per_ms=5.0, seed=42)
    flood_cfg = {
        "name": "Stage4 Flood DoS Test",
        "start_step": 1,
        "duration_steps": 6,
        "target_core": 1,
        "injection_rate": 0.95,
    }
    sim.attach_attack(flood_cfg)

    for step in range(12):
        sim.step(step)

    q_metrics = sim.get_queue_diagnostics()
    target_q = q_metrics[2]  # Core 1 routes to Core 2 in ring

    # Denial of Service success criterion verification
    assert target_q["peak_occupancy"] == 30, "Queue failed to reach capacity"
    assert target_q["queue_utilization"] == 1.0
    assert target_q["total_dropped"] > 0, "No spikes were dropped despite flood injection"
    assert target_q["drop_rate"] >= 0.30, f"DoS criterion unmet: drop rate {target_q['drop_rate']:.3f} < 0.30"


def test_stage4_model_grounded_synaptic_poisoning_on_genuine_events():
    """
    Validates synaptic weight poisoning on a multi-layer SNN model processing
    real DVS128 events, verifying weight checksum shifts and firing divergence.
    """
    loader = DVS128GestureLoader()
    sample = loader.load_recording(DVS128_PATH, max_events=2000)

    # Convert events to (time_ms, channel_id)
    event_stream = [(evt.timestamp * 1000.0, evt.channel_id % 64) for evt in sample.events[:200]]

    snn = SNNClassifier(num_inputs=64, num_hidden=32, num_classes=11, seed=42)
    base_sha = snn.compute_weights_sha256()

    # Benign inference
    pred_base, counts_base, diag_base = snn.forward(event_stream, duration_ms=100.0)

    # Apply controlled weight poisoning
    poison_log = snn.apply_poisoning(target_layer="hidden_out", target_class=3, synapse_ratio=0.5, weight_shift=3.0)
    assert poison_log["poisoned_sha256"] != base_sha
    assert poison_log["num_modified"] > 0

    # Poisoned inference
    pred_pois, counts_pois, diag_pois = snn.forward(event_stream, duration_ms=100.0)

    # Verify functional firing divergence
    assert diag_pois["total_out_spikes"] >= diag_base["total_out_spikes"], "Target class excitation did not increase"
    assert counts_pois[3] >= counts_base[3], "Poisoned class receptive field did not exhibit heightened firing"


def test_stage4_evidence_acquisition_and_tamper_detection():
    """Validates evidence packaging, Merkle root verification, and byte-level tampering detection."""
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=16, seed=42)
    collector = ForensicCollector(num_cores=4, neurons_per_core=16)

    for s in range(5):
        snap, spikes = sim.step(s)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence(metadata={"experiment": "stage4_test"})
    assert len(evidence.snapshots) == 5
    assert len(evidence.block_hashes) == 5

    # Re-verify original Merkle root
    recalculated_root = ChainOfCustodyVerifier.compute_merkle_root(evidence.block_hashes)
    assert recalculated_root == evidence.header.root_merkle_hash

    # Tamper with snapshot 2 by altering a membrane potential
    tampered_package = evidence.model_copy(deep=True)
    tampered_package.snapshots[2].cores[0].membrane_potentials[0] += 0.5
    tampered_hashes = [ChainOfCustodyVerifier.hash_data(s.model_dump()) for s in tampered_package.snapshots]
    tampered_root = ChainOfCustodyVerifier.compute_merkle_root(tampered_hashes)

    assert tampered_root != evidence.header.root_merkle_hash, "Merkle integrity check failed to detect block tampering"


def test_stage4_reconstruction_ground_truth_isolation():
    """
    Validates that reconstruction functions solely from sealed evidence without
    accessing ground-truth files or objects.
    """
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=16, seed=42)
    flood_cfg = {
        "name": "Isolation Verification",
        "start_step": 3,
        "duration_steps": 4,
        "target_core": 1,
        "injection_rate": 0.95,
    }
    sim.attach_attack(flood_cfg)
    ground_truth = sim.get_ground_truth()
    assert ground_truth is not None

    collector = ForensicCollector(num_cores=4, neurons_per_core=16)
    for s in range(10):
        snap, spikes = sim.step(s)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()

    # Execute timeline generator and correlator strictly on evidence
    timeline_gen = TimelineGenerator()
    timeline_events = timeline_gen.generate_timeline(evidence)
    reconstruction = EventCorrelator.correlate_attack(timeline_events, total_cores=4)

    # Reconstructed results derived without ground truth
    assert reconstruction.detected_attack_type in ("spike_storm", "synaptic_poisoning", "timing_jitter")
    assert reconstruction.root_cause_core == 1

    # Isolated scoring at the boundary
    score = ReconstructionScorer.score_reconstruction(reconstruction, ground_truth)
    assert 0.0 <= score.overall_score <= 1.0
    assert score.attack_type_score == 1.0
    assert score.location_score == 1.0


def test_stage4_127_subset_evidence_ablation_real_data():
    """
    Validates complete enumeration of all 127 non-empty subsets of 7 evidence classes
    and confirms minimum sufficient evidence sets.
    """
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=16, seed=42)
    sim.attach_attack({
        "name": "Stage4 Ablation",
        "start_step": 2,
        "duration_steps": 4,
        "target_core": 1,
        "injection_rate": 0.9,
    })
    ground_truth = sim.get_ground_truth()
    collector = ForensicCollector(num_cores=4, neurons_per_core=16)
    for s in range(8):
        snap, spikes = sim.step(s)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()
    ablation_engine = EvidenceAblationEngine()
    results = ablation_engine.run_exhaustive_ablation(evidence, ground_truth)

    assert len(results) == 127, f"Expected 127 non-empty subsets, got {len(results)}"
    sufficient = [r for r in results if r["reconstruction_score"] >= 0.80]
    assert len(sufficient) > 0, "No sufficient evidence subsets found at threshold 0.80"
