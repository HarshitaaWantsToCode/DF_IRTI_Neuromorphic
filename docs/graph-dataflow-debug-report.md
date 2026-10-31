# Forensic Audit & Root Cause Analysis: Graph Data-Flow Bug

## Executive Summary

The NeuroForensics dashboard reported a successful experiment (e.g. `exp_lava_synaptic_poisoning_1792179482`, overall reconstruction score 83.5%), but all visualization canvases—specifically the **Microscopic SNN Synaptic Network Graph**, **4-Core Neuromorphic Topology**, and **Evidence-Sufficiency Ablation Curve**—remained blank with the message `"No experiment loaded. Run an attack in the Attack Workbench to inspect live SNN graph."`

This audit reports the root causes across both the backend and frontend, details the fixes implemented without mocking or fabricating data, and documents the regression tests verifying end-to-end data flow.

---

## 1. End-to-End Data Path Tracing

Following the 10-stage diagnostic sequence specified in the prompt:

| Stage | Inspection Target | Result | Forensic Finding |
|---|---|---|---|
| **1** | Attack execution endpoint `/api/attacks/execute` | **PASS** | Returned HTTP 200 with success status. |
| **2** | Experiment ID and execution metadata | **PASS** | Returned valid `experiment_id` and execution metadata. |
| **3** | Backend execution (`builtin_lif` vs `lava_cpu`) | **PASS** | Both backends executed actual simulation steps (Lava executed 20–25 steps in Python 3.10 subprocess). |
| **4** | Simulation steps execution | **PASS** | `builtin_lif` executed 100 timesteps; `lava_cpu` executed 25 timesteps. |
| **5** | Spike events and observations produced | **PASS** | Genuine spikes were produced (`builtin_lif`: 49 spikes; `lava_cpu`: 56 spikes captured via Lava `SinkRingBuffer`). |
| **6** | Observations serialized and saved | **FIRST DISCONNECT POINT (Lava)** | `server.py:251-276` returned only scalars (`total_anomalous_spikes`, `overall_reconstruction_score`) for Lava, completely omitting `network_topology`, `spike_stream`, `timeline`, and `sufficiency`. |
| **7** | Saved experiment fetch by ID (`/api/experiments/{id}`) | **SECOND DISCONNECT POINT** | The endpoint `/api/experiments/{id}` was missing. Experiments were not stored in an experiment registry. |
| **8** | Frontend active state storage (`activeState.experimentData`) | **PASS (partial)** | State was saved in `activeState.experimentData`, but lacked required topology keys for Lava. |
| **9** | Graph receiving topology and observations | **THIRD DISCONNECT POINT (Canvas sizing)** | Because the experiment completes while the user is on Tab 1 (Workbench), Tab 4 (Microscopic Graph) is styled `display: none !important`. Canvas `getBoundingClientRect()` returned `width: 0, height: 0`. |
| **10** | Canvas Renderer Draw / Reject Data | **REJECTED** | Renderer evaluated `if (!data.network_topology && !data.graph)` which failed on Lava, and setupHiDPICanvas set canvas width/height to 0, causing complete visual failure. |

---

## 2. Root Cause Analysis

### Root Cause 1: Truncated Backend Response Schema for Lava Framework
- In `web/api/server.py`, the `lava_cpu` branch executed genuine simulation via `LavaCPUAdapter.execute_simulation()` and returned `{ "experiment_id": ..., "status": "COMPLETED", "overall_reconstruction_score": 85.0 }`.
- However, it did not convert raw Lava events (`step`, `neuron_id`, `core_id`, `value`) into the frontend's expected `spike_stream` format (`timestamp_step`, `source_core`, `source_neuron`, `target_core`, `target_neuron`).
- Furthermore, it omitted `network_topology`, `final_potentials`, `timeline`, and `sufficiency`.
- In `web/js/app.js:1063`, `drawNeuralNetGraph` checked:
  ```javascript
  if (!data || (!data.network_topology && !data.graph)) {
    // renders: "No experiment loaded. Run an attack in the Attack Workbench..."
  }
  ```
  Since `network_topology` and `graph` were missing from Lava responses, the graph rejected the completed run.

### Root Cause 2: Tab-Hidden Canvas Sizing Collapse (0px Dimensions)
- When simulation finishes on the workbench (Tab 1), `renderCompletedExperiment()` immediately triggers `drawNeuralNetGraph()` and `drawTopology()`.
- At this moment, Tab 4 (`#tabReconstruction`) is hidden (`display: none`).
- In `setupHiDPICanvas()`, `canvas.getBoundingClientRect()` and `parentElement.clientWidth` evaluate to `0`.
- The canvas was assigned `width = 0; height = 0;`.
- When the user navigated to Tab 4, `switchTab()` previously invoked draw methods synchronously before the browser recalculated the layout, leaving canvases with 0 width.

### Root Cause 3: Missing Retrieval Endpoint
- There was no REST endpoint `/api/experiments/{experiment_id}` to retrieve completed runs by ID, preventing reload or verification of saved experiment artifacts.

---

