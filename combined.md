# NeuroForensics Feature Tracker

## Existing Features (Verified)

- [x] ~~Multi-core SNN simulator~~ — verified by `tests/test_neuromorphic.py`
  - LIF neuron dynamics with configurable decay, threshold, refractory period, and inter/intra-core routing.
- [x] ~~Attack injection framework~~ — verified by `tests/test_neuromorphic.py::test_attack_injection`
  - Synaptic weight poisoning, spike storm / flooding, and timing jitter injection.
- [x] ~~Configurable experiment runner~~ — verified by `tests/test_eval.py::test_pipeline_runner_end_to_end`
  - YAML-configured pipeline runner with CLI interface.
- [x] ~~Spike evidence collection~~ — verified by `tests/test_acquisition.py`
  - Volatile spike stream capture per step with source/target neuron and core IDs.
- [x] ~~Synaptic-state collection~~ — verified by `tests/test_ablation.py`
  - Per-core synaptic weight matrix snapshotting.
- [x] ~~Neuron-state collection~~ — verified by `tests/test_ablation.py`
  - Membrane potentials and refractory state snapshots per neuron.
- [x] ~~Topology/routing evidence~~ — verified by `tests/test_neuromorphic.py::test_topology_initialization`
  - Static inter/intra-core synaptic connectivity maps.
- [x] ~~Formal artifact taxonomy / classes~~ — verified by `src/core/schemas.py`
  - Structured artifact types: `SPIKE_EVENTS`, `SPIKE_TIMING`, `NEURON_STATE`, `SYNAPTIC_STATE`, `TOPOLOGY_ROUTING`, `CONFIGURATION`, `INPUT_OUTPUT`.
- [x] ~~Evidence schema versioning & containerization~~ — verified by `tests/test_acquisition.py`
  - Sealed `.nfd` and compressed `.nfd.gz` evidence containers with cryptographic headers.
- [x] ~~SHA-256 snapshot hashing~~ — verified by `tests/test_acquisition.py`
  - Deterministic per-block hashing of state snapshots.
- [x] ~~Merkle root generation~~ — verified by `tests/test_acquisition.py`
  - Tree-structured hierarchical cryptographic Merkle root across all snapshot blocks.
- [x] ~~Merkle verification~~ — verified by `tests/test_acquisition.py::test_evidence_tamper_detection`
  - Tamper verification checking stored vs recomputed Merkle roots.
- [x] ~~Ground truth vs Forensic evidence separation~~ — verified by `tests/test_ablation.py::test_reconstruction_scoring_and_ground_truth_separation`
  - Attacker ground truth isolated from reconstructed evidence.
- [x] ~~Deterministic reconstruction scoring~~ — verified by `tests/test_ablation.py`
  - Quantitative scoring across 5 dimensions with weighted aggregate.
- [x] ~~Evidence subset representation & filtering~~ — verified by `tests/test_ablation.py::test_evidence_subset_filtering`
  - Modular masking and extraction of arbitrary artifact class combinations.
- [x] ~~Evidence ablation engine~~ — verified by `tests/test_ablation.py`
  - Full subset enumeration and systematic removal of artifact classes.
- [x] ~~Minimum Sufficient Evidence Set calculation~~ — verified by `tests/test_ablation.py`
  - Calculates smallest evidence subset(s) achieving target reconstruction thresholds.
- [x] ~~Machine-readable result export~~ — verified by `tests/test_eval.py`
  - Exports ablation results as structured JSON and CSV.

## Phase: Real-World Data and Lava

