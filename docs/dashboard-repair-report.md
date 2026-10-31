# Dashboard Repair & Functional Data Flow Report

**Date:** 2026-10-17  
**Status:** Completed & Empirically Verified  

---

## 1. Root Causes Found

1. **Global Contradictory Stats Bar:**
   - The top KPI row (`Reconstruction Score: 91.5%`, `Root Cause Core: Core 1`, `Min Cardinality: 1`) was previously placed globally above all tabs and defaulted to hardcoded dummy objects (`VERIFIED_SCENARIO_DATA['synaptic_poisoning']`) on page load before any experiment ran.
   - This conflicted directly with the Workbench tab displaying different configurations (e.g. Synaptic Poisoning on Core 2 vs Spike Storm).
2. **Missing Real Data Flow in Dataset Explorer:**
   - `DatasetRegistry` was only registering an in-memory synthetic fixture on startup; genuine local files (`data/dvs128/events_128.aedat`) were not discovered.
   - The Dataset Explorer tab had static HTML cards and an unparsed static checklist rather than calling `/api/datasets` and `/api/datasets/{id}/samples`.
3. **Intel Lava Selection & Execution Guarding:**
   - Lava was selectable as a runtime target in HTML dropdowns without reactive disabling when the backend reported itself as unavailable on Python 3.14.4.
4. **Root Endpoint 404:**
   - The FastAPI server mounted `/dashboard/` but had no route or redirect on `/`, resulting in a 404 when navigating to `http://127.0.0.1:8000`.

---

## 2. Files Changed

1. **`web/api/server.py`**:
   - Added automatic root redirect (`/` -> `/dashboard/`).
   - Added automatic discovery and registration of local DVS128 (`data/dvs128/events_128.aedat`) and SHD files into `DatasetRegistry`.
   - Updated `/api/datasets/{id}/samples` to parse genuine sample events with spatial coordinates, timestamps, and SHA-256 hashes.
   - Attached unique `experiment_id`, `backend_used`, and `dataset_used` to `/api/attacks/execute` responses.
2. **`web/index.html`**:
   - Replaced contradictory top stats with an **Active Experiment Context Banner** (`bannerExpId`, `bannerScenario`, `bannerBackend`, `bannerScore`).
   - Contextualized each tab so that metrics and timelines only appear for an executed or explicitly loaded experiment.
   - Replaced static dataset markup with a dynamic sample metadata card and a paginated event stream table.
3. **`web/js/app.js`**:
   - Implemented an explicit state model (`activeState`: `status`, `experimentId`, `selectedBackend`, `selectedDataset`, `experimentData`).
   - Dynamic `/api/backends` loading: detects unsupported environments (Lava on Python 3.14) and disables execution with clear diagnostic text.
   - Interactive Dataset Explorer: dynamically fetches `/api/datasets`, handles card selection, inspects sample metadata, and streams real events into the table.
4. **`tests/test_dashboard_repair.py`**:
   - Added 6 automated tests verifying redirect, dataset discovery, sample parsing, backend guarding, and contextual experiment response.

---

## 3. Verified Endpoints & Backend Operations

| Endpoint | Method | Operation Verified |
|---|---|---|
| `/` | GET | HTTP 307 redirect to `/dashboard/` |
| `/api/health` | GET | Health check returns `{"status": "ok", "app": "NeuroForensics"}` |
| `/api/datasets` | GET | Returns genuine `dvs128_events_128.aedat` and `synthetic_42` |
| `/api/datasets/{id}/samples` | GET | Parses genuine DVS128 events (`x`, `y`, `polarity`, `timestamp`) |
| `/api/backends` | GET | Reports Built-in simulator as Available, Intel Lava as Available via Python 3.10 Worker |
| `/api/simulation/step` | POST | Advances discrete simulation step by 1 ms and returns observations |
| `/api/simulation/reset` | POST | Resets simulation states to step 0 |
| `/api/attacks/execute` | POST | Rejects unknown backends; executes full pipeline on simulator with real dataset stimulus or genuine Lava CPU PyProcModel |

---

## 4. Manual Verification Steps for Each Tab

1. **Launch Server:**
   ```powershell
   py -3.14 -m uvicorn web.api.server:app --host 127.0.0.1 --port 8000
   ```
2. **Access Root URL:**
   - Navigate to `http://127.0.0.1:8000/`. Confirm automatic redirect to `/dashboard/`.
3. **Tab 1: Attack Workbench & Backends:**
   - Select **Intel Lava CPU Adapter**: Observe the status badge indicating `Intel Lava Framework (Python 3.10 Subprocess Worker)` and execution enabled with full observable spike flow.
   - Switch to **Built-in Multi-Core LIF Simulator**: Observe the execution button enables.
   - Click **Run Attack Simulation**: Watch the status change to "Simulating...", followed by completion with a unique `exp_*` identifier and updated banner score.
4. **Tab 2: Dataset Explorer:**
   - Click the **DVS128 Gesture** card. Observe the sample metadata update with file SHA-256 (`6d982a802018cf...`), 1000 events, and the event preview table populating with actual camera polarity events.
5. **Tab 3: Evidence Sufficiency & Ablation:**
   - Inspect the empirical ablation curve and minimum sufficient sets derived from the completed run.
6. **Tab 4: Attack Reconstruction & Topology:**
   - Verify the 4-core ring architecture highlights the reconstructed target core and causal edges without hardcoded default values.
7. **Tab 5: DFIR Playbook & CTI:**
   - View the incident containment actions and mapped STIX 2.1 threat indicators generated from the actual run.
