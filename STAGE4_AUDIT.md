# STAGE 4 AUDIT: Real-World Dataset Validation and Forensic Evaluation Pipeline

## 1. Executive Summary

This audit assesses the state of the NeuroForensics codebase prior to Stage 4 development. NeuroForensics previously implemented a multi-core Leaky Integrate-and-Fire (LIF) simulator, an artifact container format (`.nfd` / `.nfd.gz`), Merkle-tree cryptographic integrity verification, timeline reconstruction, MITRE ATT&CK / STIX 2.1 CTI mapping, deterministic reconstruction scoring, and combinatorial 7-class evidence ablation.

However, prior validation runs were primarily driven by synthetic stimulus or simplistic event re-binning inside a step-discrete simulator. Furthermore:
1. Timestamp perturbations under "timing jitter" modified `timestamp_ms` metadata without altering simulator event arrival or scheduling.
2. Synaptic weight poisoning was applied to arbitrary matrix entries without an actual trained neural architecture or task-level accuracy tracking on held-out test splits.
3. Spike flooding lacked queue saturation dynamics, arrival/service rate accounting, and an explicit DoS operational criterion.
4. Dataset ingestion for DVS128 and SHD lacked a unified adapter interface, split preservation, and real-input evaluation against the attack suite.

This document inventories existing functionality, identifies critical gaps, specifies exact file modifications, and details the rigorous experiment design for Stage 4.

---

## 2. Existing Functionality Inventory

| Subsystem | Module | Current Implementation Status |
| :--- | :--- | :--- |
| **Datasets** | `src/datasets/dvs128_loader.py` | AEDAT 3.1 parser exists. Successfully extracts 119,960 microsecond polarity events from `data/dvs128/events_128.aedat`. Missing split mapping and continuous event queueing. |
| | `src/datasets/shd_loader.py` | HDF5 Spiking Heidelberg Digits parser exists. `h5py` dependency now verified and functional. Handles variable-length spikes and labels. |
| | `src/datasets/synthetic.py` | Explicitly marked as synthetic test fixture. Monotonic Poisson spike generation. |
| | `src/datasets/base.py` | `DatasetLoader`, `DatasetMetadata`, `DatasetSample`, `NeuromorphicEvent`, `DatasetRegistry`. Missing explicit `get_events()`, `get_labels()`, `get_source_provenance()`, `validate_integrity()`. |
| **Neuromorphic Core** | `src/neuromorphic/simulator.py` | Multi-core LIF simulation (`v_membrane`, decay, refractory period, ring topology). Discrete step indices (`step_idx`) drive updates rather than real `timestamp_ms`. |
| | `src/neuromorphic/attacks.py` | Injects weight shifts, extra spikes, or adds jitter to `spike.timestamp_ms`. Jitter does not influence delivery time or scheduling. |
| | `src/neuromorphic/topology.py` | Ring topology with intra-core and inter-core synaptic weights. |
| **Acquisition & Integrity**| `src/acquisition/collector.py` | Ingests snapshots, computes SHA-256 block hashes, builds Merkle root, packages `.nfd`. Placeholder signature documented. |
| | `src/acquisition/integrity.py` | SHA-256 data hashing and Merkle tree generation / verification. Detects tampering. |
| | `src/acquisition/dump_format.py`| Gzip JSON serialization for `.nfd` files. |
| **Reconstruction** | `src/reconstruction/timeline.py` | Detects `SYNAPSE_ANOMALY`, `SPIKE_BURST`, `MEMBRANE_ANOMALY`, `TIMING_DEVIATION`. |
| | `src/reconstruction/correlator.py` | Correlates chronological events, identifies root-cause core, infers causal edges and attack type. Operates solely on evidence package without ground truth. |
| **Evaluation** | `src/eval/reconstruction_score.py`| 5-dimension deterministic scoring (attack_type, location, temporal, mechanism, impact). Default threshold = 0.80. |
| | `src/eval/evidence_ablation.py` | Evaluates all $2^7 - 1 = 127$ non-empty artifact subsets to find Minimum Sufficient Evidence Sets. |
| **Web Dashboard** | `web/index.html`, `web/js/app.js` | Interactive GUI, D3 network visualization, timeline scrubber, dataset explorer, evidence verification tab. |

