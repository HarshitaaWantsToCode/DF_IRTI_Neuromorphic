# NeuroForensics Implementation & System Verification Audit

**Date:** October 20, 2026  
**Auditor:** Senior Neuromorphic Systems & Forensic Research Engineer  
**Workspace:** `DF+IRTI Project` (NeuroForensics)  
**Primary Environment:** Python 3.14.4 (win32, x64)  
**Lava Worker Environment:** Python 3.10.11 (`.venv-lava`, lava-nc v0.10.0)

---

## 1. System Overview & Architecture

NeuroForensics is a deterministic digital-forensics and incident-reconstruction platform designed for multi-core Neuromorphic Spiking Neural Networks (SNNs). The system is structured into five core pipelines:
1. **Neuromorphic Execution & Stimulation:** Multi-core Leaky Integrate-and-Fire (LIF) network with deterministic ring routing bus topology (4 cores, 128 total neurons, 2,048 intra-core synapses, 512 inter-core synapses) or isolated Intel Lava CPU PyProcModel process networks.
2. **Forensic Acquisition & Chain-of-Custody:** Snapshot-based non-volatile evidence capture computing block SHA-256 hashes and verifiable cryptographic Merkle trees, serialized into compressed `.nfd.gz` forensic containers.
3. **Deterministic Forensic Reconstruction:** Pure-evidence, rule-based temporal state divergence analysis and causal progression correlation without privileged access to ground-truth scenario configs.
4. **DFIR & Threat Intelligence:** Incident containment planning and STIX 2.1 indicator mapping (MITRE ATT&CK TTPs: T1565.001, T1499.004, T1071.004).
5. **Evidence Ablation Engine:** Combinatorial subset evaluation (\(2^N - 1 = 127\) subsets across 7 forensic artifact classes) computing empirical sufficiency curves and identifying inclusion-minimal sufficient evidence sets (\(R(A,S) \ge \tau = 0.80\)).

---

## 2. Verified Test Execution Baseline

Execution command:
```powershell
C:\Python314\python.exe -m pytest tests/ -v
```
**Outcome:** All 43 tests pass (100% pass rate) in 87.50 seconds.

### Test Breakdown by Subsystem:
- `tests/test_ablation.py` (3 tests): Verifies artifact class subset masking, ground-truth isolation during scoring, score degradation, and minimum sufficient set identification.
- `tests/test_acquisition.py` (2 tests): Verifies Merkle tree generation, block hashes, root integrity, and bit-level tamper detection.
- `tests/test_api.py` (5 tests): Validates health checks, `/api/datasets`, `/api/backends`, `/api/simulation/step`, and `/api/attacks/execute`.
- `tests/test_backends.py` (3 tests): Verifies multi-core LIF lifecycle, attack attachments, and Lava CPU subprocess adapter status reporting.
- `tests/test_dashboard_repair.py` (6 tests): Validates root redirect to dashboard, genuine DVS128 local file availability, real event pagination, Lava guard rails, and execution context stamping.
- `tests/test_datasets.py` (5 tests): Validates synthetic Poisson stream loader, genuine AEDAT 3.1 binary packet parser, corrupted file detection, SHD fallback behavior without h5py, and dataset registry.
- `tests/test_dfir_cti.py` (1 test): Validates DFIR containment playbooks and STIX 2.1 JSON bundle serialization.
- `tests/test_eval.py` (1 test): Full pipeline integration runner across simulation, acquisition, reconstruction, and metric generation.
- `tests/test_graph_dataflow.py` (3 tests): Proves that both built-in LIF and Lava CPU return complete topology structures (`num_cores`, `neurons_per_core`, `intra_synapses`, `inter_synapses`), timestamp-stamped spike streams, and 404 on nonexistent IDs.
- `tests/test_neuromorphic.py` (3 tests): Proves network topology matrices, LIF membrane leak/integration/fire, and attack injection.
- `tests/test_phase2_validation.py` (6 tests): Validates genuine sample ingestion, Merkle tamper detection, zero false positives on benign controls, and repeated run determinism.
- `tests/test_reconstruction.py` (1 test): Validates timeline reconstruction from discrete evidence snapshots.
- `tests/test_visualization.py` (4 tests): Proves microscopic neuron/synapse topology export, `/api/simulation/topology` endpoint, DVS128 relative microsecond/millisecond normalization, and full payload returns.

---

## 3. Discovered Defects and Remediations

| ID | Component | Defect Description | Severity | Remediation & Status |
|:---|:---|:---|:---|:---|
| **DEF-01** | UI State Store (`web/js/app.js`) | Switching between scenarios in the Attack Workbench or selecting pre-loaded scenarios rendered "No experiment loaded" or missing topology because static scenario templates lacked `network_topology`. | **Critical** | Patched `app.js` to pre-load all scenarios with full 4-core topology and verified spike observations from `data.json`, `data_spike_storm.json`, and `data_timing_jitter.json`. |
| **DEF-02** | Lava Environment Isolation | Lava-nc is unmaintained on Python 3.14 (requires Python 3.8-3.10). Invoking Lava in the primary Python runtime fails. | **High** | Verified Python 3.10 virtual environment (`.venv-lava`) with `lava-nc` 0.10.0 and verified `src/backends/lava_worker.py` subprocess execution returning genuine spikes and final voltages. |
| **DEF-03** | AEDAT 3.1 Header / Timestamp Offset | Raw DVS128 hardware timestamps start at arbitrary system boot offsets (e.g. 194.08 seconds), which if unnormalized causes desynchronization with simulation step time (dt = 1ms). | **Medium** | Normalized `relative_time_ms = (timestamp_raw - t0) / 1000.0` preserving both raw hardware clocks and zero-aligned millisecond offsets. |
| **DEF-04** | Ground-Truth Leakage in Reconstruction | Reconstruction engine could theoretically inspect scenario configs if passed directly. | **High** | Architecturally verified: `TimelineGenerator` and `EventCorrelator` consume strictly `EvidencePackage` objects; ground-truth is evaluated strictly in `ForensicEvaluator` and `EvidenceAblationEngine` post-reconstruction. |
