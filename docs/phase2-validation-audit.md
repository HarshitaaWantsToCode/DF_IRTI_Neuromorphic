# Phase 2 Validation Audit & Verification

**Date:** 2026-10-17  
**Environment:** Windows, Python 3.14.4, pytest-9.1.1  
**Baseline Test Run:** 24/24 tests PASSED (19.76s) -> 30/30 tests PASSED with Phase 2 validation  

---

## 1. Module-by-Module Inspection & Findings

### Datasets (`src/datasets/`)
- **Initial Claim:** Supported DVS128 Gesture and SHD loaders.
- **Audit Reality:**
  - `shd_loader.py`: Implements genuine HDF5 group navigation (`/spikes/times`, `/spikes/units`, `/labels`). Clean fallback when `h5py`/`tables` is uninstalled.
  - `dvs128_loader.py`: Originally parsed only AEDAT 3.1 packet headers. Real-world recordings from standard DVS128 cameras (such as jAER recordings) use AEDAT 2.0 (8-byte binary words: Big-endian address + timestamp in microseconds).
  - **Correction Applied:** Extended `DVS128GestureLoader` to automatically detect AEDAT 2.0 vs 3.1 format, unpack 128x128 retina events (x, y, polarity), normalize timestamps to canonical seconds, and compute chunked SHA-256 hashes without modifying raw files.

### Neuromorphic Execution Backend (`src/neuromorphic/`, `src/backends/`)
- **Initial Claim:** Built-in multi-core simulator and Lava adapter.
- **Audit Reality:**
  - `simulator.py`: Previously used hardcoded internal Poisson noise injection on Core 0 on every step, ignoring external input spikes.
  - **Correction Applied:** Added `input_spikes: Optional[Dict[int, List[int]]]` to `NeuromorphicSimulator.step()` and forwarded it through `BuiltinSimulatorAdapter.step()`. Real sensory DVS128 spike packets now directly depolarize Core 0 neurons, generating genuine spike cascades across cores.
  - `lava_adapter.py`: Correctly identified that `lava-nc` cannot install on Python 3.14 (requires Python `<3.11`, repo archived May 2026). Correctly guarded to raise `RuntimeError` rather than fabricating execution.

### Forensic Acquisition & Integrity (`src/acquisition/`)
- **Initial Claim:** Merkle tree verification and ECDSA signature.
- **Audit Reality:**
  - Merkle root re-computation is fully functional and cryptographically sound using SHA-256 block hashes.
  - `collector_signature`: Was an unauthenticated string `ECDSA-SIG-...`.
  - **Correction Applied:** Documented as an explicit placeholder (`ECDSA-PLACEHOLDER-...`) and recorded in metadata as non-cryptographic emulation, avoiding false security claims.
  - Dynamic verification in `src/eval/metrics.py` now recalculates block hashes and re-verifies against `header.root_merkle_hash`.

### Reconstruction & Anomaly Correlation (`src/reconstruction/`)
- **Initial Claim:** Causal graph reconstruction from evidence.
- **Audit Reality:**
  - Reconstruction correctly receives only the sealed `EvidencePackage` without access to `AttackGroundTruth`.
  - Fixed hardcoded multiplier `len(sorted_events) * 12` in `correlator.py` to count actual anomaly events.
  - Added benign control baseline verification: zero false-positive anomaly events when feeding real DVS128 events under nominal conditions.

### Evidence-Sufficiency Experiments (`src/eval/evidence_ablation.py`)
- **Mathematical Formulation:**
  $$\mathcal{S}^* = \arg\min |S|, \quad \text{subject to } R(A, S) \ge \tau$$
  where $\tau = 0.80$.
- **Verification:** Evaluated all $2^7 - 1 = 127$ subsets.
- When `SYNAPTIC_STATE` is removed during a synaptic poisoning attack, the reconstruction score drops from 0.835 to below threshold (0.0–0.2), proving that removing evidence classes causes measurable degradation.
