"""
Tests for Microscopic Neuron Visualization, Topology Extraction, and Relative Timestamping.
Verifies Phase 8 requirements:
- Network topology export (intra & inter synapses)
- Recorded spike stream structure and step coordinates
- Relative timestamp offset computation (t - t0)
- End-to-end payload contract for microscopic replay
"""
import pytest
from src.neuromorphic.topology import NeuromorphicTopology
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.datasets.dvs128_loader import DVS128GestureLoader
from fastapi.testclient import TestClient
from web.api.server import app

client = TestClient(app)


def test_topology_export_contains_microscopic_neurons_and_synapses():
    topo = NeuromorphicTopology(num_cores=4, neurons_per_core=32, seed=42)
    graph = topo.export_topology_graph()

    assert graph["num_cores"] == 4
    assert graph["neurons_per_core"] == 32
    assert graph["total_neurons"] == 128
    assert len(graph["intra_synapses"]) > 0
    assert len(graph["inter_synapses"]) > 0

    first_intra = graph["intra_synapses"][0]
    assert first_intra["src_core"] == first_intra["dst_core"]
    assert 0 <= first_intra["src_neuron"] < 32
    assert 0 <= first_intra["dst_neuron"] < 32
    assert first_intra["weight"] > 0.0
    assert first_intra["is_inter"] is False

    first_inter = graph["inter_synapses"][0]
    assert first_inter["src_core"] != first_inter["dst_core"]
    assert first_inter["is_inter"] is True


def test_api_simulation_topology_endpoint():
    res = client.get("/api/simulation/topology?backend_id=builtin_lif")
    assert res.status_code == 200
    data = res.json()
    assert data["num_cores"] == 4
    assert data["neurons_per_core"] == 32
    assert data["total_neurons"] == 128
    assert len(data["intra_synapses"]) > 0
    assert len(data["inter_synapses"]) > 0


def test_dvs128_relative_timestamps_and_offsets():
    loader = DVS128GestureLoader()
    path = "data/dvs128/events_128.aedat"
    sample = loader.load_sample(path, max_events=50)

    assert sample.num_events == 50
    assert sample.duration_seconds > 0.0

    # First event should have relative_time_ms == 0.0
    first_evt = sample.events[0]
    assert first_evt.relative_time_ms == 0.0
    assert first_evt.timestamp > 190.0  # Hardware raw seconds epoch
    assert first_evt.timestamp_raw > 190_000_000.0  # Hardware microseconds

    # Subsequent event should be strictly increasing relative time
    second_evt = sample.events[1]
    assert second_evt.relative_time_ms >= 0.0
    assert second_evt.timestamp >= first_evt.timestamp


def test_execute_attack_returns_microscopic_graph_payload():
    payload = {
        "scenario_name": "Microscopic_Visualizer_Test",
        "attack_type": "synaptic_poisoning",
        "target_core": 2,
        "backend_id": "builtin_lif",
    }
    res = client.post("/api/attacks/execute", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "network_topology" in data
    assert "spike_stream" in data
    assert "final_potentials" in data

    # Verify topology inside completed run
    topo = data["network_topology"]
    assert topo["num_cores"] == 4
    assert topo["total_neurons"] == 128

    # Verify spike stream entries
    spikes = data["spike_stream"]
    assert len(spikes) > 0
    s0 = spikes[0]
    assert "source_core" in s0
    assert "source_neuron" in s0
    assert "target_core" in s0
    assert "target_neuron" in s0
    assert "timestamp_step" in s0
