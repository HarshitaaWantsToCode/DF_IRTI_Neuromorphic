"""
Attack Injection Engine for Neuromorphic Systems (Person 1).
Provides controlled attack vectors and generates isolated Ground Truth records.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from src.core.schemas import SpikeEvent, AttackGroundTruth
from .topology import NeuromorphicTopology


class NeuromorphicAttackInjector:
    """Simulates realistic cyber threats targeting the physical and logical layers of neuromorphic hardware."""

    def __init__(self, scenario_config: Dict[str, Any], topology: NeuromorphicTopology, seed: Optional[int] = None):
        self.config = scenario_config
        self.topology = topology
        self.rng = np.random.RandomState(seed if seed is not None else 42)
        self.ground_truth: Optional[AttackGroundTruth] = None
        self._init_ground_truth()

    def _init_ground_truth(self):
        """Constructs a logically separate AttackGroundTruth object."""
        target_core = int(self.config.get("target_core", 1))
        start_step = int(self.config.get("start_step", 25))
        duration = int(self.config.get("duration_steps", 35))
        end_step = start_step + duration

        scenario_name = self.config.get("name", "Unknown Scenario")
        attack_type = "unknown"
        attack_category = "unknown"

        if "weight_shift" in self.config:
            attack_type = "synaptic_poisoning"
            attack_category = "integrity"
        elif "injection_rate" in self.config:
            attack_type = "spike_storm"
            attack_category = "dos"
        elif "jitter_magnitude_ms" in self.config:
            attack_type = "timing_jitter"
            attack_category = "temporal"

        # Predict direct cascade path based on ring topology
        affected_cores = [target_core]
        next_core = (target_core + 1) % self.topology.num_cores
        affected_cores.append(next_core)

        self.ground_truth = AttackGroundTruth(
            attack_type=attack_type,
            attack_category=attack_category,
            target_core=target_core,
            affected_cores=affected_cores,
            start_step=start_step,
            end_step=end_step,
            duration_steps=duration,
            modified_parameters=self.config,
            true_propagation_path=[target_core, next_core],
            true_impact={
                "target_core": target_core,
                "scenario_name": scenario_name,
            },
        )

    def apply_attack(
        self,
        current_step: int,
        membrane_potentials: Dict[int, np.ndarray],
        recent_spikes: List[SpikeEvent],
    ) -> List[SpikeEvent]:
        """
        Executes attack perturbations if the current step falls within the attack window.
        Returns newly injected or modified spike events.
        """
        start_step = self.config.get("start_step", 25)
        duration = self.config.get("duration_steps", 35)
        target_core = self.config.get("target_core", 1)

        injected_spikes: List[SpikeEvent] = []

        if start_step <= current_step < (start_step + duration):
            # 1. Synaptic Weight Poisoning (Trojan/Integrity Tampering)
            if "weight_shift" in self.config:
                if current_step == start_step:
                    weights = self.topology.get_synaptic_weights(target_core)
                    ratio = self.config.get("target_synapse_ratio", 0.3)
                    shift = self.config.get("weight_shift", 2.0)
                    mask = self.rng.rand(*weights.shape) < ratio
                    weights[mask] += shift
                    self.topology.set_synaptic_weights(target_core, weights)

            # 2. Spike Flooding Storm (Denial of Service)
            if "injection_rate" in self.config:
                rate = self.config.get("injection_rate", 0.8)
                num_neurons = self.topology.neurons_per_core
                for n in range(num_neurons):
                    if self.rng.rand() < rate:
                        injected_spikes.append(
                            SpikeEvent(
                                timestamp_step=current_step,
                                timestamp_ms=float(current_step),
                                source_core=target_core,
                                source_neuron=n,
                                target_core=(target_core + 1) % self.topology.num_cores,
                                target_neuron=int(self.rng.randint(0, num_neurons)),
                                voltage_mv=1.5,
                            )
                        )

            # 3. Temporal Jitter / Desynchronization
            if "jitter_magnitude_ms" in self.config:
                jitter = self.config.get("jitter_magnitude_ms", 4.5)
                # If there are spikes from target core, jitter them
                target_spikes = [s for s in recent_spikes if s.source_core == target_core]
                if target_spikes:
                    for spike in target_spikes:
                        spike.timestamp_ms += float(self.rng.normal(0, jitter))
                else:
                    # Inject jittered routing pulses from target core to ensure temporal phase anomaly
                    num_neurons = self.topology.neurons_per_core
                    injected_spikes.append(
                        SpikeEvent(
                            timestamp_step=current_step,
                            timestamp_ms=float(current_step) + float(self.rng.uniform(2.5, jitter)),
                            source_core=target_core,
                            source_neuron=int(self.rng.randint(0, num_neurons)),
                            target_core=(target_core + 1) % self.topology.num_cores,
                            target_neuron=int(self.rng.randint(0, num_neurons)),
                            voltage_mv=0.25,
                        )
                    )

        return injected_spikes
