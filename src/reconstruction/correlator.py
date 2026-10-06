"""
Event Correlator and Root-Cause Analyzer (Person 3).
Correlates chronological anomaly events across cores to establish the root cause and propagation sequence.
"""
from typing import List, Dict, Any, Optional
from src.core.schemas import TimelineEvent, AttackReconstructionGraph


class EventCorrelator:
    """Links multi-core forensic events into a structured attack progression chain."""

    @staticmethod
    def correlate_attack(events: List[TimelineEvent], total_cores: int = 4) -> AttackReconstructionGraph:
        """Analyzes chronological anomalies and isolates initial compromise and cascading paths."""
        if not events:
            return AttackReconstructionGraph(
                scenario_name="Benign Execution",
                detected_attack_type="benign",
                root_cause_core=-1,
                initial_compromise_step=-1,
                progression_steps=[],
                compromised_cores=[],
                total_anomalous_spikes=0,
                causal_edges=[],
                confidence=0.0,
            )

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: (e.step, e.timestamp_ms))
        
        # Classify attack type based strictly on observed forensic events
        synapse_events = [e for e in sorted_events if e.event_type == "SYNAPSE_ANOMALY"]
        burst_events = [e for e in sorted_events if e.event_type == "SPIKE_BURST"]
        timing_events = [e for e in sorted_events if e.event_type == "TIMING_DEVIATION"]
        membrane_events = [e for e in sorted_events if e.event_type == "MEMBRANE_ANOMALY"]

        detected_attack_type = "unknown"
        scenario_name = "Neuromorphic Cyber Anomaly"

        if synapse_events:
            detected_attack_type = "synaptic_poisoning"
            scenario_name = "Synaptic Poisoning / Weight Trojan"
            root_event = synapse_events[0]
        elif timing_events:
            detected_attack_type = "timing_jitter"
            scenario_name = "Temporal Desynchronization / Jitter Attack"
            root_event = timing_events[0]
        elif burst_events:
            detected_attack_type = "spike_storm"
            scenario_name = "Denial-of-Service Spike Flooding Storm"
            root_event = burst_events[0]
        elif membrane_events:
            detected_attack_type = "membrane_saturation"
            scenario_name = "Neuron State Depolarization Anomaly"
            root_event = membrane_events[0]
        else:
            root_event = sorted_events[0]

        root_cause_core = root_event.affected_core
        initial_step = root_event.step

        affected_cores_set = set()
        causal_edges: List[Dict[str, Any]] = []

        prev_event = None
        for evt in sorted_events:
            affected_cores_set.add(evt.affected_core)
            if prev_event and prev_event.affected_core != evt.affected_core:
                causal_edges.append(
                    {
                        "source_core": prev_event.affected_core,
                        "target_core": evt.affected_core,
                        "step_delta": evt.step - prev_event.step,
                        "propagation_type": "INTER_CORE_CASCADE",
                    }
                )
            prev_event = evt

        confidence = min(1.0, len(sorted_events) * 0.15)

        return AttackReconstructionGraph(
            scenario_name=scenario_name,
            detected_attack_type=detected_attack_type,
            root_cause_core=root_cause_core,
            initial_compromise_step=initial_step,
            progression_steps=sorted_events,
            compromised_cores=sorted(list(affected_cores_set)),
            total_anomalous_spikes=len(sorted_events) * 12,
            causal_edges=causal_edges,
            confidence=confidence,
        )
