# Real Dataset Ingestion & Neuromorphic Event-to-SNN Data Lineage

**Date:** October 20, 2026  
**Auditor:** Neuromorphic Digital Forensics Research Engineer  
**Loaders Audited:**
1. IBM DVS128 Gesture Loader (`src/datasets/dvs128_loader.py`)
2. Spiking Heidelberg Digits Loader (`src/datasets/shd_loader.py`)
3. Synthetic Poisson Fixture (`src/datasets/synthetic.py`)

---

## 1. DVS128 Gesture Recording Validation

### 1.1 Local File Verification
- **File path:** `data/dvs128/events_128.aedat`
- **File size:** 856 KB (compressed sample)
- **SHA-256 Checksum:** `6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3`
- **Total Valid Events:** 119,960 events
- **Spatial Resolution:** 128 &times; 128 pixels
- **Duration:** 148.76 seconds

### 1.2 Binary Parser & Timestamp Normalization
The AEDAT 3.1 parser reads the ASCII header ending at `#!END-HEADER\r\n` and unpacks 8-byte event records:
- Bit 0: Polarity (0 = OFF event, 1 = ON event)
- Bits 1–11: Y coordinate ($0 \le y \le 127$)
- Bits 12–22: X coordinate ($0 \le x \le 127$)
- Hardware Clock: 32-bit unsigned integer ($\mu\text{s}$)

**Timestamp Alignment:**
- Initial hardware timestamp: $t_0 = 194.087614\text{ s}$ ($194,087,614\ \mu\text{s}$).
- Final event timestamp: $t_{\text{final}} = 342.850310\text{ s}$ ($342,850,310\ \mu\text{s}$).
- Zero-aligned relative time: $\Delta t = (t - t_0) / 1000.0\text{ ms}$, ensuring synchronous time-step binning without drift.

---

## 2. Event-to-SNN Spatial & Polarity Mapping

When stimulating the multi-core SNN with genuine event streams:
1. **Spatial Aggregation:** Channel ID is computed as:
   \[
   \text{channel\_id} = y \times 128 + x
   \]
2. **Core Injection:** Sensory events are mapped into Core 0 neuron indices:
   \[
   \text{neuron\_idx} = \text{channel\_id} \pmod{32}
   \]
3. **Temporal Binning:** Events are discretized into simulation intervals ($\Delta t = 1.0\text{ ms}$):
   \[
   \text{step\_idx} = \lfloor \Delta t_{\text{ms}} \rfloor \pmod{100}
   \]
4. **Current Influx:** Arrival of input spikes injects EPSP currents into the target LIF neurons, driving somatic depolarization and triggering downstream cascades across the inter-core ring bus.

---

## 3. Provenance & Cryptographic Chain of Custody

The immutable dataset sample is bound to every execution:
- The raw source file is preserved intact on disk; all simulation transformations operate on derived copies.
- Metadata recorded into `.nfd.gz` includes:
  - `source_file`
  - `dataset_name`
  - `events_ingested`
  - `duration_seconds`
  - `sha256_checksum`
- The Merkle root of the resulting forensic container captures the exact input stream configuration alongside recorded spike events.

---

## 4. Spiking Heidelberg Digits (SHD) Status

- Loader implementation exists at `src/datasets/shd_loader.py`.
- **Status:** Fixture-tested (`tests/test_datasets.py`).
- **Limitation:** The full SHD HDF5 file (~700 MB) is not present locally, and `h5py` is not installed in the primary Python 3.14 environment. The system gracefully reports SHD as unavailable or unit-tested on fixtures without fabricating synthetic digits.
