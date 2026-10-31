# NeuroForensics — Microscopic Neuron Visualization & Forensic UI Report

**Date:** 2026-10-17  
**Author:** Antigravity / NeuroForensics Engineering  
**Test Suite Status:** 40 / 40 PASSED  

---

## 1. Executive Summary

NeuroForensics has been upgraded from a static, decorative dot display to an interactive, state-driven microscopic SNN forensics visualizer. 

The application now supports:
1. **Interactive Microscopic SNN Canvas (`#neuralNetCanvas`):**
   - Renders 128 genuine biological LIF neurons grouped into their 4 physical cores (32 neurons per core).
   - Renders genuine intra-core and inter-core synaptic connectivity edges directly from `NeuromorphicTopology`.
   - Distinguishes Resting, Depolarized, Firing (transient white spike glow), and Compromised/Suspect states.
2. **Timeline Playback & Scrubbing:**
   - Controls: Play/Pause, Step +1, Step -1, Reset, Speed selector (0.5x, 1x, 2x, 4x), and Timeline range slider ($t \in [0, 100]$ ms).
   - Animates actual spike events recorded by `ForensicCollector`.
3. **Interactive Inspection & Zoom/Pan:**
   - Mouse wheel zoom (0.5x to 4.0x) and mouse drag panning.
   - Click-to-inspect neuron: opens the **Neuron Inspector Panel** displaying Neuron ID, Core, Live Membrane Potential ($V_m$), Spikes Fired, and Forensic Classification (Suspect vs Benign).
4. **Bidirectional Topology Synchronization:**
   - Clicking any core ($C_0, C_1, C_2, C_3$) in the 4-core ring topology filters and expands that core's microscopic population.
   - Selecting a neuron in the microscopic graph highlights its parent core in the topology view.
5. **Timestamp Disambiguation & Validation (DVS128):**
   - Disambiguated raw hardware clock epoch (194.08s from camera start) from relative elapsed time ($t - t_0$).
   - The Dataset Explorer and Event Table now explicitly show both relative millisecond offset (`+X.XX ms`) and canonical second timestamps.
6. **Functional Empty State Actions:**
   - Tab 3 (Evidence Sufficiency) includes an interactive **Run Ablation** action that dynamically executes an ablation study if no prior run is loaded.

---

## 2. Files Changed

| File | Changes Made |
| :--- | :--- |
| `src/datasets/base.py` | Added `relative_time_ms` to `NeuromorphicEvent` schema. |
| `src/datasets/dvs128_loader.py` | Calculated `relative_time_ms` for each event relative to the start of the recording ($t - t_0$). |
| `src/neuromorphic/topology.py` | Implemented `export_topology_graph()` extracting all genuine intra/inter-core synaptic edges with weights. |
| `src/eval/runner.py` | Exported `network_topology`, `spike_stream`, and `final_potentials` in `dashboard_state`. |
| `web/api/server.py` | Added `/api/simulation/topology` endpoint; enhanced sample inspection response with relative timestamps. |
| `web/index.html` | Redesigned Tab 4 with microscopic workspace, playback controls, and Neuron Inspector; added `Relative (ms)` column in Tab 2; added `Run Ablation` button in Tab 3. |
| `web/js/app.js` | Built complete SNN playback engine, zoom/pan transforms, hit-testing for neuron selection, and bidirectional synchronization. |
| `tests/test_visualization.py` | Added 4 automated regression tests covering topology export, API endpoint, DVS128 offsets, and payload contracts. |
| `docs/neuron-visualization-audit.md` | Full data path audit and root cause documentation. |

---

## 3. Automated Test Verification

Command:
```powershell
py -3.14 -m pytest tests/ -v --tb=short
```

Output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\harsh\OneDrive\Desktop\K S Harshitaa\Projects\DF+IRTI Project
plugins: anyio-4.13.0, langsmith-0.8.0, mock-3.15.1
collecting ... collected 40 items

