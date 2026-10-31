# Stage 4.1 — Attack Reconstruction Failure Analysis (Spike Flooding on DVS128)

## 1. Executive Summary

An investigation was conducted into why spike flooding under genuine DVS128 gesture input is **consistently detected as `spike_storm` (100% type accuracy), yet localized to Core 0 rather than the true ground-truth Core 1** across all three seeds ($42, 101, 2026$).

This failure analysis isolates the operational dynamics of neuromorphic input streaming, inter-core queues, and the root-cause heuristic algorithm.

---

## 2. Experimental Discrepancy Overview

| Experiment Run | Ground Truth Target Core | Ground Truth Start Step | Reconstructed Root Cause Core | Reconstructed Initial Step |
| :--- | :---: | :---: | :---: | :---: |
| `spike_storm_seed42` | **Core 1** | **Step 15** | **Core 0** | **Step 1** |
| `spike_storm_seed101`| **Core 1** | **Step 15** | **Core 0** | **Step 1** |
| `spike_storm_seed2026`| **Core 1** | **Step 15** | **Core 0** | **Step 1** |

---

## 3. Deep-Dive Forensic Inspection of Sealed Evidence

Inspection of `results/stage4/real_data/sealed/spike_storm_seed42.nfd.gz` revealed the exact chronological sequence of timeline events:

```
step=1,  type=SPIKE_BURST, core=0, score=1.000, desc=Anomalous spike surge on Core 0 (33 spikes vs avg 6.0)
step=15, type=SPIKE_BURST, core=1, score=1.000, desc=Anomalous spike surge on Core 1 (34 spikes vs avg 0.6)
step=17, type=SPIKE_BURST, core=2, score=1.000, desc=Anomalous spike surge on Core 2 (28 spikes vs avg 0.0)
step=19, type=SPIKE_BURST, core=2, score=1.000, desc=Anomalous spike surge on Core 2 (51 spikes vs avg 4.8)
step=38, type=SPIKE_BURST, core=0, score=1.000, desc=Anomalous spike surge on Core 0 (50 spikes vs avg 28.7)
step=41, type=MEMBRANE_ANOMALY, core=0, score=0.438, desc=Elevated membrane potential on Core 0
```

### Analysis of Physical Spike Firing per Step:
Examining `active_spikes_count` across cores:
- **Step 0:** Core 0 fires 6 spikes (initial sensory integration).
- **Step 1:** Core 0 fires **33 spikes** as optical gesture activity arrives.
- **Steps 2–14:** Core 0 averages $32.4\text{ spikes/step}$, while Cores 1, 2, and 3 are quiescent ($0-4\text{ spikes/step}$).
- **Step 15 (Adversarial Attack Window Begins):** Core 1 is attacked with an injection rate of 0.95, firing **34 spikes**.
- **Step 17:** Spikes cascade from Core 1 into Core 2 via the ring crossbar, saturating Core 2's bounded queue (50 packets) and producing dropped packets ($57.4\%$ drop rate).

---

## 4. Root-Cause Algorithm Breakdown

In `src/reconstruction/correlator.py` (lines 28–59):
```python
# Sort events chronologically
sorted_events = sorted(events, key=lambda e: (e.step, e.timestamp_ms))
...
burst_events = [e for e in sorted_events if e.event_type == "SPIKE_BURST"]
...
if burst_events:
    detected_attack_type = "spike_storm"
    root_event = burst_events[0]   # <-- Earliest chronological surge
...
root_cause_core = root_event.affected_core
initial_step = root_event.step
```

### The Mechanism of Failure:
The root-cause analyzer applies a purely chronological **first-observed heuristic** (`root_event = burst_events[0]`).

In a synthetic benchmark where the system is idle before the attack, the first surge is guaranteed to be the attack injection. However, in **genuine event-stream computing**, the arrival of optical gesture activity on sensory ingress Core 0 at Step 1 creates a natural sensory spike surge (33 spikes vs 6 spikes at baseline initialization).

Because Step 1 precedes the adversarial intervention at Step 15, the correlator selects Core 0 at Step 1 as "Patient Zero."

---

## 5. Scientific Implications for Neuromorphic Forensics

This failure is a critical research finding:
1. **Conflating Operational Stimulus with Malicious Compromise:**
   The algorithm confuses normal high-bandwidth sensory stimulus with an adversarial denial-of-service flood because it lacks an awareness of external sensor ingress topology.
2. **The Ingress Boundary Principle:**
   Sensory ingress cores (e.g., Core 0 connected directly to DVS cameras) routinely experience natural burstiness. A neuromorphic root-cause analyzer cannot treat ingress bursts identically to internal routing crossbar bursts.
3. **Queue Utilization as a Disambiguating Signal:**
   At Step 1, Core 0 experienced a spike surge, but Core 1's queues remained empty. At Step 15, Core 1's surge caused immediate buffer saturation ($100\%$ queue occupancy) and packet dropping ($57\%$ drop rate) on Core 2. Incorporating queue drop telemetry (`IntercoreQueue.get_metrics()`) into the timeline correlator is required to differentiate legitimate high sensory throughput from true Denial-of-Service queue exhaustion.

### Honest Paper Reporting Commitment:
The research paper will explicitly report this failure:
> *"When processing genuine high-activity event-camera streams, naive chronological anomaly ordering misidentifies sensory ingress burstiness (Core 0, Step 1) as the initial compromise location rather than the true internal injection point (Core 1, Step 15), resulting in a localization score of 0.0 despite 100% attack-type identification."*

