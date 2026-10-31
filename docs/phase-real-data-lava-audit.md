# Phase Audit: Real-World Neuromorphic Data, Lava Integration, and Interactive Forensic Experiments

**Date:** 2026-10-16
**Python Version:** 3.14.4
**Existing Tests:** 11/11 PASSED (20.23s)

---

## 1. Existing Backend and Frontend Frameworks

### Backend
- **Language:** Python 3.14.4
- **CLI:** `click` (main.py) with commands: `run-pipeline`, `run-ablation`, `serve-dashboard`, `evaluate`
- **Web Server:** `http.server.SimpleHTTPRequestHandler` (static file server, no API backend)
- **Schemas:** `pydantic` v2.13.3 (all models in `src/core/schemas.py`)
- **Config:** YAML via `pyyaml`
- **Output:** Rich console tables

### Frontend
- **Architecture:** Single-page static HTML + vanilla JS + vanilla CSS
- **Data Source:** Pre-generated `web/data.json` and `web/matrix.json` (written by pipeline runner)
- **Visualizations:** Canvas-based (topology, sufficiency curve, neural net, synapse matrix)
- **No API Backend:** Dashboard reads static JSON files. No REST API, no WebSocket, no server-sent events.

### Observation
The dashboard is a **static visualization** of pre-computed pipeline results. There is no interactive backend. Adding interactive features requires implementing an API server.

---

## 2. Existing SNN Simulator and Attack Injection

### Simulator (`src/neuromorphic/simulator.py`)
- **Status:** ✅ Implemented and tested
- **Model:** Leaky Integrate-and-Fire (LIF) multi-core architecture
- **Topology:** Ring-bus with feedforward inter-core routing (`src/neuromorphic/topology.py`)
- **Input:** Synthetic Poisson process (rate=0.12) injected to Core 0
- **Configurable:** num_cores, neurons_per_core, decay_factor, threshold_mv, dt_ms, seed
- **No real-dataset ingestion.** Only synthetic random Poisson input.

### Attack Injection (`src/neuromorphic/attacks.py`)
- **Status:** ✅ Implemented and tested
- **Attack types:**
  1. Synaptic weight poisoning (integrity)
  2. Spike flooding / DoS (availability)
  3. Timing jitter (temporal)
- **Ground truth** (`AttackGroundTruth`) is properly isolated from reconstruction logic.
- **Note:** Attacks are software-level perturbations on the internal simulator, not hardware fault injection.

---

## 3. Evidence Schemas and Acquisition Logic

### Schemas (`src/core/schemas.py`)
- **Status:** ✅ Well-structured
- Defined artifact classes: `SPIKE_EVENTS`, `SPIKE_TIMING`, `NEURON_STATE`, `SYNAPTIC_STATE`, `TOPOLOGY_ROUTING`, `CONFIGURATION`, `INPUT_OUTPUT`
- Models: `SpikeEvent`, `CoreStateSnapshot`, `SystemStateSnapshot`, `EvidenceRecord`, `NFDHeader`, `EvidencePackage`, `AttackGroundTruth`, `TimelineEvent`, `AttackReconstructionGraph`, `ReconstructionScore`
- `EvidenceRecord` model exists but is **not used** in actual acquisition — the collector uses `SystemStateSnapshot` directly.

### Acquisition (`src/acquisition/`)
- **Collector** (`collector.py`): ✅ Records snapshots per step, seals into evidence packages with Merkle root
- **Dump format** (`dump_format.py`): ✅ JSON-based .nfd / .nfd.gz serialization
- **Integrity** (`integrity.py`): ✅ SHA-256 hashing, Merkle tree, verification
- **Limitation:** `collector_signature` is a mock string (`ECDSA-SIG-{hash[:16]}`), not a real digital signature.

---

## 4. Hashes, Merkle-Tree Implementation, and Verification Tests