tests/test_ablation.py::test_evidence_subset_filtering PASSED            [  2%]
tests/test_ablation.py::test_reconstruction_scoring_and_ground_truth_separation PASSED [  5%]
tests/test_ablation.py::test_evidence_ablation_degradation_and_minimum_sufficient_sets PASSED [  7%]
tests/test_acquisition.py::test_acquisition_and_merkle_verification PASSED [ 10%]
tests/test_acquisition.py::test_evidence_tamper_detection PASSED         [ 12%]
tests/test_api.py::test_api_health PASSED                                [ 15%]
tests/test_api.py::test_api_datasets PASSED                              [ 17%]
tests/test_api.py::test_api_backends PASSED                              [ 20%]
tests/test_api.py::test_api_simulation_stepping PASSED                   [ 22%]
tests/test_api.py::test_api_attack_execution PASSED                      [ 25%]
tests/test_backends.py::test_builtin_simulator_adapter_lifecycle PASSED  [ 27%]
tests/test_backends.py::test_builtin_simulator_attack_attachment PASSED  [ 30%]
tests/test_backends.py::test_lava_cpu_adapter_reporting_and_guarding PASSED [ 32%]
tests/test_dashboard_repair.py::test_root_redirect_to_dashboard PASSED   [ 35%]
tests/test_dashboard_repair.py::test_datasets_endpoint_includes_genuine_local_file PASSED [ 37%]
tests/test_dashboard_repair.py::test_dvs128_sample_retrieval_returns_genuine_events PASSED [ 40%]
tests/test_dashboard_repair.py::test_backends_reporting_and_lava_guard PASSED [ 42%]
tests/test_dashboard_repair.py::test_execute_attack_on_unavailable_backend_rejected PASSED [ 45%]
tests/test_dashboard_repair.py::test_execute_attack_produces_stamped_experiment_context PASSED [ 47%]
tests/test_datasets.py::test_synthetic_dataset_loader PASSED             [ 50%]
tests/test_datasets.py::test_dvs128_aedat_parser_valid PASSED            [ 52%]
tests/test_datasets.py::test_dvs128_invalid_file PASSED                  [ 55%]
tests/test_datasets.py::test_shd_loader_without_h5py PASSED              [ 57%]
tests/test_datasets.py::test_dataset_registry PASSED                     [ 60%]
tests/test_dfir_cti.py::test_dfir_and_stix_generation PASSED             [ 62%]
tests/test_eval.py::test_pipeline_runner_end_to_end PASSED               [ 65%]
tests/test_neuromorphic.py::test_topology_initialization PASSED          [ 67%]
tests/test_neuromorphic.py::test_simulator_step PASSED                   [ 70%]
tests/test_neuromorphic.py::test_attack_injection PASSED                 [ 72%]
tests/test_phase2_validation.py::test_genuine_sample_ingestion_and_immutability PASSED [ 75%]
tests/test_phase2_validation.py::test_real_dataset_stimulation_drives_simulator PASSED [ 77%]
tests/test_phase2_validation.py::test_merkle_independent_verification_and_tamper_detection PASSED [ 80%]
tests/test_phase2_validation.py::test_benign_control_produces_zero_false_positives PASSED [ 82%]
tests/test_phase2_validation.py::test_evidence_sufficiency_ablation_degradation PASSED [ 85%]
tests/test_phase2_validation.py::test_repeated_run_determinism PASSED    [ 87%]
tests/test_reconstruction.py::test_timeline_reconstruction PASSED        [ 90%]
tests/test_visualization.py::test_topology_export_contains_microscopic_neurons_and_synapses PASSED [ 92%]
tests/test_visualization.py::test_api_simulation_topology_endpoint PASSED [ 95%]
tests/test_visualization.py::test_dvs128_relative_timestamps_and_offsets PASSED [ 97%]
tests/test_visualization.py::test_execute_attack_returns_microscopic_graph_payload PASSED [100%]

============================= 40 passed in 45.89s =============================
```

---

## 4. Manual Verification Steps

1. **Launch Server:**
   ```powershell
   py -3.14 -m uvicorn web.api.server:app --host 127.0.0.1 --port 8000
   ```
2. **Tab 1: Execute Attack Workbench Experiment:**
   - Execute an attack (e.g., Synaptic Weight Poisoning). The Active Banner updates with a new experiment ID.
3. **Tab 4: Attack Reconstruction & Microscopic Visualizer:**
   - Click **Tab 4**. The 4-core ring topology and the **Microscopic SNN Synaptic Network Graph** render.
   - Observe the 128 genuine neurons with active synaptic connection lines.
   - Click **Play (▶)**: Watch the step counter increment, with genuine firing pulses and white glowing spike cascades at each step.
   - Move the **Timeline Scrubber**: Jump to any specific step (e.g., Step 30, where the attack starts).
   - Click on any neuron: The **Neuron Inspector** on the right displays the exact membrane potential ($V_m$), firing count, and suspect classification.
   - Click **Core 2** in the top topology graph: The microscopic graph transitions into the detailed single-core view for Core 2 (32 neurons).
   - Test Zoom & Pan: Scroll wheel zooms in/out; dragging pans the view. Click **Reset Zoom** to reset.
4. **Tab 2: Dataset Explorer:**
   - Select `dvs128_events_128.aedat`. Confirm the table displays **Relative (ms)** alongside **Timestamp (s)** and **Raw (µs)**.
5. **Tab 3: Evidence Sufficiency:**
   - Confirm the **Run Ablation** button executes the combinatorial study and plots the evidence-sufficiency curve.
