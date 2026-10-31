# Forensic Audit: Dashboard Repair, Functional Data Flow, and Truthful UI

**Date:** 2026-10-17  
**Auditor:** Senior Forensic Systems & Frontend Engineer  
**Scope:** `web/index.html`, `web/js/app.js`, `web/api/server.py`, `web/css/style.css`, and related backend endpoints.

---

## 1. Classification of Visible Metrics & UI State

| Metric / Label / Element | Location | Value Observed | Data Source Classification | Findings & Defect Analysis |
|---|---|---|---|---|
| **Investigated Attack Scenario** | Top Stats Grid (`#scenarioSelect`) | Synaptic Poisoning / Spike Flooding / Timing Jitter | (2) Static Pre-cooked fallback | Selectable dropdown is placed globally across all tabs, including tabs where no experiment has been run yet. |
| **Reconstruction Score** | Top Stats Grid (`#statReconScore`) | 91.5% / 88.5% | (4) Fabricated / Hardcoded Fallback | Hardcoded fallback (`0.885` / `VERIFIED_SCENARIO_DATA`) displayed immediately upon load even when no experiment was executed. |
| **Min Sufficient Cardinality** | Top Stats Grid (`#statMinCard`) | 1 / 2 Artifact Classes | (4) Fabricated / Hardcoded Fallback | Hardcoded from `VERIFIED_SCENARIO_DATA` dictionary in `app.js` prior to any user execution. |
| **Root Cause Core** | Top Stats Grid (`#statRootCore`) | Core 1 / Core 2 | (4) Fabricated / Hardcoded Fallback | Hardcoded default fallback `Core 2` displayed regardless of actual run state. |
| **Live Stream Badge** | Neural Net header (`#liveSynapseBadge`) | "Live Dynamic SNN Stream" | (4) Decorative / Fabricated | Canvas animation runs a purely synthetic oscillating sine-wave canvas loop (`startSynapseAnimation`) giving a false impression of live hardware execution. |
| **Attack Workbench Backend Select** | Tab 4 (`#workbenchBackendSelect`) | Intel Lava CPU Adapter | (3) Static HTML / (4) Misleading State | Intel Lava is selectable in the dropdown despite being unavailable on Python 3.14.4. |
| **Dataset Explorer Cards** | Tab 5 (`#datasetsListContainer`) | SHD, DVS128, Synthetic | (3) Static HTML strings | Hardcoded static HTML blocks in `index.html`. Does not fetch `/api/datasets`, does not allow selecting samples, and does not show actual event tables. |
| **Dataset Event Stream Preview** | Tab 5 (`#datasetPreviewBox`) | `[✓] DVS128 AEDAT parser...` | (3) Static HTML / Hardcoded text | Static checklist in a `<div>` masquerading as a dynamic validation check. Never calls `/api/datasets/{id}/samples`. |
| **Empirical Matrix Table** | Tab 1 (`#matrixTable`) | 3 rows × 7 columns | (2) Saved file (`web/matrix.json`) | Valid empirical matrix from prior combinatorial ablation, but presented without provenance metadata or experiment ID. |
| **STIX 2.1 Threat Intel** | Tab 3 (`#ctiCardsContainer`) | T1565.001 / T1499.004 | (2) Saved file (`web/data.json`) | Matches STIX export schemas, but linked to static fallback scenarios instead of currently executed experiment ID. |

---

## 2. Identified Inconsistencies & Root Causes

1. **Stale/Contradictory State Across Tabs:**
   - The top stats cards (`statReconScore`, `statMinCard`, `statRootCore`) are rendered globally above the navigation tabs. Because they initialized from `VERIFIED_SCENARIO_DATA['synaptic_poisoning']`, switching tabs or selecting a different scenario in the workbench caused contradictory metrics across views.
2. **Missing Real Sample Explorer:**
   - `/api/datasets` only registered the synthetic fixture in memory at server boot. Real datasets located on disk (`data/dvs128/events_128.aedat`) were not registered with the registry on startup, so `/api/datasets` never listed actual local files.
   - `/api/datasets/{id}/samples` only handled `synthetic` IDs and returned empty arrays for all other datasets.
3. **Intel Lava Selection & Guarding:**
   - `updateBackendStatus()` in `app.js` only adjusted a text badge rather than checking real capability from `/api/backends` and properly disabling execution when unsupported.
4. **No Explicit Experiment-State Model:**
   - There was no unified state object tracking:
     - `currentExperimentId`
     - `executionState` (`IDLE`, `RUNNING`, `SUCCESS`, `FAILED`)
     - `activeDataset`
     - `activeSample`
     - `activeBackend`
5. **No True Event Table Preview:**
   - Dataset explorer lacked sample selection, sample metadata cards (dimensions, channels, event count, SHA-256), and paginated event tables.

---

## 3. Planned Remediation

1. **Unified Experiment State:** Introduce a single state manager in `app.js` with clear states: `NO_EXPERIMENT`, `RUNNING`, `COMPLETED`, `FAILED`. Empty states displayed when no run has executed.
2. **Context-Appropriate Metrics:** Relocate the top stats bar to be contextual to the active experiment only, clearly displaying the associated Experiment ID.
3. **Dynamic Dataset Explorer:**
   - Auto-register existing local datasets (`data/dvs128/events_128.aedat`, `data/shd/`) in `server.py`.
   - Update `/api/datasets/{id}/samples` to parse and return genuine sample events from `.aedat` and `.h5` files.
   - Implement interactive dataset card selection, sample dropdown, metadata inspector, integrity hash check, and paginated event table in Tab 5.
4. **Truthful Backend Availability:**
   - Query `/api/backends` dynamically on load.
   - If a backend is unavailable (e.g. Intel Lava on Python 3.14), mark it as `[UNSUPPORTED ENVIRONMENT]`, show its exact diagnostic reason, and disable execution.
5. **Attack Workbench Contextual Output:**
   - Keep Workbench parameters, execution logs, and run results isolated to the current run.
6. **Automated Testing:**
   - Add comprehensive tests in `tests/test_dashboard_repair.py` validating the corrected endpoints, sample loading, backend guarding, and state responses.