- **SHA-256 per-block hashing:** ✅ Implemented (`ChainOfCustodyVerifier.hash_data`)
- **Merkle tree:** ✅ Implemented (`compute_merkle_root`) — standard binary tree with hash concatenation
- **Verification:** ✅ `verify_integrity` re-computes Merkle root from snapshots and compares to stored root
- **Tamper test:** ✅ `test_evidence_tamper_detection` modifies a snapshot and verifies integrity fails
- **Serialization round-trip test:** ✅ Saves .nfd, reloads, checks root hash matches

---

## 5. Timeline Reconstruction and Attack Propagation Graph

### Timeline Generator (`src/reconstruction/timeline.py`)
- **Status:** ✅ Implemented
- Detects: SYNAPSE_ANOMALY, SPIKE_BURST, MEMBRANE_ANOMALY, TIMING_DEVIATION
- Operates on evidence artifacts only (checks `included_artifacts` set)
- Uses deterministic thresholds, no ML

### Event Correlator (`src/reconstruction/correlator.py`)
- **Status:** ✅ Implemented
- Classifies attack type from observed event types
- Identifies root cause core, builds causal edge chain
- Does **not** receive ground truth as input ✅

### Graph Builder (`src/reconstruction/graph_builder.py`)
- **Status:** ✅ Builds networkx graph and D3.js JSON

### Observation
- `total_anomalous_spikes` is set to `len(sorted_events) * 12` — a synthetic multiplier, not a measured count.
- Graph builder hardcodes 4 cores in `to_d3_json`.

---

## 6. Dataset Ingestion and Event Normalization

- **Status:** ❌ Missing
- No dataset loader exists.
- No event normalization or conversion pipeline.
- All input is synthetic Poisson noise generated internally by the simulator.
- No external data ingestion interface, file format parsers, or dataset registry.

---

## 7. Dashboard Routes, Components, and API Contracts

- **Status:** Partially implemented (static only)
- **Tabs:** Evidence Sufficiency & Ablation, Attack Reconstruction & Topology, DFIR Playbook & CTI
- **Data:** Reads from `data.json` and `matrix.json` pre-generated by pipeline runner
- **No API:** No REST endpoints, no dynamic data fetching, no interactive experiment execution
- **Visualization:** Canvas-based topology, sufficiency curve, neural net graph, synapse matrix animation
- **Controls:** Scenario dropdown (loads different JSON data), tab switching, STIX JSON toggle, synapse animation pause

---

## 8. Benchmark Implementation and Ground-Truth Handling

### Reconstruction Scorer (`src/eval/reconstruction_score.py`)
- **Status:** ✅ Deterministic, well-tested
- Dimensions: attack_type, location, temporal, mechanism, impact
- Weighted aggregate with configurable weights
- Threshold-based pass/fail

### Evidence Ablation Engine (`src/eval/evidence_ablation.py`)
- **Status:** ✅ Fully implemented
- Exhaustive 2^N subset evaluation
- Minimum sufficient set calculation
- Attack × Artifact matrix computation
- JSON/CSV export

### Baselines (`src/eval/baselines.py`)
- **Status:** ✅ Two baselines (spike rate threshold, periodic sampling)

### Ground-Truth Handling
- ✅ Ground truth isolated in `AttackGroundTruth` model
- ✅ Not passed to reconstruction engine
- ✅ Only used in scoring after reconstruction completes

---

## 9. Existing Tests, Dependencies, and Setup

### Tests (11/11 PASSED)
| Test | Status |
|------|--------|
| `test_topology_initialization` | ✅ PASSED |
| `test_simulator_step` | ✅ PASSED |
| `test_attack_injection` | ✅ PASSED |
| `test_acquisition_and_merkle_verification` | ✅ PASSED |
| `test_evidence_tamper_detection` | ✅ PASSED |
| `test_dfir_and_stix_generation` | ✅ PASSED |
| `test_pipeline_runner_end_to_end` | ✅ PASSED |
| `test_evidence_subset_filtering` | ✅ PASSED |
| `test_reconstruction_scoring_and_ground_truth_separation` | ✅ PASSED |
| `test_evidence_ablation_degradation_and_minimum_sufficient_sets` | ✅ PASSED |
| `test_timeline_reconstruction` | ✅ PASSED |