---

## 3. Existing Test Coverage

All 45 existing test cases pass across the suite:
- `tests/test_ablation.py`: 3 tests (ablation engine, filtering, score calculation)
- `tests/test_acquisition.py`: 2 tests (sealing, tamper detection)
- `tests/test_api.py`: 5 tests (REST endpoints)
- `tests/test_backends.py`: 3 tests (simulator adapter, capabilities)
- `tests/test_benchmarks.py`: 1 test (benchmarking script validation)
- `tests/test_dashboard_repair.py`: 6 tests (genuine DVS128 inspection, backend availability guards)
- `tests/test_datasets.py`: 6 tests (synthetic, DVS128 AEDAT, SHD HDF5 parsing)
- `tests/test_dfir_cti.py`: 1 test (STIX 2.1 exporter)
- `tests/test_eval.py`: 1 test (pipeline runner end-to-end)
- `tests/test_graph_dataflow.py`: 3 tests (graph topology export)
- `tests/test_neuromorphic.py`: 3 tests (LIF dynamics, attack injection, topology)
- `tests/test_phase2_validation.py`: 6 tests (phase 2 protocol checks)
- `tests/test_reconstruction.py`: 1 test (correlator and timeline)
- `tests/test_visualization.py`: 4 tests (neuron state rendering)

---

## 4. Prior Findings to Preserve

The following historical findings remain established facts and must not be misrepresented:
1. **Spike flooding:** Under high injection rates, inter-core queues drop spikes once buffer limits are exceeded.
2. **Synaptic-weight poisoning:** Perturbing random weight matrices changes weight values across seeds, but behavioral divergence depends strongly on whether input spikes activate the altered synapses.
3. **Temporal jitter:** Perturbing `spike.timestamp_ms` records anomalous timing in evidence metadata, but a step-discrete simulator with unit step delays does not alter neural firing times unless the scheduler is timestamp-aware.
4. **Reproducibility:** Experiments using fixed random seeds yield deterministic Merkle roots and reconstruction scores.
5. **Integrity:** Modifying any byte within a recorded `.nfd` block invalidates the Merkle root.
6. **Output safety:** Stage 3 outputs are archived in `results/phase2_validation/` and `results/ablation/` and must remain untouched.

---

## 5. Critical Implementation & Validation Gaps

### A. Dataset Integration Architecture Gaps
- `DatasetLoader` in `src/datasets/base.py` lacks standard methods required by Stage 4:
  - `load_recording()`
  - `get_events()`
  - `get_labels()`
  - `get_metadata()`
  - `get_source_provenance()`
  - `validate_integrity()`
- Need unified sample slicing, train/test split identification, and deterministic conversion to SNN input streams without destroying original event timestamps.

### B. Timestamp-Aware Scheduling Gap
- In `src/neuromorphic/simulator.py`, the simulator executes step-by-step ($t = \text{step} \times \text{dt}$). Incoming events are only indexed by integer `step_idx`.
- If an attack delays or advances a spike's `timestamp_ms`, the spike was still delivered in `step_idx`.
- **Stage 4 Solution:** Implement an event priority queue (`EventQueue`) that schedules and releases events based on true continuous time ($t_{\text{arrival}} = t_{\text{emit}} + \Delta t_{\text{delay}} + \delta_{\text{jitter}}$). Jitter directly determines in which discrete evaluation window or time slice the neuron integrates the charge.

