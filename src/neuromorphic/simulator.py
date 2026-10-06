"""
Leaky Integrate-and-Fire (LIF) Multi-Core Neuromorphic Simulator (Person 1).
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from src.core.schemas import SpikeEvent, CoreStateSnapshot, SystemStateSnapshot, AttackGroundTruth
from .topology import NeuromorphicTopology
from .attacks import NeuromorphicAttackInjector


class NeuromorphicSimulator:
    """Simulates an event-driven, multi-core SNN architecture with membrane dynamics and spike routing."""

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

        self.topology = NeuromorphicTopology(num_cores, neurons_per_core, seed=seed)
        self.rng = np.random.RandomState(seed)

        # State vectors: core_id -> (N,)
        self.v_membrane: Dict[int, np.ndarray] = {
            c: np.zeros(neurons_per_core, dtype=np.float64) for c in range(num_cores)
        }
        self.refractory: Dict[int, np.ndarray] = {
            c: np.zeros(neurons_per_core, dtype=np.int32) for c in range(num_cores)
        }

        self.attack_injector: Optional[NeuromorphicAttackInjector] = None

    def attach_attack(self, scenario_config: Dict[str, Any]):
        """Attaches an attack injector module to the simulation run."""
        self.attack_injector = NeuromorphicAttackInjector(scenario_config, self.topology, seed=self.seed)

    def get_ground_truth(self) -> Optional[AttackGroundTruth]:
        """Returns the isolated ground truth object from the attacker simulation."""
        if self.attack_injector:
            return self.attack_injector.ground_truth
        return None

    def step(self, step_idx: int) -> Tuple[SystemStateSnapshot, List[SpikeEvent]]:
        """Simulates 1 discrete time-step of the multi-core SNN."""
        step_spikes: List[SpikeEvent] = []

        # 1. External sensory Poisson input injection to Core 0
        input_mask = self.rng.rand(self.neurons_per_core) < 0.12
        sensory_active = np.where(input_mask)[0].tolist()
        self.v_membrane[0] += input_mask * 0.35

        # 2. Update Membrane Dynamics (LIF model)
        for c in range(self.num_cores):
            # Leaky integration decay
            self.v_membrane[c] *= self.decay_factor

            # Threshold check for spike emission
            fired = (self.v_membrane[c] >= self.threshold_mv) & (self.refractory[c] == 0)
            fired_indices = np.where(fired)[0]

            for idx in fired_indices:
                # Intra-core synaptic stimulation
                intra_w = self.topology.get_synaptic_weights(c)
                self.v_membrane[c] += intra_w[idx, :] * 0.10

                # Inter-core spike generation
                for dst_c in range(self.num_cores):
                    if (c, dst_c) in self.topology.inter_weights:
                        inter_w = self.topology.inter_weights[(c, dst_c)]
                        target_neurons = np.where(inter_w[idx, :] > 0)[0]
                        for dst_n in target_neurons:
                            step_spikes.append(
                                SpikeEvent(
                                    timestamp_step=step_idx,
                                    timestamp_ms=float(step_idx * self.dt_ms),
                                    source_core=c,
                                    source_neuron=int(idx),
                                    target_core=dst_c,
                                    target_neuron=int(dst_n),
                                    voltage_mv=float(inter_w[idx, dst_n]),
                                )
                            )

                # Reset membrane potential and trigger refractory state
                self.v_membrane[c][idx] = self.reset_mv
                self.refractory[c][idx] = 2

            # Decrement refractory counter
            self.refractory[c] = np.maximum(0, self.refractory[c] - 1)

        # 3. Deliver inter-core spikes
        for spike in step_spikes:
            dst_c = spike.target_core
            dst_n = spike.target_neuron
            if dst_c in self.v_membrane:
                self.v_membrane[dst_c][dst_n] += spike.voltage_mv

        # 4. Apply Attack Perturbations if active
        if self.attack_injector:
            injected = self.attack_injector.apply_attack(step_idx, self.v_membrane, step_spikes)
            step_spikes.extend(injected)

        # 5. Build Core Snapshots
        core_snapshots: Dict[int, CoreStateSnapshot] = {}
        for c in range(self.num_cores):
            active_cnt = sum(1 for s in step_spikes if s.source_core == c)
            core_snapshots[c] = CoreStateSnapshot(
                core_id=c,
                membrane_potentials=self.v_membrane[c].tolist(),
                synaptic_weights=self.topology.get_synaptic_weights(c).tolist(),
                refractory_counters=self.refractory[c].tolist(),
                active_spikes_count=active_cnt,
            )

        system_snapshot = SystemStateSnapshot(
            step=step_idx,
            cores=core_snapshots,
            recent_spikes=step_spikes,
            sensory_inputs=sensory_active,
        )

        return system_snapshot, step_spikes
