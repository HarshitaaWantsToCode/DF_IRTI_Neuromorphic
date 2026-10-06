"""
Evidence Ablation and Minimum Sufficient Evidence Calculation Engine.
Systematically evaluates all evidence combinations against Ground Truth to calculate minimum sufficient sets.
"""
import itertools
import time
import os
import json
import csv
from typing import List, Dict, Any, Set, Tuple, Optional
from src.core.schemas import (
    ArtifactClass,
    EvidencePackage,
    AttackGroundTruth,
    AttackReconstructionGraph,
    ReconstructionScore,
)
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator
from .evidence_filter import EvidenceFilter
from .reconstruction_score import ReconstructionScorer


class EvidenceAblationEngine:
    """Evaluates arbitrary combinations of evidence classes to find sufficiency thresholds and minimum sets."""

    DEFAULT_CANDIDATE_CLASSES = [
        ArtifactClass.SPIKE_EVENTS,
        ArtifactClass.SPIKE_TIMING,
        ArtifactClass.NEURON_STATE,
        ArtifactClass.SYNAPTIC_STATE,
        ArtifactClass.TOPOLOGY_ROUTING,
        ArtifactClass.CONFIGURATION,
        ArtifactClass.INPUT_OUTPUT,
    ]

    def __init__(
        self,
        candidate_classes: Optional[List[ArtifactClass]] = None,
        scoring_weights: Optional[Dict[str, float]] = None,
    ):
        self.candidate_classes = candidate_classes if candidate_classes is not None else self.DEFAULT_CANDIDATE_CLASSES
        self.scoring_weights = scoring_weights

    def generate_all_subsets(
        self,
        min_size: int = 1,
        max_size: Optional[int] = None,
    ) -> List[List[ArtifactClass]]:
        """Generates power set of artifact class combinations."""
        n = len(self.candidate_classes)
        limit = max_size if max_size is not None else n
        subsets = []
        for r in range(min_size, limit + 1):
            for combo in itertools.combinations(self.candidate_classes, r):
                subsets.append(list(combo))
        return subsets

    def evaluate_subset(
        self,
        full_evidence: EvidencePackage,
        ground_truth: AttackGroundTruth,
        subset: List[ArtifactClass],
        threshold: float = 0.80,
    ) -> Dict[str, Any]:
        """Evaluates a single evidence subset against ground truth."""
        t0 = time.perf_counter()
        
        # 1. Filter evidence package
        allowed_set = set(subset)
        filtered_evidence = EvidenceFilter.filter_evidence(full_evidence, allowed_set)
        volume_bytes = EvidenceFilter.calculate_evidence_volume_bytes(filtered_evidence)

        # 2. Run Reconstruction Engine from Evidence ONLY
        timeline_gen = TimelineGenerator()
        events = timeline_gen.generate_timeline(filtered_evidence)
        reconstruction = EventCorrelator.correlate_attack(events, total_cores=full_evidence.header.num_cores)

        # 3. Deterministically Score Reconstruction vs Ground Truth
        score = ReconstructionScorer.score_reconstruction(
            reconstruction=reconstruction,
            ground_truth=ground_truth,
            threshold=threshold,
            weights=self.scoring_weights,
        )
        runtime_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "evidence_subset": [a.value for a in subset],
            "evidence_count": len(subset),
            "evidence_volume_bytes": volume_bytes,
            "reconstruction_score": score.overall_score,
            "attack_identification_score": score.attack_type_score,
            "location_score": score.location_score,
            "temporal_score": score.temporal_score,
            "mechanism_score": score.mechanism_score,
            "impact_score": score.impact_score,
            "success": score.passed_threshold,
            "runtime_ms": round(runtime_ms, 2),
            "detected_attack": reconstruction.detected_attack_type,
            "root_cause_core": reconstruction.root_cause_core,
            "initial_compromise_step": reconstruction.initial_compromise_step,
            "anomalies_count": len(events),
        }

    def run_exhaustive_ablation(
        self,
        full_evidence: EvidencePackage,
        ground_truth: AttackGroundTruth,
        threshold: float = 0.80,
    ) -> List[Dict[str, Any]]:
        """Runs evaluation over all 2^N - 1 subsets of candidate artifact classes."""
        subsets = self.generate_all_subsets(min_size=1)
        results = []
        for subset in subsets:
            eval_res = self.evaluate_subset(full_evidence, ground_truth, subset, threshold=threshold)
            results.append(eval_res)
        return results

    def find_minimum_sufficient_evidence(
        self,
        full_evidence: EvidencePackage,
        ground_truth: AttackGroundTruth,
        reconstruction_threshold: float = 0.80,
    ) -> Dict[str, Any]:
        """
        Determines the smallest evidence subset(s) whose reconstruction score reaches the configured threshold.
        Returns minimum cardinality, all equivalent minimum sufficient sets, scores, and volume.
        """
        all_results = self.run_exhaustive_ablation(
            full_evidence=full_evidence,
            ground_truth=ground_truth,
            threshold=reconstruction_threshold,
        )

        successful = [r for r in all_results if r["success"]]

        if not successful:
            # Find best achieving subset if none reached target threshold
            best = max(all_results, key=lambda x: x["reconstruction_score"])
            return {
                "attack": ground_truth.attack_type,
                "threshold": reconstruction_threshold,
                "minimum_cardinality": None,
                "minimum_sufficient_sets": [],
                "best_achieved_subset": best["evidence_subset"],
                "best_achieved_score": best["reconstruction_score"],
                "all_results": all_results,
            }

        # Find minimum cardinality among successful subsets
        min_cardinality = min(r["evidence_count"] for r in successful)
        min_sets = [r for r in successful if r["evidence_count"] == min_cardinality]

        # Sort minimum sets by evidence volume bytes
        min_sets.sort(key=lambda x: x["evidence_volume_bytes"])

        return {
            "attack": ground_truth.attack_type,
            "threshold": reconstruction_threshold,
            "minimum_cardinality": min_cardinality,
            "minimum_sufficient_sets": [r["evidence_subset"] for r in min_sets],
            "details": min_sets,
            "all_results": all_results,
        }

    @classmethod
    def compute_attack_artifact_matrix(
        cls,
        ablation_results_by_attack: Dict[str, List[Dict[str, Any]]],
        threshold: float = 0.80,
    ) -> Dict[str, Dict[str, str]]:
        """
        Derives an empirical Attack × Artifact matrix from measured ablation experiments.
        Values: 'Required', 'Helpful', 'Redundant', 'Insufficient', 'Not applicable'.
        """
        matrix: Dict[str, Dict[str, str]] = {}

        for attack_name, results in ablation_results_by_attack.items():
            matrix[attack_name] = {}
            all_classes = [c.value for c in cls.DEFAULT_CANDIDATE_CLASSES]

            # Identify full evidence score
            full_res = next((r for r in results if r["evidence_count"] == len(all_classes)), None)
            full_score = full_res["reconstruction_score"] if full_res else 1.0

            for artifact in all_classes:
                # 1. Check if ANY successful subset excludes this artifact
                successful = [r for r in results if r["success"]]
                success_without = [r for r in successful if artifact not in r["evidence_subset"]]

                # 2. Check single artifact score
                single_res = next((r for r in results if r["evidence_subset"] == [artifact]), None)
                single_score = single_res["reconstruction_score"] if single_res else 0.0

                # 3. Check leave-one-out score (all except this artifact)
                leave_one_out = next(
                    (r for r in results if len(r["evidence_subset"]) == len(all_classes) - 1 and artifact not in r["evidence_subset"]),
                    None,
                )
                loo_score = leave_one_out["reconstruction_score"] if leave_one_out else full_score

                if not success_without and successful:
                    # If every successful subset MUST contain this artifact -> Required
                    matrix[attack_name][artifact] = "Required"
                elif loo_score < full_score:
                    # Removing it drops score, but alternative subset can reach threshold -> Helpful
                    matrix[attack_name][artifact] = "Helpful"
                elif single_score > 0.3 and not success_without:
                    matrix[attack_name][artifact] = "Helpful"
                elif loo_score == full_score and any(artifact in r["evidence_subset"] for r in successful):
                    matrix[attack_name][artifact] = "Redundant"
                else:
                    matrix[attack_name][artifact] = "Not applicable"

        return matrix

    @staticmethod
    def export_results(
        experiment_id: str,
        results: List[Dict[str, Any]],
        output_dir: str = "results/ablation",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Exports ablation experiment results to JSON and CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, f"experiment_{experiment_id}.json")
        csv_path = os.path.join(output_dir, f"experiment_{experiment_id}.csv")

        export_payload = {
            "experiment_id": experiment_id,
            "timestamp": time.time(),
            "metadata": metadata if metadata is not None else {},
            "results": results,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2)

        if results:
            fieldnames = [
                "experiment_id",
                "attack",
                "evidence_subset",
                "evidence_count",
                "evidence_volume_bytes",
                "reconstruction_score",
                "attack_identification_score",
                "location_score",
                "temporal_score",
                "mechanism_score",
                "impact_score",
                "success",
                "runtime_ms",
            ]
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for r in results:
                    row = dict(r)
                    row["experiment_id"] = experiment_id
                    row["attack"] = metadata.get("attack_type", "unknown") if metadata else "unknown"
                    row["evidence_subset"] = "+".join(r["evidence_subset"])
                    writer.writerow(row)

        return json_path, csv_path