### C. Queue Saturation & DoS Criterion Gap
- In `attacks.py`, spike storm injected spikes directly into the `step_spikes` list without passing through a bounded inter-core input queue.
- **Stage 4 Solution:** Implement an explicit FIFO `IntercoreQueue` with finite capacity $C_{\text{max}}$, measured service rate $\mu$, arrival rate $\lambda$, dropped packet counter $N_{\text{dropped}}$, and latency buffer. Define an explicit **Denial of Service (DoS) Success Criterion**:
  $$\text{DoS Condition} \iff \frac{N_{\text{dropped}}}{N_{\text{incoming}}} \ge \theta_{\text{drop}} \quad \text{and} \quad \bar{L}_{\text{service}} \ge 3 \cdot \bar{L}_{\text{baseline}}$$

### D. Model-Grounded Synaptic Poisoning Gap
- Current weight poisoning perturbs arbitrary weights in `self.topology.intra_weights`.
- **Stage 4 Solution:** Implement a documented feedforward/recurrent SNN architecture with trained weights mapping real input event features (e.g. DVS128 gesture or SHD frequency bands) to classification classes. Evaluate baseline accuracy vs. poisoned accuracy, logging exact modified synapses, weight deltas, and firing-rate divergence.

### E. Ground-Truth Isolation in Reconstruction
- Verify that `EventCorrelator` and `TimelineGenerator` operate strictly on `EvidencePackage` without reading `ground_truth`.
- Scoring in `ReconstructionScorer` must receive `reconstruction` and `ground_truth` only at the scoring phase.

### F. Complete Evidence-Ablation Study
- Systematically execute all $2^7 - 1 = 127$ combinations for each attack scenario under real dataset inputs.
- Audit the 0.80 threshold with a sensitivity analysis across $\theta \in [0.5, 0.95]$.

---

## 6. Proposed Experiment Design

1. **Dataset Sources:**
   - **Dataset A (DVS128 Gesture):** Real AEDAT 3.1 recordings (`data/dvs128/events_128.aedat`), SHA-256 `6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3`.
   - **Dataset B (Spiking Heidelberg Digits - SHD):** HDF5 audio spiking dataset parsed via `SHDDatasetLoader` with verified provenance.
2. **Experiment Runs:**
   - Matched pairs: Baseline Benign vs. Attack Perturbed vs. Benign Control Perturbation across multiple seeds ($S = \{42, 101, 2026\}$) and multiple real recordings.
3. **Evidence Acquisition:**
   - Record all 7 artifact classes ($E, T, N, W, G, K, I$).
   - Cryptographic SHA-256 per-block hashing and Merkle root calculation.
   - Tamper detection unit tests.
4. **Full 127-Subset Evidence Ablation:**
   - Compute reconstruction score, minimum sufficient evidence set, and volume tradeoff curves.
5. **Directory Isolation:**
   - Store all outputs exclusively in `results/stage4/real_data/`.

---

## 7. Files to Modify / Create

1. `STAGE4_AUDIT.md` (this audit document)
2. `src/datasets/base.py` (common dataset interface methods)
3. `src/datasets/dvs128_loader.py` & `src/datasets/shd_loader.py` (implement common interface)
4. `src/neuromorphic/intercore_queue.py` (bounded queue with DoS tracking)
5. `src/neuromorphic/simulator.py` (timestamp-aware event scheduling and queue integration)
6. `src/neuromorphic/attacks.py` (grounded attacks with explicit injection logs)
7. `src/neuromorphic/snn_classifier.py` (SNN model architecture and weights for gesture/digit inference)
8. `scripts/run_stage4_validation.py` (end-to-end reproducible experiment runner)
9. `tests/test_stage4_validation.py` (comprehensive Stage 4 test suite)
10. Stage 4 Reports:
    - `STAGE4_DATASET_VALIDATION_REPORT.md`
    - `STAGE4_ATTACK_VALIDATION_REPORT.md`
    - `STAGE4_FORENSIC_RECONSTRUCTION_REPORT.md`
    - `STAGE4_EVIDENCE_ABLATION_REPORT.md`
    - `STAGE4_FINAL_VALIDATION_REPORT.md`
11. `web/index.html` & `web/js/app.js` (UI updates to select real data vs synthetic, display Stage 4 results)

