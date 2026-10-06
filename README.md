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
