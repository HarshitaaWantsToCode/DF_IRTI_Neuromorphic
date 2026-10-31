"""
Tests for backend adapter architecture:
- SNNBackendAdapter interface
- BuiltinSimulatorAdapter step, weights, reset, and capabilities
- LavaCPUAdapter reporting and graceful error handling on unsupported runtimes
"""
import pytest
from src.backends.base import BackendType
from src.backends.simulator_adapter import BuiltinSimulatorAdapter
from src.backends.lava_adapter import LavaCPUAdapter


def test_builtin_simulator_adapter_lifecycle():
    adapter = BuiltinSimulatorAdapter(num_cores=2, neurons_per_core=16, seed=42)
    caps = adapter.get_capabilities()
    assert caps.backend_type == BackendType.BUILTIN_SIMULATOR
    assert caps.is_available is True
    assert caps.observable_potentials is True
    assert caps.observable_weights is True

    # Advance 3 steps
    obs1 = adapter.step()
    assert obs1.step == 1
    assert "core_0" in obs1.membrane_potentials
    assert len(obs1.membrane_potentials["core_0"]) == 16

    obs2 = adapter.step()
    assert obs2.step == 2

    # Weight state
    weights = adapter.get_weights()
    assert "core_0" in weights
    assert "core_1" in weights

    # Reset
    adapter.reset()
    assert adapter.step_counter == 0


def test_builtin_simulator_attack_attachment():
    adapter = BuiltinSimulatorAdapter(num_cores=2, neurons_per_core=16, seed=42)
    attack_cfg = {
        "name": "WeightPoisoning_Test",
        "target_core": 0,
        "weight_shift": 0.5,
        "start_step": 0,
        "duration_steps": 5,
    }
    adapter.attach_attack(attack_cfg)
    adapter.step()
    # Check that simulator has ground truth registered
    gt = adapter.simulator.get_ground_truth()
    assert gt is not None
    assert gt.attack_type == "synaptic_poisoning"


def test_lava_cpu_adapter_reporting_and_guarding():
    # 1. Test when valid isolated Python 3.10 venv is present
    lava_adapter = LavaCPUAdapter()
    caps = lava_adapter.get_capabilities()
    assert caps.backend_type == BackendType.LAVA_CPU
    assert caps.is_available is True
    assert caps.unavailability_reason is None

    # Verify execution produces real output spikes
    res = lava_adapter.execute_simulation(num_neurons=4, num_steps=5)
    assert res["status"] == "success"
    assert res["total_spikes"] > 0
    assert len(res["spike_events"]) > 0

    # 2. Test truthful unavailable reporting when venv is missing
    missing_adapter = LavaCPUAdapter(venv_path="C:/non_existent_venv")
    missing_caps = missing_adapter.get_capabilities()
    assert missing_caps.is_available is False
    assert missing_caps.unavailability_reason is not None
    assert "not found" in missing_caps.unavailability_reason

    # Stepping or initializing on unavailable adapter should cleanly raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        missing_adapter.step()
    assert "Cannot step Lava backend" in str(exc_info.value)

    with pytest.raises(RuntimeError):
        missing_adapter.initialize_network({})
