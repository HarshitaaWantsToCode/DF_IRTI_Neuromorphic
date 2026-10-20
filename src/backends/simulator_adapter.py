"""
Builtin LIF Neuromorphic Simulator Adapter.
Adapts NeuromorphicSimulator to the uniform SNNBackendAdapter interface.
"""
from typing import Any, Dict, List, Optional
import time

from src.backends.base import BackendCapability, BackendType, SNNBackendAdapter, StepObservation
from src.neuromorphic.simulator import NeuromorphicSimulator


class BuiltinSimulatorAdapter(SNNBackendAdapter):
    """
    Adapter wrapping the repository's native multi-core LIF neuromorphic simulator.
    Provides complete state observability (membrane potentials, refractory states, weights, and spikes).
    """

    def __init__(
        self,
        num_cores: int = 4,
        neurons_per_core: int = 32,
        decay_factor: float = 0.9,
        threshold_mv: float = 1.0,
        reset_mv: float = 0.0,
        dt_ms: float = 1.0,
        seed: int = 42,
    ):
        self.num_cores = num_cores
        self.neurons_per_core = neurons_per_core
        self.decay_factor = decay_factor
        self.threshold_mv = threshold_mv
        self.reset_mv = reset_mv
        self.dt_ms = dt_ms
        self.seed = seed
        self.step_counter = 0

        self.simulator = NeuromorphicSimulator(
            num_cores=num_cores,
            neurons_per_core=neurons_per_core,
            decay_factor=decay_factor,
            threshold_mv=threshold_mv,
            reset_mv=reset_mv,
            dt_ms=dt_ms,
            seed=seed,
        )

    def get_capabilities(self) -> BackendCapability:
        return BackendCapability(
            backend_id="builtin_lif_simulator",
            backend_name="Native Multi-Core LIF Simulator",
            backend_type=BackendType.BUILTIN_SIMULATOR,
            is_available=True,
            observable_spikes=True,
            observable_potentials=True,
            observable_weights=True,
            observable_refractory=True,
            observable_hardware_telemetry=False,
            max_cores=16,
            max_neurons_per_core=1024,
            supported_neuron_models=["LIF"],
            device_name="CPU (Software Emulation)",
            notes="Fully observable multi-core Leaky Integrate-and-Fire simulator with routing and attack injection.",
        )

    def initialize_network(self, config: Dict[str, Any]) -> bool:
        self.num_cores = config.get("num_cores", self.num_cores)
        self.neurons_per_core = config.get("neurons_per_core", self.neurons_per_core)
        self.decay_factor = config.get("decay_factor", self.decay_factor)
        self.threshold_mv = config.get("threshold_mv", self.threshold_mv)
        self.reset_mv = config.get("reset_mv", self.reset_mv)
        self.dt_ms = config.get("dt_ms", self.dt_ms)
        self.seed = config.get("seed", self.seed)

        self.simulator = NeuromorphicSimulator(
            num_cores=self.num_cores,
            neurons_per_core=self.neurons_per_core,
            decay_factor=self.decay_factor,
            threshold_mv=self.threshold_mv,
            reset_mv=self.reset_mv,
            dt_ms=self.dt_ms,
            seed=self.seed,
        )
        self.step_counter = 0
        return True

    def attach_attack(self, scenario_config: Dict[str, Any]) -> None:
        self.simulator.attach_attack(scenario_config)

    def step(self, input_spikes: Optional[Dict[int, List[int]]] = None) -> StepObservation:
        snapshot, spikes = self.simulator.step(self.step_counter, input_spikes=input_spikes)
        self.step_counter += 1

        potentials = {
            f"core_{c_id}": [float(v) for v in c_state.membrane_potentials]
            for c_id, c_state in snapshot.cores.items()
        }
        refractory = {
            f"core_{c_id}": [int(r) for r in c_state.refractory_counters]
            for c_id, c_state in snapshot.cores.items()
        }
        spike_records = [s.model_dump() for s in spikes]

        return StepObservation(
            step=self.step_counter,
            timestamp_s=(self.step_counter * self.dt_ms) / 1000.0,
            spike_events=spike_records,
            membrane_potentials=potentials,
            refractory_states=refractory,
            weights_summary={
                "intra_synapses": sum(w.size for w in self.simulator.topology.intra_weights.values()),
                "inter_synapses": sum(w.size for w in self.simulator.topology.inter_weights.values()),
            },
            telemetry={"simulated_time_ms": self.step_counter * self.dt_ms},
        )

    def get_weights(self) -> Dict[str, Any]:
        return {
            f"core_{c}": w.tolist()
            for c, w in self.simulator.topology.intra_weights.items()
        }

    def reset(self) -> None:
        self.initialize_network({
            "num_cores": self.num_cores,
            "neurons_per_core": self.neurons_per_core,
            "decay_factor": self.decay_factor,
            "threshold_mv": self.threshold_mv,
            "reset_mv": self.reset_mv,
            "dt_ms": self.dt_ms,
            "seed": self.seed,
        })
