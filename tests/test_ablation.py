"""
Unit Tests for Evidence Sufficiency, Ablation Engine, and Deterministic Scoring.
"""
import pytest
from src.core.schemas import ArtifactClass
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.acquisition.collector import ForensicCollector
from src.eval.evidence_ablation import EvidenceAblationEngine
from src.eval.evidence_filter import EvidenceFilter
from src.eval.reconstruction_score import ReconstructionScorer
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator


def test_evidence_subset_filtering():
    sim = NeuromorphicSimulator(num_cores=3, neurons_per_core=8)
    collector = ForensicCollector(num_cores=3, neurons_per_core=8)

    for i in range(5):
        snap, spks = sim.step(i)
        collector.record_step(snap, spks)

    full_evidence = collector.seal_evidence()

    # Filter to only SPIKE_EVENTS
    filtered = EvidenceFilter.filter_evidence(full_evidence, {ArtifactClass.SPIKE_EVENTS})
    assert ArtifactClass.SPIKE_EVENTS in filtered.header.included_artifacts
    assert ArtifactClass.SYNAPTIC_STATE not in filtered.header.included_artifacts

    # Check snapshots
    for snap in filtered.snapshots:
        for c_id, core_st in snap.cores.items():
            assert core_st.synaptic_weights is None
            assert core_st.membrane_potentials is None


def test_reconstruction_scoring_and_ground_truth_separation():
    sim = NeuromorphicSimulator(num_cores=3, neurons_per_core=8, seed=42)
    attack_cfg = {
        "name": "Weight Attack",
        "target_core": 1,
        "target_synapse_ratio": 0.8,
        "weight_shift": 4.0,
        "start_step": 2,
        "duration_steps": 3,
    }
    sim.attach_attack(attack_cfg)
    ground_truth = sim.get_ground_truth()
    assert ground_truth.attack_type == "synaptic_poisoning"
    assert ground_truth.target_core == 1

    collector = ForensicCollector(num_cores=3, neurons_per_core=8)
    for i in range(6):
        snap, spks = sim.step(i)
        collector.record_step(snap, spks)

    evidence = collector.seal_evidence()

    # Reconstruct from evidence ONLY
    timeline_gen = TimelineGenerator()
    events = timeline_gen.generate_timeline(evidence)
    reconstruction = EventCorrelator.correlate_attack(events, total_cores=3)

    # Deterministic Scoring
    score = ReconstructionScorer.score_reconstruction(reconstruction, ground_truth, threshold=0.8)
    assert score.location_score == 1.0
    assert score.attack_type_score == 1.0
    assert score.overall_score >= 0.8
    assert score.passed_threshold is True


def test_evidence_ablation_degradation_and_minimum_sufficient_sets():
    sim = NeuromorphicSimulator(num_cores=3, neurons_per_core=8, seed=42)
    attack_cfg = {
        "name": "Weight Attack",
        "target_core": 1,
        "target_synapse_ratio": 0.8,
        "weight_shift": 4.0,
        "start_step": 2,
        "duration_steps": 3,
    }
    sim.attach_attack(attack_cfg)
    ground_truth = sim.get_ground_truth()

    collector = ForensicCollector(num_cores=3, neurons_per_core=8)
    for i in range(6):
        snap, spks = sim.step(i)
        collector.record_step(snap, spks)

    full_evidence = collector.seal_evidence()

    ablation_engine = EvidenceAblationEngine(candidate_classes=[
        ArtifactClass.SPIKE_EVENTS,
        ArtifactClass.SPIKE_TIMING,
        ArtifactClass.SYNAPTIC_STATE,
        ArtifactClass.NEURON_STATE,
    ])

    # 1. Full evidence evaluation
    full_eval = ablation_engine.evaluate_subset(
        full_evidence,
        ground_truth,
        [ArtifactClass.SPIKE_EVENTS, ArtifactClass.SPIKE_TIMING, ArtifactClass.SYNAPTIC_STATE, ArtifactClass.NEURON_STATE],
    )
    assert full_eval["reconstruction_score"] >= 0.80

    # 2. Ablated evidence evaluation (removing SYNAPTIC_STATE for synaptic attack)
    ablated_eval = ablation_engine.evaluate_subset(
        full_evidence,
        ground_truth,
        [ArtifactClass.SPIKE_EVENTS, ArtifactClass.SPIKE_TIMING],
    )
    # Removing synaptic state for synaptic attack must significantly degrade identification and score
    assert ablated_eval["reconstruction_score"] < full_eval["reconstruction_score"]

    # 3. Minimum Sufficient Evidence Calculation
    min_info = ablation_engine.find_minimum_sufficient_evidence(
        full_evidence,
        ground_truth,
        reconstruction_threshold=0.80,
    )
    assert min_info["minimum_cardinality"] is not None
    assert len(min_info["minimum_sufficient_sets"]) >= 1
    # Check that every minimal sufficient set contains SYNAPTIC_STATE
    for s in min_info["minimum_sufficient_sets"]:
        assert ArtifactClass.SYNAPTIC_STATE.value in s
