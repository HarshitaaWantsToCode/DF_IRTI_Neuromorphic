"""
Timeline Generation and State Divergence Engine (Person 3).
Reconstructs chronological execution events and detects aberrant neural transitions based on available evidence.
"""
import numpy as np
from typing import List, Optional
from src.core.schemas import EvidencePackage, TimelineEvent, ArtifactClass


class TimelineGenerator:
    """Processes discrete state snapshots to reconstruct fine-grained temporal execution logs."""

    def __init__(self, divergence_threshold: float = 0.25, spike_burst_multiplier: float = 2.0):
        self.divergence_threshold = divergence_threshold
        self.spike_burst_multiplier = spike_burst_multiplier

    def generate_timeline(self, evidence: EvidencePackage) -> List[TimelineEvent]:
        """Iterates through snapshots and extracts chronological anomalies and key state changes."""
        events: List[TimelineEvent] = []
        snapshots = evidence.snapshots
        num_cores = evidence.header.num_cores
        included_artifacts = set(evidence.header.included_artifacts)

        has_synapses = ArtifactClass.SYNAPTIC_STATE in included_artifacts
        has_spikes = ArtifactClass.SPIKE_EVENTS in included_artifacts
        has_timing = ArtifactClass.SPIKE_TIMING in included_artifacts
        has_neuron_state = ArtifactClass.NEURON_STATE in included_artifacts

        prev_weights = {}
        core_spikes_history = {c: [] for c in range(num_cores)}

        for s_idx, snapshot in enumerate(snapshots):
            step = snapshot.step
            timestamp_ms = float(step * 1.0)

            for c_id, core_state in snapshot.cores.items():
                # Track spike counts if spike events are available
                if has_spikes:
                    core_spikes_history[c_id].append(core_state.active_spikes_count)

                # 1. Synaptic Weight Mutation / Trojan Detection
                if has_synapses and core_state.synaptic_weights is not None:
                    curr_weights = np.array(core_state.synaptic_weights)
                    if c_id in prev_weights:
                        diff = np.abs(curr_weights - prev_weights[c_id])
                        max_diff = float(np.max(diff))

                        if max_diff > self.divergence_threshold:
                            tampered_neurons = np.where(np.any(diff > self.divergence_threshold, axis=1))[0].tolist()
                            events.append(
                                TimelineEvent(
                                    step=step,
                                    timestamp_ms=timestamp_ms,
                                    event_type="SYNAPSE_ANOMALY",
                                    affected_core=c_id,
                                    affected_neurons=tampered_neurons[:5],
                                    severity="CRITICAL" if max_diff > 1.5 else "HIGH",
                                    description=f"Synaptic weight deviation detected on Core {c_id} (max delta: {max_diff:.3f})",
                                    evidence_ref=f"snapshot_{s_idx}_core_{c_id}",
                                    anomaly_score=min(1.0, max_diff / 3.0),
                                )
                            )

                    prev_weights[c_id] = curr_weights

                # 2. Spike Flooding Storm / Burst Detection
                if has_spikes and len(core_spikes_history[c_id]) >= 5:
                    recent_avg = np.mean(core_spikes_history[c_id][-10:-1]) if len(core_spikes_history[c_id]) >= 10 else np.mean(core_spikes_history[c_id][:-1])
                    recent_std = np.std(core_spikes_history[c_id][-10:-1]) if len(core_spikes_history[c_id]) >= 10 else np.std(core_spikes_history[c_id][:-1])
                    curr_val = core_state.active_spikes_count
                    
                    min_burst_threshold = 20 if c_id == 0 else 12
                    if curr_val >= min_burst_threshold and curr_val > (recent_avg + 3.5 * max(1.0, recent_std)):
                        events.append(
                            TimelineEvent(
                                step=step,
                                timestamp_ms=timestamp_ms,
                                event_type="SPIKE_BURST",
                                affected_core=c_id,
                                affected_neurons=list(range(min(4, evidence.header.neurons_per_core))),
                                severity="HIGH",
                                description=f"Anomalous spike surge on Core {c_id} ({curr_val} spikes vs avg {recent_avg:.1f})",
                                evidence_ref=f"snapshot_{s_idx}_core_{c_id}",
                                anomaly_score=min(1.0, float(curr_val) / 25.0),
                            )
                        )

                # 3. Neuron State Abnormality Detection (Membrane potential saturation / depolarized latch)
                if has_neuron_state and core_state.membrane_potentials is not None:
                    v_mem = np.array(core_state.membrane_potentials)
                    high_v_neurons = np.where(v_mem > 0.8)[0].tolist()
                    if len(high_v_neurons) > (evidence.header.neurons_per_core * 0.4):
                        events.append(
                            TimelineEvent(
                                step=step,
                                timestamp_ms=timestamp_ms,
                                event_type="MEMBRANE_ANOMALY",
                                affected_core=c_id,
                                affected_neurons=high_v_neurons[:5],
                                severity="MEDIUM",
                                description=f"Elevated membrane potential across {len(high_v_neurons)} neurons on Core {c_id}",
                                evidence_ref=f"snapshot_{s_idx}_core_{c_id}_vmem",
                                anomaly_score=min(1.0, len(high_v_neurons) / evidence.header.neurons_per_core),
                            )
                        )

            # 4. Temporal Jitter / Phase Desynchronization Detection
            if has_spikes and has_timing:
                for spike in snapshot.recent_spikes:
                    timing_delta = abs(spike.timestamp_ms - (step * 1.0))
                    if timing_delta > 1.5:
                        events.append(
                            TimelineEvent(
                                step=step,
                                timestamp_ms=spike.timestamp_ms,
                                event_type="TIMING_DEVIATION",
                                affected_core=spike.source_core,
                                affected_neurons=[spike.source_neuron],
                                severity="HIGH",
                                description=f"Microsecond phase jitter deviation ({timing_delta:.2f} ms) observed on Core {spike.source_core}",
                                evidence_ref=f"snapshot_{s_idx}_spike_{spike.event_id}",
                                anomaly_score=min(1.0, timing_delta / 5.0),
                            )
                        )

        return events
