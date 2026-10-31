"""
Tests for the FastAPI server powering the interactive dashboard.
Tests:
- Health check
- Datasets listing and sample inspection
- Backends capability querying (including Lava CPU unavailable status)
- Simulation stepping and reset
- Controlled attack workbench execution
"""
from fastapi.testclient import TestClient
from web.api.server import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "NeuroForensics"


def test_api_datasets():
    res = client.get("/api/datasets")
    assert res.status_code == 200
    datasets = res.json()
    assert len(datasets) >= 1
    # Check synthetic dataset presence
    synth_meta = next((d for d in datasets if "synthetic" in d["dataset_id"]), None)
    assert synth_meta is not None

    # Inspect samples
    samples_res = client.get(f"/api/datasets/{synth_meta['dataset_id']}/samples?limit=2")
    assert samples_res.status_code == 200
    samples_data = samples_res.json()
    assert len(samples_data["samples"]) == 2
    assert "preview_events" in samples_data["samples"][0]


def test_api_backends():
    res = client.get("/api/backends")
    assert res.status_code == 200
    backends = res.json()
    assert len(backends) == 2

    builtin = next(b for b in backends if b["backend_id"] == "builtin_lif_simulator")
    assert builtin["is_available"] is True
    assert builtin["observable_weights"] is True

    lava = next(b for b in backends if b["backend_id"] == "lava_cpu")
    # Verified operational through isolated Python 3.10 subprocess worker
    assert lava["is_available"] is True
    assert "Subprocess Worker" in lava["backend_name"]


def test_api_simulation_stepping():
    reset_res = client.post("/api/simulation/reset?backend_id=builtin_lif")
    assert reset_res.status_code == 200

    step_res = client.post("/api/simulation/step?backend_id=builtin_lif")
    assert step_res.status_code == 200
    data = step_res.json()
    assert data["step"] == 1
    assert "core_0" in data["membrane_potentials"]


def test_api_attack_execution():
    payload = {
        "scenario_name": "API_Poisoning_Test",
        "attack_type": "synaptic_poisoning",
        "target_core": 1,
        "weight_shift": 0.4,
        "start_step": 5,
        "duration_steps": 10,
        "backend_id": "builtin_lif",
    }
    res = client.post("/api/attacks/execute", json=payload)
    assert res.status_code == 200
    result = res.json()
    assert "metrics" in result
    assert "reconstruction" in result
    assert "timeline" in result
    assert "sufficiency" in result
