# Forensic Audit: Neuron-Level Visualization, Topology, and Data Flow

**Date:** 2026-10-17  
**Auditor:** NeuroForensics Core Engineering  
**Application:** NeuroForensics Interactive Dashboard (`web/`)  

---

## 1. Executive Summary & Root Cause Analysis

A forensic audit of the dashboard and visualization code was conducted across the data pipeline:
1. Dataset ingestion (`src/datasets/`)
2. Backend execution (`src/neuromorphic/simulator.py`, `src/backends/`)
3. State observation & snapshotting (`src/core/schemas.py`, `src/acquisition/collector.py`)
4. Spike event collection & persistence (`SystemStateSnapshot`, `SpikeEvent`, `.nfd.gz`)
5. Attack reconstruction (`src/reconstruction/`)
6. API and frontend rendering (`web/api/server.py`, `web/js/app.js`, `web/index.html`)

### Why was the microscopic graph showing static dots?
In `web/js/app.js` (`drawNeuralNetGraph`, lines 770–802):
```javascript
for (let c = 0; c < coresCount; c++) {
  // ...
  for (let n = 0; n < 8; n++) {
    const ny = 60 + n * 20;
    ctx.beginPath();
    ctx.arc(cx, ny, 4.5, 0, 2 * Math.PI);
    const isTargetCore = (c === data.reconstruction?.root_cause_core);
    ctx.fillStyle = isTargetCore ? '#f43f5e' : '#38bdf8';
    ctx.fill();
  }
}
```
**Exact findings:**
1. **Hardcoded Mock Grid:** `drawNeuralNetGraph` ignored all actual neuron IDs, all 32 neurons per core, all synaptic weight matrices, and all recorded spike events. It rendered 8 hardcoded static circles per core (total 32 dots across 4 columns) at fixed y-coordinates.
2. **Missing Synaptic Connections:** Zero synaptic edges were rendered between neurons inside a core or between cores.
3. **No Timeline or Event Dynamic:** Spikes were never routed to the canvas; the dots remained completely stationary regardless of simulation step or timeline playback.
4. **Data Starvation in Web Payload:** Although `ForensicCollector` captures all step-by-step membrane potentials and spike communication events (`SpikeEvent` and `SystemStateSnapshot`), the web payload serializer in `PipelineRunner` (`dashboard_state` in `runner.py`) exported high-level metrics and D3 core nodes, but did not export the detailed neuron topology and step-by-step spike event stream required for microscopic replay.

---

## 2. Classification of Visible Graphs & Components

| Component / Graph | Current Source | Status & Defect |
| :--- | :--- | :--- |
| **Microscopic SNN Graph (`#neuralNetCanvas`)** | Hardcoded loop in `app.js:770` | **Fabricated / Decorative Mockup.** Renders 8 static blue dots per core. Zero real connectivity, zero dynamics, zero interaction. |
| **Core Topology Graph (`#topologyCanvas`)** | Static layout in `app.js:710` | **Static 4-node layout.** Uses genuine 4-core ring topology, but lacked interactive drill-down to constituent neuron populations and bidirectional core/neuron synchronization. |
| **Evidence Sufficiency Chart (`#curveCanvas`)** | `data.sufficiency` | **Genuine when loaded**, but empty on initial load. Needs explicit actionable button to trigger ablation study. |
| **Timeline List (`#timelineList`)** | `data.timeline` | **Genuine from reconstruction.** Displays chronological anomaly steps when an experiment completes. |
| **Containment & CTI (`#irPlanContainer`)** | `data.ir_plan`, `data.indicators` | **Genuine from STIX / DFIR mapper.** Accurately displays mapped MITRE technique and proposed containment actions. |
| **DVS128 Dataset Timestamps** | `dvs128_loader.py` | **Timestamp Unit Offset.** First timestamp starts at ~194.08s (microsecond clock offset of hardware camera), whereas duration calculation is relative (span = 148.76s). The relative time offset was not separated from the raw sensor epoch. |

---

## 3. Investigation of Timestamp Handling (DVS128 Gesture)

### Problem Description
The user observed that DVS128 event preview reported a duration of 0.6524s, while the first displayed timestamp was ~194.08s.

### Root Cause
1. **Raw Sensor Hardware Epoch:** In AEDAT 2.0 files recorded with jAER / iniVation sensors, `ts_raw` is a 32-bit unsigned integer representing microseconds from camera power-on or acquisition session start. In `data/dvs128/events_128.aedat`, the recording started at raw microsecond count `194,087,614` (~194.087 seconds).
2. **Normalized vs Relative Timestamps:**
   - Canonical `timestamp`: `float(ts_raw) / 1,000,000.0` (194.087s).
   - Sample duration: `events[-1].timestamp - events[0].timestamp` (relative time span).
   - When a slice of 1000 events was taken, `events[-1].timestamp - events[0].timestamp` spanned ~0.652s.
3. **Remediation Plan:**
   - Expose both canonical timestamps: `timestamp_raw_us` (sensor hardware microseconds), `timestamp_sec` (absolute recording seconds), and `relative_time_ms` (milliseconds offset from sample start: `(t - t_0) * 1000`).
   - Clearly document and display relative event offset and sensor timestamp separately in the table and inspector.

---

## 4. Architecture Plan for Microscopic SNN Graph

### A. Data Contract & Payload
Enhance `/api/simulation/topology` and experiment execution payloads to include:
- `network_topology`:
  - `num_cores`: 4
  - `neurons_per_core`: 32 (total 128 neurons)
  - `intra_core_synapses`: list of `{src_core, src_neuron, dst_core, dst_neuron, weight}` from `NeuromorphicTopology.intra_weights`
  - `inter_core_synapses`: list of active synaptic connections from `NeuromorphicTopology.inter_weights`
- `spike_stream`: Chronological list of recorded spike communication events `{step, timestamp_ms, source_core, source_neuron, target_core, target_neuron, voltage_mv}`
- `membrane_potentials`: Recorded step-by-step or final potential vectors per core
- `anomalous_neurons`: Implicated neurons identified by timeline reconstruction

### B. Interactive Controls & Capabilities
- **Core View / Microscopic View Synchronizer:** Clicking Core in Topology opens Microscopic focus; clicking a neuron highlights parent core.
- **Microscopic Canvas Features:**
  - Play, Pause, Single-Step, Scrub Timeline slider, Speed multiplier (0.5x, 1x, 2x, 5x).
  - Zoom & Pan with mouse drag and wheel.
  - Interactive selection: Click any neuron to open **Neuron Inspector Panel** showing Neuron ID, Core, Membrane Potential ($V_m$), Firing Spike Count, and In/Out Synaptic Edges.
  - Dynamic edge transmission highlights: When a spike travels from neuron $A$ to neuron $B$ at step $T$, animate pulse across the genuine synaptic edge.
  - Distinct visual states: Resting ($V_m < 0.5$), Depolarized ($0.5 \le V_m < 1.0$), Firing Pulse (Glow at step $T$), Refractory, and Anomaly-Implicated.
