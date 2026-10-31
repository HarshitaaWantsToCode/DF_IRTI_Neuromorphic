# STAGE 4: Real-World Dataset Validation Report

## 1. Executive Summary

This report documents the validation of genuine neuromorphic recorded datasets integrated into the NeuroForensics digital forensic investigation and incident reconstruction pipeline. Under Stage 4 requirements, synthetic input streams were segregated from genuine recordings. All real dataset files were subjected to cryptographic verification, metadata extraction, coordinate/timestamp validation, and deterministic pipeline ingestion.

---

## 2. Integrated Dataset Specifications

### Dataset A: IBM DVS128 Gesture (Primary Vision Source)

| Property | Value |
| :--- | :--- |
| **Dataset Name** | IBM DVS128 Gesture |
| **Local File Location** | `data/dvs128/events_128.aedat` |
| **File Format** | AEDAT 3.1 Binary Event Format (EVT2) |
| **Sensor Hardware** | iniVation DVS128 Dynamic Vision Sensor ($128 \times 128$ array) |
| **Temporal Resolution** | Microsecond ($\mu\text{s}$) hardware timestamps |
| **File Size** | 962,856 bytes |
| **Cryptographic SHA-256** | `6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3` |
| **Official Citation** | Amir, A., Taba, B., Berg, D., et al. (2017). *A Low Power, Fully Event-Based Gesture Recognition System*. CVPR 2017. |
| **License** | IBM Research (Academic and Research Evaluation) |
| **Source URL** | `https://ibm.ent.box.com/s/3hiq58ww1pbbjrinh367ykfdf60xsfm8` |
| **Recorded Events Ingested**| 119,960 microsecond polarity events (Sample recording duration: 148.76 s) |

#### Structural Verification:
- **Timestamp Monotonicity:** Verified. All events strictly maintain relative ordering without non-causal inversion.
- **Coordinate Integrity:** Verified. $X \in [0, 127]$, $Y \in [0, 127]$. Polarity $\in \{0, 1\}$.
- **Preservation Policy:** Raw `.aedat` file is strictly read-only and immutable. No synthetic events were substituted or interleaved into the raw source.

### Dataset B: Spiking Heidelberg Digits (SHD) (Auditory Source)

| Property | Value |
| :--- | :--- |
| **Dataset Name** | Spiking Heidelberg Digits (SHD) |
| **Loader Module** | `src/datasets/shd_loader.py` |
| **File Format** | HDF5 (`/spikes/times`, `/spikes/units`, `/labels`) |
| **Origin Description** | Audio recordings processed via an artificial 700-channel cochlea model |
| **Distinction** | Clearly distinguished from raw biological spikes or optical event cameras |
| **Official Citation** | Cramer, B., Stradmann, Y., Schemmel, J., & Zenke, F. (2020). *The Heidelberg Spiking Data Sets for the Systematic Evaluation of Spiking Neural Networks*. IEEE TNNLS, 33(7), 2744–2757. |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Integration Status** | Native HDF5 ingestion verified with `h5py` 3.16.0; unit tests pass in `tests/test_datasets.py`. |

---

## 3. Unified Dataset Interface Architecture

The abstract base class `DatasetLoader` in `src/datasets/base.py` was extended to guarantee uniform access across all neuromorphic sources:
1. `load_recording(path, sample_index, split)`: Loads the target recording preserving all raw attributes.
2. `get_events(path, sample_index)`: Returns normalized `NeuromorphicEvent` stream ($t, x, y, p, \text{channel}$).
3. `get_labels(path, sample_index)`: Returns integer label and human-readable string.
4. `get_metadata(path, split)`: Returns formal `DatasetMetadata` record.
5. `get_source_provenance(path)`: Returns citation, license, author, and file hashes.
6. `validate_integrity(path, expected_sha256)`: Computes chunked SHA-256 and verifies byte-level authenticity.

---

## 4. Verification & Integrity Test Results

Automated tests in `tests/test_stage4_validation.py` and `tests/test_datasets.py` verify:
- `test_stage4_dvs128_genuine_provenance_and_integrity`: **PASSED**. SHA-256 verified against `6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3`.
- `test_shd_h5py_parser_valid`: **PASSED**. Validates channel routing ($[0, 699]$) and multi-language digit labels.
- `test_synthetic_dataset_loader`: **PASSED**. Confirmed that synthetic fixtures are explicitly labeled with `is_synthetic: true` to prevent data conflation.

