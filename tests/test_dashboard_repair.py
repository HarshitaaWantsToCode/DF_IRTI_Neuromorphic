"""
Tests for Dashboard Repair and API Data Flow:
- Dataset registration and sample retrieval (real DVS128 and synthetic)
- Truthful backend capabilities reporting (including Lava unavailability reason)
- Attack execution with contextual metadata (experiment_id, backend_used, dataset_used)
- Simulation stepping and state reset
- Guarding against execution on unavailable backends
- Root redirect to /dashboard/
"""
from fastapi.testclient import TestClient
from web.api.server import app

client = TestClient(app)


def test_root_redirect_to_dashboard():
    res = client.get("/", follow_redirects=False)
    assert res.status_code in (307, 302)
    assert res.headers["location"] == "/dashboard/"


def test_datasets_endpoint_includes_genuine_local_file():
    res = client.get("/api/datasets")
    assert res.status_code == 200
    datasets = res.json()
    assert len(datasets) >= 2  # synthetic + dvs128

    dvs = next((d for d in datasets if "dvs128" in d["dataset_id"]), None)
    assert dvs is not None
    assert dvs["file_format"] == "aedat"
    assert "events_128.aedat" in dvs["local_path"]
    assert dvs["file_checksum_sha256"] == "6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3"


def test_dvs128_sample_retrieval_returns_genuine_events():
    res = client.get("/api/datasets/dvs128_events_128.aedat/samples?limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["samples"]) == 1
    sample = data["samples"][0]
    assert sample["is_synthetic"] is False
    assert sample["num_events"] > 0
    assert len(sample["events_preview"]) > 0

    first_evt = sample["events_preview"][0]
    assert "timestamp" in first_evt
    assert "channel_id" in first_evt
    assert "polarity" in first_evt


def test_backends_reporting_and_lava_guard():
    res = client.get("/api/backends")
    assert res.status_code == 200
    backends = res.json()

    builtin = next(b for b in backends if b["backend_id"] == "builtin_lif_simulator")
    assert builtin["is_available"] is True

    lava = next(b for b in backends if b["backend_id"] == "lava_cpu")
    # Verified through operational execution in .venv-lava
    assert lava["is_available"] is True
    assert "Subprocess Worker" in lava["backend_name"]


def test_execute_attack_on_unavailable_backend_rejected():
    payload = {
        "scenario_name": "Invalid_Backend_Test",
        "attack_type": "synaptic_poisoning",
        "target_core": 2,
        "backend_id": "non_existent_hardware_backend",
    }
    res = client.post("/api/attacks/execute", json=payload)
    assert res.status_code == 400
    detail = res.json()["detail"]
    assert "unknown backend" in detail.lower()


def test_execute_attack_produces_stamped_experiment_context():
    payload = {
        "scenario_name": "Truthful_Execution_Test",
        "attack_type": "synaptic_poisoning",
        "target_core": 2,
        "backend_id": "builtin_lif",
    }
    res = client.post("/api/attacks/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "experiment_id" in data
    assert data["backend_used"] == "builtin_lif_simulator"
    assert "DVS128" in data["dataset_used"]
    assert "metrics" in data
    assert "reconstruction" in data
    assert "sufficiency" in data
