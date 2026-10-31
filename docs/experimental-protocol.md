# Reproducible Experimental Protocol: Baselines, Benign Disturbances & Malicious Attacks

**Date:** October 20, 2026  
**Research Focus:** Observable evidence necessary to distinguish malicious event-stream manipulation from benign operational disturbances in multi-core Neuromorphic SNNs.

---

## 1. Experimental Protocol & Conditions

The evaluation framework defines three distinct operating conditions evaluated across identical network topologies (4 cores, 128 neurons, 2,560 synapses, seed = 42, $dt = 1.0\text{ ms}$):

### Condition A: Benign Baseline (Reference)
- **Definition:** Unperturbed neuromorphic simulation driven either by background thermal noise or real sensor input.
- **Injected Perturbations:** 0
- **Expected Forensic Finding:**
  - Anomaly events detected: 0
  - Detected attack type: `"benign"`
  - Root cause core: `-1` (None)
  - Reconstruction score: Normal execution, zero false alarms.

### Condition B: Benign Event-Stream Disturbances (Non-Malicious Noise)
- **Definition:** Deterministic stochastic disturbances representing sensor noise, network jitter, or dropped packets.
  1. **Phase Jitter:** Zero-mean Gaussian timing variations ($\mu=0, \sigma=2.0\text{ ms}$).
  2. **Event Dropout:** Random loss of up to 15% of sensory events.
  3. **Background Noise Injection:** Low-rate uncorrelated Poisson background spikes ($< 0.05$ rate).
- **Distinguishing Factor:** Non-concentrated, statistically symmetric, zero directional weight mutation, absence of sustained cross-core propagation cascades.

### Condition C: Controlled Malicious Manipulations
- **Vectors Implemented & Evaluated:**
  1. **Synaptic Weight Poisoning (Integrity / Neural Trojan):**
     - Target: Core 2
     - Target Synapse Ratio: 35%
     - Weight Shift ($\Delta W$): +2.8 mV
     - Window: Steps 30–70
     - Observable Signature: Persistent step-function change in non-volatile synaptic matrix registers (`SYNAPTIC_STATE`).
  2. **Spike Flooding Storm (Denial-of-Service / Exhaustion):**
     - Target: Core 1
     - Injection Rate: 0.95 spikes/step across neurons
     - Window: Steps 20–50
     - Observable Signature: Massive high-frequency spike surge ($> 900$ spikes) on inter-core routing buses (`SPIKE_EVENTS`).
  3. **Temporal Phase Desynchronization (Timing Manipulation):**
     - Target: Core 1
     - Jitter Magnitude: 4.5 ms
     - Window: Steps 25–60
     - Observable Signature: Uncorrelated spike arrival times corrupting STDP plasticity (`SPIKE_TIMING` + `SPIKE_EVENTS`).

---

## 2. Ground-Truth Isolation & Chain of Custody

To guarantee scientific rigor:
1. **Separation of Concerns:** The simulation and attack injector generate an `AttackGroundTruth` metadata record stored in an isolated data structure.
2. **Pure-Evidence Reconstruction:** The `TimelineGenerator` and `EventCorrelator` receive only the sealed `EvidencePackage` (snapshots, Merkle root, spike stream). They cannot inspect ground-truth labels, scenario names, or injector configurations.
3. **Independent Evaluation:** The `ReconstructionScorer` compares the independently reconstructed graph against ground truth only after reconstruction has completed.
