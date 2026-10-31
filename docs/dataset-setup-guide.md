# Neuromorphic Dataset Setup & Reproducibility Guide

## 1. Overview
NeuroForensics supports real-world neuromorphic event streams (vision and auditory) alongside strictly labelled synthetic fixtures.

Supported dataset loaders:
- **Spiking Heidelberg Digits (SHD)**: Auditory neuromorphic speech spikes (700 channels).
- **IBM DVS128 Gesture**: Dynamic Vision Sensor polarity events (128x128 pixels, AER format).
- **Synthetic Poisson Stream**: Labelled in-memory baseline fixture for deterministic regression testing.

---

## 2. Ingestion & Preprocessing

### Spiking Heidelberg Digits (SHD)
- **Source**: Zenke Lab (https://zenkelab.org/resources/spiking-heidelberg-datasets-shd/)
- **Format**: HDF5 (`.h5` / `.hdf5`)
- **Structure**:
  - `/spikes/times`: Spike timestamps in seconds.
  - `/spikes/units`: Channel/unit ID (0 to 699).
  - `/labels`: Integer target class (0 to 19).
- **Setup**:
  Download `shd_train.h5` and `shd_test.h5` and place them in `data/shd/`:
  ```bash
  mkdir -p data/shd
  # Move downloaded files to data/shd/
  ```

### IBM DVS128 Gesture Dataset
- **Source**: IBM Research / Research Gate
- **Format**: AEDAT 3.1 binary (`.aedat`)
- **Structure**:
  - Header: ASCII header ending in `#!END-HEADER\r\n`.
  - Event records: 8 bytes per polarity event (`uint32 data_word`, `int32 timestamp_us`).
  - Bitfields:
    - Bit 0: Polarity (1=ON, 0=OFF)
    - Bits 1–11: Y coordinate (0–127)
    - Bits 12–22: X coordinate (0–127)
    - Bit 23: Event validity flag
  - Normalization: Microseconds are converted to canonical seconds (`timestamp_s = ts_raw / 1,000,000.0`).
- **Setup**:
  Place `.aedat` recordings in `data/dvs128/`:
  ```bash
  mkdir -p data/dvs128
  ```

---

## 3. Data Integrity & Provenance Policy
1. **Source Immutability**: Raw downloaded files are never modified in-place.
2. **Cryptographic Checksums**: Chunked SHA-256 hashes are computed for provenance tracking.
3. **Out-of-Order Events**: Real sensor data may contain timestamp jitter. The loaders preserve events as recorded and log diagnostic warnings rather than silently dropping data.

---

## 4. Lava Framework Compatibility Notice
- **Status**: Blocked on Python 3.14.4.
- **Root Cause**: `lava-nc` requires Python `>=3.8,<3.11`. Upstream GitHub repository `lava-nc/lava` was archived in May 2026.
- **Handling**: A diagnostic adapter `src/backends/lava_adapter.py` reports capabilities and provides informative failure messages when invoked.
