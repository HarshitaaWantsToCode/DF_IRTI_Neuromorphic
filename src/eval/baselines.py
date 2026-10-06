"""
Baseline Anomaly Detectors for Comparison & Benchmarking (Person 5).
Implements classical statistical baselines (Moving Average Spike Rate, Raw Log Scanning) to prove the novelty and superior fidelity of NeuroForensics.
"""
import numpy as np
from typing import List, Dict, Any
from src.core.schemas import EvidencePackage


class BaselineAnomalyDetectors:
    """Conventional baseline detectors to benchmark NeuroForensics against."""

    @staticmethod
    def simple_spike_rate_threshold(evidence: EvidencePackage, threshold_multiplier: float = 3.0) -> Dict[str, Any]:
        """Baseline 1: Naive global spike counter without spatial/synaptic state correlation."""
        spike_counts = [len(s.recent_spikes) for s in evidence.snapshots]
        mean_rate = np.mean(spike_counts)
        std_rate = np.std(spike_counts)

        threshold = mean_rate + threshold_multiplier * std_rate
        detections = [
            {"step": evidence.snapshots[i].step, "spike_count": spike_counts[i]}
            for i in range(len(spike_counts))
            if spike_counts[i] > threshold
        ]

        return {
            "baseline_name": "Global Spike Rate Thresholding",
            "detected_anomalies_count": len(detections),
            "detections": detections,
            "can_identify_root_cause_core": False,
            "can_reconstruct_synaptic_trojan": False,
        }

    @staticmethod
    def periodic_log_sampling(evidence: EvidencePackage, sample_interval: int = 20) -> Dict[str, Any]:
        """Baseline 2: Periodic coarse snapshotting without event-driven forensic triggers."""
        sampled = evidence.snapshots[::sample_interval]
        return {
            "baseline_name": f"Periodic Coarse Snapshotting (Every {sample_interval} steps)",
            "captured_steps": [s.step for s in sampled],
            "temporal_fidelity_loss_pct": round((1.0 - (len(sampled) / max(1, len(evidence.snapshots)))) * 100, 2),
            "can_reconstruct_fine_grained_timing": False,
        }
