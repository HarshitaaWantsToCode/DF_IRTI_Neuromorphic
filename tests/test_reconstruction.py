"""
Unit Tests for Reconstruction Engine (Person 3).
"""
import pytest
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.acquisition.collector import ForensicCollector
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator


def test_timeline_reconstruction():
    sim = NeuromorphicSimulator(num_cores=3, neurons_per_core=8)
    attack_cfg = {
        "name": "Weight Attack",
        "target_core": 1,
        "target_synapse_ratio": 0.8,
        "weight_shift": 4.0,
        "start_step": 2,
        "duration_steps": 3,
    }
    sim.attach_attack(attack_cfg)
    collector = ForensicCollector(num_cores=3, neurons_per_core=8)

    for i in range(6):
        snap, spikes = sim.step(i)
        collector.record_step(snap, spikes)

    evidence = collector.seal_evidence()
    timeline_gen = TimelineGenerator()
    events = timeline_gen.generate_timeline(evidence)
    assert len(events) > 0

    reconstruction = EventCorrelator.correlate_attack(events, total_cores=3)
    assert reconstruction.root_cause_core == 1
