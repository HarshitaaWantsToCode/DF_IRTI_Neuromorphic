# Stage 4.1 — Evidence Container (.nfd.gz) Provenance and Cryptographic Audit

## 1. Executive Summary

This report presents an independent cryptographic and structural audit of all nine `.nfd.gz` evidence containers generated during Stage 4 experimentation:
- Location: `results/stage4/real_data/sealed/`
- Target Containers:
  - `spike_storm_seed42.nfd.gz`, `spike_storm_seed101.nfd.gz`, `spike_storm_seed2026.nfd.gz`
  - `synaptic_poisoning_seed42.nfd.gz`, `synaptic_poisoning_seed101.nfd.gz`, `synaptic_poisoning_seed2026.nfd.gz`
  - `timing_jitter_seed42.nfd.gz`, `timing_jitter_seed101.nfd.gz`, `timing_jitter_seed2026.nfd.gz`

The independent audit was performed via a standalone verification script (`scripts/verify_nfd_containers.py`).

---

## 2. Container Inventory and Structural Verification

Each `.nfd.gz` container is a gzip-compressed JSON payload adhering to the `EvidencePackage` schema (`src/core/schemas.py`).

### Granular Inspection Findings Across All 9 Containers:
1. **Snapshot Count:** Exactly **50 state snapshots** per container ($100\%$ uniform across all 9 runs). Total: $9 \times 50 = 450$ snapshots.
2. **Block Hash Count:** Exactly **50 SHA-256 block hashes** per container ($100\%$ matching snapshot counts).
3. **Deterministic Serialization & Hashing:**
   Using JSON canonical serialization (`json.dumps(snapshot, sort_keys=True)`), every one of the 450 snapshots recomputes to the exact stored block hash (`hashes_match == True`).
4. **Merkle Tree Construction:**
   Pair-wise recursive SHA-256 hashing over the 50 block hashes was executed independently. Every recomputed root exactly matches `header.root_merkle_hash`.

### Detailed Container Provenance Table

| Container Filename | Size (Gzip Bytes) | Snapshots | Hash Check | Merkle Root Check | Computed Merkle Root |
| :--- | :---:| :---:| :---:| :---:| :--- |
| `spike_storm_seed42.nfd.gz` | 534,730 | 50 | PASSED | PASSED | `b80e2e59987dcacdb6ee8a1a27297e9ed616c4d3d34703cac4d37aa1a4b9fb26` |
| `spike_storm_seed101.nfd.gz` | 529,160 | 50 | PASSED | PASSED | `4f75b4ed98524f1be1e1ed7a20e0ef7e508ec6a362466e8c9259be9dcb5052da` |
| `spike_storm_seed2026.nfd.gz`| 525,165 | 50 | PASSED | PASSED | `39b36181ec9ec1ba7317e6460aba15bd0ac06886ea49e88919a19c0803774020` |
| `synaptic_poisoning_seed42.nfd.gz` | 557,143 | 50 | PASSED | PASSED | `c1dfc982ff4334bd4938a37aee9f34d74ab00498d8c1878129b6431c15061b3b` |
| `synaptic_poisoning_seed101.nfd.gz` | 555,635 | 50 | PASSED | PASSED | `6969582bbccfe180d80a4cb07219c5be844c4b0664c7fabdcc3b87f95d1e51cb` |
| `synaptic_poisoning_seed2026.nfd.gz`| 543,354 | 50 | PASSED | PASSED | `a560b75029a83f8b9413bf33f2966406bfcbd48a16f43be9863f96c2314fdbae` |
| `timing_jitter_seed42.nfd.gz` | 492,331 | 50 | PASSED | PASSED | `bbb8cbd0209b0911326b087b9b88e7541cae65ccad0f9bf70d47cc4a30d1e469` |
| `timing_jitter_seed101.nfd.gz` | 488,438 | 50 | PASSED | PASSED | `446814ae7ad77bd560ad2ee1e35519aca19a63583ff058215c7a0cf3e9db8fe2` |
| `timing_jitter_seed2026.nfd.gz`| 482,243 | 50 | PASSED | PASSED | `44a2db97bc10615bae4216b7587100d195546143dec2ee536dbfe91e61026f0a` |

---

## 3. Digital Signature Status: Transparent Disclosure

All nine containers currently contain header signatures formatted as:
`ECDSA-PLACEHOLDER-<root_prefix>` (e.g., `ECDSA-PLACEHOLDER-b80e2e59987dcacd`).

### Honest Reporting Statement:
As documented in `src/acquisition/collector.py` (lines 55–67), **no physical hardware security module (HSM) or genuine ECDSA private key was utilized**. The signature field serves as an architectural placeholder and proof-of-concept interface for future public-key infrastructure (PKI) integration. 

**Under no circumstances should the research paper claim digital signature authentication or non-repudiation for these experiments.** The cryptographic guarantees are strictly limited to SHA-256 block-level hashing and Merkle tree tamper detection.

---

## 4. Provenance Binding: Binding External Dataset Manifest to Evidence

In the current containers, `container["topology"]` and `container["configuration"]` were initialized as `None` by default in the test runner, while metadata in `header["metadata"]` captured only `{"attack": ..., "seed": ...}`.

### Formal Binding Architecture:
To ensure cryptographic provenance binding between external dataset files and the evidence package, the container header must store:
1. `source_dataset_name`: Human-readable identifier (`"IBM DVS128 Gesture"`).
2. `source_dataset_sha256`: Checksum of the raw input file (`6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3`).
3. `ingestion_slice`: `{"start_event": 0, "end_event": 10000, "duration_seconds": 7.622192}`.
4. `pipeline_commit`: Git commit SHA of the experimental codebase.

Binding these four fields into `header["metadata"]` before computing the container signature ensures that an investigator can independently verify which exact physical dataset file and code version generated the evidence.

