# Stage 4.1 — DVS128 Dataset Provenance and Parsing Discrepancy Audit

## 1. Executive Summary

An independent inspection identified an apparent conflict in the reporting of the IBM DVS128 Gesture dataset file:
- `dataset_manifest.json` reports: **10,000 events**, duration **7.622 seconds**.
- `STAGE4_DATASET_VALIDATION_REPORT.md` reports: **119,960 events**, duration **148.76 seconds**.
- Both cite the identical physical file `data/dvs128/events_128.aedat` and identical cryptographic SHA-256 hash `6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3`.

This audit independently verified the raw file, re-ran the parser under varying parameters, and identifies the exact technical cause.

---

## 2. Independent Verification of Dataset File Checksum

- **Target File:** `data/dvs128/events_128.aedat`
- **File Size:** 962,856 bytes
- **SHA-256 Calculation:**
  ```python
  import hashlib
  h = hashlib.sha256(open('data/dvs128/events_128.aedat', 'rb').read()).hexdigest()
  # Result: 6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3
  ```
The raw file is completely authentic, uncorrupted, and matches the recorded checksum across all files.

---

## 3. Independent AEDAT Parser Execution & Event Count Resolution

The AEDAT 3.1 parser in `src/datasets/dvs128_loader.py` was executed independently using two distinct operational paths:

### Path A: Full Recording Ingestion (`max_events=None`)
```python
loader = DVS128GestureLoader()
sample_full = loader.load_sample("data/dvs128/events_128.aedat")
# Results:
# sample_full.num_events = 119,960
# sample_full.duration_seconds = 148.762696 s
```
- Total AEDAT polarity packets parsed: 119,960 events.
- First raw timestamp: $t_0 = 1,173,086\text{ }\mu\text{s}$.
- Final raw timestamp: $t_{\text{end}} = 149,935,782\text{ }\mu\text{s}$.
- Elapsed duration: $\Delta t = (149,935,782 - 1,173,086) / 10^6 = \mathbf{148.762696\text{ s}}$.

### Path B: Bounded SNN Evaluation Window (`max_events=10000`)
```python
loader = DVS128GestureLoader()
sample_bounded = loader.load_sample("data/dvs128/events_128.aedat", max_events=10000)
# Results:
# sample_bounded.num_events = 10,000
# sample_bounded.duration_seconds = 7.622192 s
```
- Parsed packet limit: First 10,000 events of the recording.
- Timestamp of event #0: $t_0 = 1,173,086\text{ }\mu\text{s}$.
- Timestamp of event #9,999: $t_{9999} = 8,795,278\text{ }\mu\text{s}$.
- Elapsed duration: $\Delta t = (8,795,278 - 1,173,086) / 10^6 = \mathbf{7.622192\text{ s}}$.

---

## 4. Root Cause of the Discrepancy

In `scripts/run_stage4_validation.py` (lines 37–40):
```python
dvs_sample = loader_dvs.load_recording(dvs_path, max_events=10000)
```
The experiment runner deliberately capped the ingestion window at `max_events=10000` (representing the first 7.62 seconds of the gesture recording) so that the simulation would execute within reasonable compute limits for 50-step and 100-step test runs.

When `dataset_manifest.json` was generated, it logged `len(dvs_sample.events)` (`10,000`) and `dvs_sample.duration_seconds` (`7.622192`), reflecting the **evaluation window subset**.

Conversely, `STAGE4_DATASET_VALIDATION_REPORT.md` described the **entire physical file capacity** on disk, which contains all **119,960 events** spanning **148.76 seconds**.

---

## 5. Resolution & Clarification

Both figures are technically correct and reproducible, but refer to different scopes:
- **Total Physical File Contents:** **119,960 events** spanning **148.76 seconds** ($100\%$ of `events_128.aedat`).
- **Experimental Evaluation Slice:** The first **10,000 events** spanning **7.62 seconds** ($8.33\%$ of the stream), used for simulation and attack injection.

### Recommended Formal Paper Documentation:
> *"The raw IBM DVS128 Gesture recording (`events_128.aedat`, SHA-256 `6d982a80...`) contains 119,960 microsecond events across 148.76 s. For multi-seed forensic simulation and combinatorial ablation experiments, a standardized continuous slice consisting of the first 10,000 events (7.62 s duration) was ingested to evaluate the attack suite."*