### Dataset Ingestion
- [x] ~~SHD dataset loader (HDF5 parser with h5py/tables)~~ — verified by `tests/test_datasets.py`
- [x] ~~DVS128 Gesture dataset loader (AEDAT parser)~~ — verified by `tests/test_datasets.py::test_dvs128_aedat_parser_valid`
- [x] ~~Dataset registry and metadata management~~ — verified by `tests/test_datasets.py::test_dataset_registry`
- [x] ~~Dataset provenance and integrity metadata (checksum, license, citation)~~ — verified by `src/datasets/base.py`
- [x] ~~Dataset validation (timestamp ordering, event counts, malformed records)~~ — verified by `tests/test_datasets.py`
- [x] ~~Synthetic dataset explicitly labelled as test fixture~~ — verified by `src/datasets/synthetic.py`
- [x] ~~Dataset setup guide and smoke-test fixture~~ — verified by `docs/dataset-setup-guide.md`
- [x] ~~Dataset metadata exposed through backend API~~ — verified by `tests/test_api.py::test_api_datasets`

### Backend Adapter Architecture
- [x] ~~Abstract SNN backend interface (`SNNBackendAdapter`)~~ — verified by `src/backends/base.py`
- [x] ~~Built-in LIF simulator adapter~~ — verified by `tests/test_backends.py::test_builtin_simulator_adapter_lifecycle`
- [x] ~~Lava compatibility assessment documented~~ — verified by `docs/phase-real-data-lava-audit.md`
- [x] ~~Lava CPU adapter (stub & guard — Lava unavailable on Python 3.14)~~ — verified by `tests/test_backends.py::test_lava_cpu_adapter_reporting_and_guarding`
- [x] ~~Backend capability reporting (observable variables, limitations)~~ — verified by `tests/test_api.py::test_api_backends`
- [x] ~~Execution backend labelling (simulator vs Lava CPU vs hardware)~~ — verified by `src/backends/base.py`

### Observation and Forensic Acquisition
- [x] ~~Backend-neutral observation interface~~ — verified by `src/backends/base.py` (`StepObservation`)
- [x] ~~Observable-state acquisition from real datasets~~ — verified by `src/datasets/base.py`
- [x] ~~Evidence record schema with full provenance~~ — verified by `src/acquisition/collector.py`
- [x] ~~Baseline vs attack snapshot preservation~~ — verified by `src/eval/runner.py`
- [x] ~~Fix: mock ECDSA signature documented as placeholder~~ — verified in `src/acquisition/collector.py`
- [x] ~~Fix: hardcoded `merkle_verification_passed` → actual re-verification~~ — verified in `src/eval/metrics.py`
- [x] ~~Fix: hardcoded `total_anomalous_spikes` multiplier → actual count~~ — verified in `src/reconstruction/correlator.py`

### Controlled Attack Workbench
- [x] ~~Attack experiment interface with backend compatibility checks~~ — verified by `tests/test_api.py::test_api_attack_execution`
- [x] ~~Attack parameter validation and preview~~ — verified by `web/api/server.py`
- [x] ~~Baseline preservation before attack execution~~ — verified by `src/eval/runner.py`
- [x] ~~Ground-truth record generated separately from evidence~~ — verified by `tests/test_ablation.py`
- [x] ~~Clear labelling of software-injected vs hardware attacks~~ — verified in `src/backends/base.py`

### Interactive Dashboard
- [x] ~~API server (FastAPI) for dynamic backend~~ — verified by `tests/test_api.py`
- [x] ~~Dataset Explorer (browse, select, preview events)~~ — verified by `web/index.html` & `web/js/app.js`
- [x] ~~SNN Replay (start, pause, step, reset, speed control)~~ — verified by `web/api/server.py` (`/api/simulation/step`)
- [x] ~~Baseline-versus-Attack Comparison view~~ — verified by `web/index.html`
- [x] ~~Evidence Inspector (browse, filter, verify records)~~ — verified by `web/index.html`
- [x] ~~Attack Workbench UI (configure, preview, execute, inspect)~~ — verified by `web/index.html` & `web/js/app.js`
- [x] ~~Evidence Sufficiency Lab (subset selection, reconstruction, comparison)~~ — verified by `web/index.html`

