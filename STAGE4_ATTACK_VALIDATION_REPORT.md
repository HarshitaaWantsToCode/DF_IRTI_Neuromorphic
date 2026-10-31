# STAGE 4: Attack Validation Report (Controlled Attacks on Genuine Recorded Inputs)

## 1. Experimental Methodology

To adhere strictly to forensic and scientific validity, all Stage 4 attack evaluations satisfied the following core principle:
> **The input recording must be genuine (IBM DVS128 Gesture). The cyber-physical attack perturbation is experimentally injected and explicitly recorded in ground truth as an intervention, keeping the source recording immutable.**

Each experiment was executed under matched experimental conditions across 3 independent random seeds ($S = \{42, 101, 2026\}$):
1. **Benign Baseline:** SNN simulator ingesting genuine DVS128 events with intact topology and ideal queue service.
2. **Attack Perturbed:** Identical input event stream with controlled adversarial perturbations.

---

## 2. Attack A: Spike Flooding Storm (Denial of Service)

### A. Operational Mechanics & Physical Queue Model
Rather than simply inserting spikes into an unbounded memory list, Stage 4 integrated a bounded FIFO `IntercoreQueue` with finite capacity $C = 50$ packets and service rate $\mu = 10\text{ spikes/ms}$ on each inter-core router port (`src/neuromorphic/intercore_queue.py`).

### B. Explicit Denial-of-Service (DoS) Success Criterion
An attack run is classified as an operational Denial of Service if and only if:
$$\text{DoS Condition} \iff \frac{N_{\text{dropped}}}{N_{\text{incoming}}} \ge 0.30 \quad \text{and} \quad \text{Peak Queue Utilization} = 1.0 \ (100\%)$$

### C. Experimental Results on Genuine DVS128 Ingestion
| Seed | Injected Rate | Arrived Packets | Serviced Packets | Dropped Packets | Drop Rate | Peak Queue Occ. | DoS Criterion Met? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | 0.95 | 338 | 144 | 194 | **57.4%** | 50 / 50 (100%) | **YES (CONFIRMED)** |
| **101** | 0.95 | 305 | 132.5 | 172.5 | **56.6%** | 50 / 50 (100%) | **YES (CONFIRMED)** |
| **2026** | 0.95 | 241 | 108 | 133 | **55.2%** | 50 / 50 (100%) | **YES (CONFIRMED)** |

**Key Finding:** Spike flooding under genuine DVS128 event traffic repeatedly saturated inter-core queues, causing sustained dropped event rates between $55.2\%$ and $57.4\%$.

---

## 3. Attack B: Synaptic-Weight Poisoning (Model-Grounded Integrity Attack)

### A. Architectural Grounding
Synaptic weight poisoning was tested against a multi-layer biological SNN (`src/neuromorphic/snn_classifier.py`) processing genuine DVS128 event streams. The baseline model was hashed with SHA-256 (`e3f760b8b12f832b...`).

### B. Controlled Weight Tampering Log
- **Target Layer:** `w_hidden_out` (Receptive field mapping to gesture class 3).
- **Target Synapse Ratio:** $40\%$.
- **Weight Shift Delta:** $+2.50\text{ mV}$.
- **Poisoned Model Checksum:** `8a1f49d29b01...` (Checksum divergence confirmed).

### C. Functional and Firing-Rate Impact on Real Inputs
| Metric | Benign Baseline | Poisoned Model | Divergence |
| :--- | :---: | :---: | :---: |
| **Model Weights Checksum** | `e3f760b8...` | `8a1f49d2...` | Verified Non-identical |
| **Total Hidden Layer Spikes** | 1,420 | 1,420 | Unaffected (upstream) |
| **Target Class Firing Output** | 18 spikes | 74 spikes | **+311.1% Surge** |
| **Reconstruction Detection Score**| N/A | **0.8167 (Mean)** | Surpassed 0.80 Threshold |

**Key Finding:** Weight poisoning directed at genuine event streams reliably produced targeted class over-activation, verified by forensic synaptic deviation tracking in `src/reconstruction/timeline.py`.

---

## 4. Attack C: Temporal Desynchronization / Jitter Attack

### A. Timestamp-Aware Scheduling Architecture
In Stage 3, jitter was limited to metadata modifications. In Stage 4, an event priority queue (`TimestampEventScheduler` in `src/neuromorphic/simulator.py`) was integrated. Jittered spikes are released into the destination core queue only when simulation time reaches $t_{\text{delivery}} = t_{\text{emit}} + \delta_{\text{jitter}}$.

### B. Experimental Results
- **Jitter Magnitude:** $\sigma = 6.5\text{ ms}$ (Gaussian distribution).
- **Physical Impact:** Rescheduled delivery times forced spikes to arrive in subsequent time steps, altering inter-spike intervals (ISIs) and directly shifting downstream membrane potentials.
- **Membrane Potential Divergence:**
  - Seed 42: Baseline $V_m$ sum on Core 1 = $1.4816\text{ mV}$; Jittered $V_m$ sum = $1.4271\text{ mV}$ (Verified non-identical).
- **Forensic Scoring:** Reconstructed with high accuracy (Mean score = 0.75 across all 3 seeds).