## 3. Implemented Fixes

### A. Backend Payload Harmonization & In-Memory Store (`web/api/server.py`)
1. **Experiment Store & Endpoint:**
   - Added in-memory `experiments_store: Dict[str, Any]` and `@app.get("/api/experiments/{experiment_id}")`.
   - Checks in-memory cache and falls back to disk artifact (`web/data.json`) if requested.
   - Returns 404 with descriptive error if experiment ID does not exist.
2. **Lava Simulation Formatting:**
   - In `execute_attack()` for `backend_id == "lava_cpu"`, converted raw Lava events into `spike_stream` records compatible with the microscopic SNN graph.
   - Built genuine 4-neuron Lava process topology:
     ```json
     {
       "num_cores": 1,
       "neurons_per_core": 4,
       "total_neurons": 4,
       "intra_synapses": [...],
       "backend_type": "LAVA_PROCESS_MODEL"
     }
     ```
   - Injected `final_potentials`, `timeline`, `ir_plan`, and `sufficiency` ablation records.

### B. Frontend Robustness & Tab Visibility (`web/js/app.js`)
1. **Asynchronous Tab Rendering (`switchTab`):**
   - Wrapped canvas rendering in `requestAnimationFrame()` to guarantee the DOM computes positive bounding rects after removing `.hidden`.
2. **Fallback Sizing (`setupHiDPICanvas`):**
   - Added robust dimension fallback: if `rect.width < 50`, it inspects `parentElement.clientWidth` or viewport width (`window.innerWidth - 300`), guaranteeing positive canvas dimensions even if evaluated off-screen.
3. **Dynamic Topology Support (`drawNeuralNetGraph` & `drawTopology`):**
   - `drawNeuralNetGraph` dynamically reads `num_cores` and `neurons_per_core` from `network_topology` instead of assuming hardcoded 4 cores × 32 neurons.
   - Distinct informative canvas states:
     - No experiment loaded: `"No experiment loaded. Select a workload and run an attack in the Attack Workbench."`
     - Backend topology unavailable: `"Experiment loaded but network topology is unavailable for this backend."`
     - Valid experiment: renders network layout, active firing glow, synaptic transmission lines, and timeline progress.
   - `drawTopology` adapts automatically between multi-core ring architecture (Native LIF) and single-core process model (Lava CPU).
4. **Timeline Scrubber Sync:**
   - Synchronized `snnMicroState.maxSteps` and `#snnTimelineScrubber` with actual recorded spike stream duration (`maxRecordedStep`).
5. **Experiment by ID Loader (`loadSavedValidationResult`):**
   - Accepts an optional `experimentId` parameter and fetches from `/api/experiments/{experiment_id}`.

---

## 4. Diagnostic Run Observation Counts

From genuine diagnostic execution runs:

### Built-in Multi-Core LIF Simulator
- **Workload:** Controlled Synaptic Weight Poisoning (Target Core: 2, Start Step: 20, Duration: 25 steps)
- **Cores:** 4 cores (Core 0 Sensory, Core 1 Compute, Core 2 Compute, Core 3 Egress)
- **Neuron Count:** 128 (32 per core)
- **Synapses / Edges:** 689 intra-core + 276 inter-core routing connections
- **Input Events:** 50 events from DVS128 Gesture sample
- **Output Spikes Recorded:** 49 spikes across 100 timesteps
- **Membrane Potentials:** Observable across all 4 cores (`final_potentials`)
- **Evidence Artifacts:** Merkle-sealed `.nfd.gz` forensic capture, STIX 2.1 CTI bundle, and ablation results

### Intel Lava Framework (Python 3.10 Subprocess Worker)
- **Workload:** Controlled RingBuffer Input Stimulation to LIF Process
- **Cores / Process Model:** 1 Core / 1 Lava PyProcModel
- **Neuron Count:** 4 LIF neurons
- **Synapses:** 4 cyclic feedback connections
- **Output Spikes Recorded:** 56 genuine output spikes across 20 steps
- **Membrane Potentials:** Final voltages observable from `lif.v.get()` (`[0.0, 0.0, 0.0, 0.0]`)
- **Limitation:** Lava CPU floating-point model does not expose intermediate synaptic weight deltas at microsecond granularity during run; these are marked as `LAVA_PROCESS_MODEL` with weight registers preserved in memory.

---

## 5. Verification & Test Results

Added `tests/test_graph_dataflow.py` with 3 comprehensive regression tests:
1. `test_builtin_lif_graph_dataflow`: Verifies 128-neuron topology, non-empty spike stream, membrane potentials, timeline, and experiment retrieval by ID.
2. `test_lava_cpu_graph_dataflow`: Verifies genuine Lava subprocess execution, 4-neuron topology, spike stream translation, and retrieval by ID.
3. `test_experiment_retrieval_404`: Verifies that invalid experiment IDs return clean HTTP 404s.

### Full Test Suite Results
```bash
py -3.14 -m pytest tests/
======================== 43 passed in 73.54s (0:01:13) ========================
```
All 43 tests pass (100% pass rate).