### Dependencies
```
numpy>=1.24.0, scipy>=1.10.0, networkx>=3.0, pandas>=2.0.0
matplotlib>=3.7.0, seaborn>=0.12.0, click>=8.1.0, pydantic>=2.0.0
pytest>=7.3.0, pyyaml>=6.0, stix2>=3.0.1, rich>=13.0.0
```

### Missing optional dependencies
- `h5py` / `tables` — needed for SHD dataset
- `lava-nc` — incompatible (requires Python <3.11, repo archived May 2026)

---

## 10. Hardcoded Metrics, Mock Telemetry, and Unsupported Claims

### Issues Found

| Item | Location | Issue |
|------|----------|-------|
| `collector_signature` | `collector.py:60` | Mock string `ECDSA-SIG-{hash[:16]}`, not a real ECDSA signature |
| `total_anomalous_spikes` | `correlator.py:88` | `len(sorted_events) * 12` — fabricated multiplier |
| `confidence_score` | `ttp_mapper.py:53` | Hardcoded `0.92` for all indicators |
| `merkle_verification_passed` | `metrics.py:63` | Hardcoded `True`, never actually re-verified |
| `Merkle Integrity Check` | `runner.py:170` | Hardcoded `"PASSED (Tamper-Free)"` in output table |
| `graph_builder.py:37` | `graph_builder.py:37` | Hardcodes 4 cores in `to_d3_json` |
| Dashboard badge | `index.html:20` | Shows "6-Core LIF Architecture" but config uses 4 cores |

### Claims that need caveats
- "Cryptographic seal" — uses SHA-256 hashes but the ECDSA signature is a mock string
- All data is synthetic; no claims about real-world attack detection are supported
- Baseline comparisons are valid only within the simulated environment

---

## 11. Lava Compatibility Assessment & Isolated Worker Architecture

| Factor | Status |
|--------|--------|
| Repository | Archived May 13, 2026 (read-only) |
| Latest release | v0.10.0 (requires Python >=3.8, <3.11) |
| Host Python | 3.14.4 (incompatible for direct installation) |
| Secondary Python | 3.10 (installed at `C:\Users\harsh\AppData\Local\Programs\Python\Python310\python.exe`) |
| Installation | ✅ SUCCESS in `.venv-lava` (Python 3.10 virtual environment) |
| Core Execution | ✅ PASSED — `Loihi1SimCfg(select_tag='floating_pt')` CPU simulation verified |
| Worker Architecture | Isolated Subprocess Worker (`src/backends/lava_worker.py`) communicating via JSON IPC |
| Availability Rule | Truthful: Marked available only after verified execution of LIF process smoke test |

**Decision & Implementation:** To avoid polluting or downgrading the main Python 3.14 environment, Lava is hosted inside `.venv-lava`. The `LavaCPUAdapter` executes genuine neuromorphic simulations through `lava_worker.py` over an isolated subprocess. If the virtual environment or execution test fails, Lava is truthfully marked unavailable and never falls back silently to the simulator.

---

## Summary: Implementation Priorities

1. **Dataset ingestion** — SHD (HDF5) and DVS128 Gesture (AEDAT) loaders
2. **Backend adapter architecture** — Abstract SNN backend with built-in LIF and Lava stub
3. **API server** — Flask/FastAPI backend for interactive dashboard
4. **Observation schema** — Backend-neutral evidence collection
5. **Interactive dashboard** — Dataset explorer, SNN replay, attack workbench
6. **Evidence sufficiency experiments** — With real data
7. **Tests** — Unit, integration, and end-to-end
