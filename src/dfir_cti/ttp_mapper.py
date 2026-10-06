"""
Neuromorphic MITRE ATT&CK TTP Taxonomy and Threat Mapper (Person 4).
Translates hardware and SNN anomalies into standardized cyber threat intelligence (CTI) entities.
"""
from typing import List, Dict, Any
from src.core.schemas import AttackReconstructionGraph, ThreatIndicator


class NeuromorphicTTPMapper:
    """Maps event-driven anomalies to MITRE ATT&CK techniques with neuromorphic domain extensions."""

    TTP_TAXONOMY = {
        "SYNAPSE_ANOMALY": {
            "ttp_code": "T1565.001",
            "technique_name": "Stored Data Manipulation: Synaptic Weight Tampering",
            "tactic": "Impact",
            "description": "Adversary altered non-volatile memory or SRAM registers storing synaptic connection weights to induce targeted misclassification.",
            "pattern_template": "[neuromorphic-core:synaptic_weight_delta > 0.25]",
        },
        "SPIKE_BURST": {
            "ttp_code": "T1499.004",
            "technique_name": "Endpoint Denial of Service: Spike Flooding Storm",
            "tactic": "Impact",
            "description": "Adversary flooded inter-core asynchronous routing buses with artificial spikes to cause power surge and queue exhaustion.",
            "pattern_template": "[neuromorphic-bus:spike_rate > 2.5 * baseline]",
        },
        "TIMING_DEVIATION": {
            "ttp_code": "T1071.004",
            "technique_name": "Application Layer Protocol: Microsecond Spike Desynchronization",
            "tactic": "Command and Control",
            "description": "Adversary introduced artificial phase jitters into spike arrival times to distort temporal spike-timing-dependent plasticity (STDP).",
            "pattern_template": "[neuromorphic-spike:arrival_jitter_ms > 2.0]",
        },
    }

    @classmethod
    def map_threats(cls, reconstruction: AttackReconstructionGraph) -> List[ThreatIndicator]:
        """Extracts formal Threat Indicators from the reconstructed attack progression."""
        indicators: List[ThreatIndicator] = []
        seen_types = set()

        for step in reconstruction.progression_steps:
            evt_type = step.event_type
            if evt_type in cls.TTP_TAXONOMY and evt_type not in seen_types:
                seen_types.add(evt_type)
                info = cls.TTP_TAXONOMY[evt_type]
                indicators.append(
                    ThreatIndicator(
                        ttp_code=info["ttp_code"],
                        technique_name=info["technique_name"],
                        tactic=info["tactic"],
                        confidence_score=0.92,
                        description=info["description"],
                        stix_pattern=info["pattern_template"],
                        observable_artifacts={
                            "affected_core": step.affected_core,
                            "severity": step.severity,
                            "step_recorded": step.step,
                            "anomaly_score": step.anomaly_score,
                        },
                    )
                )

        return indicators
