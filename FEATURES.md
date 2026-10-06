# NeuroForensics Feature Tracker

## Core Platform
- [x] ~~Multi-core SNN simulator~~
  - LIF neuron dynamics with configurable decay, threshold, refractory period, and inter/intra-core routing.
- [x] ~~Attack injection framework~~
  - Synaptic weight poisoning, spike storm / flooding, and timing jitter injection.
- [x] ~~Configurable experiment runner~~
  - YAML-configured pipeline runner with CLI interface.

## Evidence & Schemas
- [x] ~~Spike evidence collection~~
  - Volatile spike stream capture per step with source/target neuron and core IDs.
- [x] ~~Synaptic-state collection~~
  - Per-core synaptic weight matrix snapshotting.
- [x] ~~Neuron-state collection~~
  - Membrane potentials and refractory state snapshots per neuron.
- [x] ~~Topology/routing evidence~~
  - Static inter/intra-core synaptic connectivity maps.
- [x] ~~Formal artifact taxonomy / classes~~
  - Structured artifact types: `SPIKE_EVENTS`, `SPIKE_TIMING`, `NEURON_STATE`, `SYNAPTIC_STATE`, `TOPOLOGY_ROUTING`, `CONFIGURATION`, `INPUT_OUTPUT`.
- [x] ~~Evidence schema versioning & containerization~~
  - Sealed `.nfd` and compressed `.nfd.gz` evidence containers with cryptographic headers.
- [x] ~~Evidence provenance metadata~~
  - Dump ID, step stamps, acquisition timestamps, collector signatures, and block hashes.

## Integrity & Cryptographic Chain of Custody
- [x] ~~SHA-256 snapshot hashing~~
  - Deterministic per-block hashing of state snapshots.
- [x] ~~Merkle root generation~~
  - Tree-structured hierarchical cryptographic Merkle root across all snapshot blocks.
- [x] ~~Merkle verification~~
  - Tamper verification checking stored vs recomputed Merkle roots.
- [x] ~~Tamper test~~
  - Validated test ensuring modified evidence blocks fail Merkle verification.

## Research: Evidence Sufficiency & Ablation
- [x] ~~Ground truth vs Forensic evidence separation~~
  - Attacker ground truth (attack type, target core/neuron, start/duration, true modifications, true propagation) isolated from reconstructed evidence.
- [x] ~~Deterministic reconstruction scoring~~
  - Quantitative scoring evaluating: `attack_identification_score`, `location_score`, `temporal_score`, `mechanism_score`, `impact_score`, and `overall_score`.
- [x] ~~Evidence subset representation & filtering~~
  - Modular masking and extraction of arbitrary artifact class combinations.
- [x] ~~Evidence ablation engine~~
  - Full subset enumeration and systematic removal of artifact classes to measure reconstruction degradation.
- [x] ~~Minimum Sufficient Evidence Set calculation~~
  - Calculates smallest evidence subset(s) achieving target reconstruction thresholds, identifying equivalent minimal sets and volume tradeoffs.
- [x] ~~Evidence sufficiency curves~~
  - Measured reconstruction score vs evidence volume bytes / cardinality.
- [x] ~~Attack × Artifact matrix computation~~
  - Empirically computed artifact necessity table (`Required`, `Helpful`, `Redundant`, `Insufficient`, `Not Applicable`).

## Research Reproducibility & Export
- [x] ~~Reproducible experiment configuration & seed recording~~
  - Captures random seed, simulator parameters, attack configs, and timestamps.
- [x] ~~Machine-readable result export~~
  - Exports ablation results as structured JSON and CSV in `results/ablation/`.
- [x] ~~CLI experiment command~~
  - `python main.py run-ablation` and `python main.py evaluate-sufficiency`.

## Dashboard & Visualizations
- [x] ~~Evidence selection & ablation explorer~~
  - Interactive subset selector and measured reconstruction score visualizer.
- [x] ~~Evidence sufficiency curve chart~~
  - Interactive SVG / Canvas curve showing quality vs evidence footprint.
- [x] ~~Empirical Attack × Artifact matrix~~
  - Data-driven table displaying verified evidence requirements across attack types.
- [x] ~~Cleaned scientific UI claims~~
  - Removed misleading mock/unverified 100% detection claims and clearly demarcated simulated vs hardware-backed features.
