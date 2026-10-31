# Stage 4.1 — Evidence Ablation Reconciliation Report

## 1. Executive Summary

This report reconciles the empirical findings of the Stage 4 combinatorial evidence-ablation experiments with the summary artifacts and reports. An independent audit identified discrepancies in reported threshold counts, maximum scores, and minimum sufficient set reporting.

By directly inspecting the three original ablation CSV artifacts:
- `results/stage4/real_data/ablation_spike_storm.csv`
- `results/stage4/real_data/ablation_synaptic_poisoning.csv`
- `results/stage4/real_data/ablation_timing_jitter.csv`

this audit documents the exact mathematical ground truth without altering historical CSV outputs.

---

## 2. Recomputed Threshold Counts Directly from CSVs

Every CSV represents an exhaustive power-set enumeration of all $2^7 - 1 = 127$ non-empty combinations of the 7 formal neuromorphic artifact classes:
1. `SPIKE_EVENTS` ($E$)
2. `SPIKE_TIMING` ($T$)
3. `NEURON_STATE` ($N$)
4. `SYNAPTIC_STATE` ($W$)
5. `TOPOLOGY_ROUTING` ($G$)
6. `CONFIGURATION` ($K$)
7. `INPUT_OUTPUT` ($I$)

### Exact Empirical Score Distribution (127 Subsets per Attack)

| Attack Scenario | Max Score | $\ge 0.50$ | $\ge 0.60$ | $\ge 0.70$ | $\ge 0.75$ | $\ge 0.80$ (Reported $\theta$) | $\ge 0.85$ |
| :--- | :---:| :---:| :---:| :---:| :---:| :---:| :---:|
| **Spike Flooding Storm** | **0.500** | 64 ($50.4\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) |
| **Synaptic Poisoning** | **0.835** | 64 ($50.4\%$) | 64 ($50.4\%$) | 64 ($50.4\%$) | 64 ($50.4\%$) | **16 ($12.6\%$)** | 0 ($0.0\%$) |
| **Timing Jitter** | **0.750** | 32 ($25.2\%$) | 32 ($25.2\%$) | 32 ($25.2\%$) | 32 ($25.2\%$) | 0 ($0.0\%$) | 0 ($0.0\%$) |

#### Verification of Finding 1:
The actual CSV results completely match the independently audited findings:
- **Spike storm:** Maximum score is **0.500**. Exactly 64 subsets achieve $\ge 0.50$, and 0 achieve $\ge 0.75$ or $\ge 0.80$.
- **Synaptic poisoning:** Maximum score is **0.835**. Exactly 64 subsets achieve $\ge 0.50, 0.60, 0.70, 0.75$, and exactly 16 subsets achieve $\ge 0.80$.
- **Timing jitter:** Maximum score is **0.750**. Exactly 32 subsets achieve $\ge 0.50, 0.60, 0.70, 0.75$, and 0 achieve $\ge 0.80$.

The previous `STAGE4_EVIDENCE_ABLATION_REPORT.md` draft inadvertently quoted counts from a synthetic prototype run (which erroneously reported 96, 80, etc.). The values above are the definitive empirical counts.

---

## 3. Investigation of Key Inconsistencies

### Task 6: Why `experiment_manifest.json` Reported Empty `min_sets` for Synaptic Poisoning

Inspection of `experiment_manifest.json` showed:
```json
"synaptic_poisoning": {
  "total_subsets_evaluated": 127,
  "min_cardinality": 1,
  "min_sets": [],
  "best_score": null
}
```
**Root Cause in Code:**
In `scripts/run_stage4_validation.py` (lines 205–210):
```python
min_set_info = ablation_engine.find_minimum_sufficient_evidence(ev_attack, ground_truth, 0.80)
ablation_summary[att_key] = {
    "total_subsets_evaluated": len(ablation_results),
    "min_cardinality": min_set_info.get("minimum_cardinality"),
    "min_sets": min_set_info.get("minimum_sufficient_subsets", []),  # <-- BUG
    "best_score": min_set_info.get("best_achieved_score"),
}
```
However, inspecting `src/eval/evidence_ablation.py` (line 162), the returned dictionary key is named:
`"minimum_sufficient_sets"` (NOT `"minimum_sufficient_subsets"`).

Because `min_set_info.get("minimum_sufficient_subsets", [])` queried a non-existent key, it defaulted to an empty list `[]`. Furthermore, when `successful` is non-empty, `find_minimum_sufficient_evidence()` does not populate `"best_achieved_score"`, leaving it as `null`.

