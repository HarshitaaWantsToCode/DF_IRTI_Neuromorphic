"""
Unit Tests for Neuromorphic Simulator and Attack Injection (Person 1).
"""
import pytest
import numpy as np
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.neuromorphic.topology import NeuromorphicTopology


def test_topology_initialization():
    topology = NeuromorphicTopology(num_cores=4, neurons_per_core=16)
    assert len(topology.intra_weights) == 4
    for c in range(4):
        w = topology.get_synaptic_weights(c)
        assert w.shape == (16, 16)
        assert np.all(np.diag(w) == 0.0)


def test_simulator_step():
    sim = NeuromorphicSimulator(num_cores=2, neurons_per_core=10)
    snapshot, spikes = sim.step(0)
    assert snapshot.step == 0
    assert len(snapshot.cores) == 2
    assert isinstance(spikes, list)


def test_attack_injection():
    sim = NeuromorphicSimulator(num_cores=4, neurons_per_core=16)
    attack_cfg = {
        "name": "Synaptic Test",
        "target_core": 1,
        "target_synapse_ratio": 0.5,
        "weight_shift": 3.0,
        "start_step": 2,
        "duration_steps": 5,
    }
    sim.attach_attack(attack_cfg)

    # Initial weights
    w_before = sim.topology.get_synaptic_weights(1).copy()
    sim.step(0)
    sim.step(1)
    sim.step(2)  # Attack triggers here
    w_after = sim.topology.get_synaptic_weights(1)

    assert not np.array_equal(w_before, w_after)
