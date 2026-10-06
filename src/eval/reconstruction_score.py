"""
Deterministic Reconstruction Scoring Engine.
Scores the fidelity of forensic reconstruction against ground truth across multiple orthogonal dimensions without ML/LLMs.
"""
from typing import Dict, Any, Optional
from src.core.schemas import AttackReconstructionGraph, AttackGroundTruth, ReconstructionScore


class ReconstructionScorer:
    """Computes deterministic reconstruction fidelity scores in [0.0, 1.0]."""

    DEFAULT_WEIGHTS = {
        "attack_type": 0.25,
        "location": 0.25,
        "temporal": 0.20,
        "mechanism": 0.15,
        "impact": 0.15,
    }

    @classmethod
    def score_reconstruction(
        cls,
        reconstruction: AttackReconstructionGraph,
        ground_truth: AttackGroundTruth,
        threshold: float = 0.80,
        weights: Optional[Dict[str, float]] = None,
    ) -> ReconstructionScore:
        """
        Compares an AttackReconstructionGraph against an AttackGroundTruth.
        """
        w = weights if weights is not None else cls.DEFAULT_WEIGHTS

        # 1. Attack Type Identification Score
        # Match detected_attack_type or scenario match
        type_score = 0.0
        if reconstruction.detected_attack_type == ground_truth.attack_type:
            type_score = 1.0
        elif reconstruction.detected_attack_type != "unknown" and reconstruction.detected_attack_type != "benign":
            # Partial credit if category matches or detected something
            type_score = 0.2

        # 2. Root Cause Location Score
        location_score = 0.0
        if reconstruction.root_cause_core == ground_truth.target_core:
            location_score = 1.0
        elif reconstruction.root_cause_core in ground_truth.affected_cores:
            location_score = 0.5

        # 3. Temporal Accuracy Score
        temporal_score = 0.0
        if reconstruction.initial_compromise_step >= 0:
            step_delta = abs(reconstruction.initial_compromise_step - ground_truth.start_step)
            # Full score if exact, decays gracefully within 5 steps
            if step_delta == 0:
                temporal_score = 1.0
            elif step_delta <= 2:
                temporal_score = 0.8
            elif step_delta <= 5:
                temporal_score = 0.5
            elif step_delta <= 10:
                temporal_score = 0.2
            else:
                temporal_score = 0.0

        # 4. Attack Mechanism / Propagation Path Score
        mechanism_score = 0.0
        if reconstruction.causal_edges and ground_truth.true_propagation_path:
            # Check how many causal edges match true propagation transitions
            true_transitions = set()
            for i in range(len(ground_truth.true_propagation_path) - 1):
                true_transitions.add((ground_truth.true_propagation_path[i], ground_truth.true_propagation_path[i + 1]))

            reconstructed_transitions = set()
            for edge in reconstruction.causal_edges:
                reconstructed_transitions.add((edge["source_core"], edge["target_core"]))

            if true_transitions:
                intersection = true_transitions.intersection(reconstructed_transitions)
                mechanism_score = len(intersection) / len(true_transitions)
            else:
                mechanism_score = 1.0 if not reconstruction.causal_edges else 0.5
        elif not reconstruction.causal_edges and len(ground_truth.true_propagation_path) <= 1:
            mechanism_score = 1.0
        elif reconstruction.progression_steps:
            mechanism_score = 0.4

        # 5. Impact / Blast Radius Score (Jaccard similarity of affected cores)
        impact_score = 0.0
        true_cores = set(ground_truth.affected_cores)
        reconstructed_cores = set(reconstruction.compromised_cores)
        if true_cores and reconstructed_cores:
            union = true_cores.union(reconstructed_cores)
            intersection = true_cores.intersection(reconstructed_cores)
            impact_score = len(intersection) / len(union) if union else 0.0
        elif not true_cores and not reconstructed_cores:
            impact_score = 1.0

        # Overall weighted aggregate score
        overall = (
            w["attack_type"] * type_score
            + w["location"] * location_score
            + w["temporal"] * temporal_score
            + w["mechanism"] * mechanism_score
            + w["impact"] * impact_score
        )
        overall = max(0.0, min(1.0, float(overall)))

        passed = overall >= threshold

        details = {
            "ground_truth_attack": ground_truth.attack_type,
            "detected_attack": reconstruction.detected_attack_type,
            "ground_truth_core": ground_truth.target_core,
            "reconstructed_core": reconstruction.root_cause_core,
            "ground_truth_start": ground_truth.start_step,
            "reconstructed_start": reconstruction.initial_compromise_step,
            "ground_truth_cores": ground_truth.affected_cores,
            "reconstructed_cores": reconstruction.compromised_cores,
            "threshold": threshold,
        }

        return ReconstructionScore(
            attack_type_score=round(type_score, 4),
            location_score=round(location_score, 4),
            temporal_score=round(temporal_score, 4),
            mechanism_score=round(mechanism_score, 4),
            impact_score=round(impact_score, 4),
            overall_score=round(overall, 4),
            weights_used=w,
            passed_threshold=passed,
            details=details,
        )