In the actual CSV, row 3 has:
- `evidence_subset`: `['SYNAPTIC_STATE']`
- `evidence_count`: `1`
- `reconstruction_score`: `0.835`
- `success`: `True`

Therefore, **the minimum sufficient evidence set for synaptic poisoning under real DVS128 data is unambiguously `['SYNAPTIC_STATE']` (Cardinality 1).**

---

### Task 7 & 8: Why Full Evidence Scores 0.75 While `SYNAPTIC_STATE` Alone Scores 0.835 (The "More Evidence Decreases Score" Paradox)

In `ablation_synaptic_poisoning.csv`:
- Subset `['SYNAPTIC_STATE']` (1 class): Score = **0.835**
- Subset `['SPIKE_EVENTS', 'SPIKE_TIMING', 'NEURON_STATE', 'SYNAPTIC_STATE', 'TOPOLOGY_ROUTING', 'CONFIGURATION', 'INPUT_OUTPUT']` (7 classes): Score = **0.750**

#### Detailed Forensic Dimensional Breakdown:
| Dimension | Weight ($w$) | `['SYNAPTIC_STATE']` | Full 7 Classes | Difference |
| :--- | :---: | :---: | :---: | :---: |
| **Attack Type** | 0.25 | 1.000 | 1.000 | 0.000 |
| **Root Cause Location**| 0.25 | 1.000 | 1.000 | 0.000 |
| **Temporal Step** | 0.20 | 1.000 | 1.000 | 0.000 |
| **Mechanism / Propagation**| 0.15 | **0.400** | **0.000** | **-0.400** |
| **Impact / Blast Radius** | 0.15 | **0.500** | **0.333** | **-0.167** |
| **Weighted Aggregate** | — | **0.835** | **0.750** | **-0.085** |

#### Why Does Including More Evidence Degrade the Score?
1. **Background Noise vs. Adversarial Signal:**
   - When only `SYNAPTIC_STATE` is present, the timeline generator observes exactly **1 anomaly event**: the weight delta on Core 1 at step 15. Because there are no causal edges, `ReconstructionScorer` gives a fallback baseline mechanism credit of `0.40` for localizing the step without introducing false causal edges.
   - When `SPIKE_EVENTS` and `NEURON_STATE` are introduced, genuine background neuromorphic sensory activity from the real DVS128 recording (which continuously stimulates Core 0) creates genuine spike bursts on Core 0. The correlator detects bursts on Core 0 and Core 1, generating spurious causal transitions (`Core 0 -> Core 1`, `Core 1 -> Core 0`). Because ground truth for the synthetic intervention specifies only `[Core 1 -> Core 2]`, the reconstructed transitions fail to match `true_propagation_path`, driving `mechanism_score` from `0.400` down to `0.000`.
2. **Blast Radius Penalty (Impact Score):**
   - Ground truth affected cores are `[1, 2]`.
   - With `SYNAPTIC_STATE` alone: `compromised_cores = [1]`. Jaccard similarity: $|[1] \cap [1, 2]| / |[1] \cup [1, 2]| = 1/2 = 0.500$.
   - With full evidence: spurious sensory bursts add Core 0 to `compromised_cores = [0, 1]`. Jaccard similarity: $|[0, 1] \cap [1, 2]| / |[0, 1, 2]| = 1/3 = 0.3333$.

**Scientific Insight:**
In digital forensics on live neuromorphic workloads, **more telemetry is not monotonically better**. Non-specific high-volume telemetry (`SPIKE_EVENTS`, `NEURON_STATE`) introduces normal operational background noise that dilutes forensic causal correlation, whereas targeted structural artifacts (`SYNAPTIC_STATE`) isolate the true compromise with surgical precision.

---

### Task 9: Threshold Consistency Between `success` and the Ablation Report

Inspection of `src/eval/evidence_ablation.py` confirms:
- Default threshold is hardcoded to `threshold: float = 0.80`.
- In `ablation_synaptic_poisoning.csv`, `success == True` occurs if and only if `reconstruction_score >= 0.80`.
- Exactly 16 rows have `success == True`, corresponding to scores of `0.835`.
- For `spike_storm` (max 0.500) and `timing_jitter` (max 0.750), `success == True` is 0, because no subset reached the strict 0.80 bar.

The threshold used for `success` in the CSVs is **100% consistent** with the 0.80 threshold.