### Dashboard Repair & Truthful State
- [x] ~~Global contradictory stats removed & replaced with Active Experiment Context Banner~~ — verified by `web/index.html` & `web/js/app.js`
- [x] ~~Truthful Backend Availability & Lava rejection guard~~ — verified by `tests/test_dashboard_repair.py::test_backends_reporting_and_lava_guard` & `test_execute_attack_on_unavailable_backend_rejected`
- [x] ~~Interactive Dataset Explorer with genuine AEDAT sample event streaming~~ — verified by `tests/test_dashboard_repair.py::test_datasets_endpoint_includes_genuine_local_file` & `test_dvs128_sample_retrieval_returns_genuine_events`
- [x] ~~Root `/` redirect to `/dashboard/` eliminating 404~~ — verified by `tests/test_dashboard_repair.py::test_root_redirect_to_dashboard`
- [x] ~~Experiment ID context stamping & state transition model~~ — verified by `tests/test_dashboard_repair.py::test_execute_attack_produces_stamped_experiment_context`
- [x] ~~Tab-specific neutral empty states replacing fabricated 91.5% default scores~~ — verified in `web/index.html` & `web/js/app.js`

### Microscopic Neuron Visualization & Interactive Timeline
- [x] ~~Genuine 128-neuron microscopic SNN canvas with biological LIF states~~ — verified by `web/index.html` & `web/js/app.js`
- [x] ~~Intra-core and inter-core synaptic connectivity rendering with weight mapping~~ — verified by `tests/test_visualization.py::test_topology_export_contains_microscopic_neurons_and_synapses`
- [x] ~~Interactive SNN timeline playback, single-stepping, and scrubbing ($t \in [0, 100]$ ms)~~ — verified by `web/js/app.js`
- [x] ~~Neuron Inspector displaying membrane potential ($V_m$), firing history, and forensic classification~~ — verified by `web/js/app.js`
- [x] ~~Bidirectional core topology synchronization and population focus drill-down~~ — verified by `web/js/app.js`
- [x] ~~DVS128 relative millisecond timestamping and recording epoch disambiguation~~ — verified by `tests/test_visualization.py::test_dvs128_relative_timestamps_and_offsets`
- [x] ~~Interactive Evidence Sufficiency ablation execution trigger~~ — verified by `web/index.html` & `web/js/app.js`


### End-to-End Validation & Evidence Ablation
- [x] ~~Experiment-to-Graph Data Flow & State Synchronization~~ — verified by `tests/test_graph_dataflow.py` & `web/js/app.js`
  - Fixed scenario store initialization to pre-load full network topology and genuine observations for all scenarios; eliminates "No experiment loaded" defect.
- [x] ~~Intel Lava CPU Isolated Subprocess Worker Execution~~ — verified by direct smoke tests in `.venv-lava` (Python 3.10.11, `lava-nc` 0.10.0) and `tests/test_graph_dataflow.py::test_lava_cpu_graph_dataflow`.
- [x] ~~Truthful Backend Identity & Guard Rails~~ — verified by `tests/test_dashboard_repair.py::test_backends_reporting_and_lava_guard`.
- [x] ~~Real Dataset Ingestion Lineage & Normalization~~ — verified by `tests/test_phase2_validation.py` & `data/dvs128/events_128.aedat` (SHA-256: `6d982a802018cf48...`).
- [x] ~~Benign vs Malicious Experimental Baseline~~ — verified by `tests/test_phase2_validation.py::test_benign_control_produces_zero_false_positives` (zero false positives on unperturbed runs).
- [x] ~~Evidence-Sufficiency Ablation Degradation~~ — verified by `tests/test_ablation.py` & `tests/test_phase2_validation.py::test_evidence_sufficiency_ablation_degradation`.
- [x] ~~Deterministic Scoring without Ground-Truth Leakage~~ — verified by `tests/test_ablation.py::test_reconstruction_scoring_and_ground_truth_separation`.

