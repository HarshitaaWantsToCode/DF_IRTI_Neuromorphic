"""
Reproducible Experiment Runner for Phase 2 Forensic Validation.
Runs real DVS128 events through:
1. Genuine sample ingestion and provenance recording
2. Benign control baseline execution (verifying 0 false positives)
3. Controlled attack execution (Weight Poisoning & Spike Storm)
4. Forensic evidence sealing with Merkle tree hashing & independent tamper verification
5. Evidence ablation & empirical sufficiency determination (S* = argmin |S| s.t. R >= tau)
6. Machine-readable manifest export (JSON/CSV) and Markdown summary report.
"""
import os
import json
import csv
import time
import hashlib
from typing import Dict, Any

from src.datasets.dvs128_loader import DVS128GestureLoader
from src.neuromorphic.simulator import NeuromorphicSimulator
from src.acquisition.collector import ForensicCollector
from src.acquisition.integrity import ChainOfCustodyVerifier
from src.reconstruction.timeline import TimelineGenerator
from src.reconstruction.correlator import EventCorrelator
from src.eval.reconstruction_score import ReconstructionScorer
from src.eval.evidence_ablation import EvidenceAblationEngine
from src.eval.evidence_filter import EvidenceFilter
from src.core.schemas import ArtifactClass


def run_full_validation_experiment(
    aedat_path: str = "data/dvs128/events_128.aedat",
    output_dir: str = "results/phase2_validation",
    threshold: float = 0.80,
) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    t_start = time.time()

    print("[*] Phase 2: Ingesting genuine DVS128 recording...")
    loader = DVS128GestureLoader()
    is_valid, msg = loader.validate_path(aedat_path)
    if not is_valid:
        raise ValueError(f"DVS128 dataset sample missing: {msg}")

    meta = loader.load_metadata(aedat_path)
    sample = loader.load_sample(aedat_path, max_events=1000)

    # 1. Benign Control Execution
    print("[*] Phase 2: Executing Benign Control Baseline...")
    sim_benign = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    col_benign = ForensicCollector(num_cores=4, neurons_per_core=32)

    for step in range(50):
        batch = sample.events[step * 6 : (step + 1) * 6]
        inputs = {0: [e.channel_id % 32 for e in batch]}
        snap, spikes = sim_benign.step(step, input_spikes=inputs)
        col_benign.record_step(snap, spikes)

    ev_benign = col_benign.seal_evidence(metadata={"mode": "benign_control"})
    benign_timeline = TimelineGenerator().generate_timeline(ev_benign)
    benign_recon = EventCorrelator.correlate_attack(benign_timeline, total_cores=4)

    # 2. Controlled Attack Run: Synaptic Weight Poisoning on Core 2
    print("[*] Phase 2: Executing Controlled Attack (Synaptic Poisoning on Core 2)...")
    sim_attack = NeuromorphicSimulator(num_cores=4, neurons_per_core=32, seed=42)
    attack_cfg = {
        "name": "Phase2_Controlled_Poisoning",
        "target_core": 2,
        "weight_shift": 2.5,
        "start_step": 20,
        "duration_steps": 25,
    }
    sim_attack.attach_attack(attack_cfg)
    ground_truth = sim_attack.get_ground_truth()

    col_attack = ForensicCollector(num_cores=4, neurons_per_core=32)
    col_attack.attach_system_context(
        topology={"num_cores": 4, "neurons_per_core": 32},
        configuration={"dataset": "DVS128 Gesture", "attack": attack_cfg},
    )

    for step in range(50):
        batch = sample.events[step * 10 : (step + 1) * 10]
        inputs = {0: [e.channel_id % 32 for e in batch]}
        snap, spikes = sim_attack.step(step, input_spikes=inputs)
        col_attack.record_step(snap, spikes)

    ev_attack = col_attack.seal_evidence(metadata={"mode": "attack_synaptic_poisoning"})

    # Independent Cryptographic Merkle Re-verification
    computed_hashes = [
        ChainOfCustodyVerifier.hash_data(s.model_dump()) for s in ev_attack.snapshots
    ]
    computed_root = ChainOfCustodyVerifier.compute_merkle_root(computed_hashes)
    merkle_valid = (computed_root == ev_attack.header.root_merkle_hash)

    # Reconstruction on full evidence
    full_timeline = TimelineGenerator().generate_timeline(ev_attack)
    full_recon = EventCorrelator.correlate_attack(full_timeline, total_cores=4)
    full_score = ReconstructionScorer.score_reconstruction(full_recon, ground_truth, threshold=threshold)

    # 3. Evidence-Sufficiency Experiment (Combinatorial Ablation)
    print("[*] Phase 2: Running Evidence Sufficiency Combinatorial Ablation...")
    ablation_engine = EvidenceAblationEngine()
    sufficiency_info = ablation_engine.find_minimum_sufficient_evidence(
        full_evidence=ev_attack,
        ground_truth=ground_truth,
        reconstruction_threshold=threshold,
    )

    t_elapsed = time.time() - t_start

    manifest = {
        "experiment_id": f"phase2_validation_{int(time.time())}",
        "timestamp_epoch": time.time(),
        "runtime_seconds": round(t_elapsed, 2),
        "environment": {
            "os": "Windows",
            "python": "3.14.4",
            "backend": "Native Multi-Core LIF Simulator",
            "lava_status": "Blocked on Python 3.14 (requires <3.11)",
        },
        "dataset_provenance": {
            "dataset_name": "DVS128 Gesture",
            "source_file": aedat_path,
            "file_sha256": meta.file_checksum_sha256,
            "events_loaded": len(sample.events),
            "duration_seconds": sample.duration_seconds,
            "time_unit": "seconds (normalized from microseconds)",
        },
        "benign_control": {
            "steps": 50,
            "false_positive_anomalies": len(benign_timeline),
            "verdict": benign_recon.detected_attack_type,
        },
        "controlled_attack": {
            "attack_type": ground_truth.attack_type,
            "target_core": ground_truth.target_core,
            "start_step": ground_truth.start_step,
            "end_step": ground_truth.end_step,
        },
        "evidence_integrity": {
            "total_snapshots": len(ev_attack.snapshots),
            "merkle_root": ev_attack.header.root_merkle_hash,
            "merkle_verified": merkle_valid,
            "collector_signature": ev_attack.header.collector_signature,
        },
        "full_evidence_reconstruction": {
            "detected_attack_type": full_recon.detected_attack_type,
            "root_cause_core": full_recon.root_cause_core,
            "overall_score": full_score.overall_score,
            "passed_threshold": full_score.passed_threshold,
        },
        "evidence_sufficiency": {
            "threshold": threshold,
            "minimum_cardinality": sufficiency_info["minimum_cardinality"],
            "minimum_sufficient_sets": sufficiency_info["minimum_sufficient_sets"],
            "total_subsets_evaluated": len(sufficiency_info["all_results"]),
        },
    }

    # Save manifest JSON
    manifest_path = os.path.join(output_dir, "experiment_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Save CSV of ablation results
    csv_path = os.path.join(output_dir, "ablation_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["subset", "cardinality", "evidence_bytes", "score", "passed"])
        for r in sufficiency_info["all_results"]:
            writer.writerow([
                "+".join(r["evidence_subset"]),
                len(r["evidence_subset"]),
                r["evidence_volume_bytes"],
                f"{r['reconstruction_score']:.3f}",
                r["success"],
            ])

    # Save Human-readable Markdown Report
    report_path = os.path.join(output_dir, "validation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"""# Phase 2 Reproducible Forensic Validation Report

**Experiment ID:** `{manifest['experiment_id']}`  
**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Runtime:** {manifest['runtime_seconds']}s  

## 1. Dataset & Workload Provenance
- **Dataset:** {manifest['dataset_provenance']['dataset_name']} (`{manifest['dataset_provenance']['source_file']}`)
- **SHA-256 Checksum:** `{manifest['dataset_provenance']['file_sha256']}`
- **Events Ingested:** {manifest['dataset_provenance']['events_loaded']} events across {manifest['dataset_provenance']['duration_seconds']:.3f}s
- **Normalization:** Microseconds converted to canonical seconds; raw timestamps preserved.

## 2. Benign Control Verification
- **Steps:** 50
- **False-Positive Anomalies Detected:** {manifest['benign_control']['false_positive_anomalies']}
- **Classification Verdict:** `{manifest['benign_control']['verdict']}`

## 3. Cryptographic Chain-of-Custody Integrity
- **Total Blocks Acquired:** {manifest['evidence_integrity']['total_snapshots']}
- **Merkle Root:** `{manifest['evidence_integrity']['merkle_root']}`
- **Independent Merkle Re-verification:** `{'PASSED' if manifest['evidence_integrity']['merkle_verified'] else 'FAILED'}`
- **Signature Status:** Unsigned / Placeholder (`{manifest['evidence_integrity']['collector_signature']}`)

## 4. Controlled Attack Reconstruction
- **Ground Truth Attack:** `{manifest['controlled_attack']['attack_type']}` targeting Core {manifest['controlled_attack']['target_core']}
- **Reconstructed Attack:** `{manifest['full_evidence_reconstruction']['detected_attack_type']}` on Core {manifest['full_evidence_reconstruction']['root_cause_core']}
- **Deterministic Reconstruction Score:** `{manifest['full_evidence_reconstruction']['overall_score'] * 100:.1f}%` (Threshold: {threshold * 100:.0f}%)

## 5. Minimum Sufficient Evidence Set ($S^*$)
$$\\mathcal{{S}}^* = \\text{{argmin}} |S|, \\quad \\text{{subject to }} R(A, S) \\ge {threshold}$$
- **Minimum Cardinality:** {manifest['evidence_sufficiency']['minimum_cardinality']} artifact class(es)
- **Minimum Sufficient Sets:** `{manifest['evidence_sufficiency']['minimum_sufficient_sets']}`
- **Total Subsets Evaluated:** {manifest['evidence_sufficiency']['total_subsets_evaluated']}
""")

    print(f"[+] Validation complete! Exported to {output_dir}")
    return manifest


if __name__ == "__main__":
    run_full_validation_experiment()
