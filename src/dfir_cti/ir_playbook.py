"""
Incident Response Engine and Automated Playbooks for Neuromorphic Architecture (Person 4).
Translates forensic attack reconstruction into concrete containment and remediation actions.
"""
from typing import List, Dict
from src.core.schemas import AttackReconstructionGraph, IncidentResponsePlan


class IncidentResponseEngine:
    """Evaluates the severity and topological blast-radius of an attack to generate containment playbooks."""

    @staticmethod
    def formulate_response(reconstruction: AttackReconstructionGraph) -> IncidentResponsePlan:
        """Determines isolation targets, synaptic recalibration plans, and evidence preservation tasks."""
        if not reconstruction.progression_steps:
            return IncidentResponsePlan(
                scenario_detected="Normal Operations / Benign",
                severity="NONE",
                containment_actions=["Continue routine telemetry monitoring."],
                isolated_cores=[],
                recalibration_targets={},
                preservation_status="ACTIVE",
            )

        root_core = reconstruction.root_cause_core
        compromised = reconstruction.compromised_cores

        containment_actions: List[str] = [
            f"Trigger hardware interrupt: Isolate Core {root_core} from inter-core asynchronous routing bus.",
            f"Halt spike transmission on downstream routing channels: {reconstruction.causal_edges}.",
            "Initiate non-volatile SRAM backup and cryptographic seal of corrupted synaptic registers.",
        ]

        recalibration: Dict[int, str] = {}
        for c in compromised:
            if c == root_core:
                recalibration[c] = "Full baseline firmware flash and synaptic weight matrix reset."
            else:
                recalibration[c] = "Membrane potential drain to reset voltage and leak recalibration."

        severity = "HIGH"
        if len(compromised) > 2 or reconstruction.scenario_name.startswith("Synaptic"):
            severity = "CRITICAL"

        return IncidentResponsePlan(
            scenario_detected=reconstruction.scenario_name,
            severity=severity,
            containment_actions=containment_actions,
            isolated_cores=[root_core],
            recalibration_targets=recalibration,
            preservation_status="PRESERVED_IN_NFD",
        )