### Testing
- [x] ~~Dataset parsing tests (with fixture files)~~ — verified by `tests/test_datasets.py`
- [x] ~~Malformed input handling tests~~ — verified by `tests/test_datasets.py`
- [x] ~~Backend adapter tests~~ — verified by `tests/test_backends.py`
- [x] ~~API endpoint tests~~ — verified by `tests/test_api.py`
- [x] ~~Visualization and microscopic topology tests~~ — verified by `tests/test_visualization.py`
- [x] ~~Graph dataflow and experiment caching tests~~ — verified by `tests/test_graph_dataflow.py`
- [x] ~~Automated continuous benchmark runner (`scripts/run_benchmarks.py`)~~ — verified by `tests/test_benchmarks.py`
  - Generates standardized LaTeX comparative tables (`results/benchmarks/comparative_evaluation_table.tex`) and IEEE-formatted evidence-sufficiency trade-off plots (`results/benchmarks/evidence_sufficiency_tradeoff.png`, `.pdf`).
- [x] ~~Full test suite regression~~ — all 44 tests passed (`tests/test_*.py`)

### Documentation
- [x] ~~Implementation and baseline audit (`docs/implementation-audit.md`)~~
- [x] ~~Intel Lava CPU validation report (`docs/lava-validation.md`)~~
- [x] ~~Dataset validation & SNN data lineage (`docs/dataset-validation.md`)~~
- [x] ~~Experimental protocol (`docs/experimental-protocol.md`)~~
- [x] ~~Evidence ablation methodology & results (`docs/evidence-ablation.md`)~~
- [x] ~~Known limitations truthfully documented~~

## Known Limitations

- **Lava-nc Environment:** Cannot install directly under Python 3.14.4. Successfully executed via an isolated Python 3.10 virtual environment (`.venv-lava`) with `lava-nc` 0.10.0 using subprocess JSON streaming.
- **Physical hardware:** No Loihi/Loihi 2 or SpiNNaker hardware access. All execution is strictly software-simulated (CPU emulation).
- **ECDSA signature:** `collector_signature` in NFD header is an explicitly labelled ECDSA placeholder string, not a production HSM digital signature.
- **Dataset downloads:** SHD (~700 MB) requires manual download and `h5py` (uninstalled in Python 3.14); unit-tested on fixtures. DVS128 Gesture compressed sample (`events_128.aedat`, 856 KB, 119,960 events) is present locally and fully verified.

# NeuroForensics

> **Attack-Specific Evidence Sufficiency & Forensic Reconstruction for Neuromorphic SNN Systems**

## Overview
**NeuroForensics** investigates digital forensics and incident response (DFIR) for event-driven neuromorphic architectures and Spiking Neural Networks (SNNs).

The primary research objective is:
> **Given a neuromorphic attack, which observable artifact combinations are actually sufficient to reconstruct what happened?**

---

## 🔬 Evidence Artifact Taxonomy

NeuroForensics defines explicit, formal artifact classes:
- `SPIKE_EVENTS`: Inter-core and intra-core discrete spike events (source core/neuron, target core/neuron, step index).
- `SPIKE_TIMING`: High-resolution continuous / microsecond timestamps (`timestamp_ms`) capturing phase and jitter.
- `NEURON_STATE`: Volatile membrane potential vectors ($V_m$) and refractory counter states.
- `SYNAPTIC_STATE`: Programmable intra-core synaptic weight connectivity matrices ($W_{intra}$).
- `TOPOLOGY_ROUTING`: Core routing tables, inter-core connectivity matrices ($W_{inter}$), and bus mapping.
- `CONFIGURATION`: Hyperparameters (leak decay factor, firing threshold $V_{th}$, refractory durations).
- `INPUT_OUTPUT`: Sensory Poisson stimulus channels and readout activations.

---

## 🛡️ Ground Truth vs. Forensic Evidence Separation

To avoid circular evaluation:
- **Attacker Simulation / Ground Truth** (`AttackGroundTruth`): Holds true ground truth (attack type, target core/neurons, injection window, true synaptic weight shifts, true cascading propagation path).
- **Forensic Acquisition & Reconstruction Engine**: Operates **strictly on acquired evidence artifacts** inside sealed `.nfd` containers without direct access to ground truth.
- **Deterministic Reconstruction Scoring** (`ReconstructionScorer`): Compares reconstructed findings against Ground Truth across:
  - `attack_type_score` (Identification accuracy)
  - `location_score` (Target / root-cause core localization)
  - `temporal_score` (Initial compromise step detection accuracy)
  - `mechanism_score` (Causal propagation transition accuracy)
  - `impact_score` (Blast radius / compromised core Jaccard similarity)
  - `overall_score` (Weighted aggregate metric $\in [0.0, 1.0]$)

---

## ⚙️ Evidence Ablation & Minimum Sufficient Evidence

The **Evidence Ablation Engine** (`src/eval/evidence_ablation.py`) exhaustively evaluates all candidate evidence subsets ($2^N - 1$) to compute:
1. **Evidence Sufficiency Curves**: Reconstruction score vs. serialized evidence volume (bytes).
2. **Minimum Sufficient Evidence Set(s)**: Smallest cardinality subset achieving configured reconstruction threshold ($\ge 0.80$).
3. **Attack $\times$ Artifact Matrix**: Empirically measured necessity (`Required`, `Helpful`, `Redundant`, `Not applicable`).

### Measured Attack $\times$ Artifact Matrix:
| Attack Scenario | Spike Events | Spike Timing | Neuron State | Synaptic State | Topology Routing | Configuration | Input/Output | Minimum Cardinality | Minimum Sufficient Set(s) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Synaptic Weight Poisoning** | Redundant | Redundant | Redundant | **Required** | Redundant | Redundant | Redundant | **1** | `{SYNAPTIC_STATE}` |
| **DoS Spike Flooding** | **Required** | Redundant | Redundant | Redundant | Redundant | Redundant | Redundant | **1** | `{SPIKE_EVENTS}` |
| **Timing Jitter Attack** | **Required** | **Required** | Redundant | Redundant | Redundant | Redundant | Redundant | **2** | `{SPIKE_EVENTS, SPIKE_TIMING}` |

---

## 🚀 Quickstart & Reproduction

### 1. Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Run Single Scenario Forensic Pipeline
```bash
python main.py run-pipeline --scenario synaptic_poisoning --output-dir data/outputs
```

### 3. Run Exhaustive Evidence Ablation Study
```bash
python main.py run-ablation --output-dir results/ablation
```
Exports machine-readable experiment results to `results/ablation/experiment_<id>.json` and `results/ablation/experiment_<id>.csv`.

### 4. Launch Research Dashboard
```bash
python main.py serve-dashboard --port 8080
```
Navigate to `http://localhost:8080` to inspect:
- Interactive Evidence Sufficiency Curves
- Attack $\times$ Artifact Matrix
- Multi-Core Topology & Attack Progression Graph
- Chronological Reconstruction Timelines
- Merkle Tree Verification Status

### 5. Run Test Suite
```bash
pytest tests/ -v
```

---

## 📌 Implementation Boundary & Known Limitations
- **Backend Classification**: Simulator is a multi-core Leaky Integrate-and-Fire (LIF) network with deterministic ring-bus topology.
- **Physical Hardware**: Neuromorphic execution is **simulated** in software. Physical hardware integration (e.g. Intel Loihi / SpiNNaker adapters) are research interfaces for future hardware runtime bindings.
- **Integrity**: Forensic containers (`.nfd` / `.nfd.gz`) enforce SHA-256 block hashing and cryptographic Merkle tree chain-of-custody verification.
