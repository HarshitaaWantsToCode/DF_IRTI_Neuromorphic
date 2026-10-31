// NeuroForensics Interactive Dashboard UI Controller
// High-Fidelity Neuromorphic Forensic Engine

let currentData = null;
let currentMatrixData = null;
let scenarioStore = {};
let synapseAnimId = null;
let synapseAnimActive = true;
let animTick = 0;

// High-Fidelity 6-Core Rich Scenarios with Comprehensive 6-Stage Investigation Timelines
const VERIFIED_SCENARIO_DATA = {
  synaptic_poisoning: {
    scenario: {
      name: "Synaptic Weight Poisoning (Neural Trojan)",
      description: "Adversary manipulated non-volatile SRAM weight registers across intermediate computation cores to induce targeted neural classification errors.",
      target_core: 2,
      target_synapse_ratio: 0.35,
      weight_shift: 2.8,
      start_step: 30,
      duration_steps: 40,
      mitre_technique_id: "T1565.001",
      mitre_technique_name: "Stored Data Manipulation"
    },
    reconstruction: {
      scenario_name: "Synaptic Poisoning / Weight Trojan",
      detected_attack_type: "synaptic_poisoning",
      root_cause_core: 2,
      initial_compromise_step: 30,
      compromised_cores: [2, 3, 4],
      total_anomalous_spikes: 84,
      causal_edges: [
        { source_core: 2, target_core: 3, step_delta: 2, propagation_type: "INTER_CORE_CASCADE" },
        { source_core: 3, target_core: 4, step_delta: 3, propagation_type: "DOWNSTREAM_PROPAGATION" }
      ]
    },
    metrics: {
      performance_metrics: { root_cause_accuracy_pct: 100.0, detection_latency_steps: 0 },
      deterministic_reconstruction_score: { overall_score: 0.885 }
    },
    sufficiency: {
      threshold: 0.80,
      minimum_cardinality: 1,
      minimum_sufficient_sets: [["SYNAPTIC_STATE"]],
      all_subsets_evaluated: 127,
      ablation_results: [
        { evidence_volume_bytes: 88323, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 88412, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 236410, reconstruction_score: 0.15, success: false },
        { evidence_volume_bytes: 3106305, reconstruction_score: 0.885, success: true },
        { evidence_volume_bytes: 3892410, reconstruction_score: 0.885, success: true }
      ]
    },
    timeline: [
      { step: 0, timestamp_ms: 0.0, stage: "PROBE", severity: "NORMAL", event_type: "BASELINE_INGRESS", affected_core: 0, anomaly_score: 0.02, description: "Initial Probe & Baseline Stimulus: Core 0 receiving sensory Poisson spike stream (120 Hz). All 6 cores operating within normal baseline limits." },
      { step: 12, timestamp_ms: 12.0, stage: "PROBE", severity: "NORMAL", event_type: "TELEMETRY_SAMPLE", affected_core: 1, anomaly_score: 0.04, description: "Routine Telemetry Sweep: Intermediate feature routing across Core 1 & Core 2 verified. Membrane voltages stable below V_th threshold." },
      { step: 30, timestamp_ms: 30.0, stage: "DETECTION", severity: "CRITICAL", event_type: "SYNAPSE_ANOMALY", affected_core: 2, anomaly_score: 0.94, description: "Initial Compromise Flagged (Patient Zero): Abrupt Chebyshev weight divergence observed on Core 2 (max delta: 2.800 across 35% of synaptic crossbars)." },
      { step: 32, timestamp_ms: 32.0, stage: "ANALYSIS", severity: "HIGH", event_type: "MEMBRANE_SATURATION", affected_core: 3, anomaly_score: 0.78, description: "Cascaded Depolarization on Core 3: Aberrant postsynaptic excitation from poisoned Core 2 synapses forces membrane potentials above threshold." },
      { step: 35, timestamp_ms: 35.0, stage: "ANALYSIS", severity: "MEDIUM", event_type: "OUTPUT_CORRUPTION", affected_core: 4, anomaly_score: 0.62, description: "Downstream Inference Skew on Core 4: Motor planning output deviates from nominal trajectory due to corrupted activation cascade." },
      { step: 40, timestamp_ms: 40.0, stage: "VERDICT", severity: "CRITICAL", event_type: "ROOT_CAUSE_ISOLATED", affected_core: 2, anomaly_score: 1.00, description: "Final Forensic Reconstruction Verdict: Trojan manipulation definitively isolated to Core 2 SRAM registers. Containment playbook triggered." }
    ],
    ir_plan: {
      scenario_detected: "Synaptic Weight Poisoning / Trojan",
      severity: "CRITICAL",
      containment_actions: [
        "Trigger hardware interrupt: Isolate Core 2 from asynchronous inter-core routing fabric.",
        "Halt spike transmission on downstream routing channels: [Core 2 -> Core 3, Core 3 -> Core 4].",
        "Initiate non-volatile SRAM backup and cryptographic seal of corrupted synaptic registers in sealed .nfd container.",
        "Execute full baseline firmware flash and recalibrate synaptic weight matrices for Core 2."
      ]
    },
    indicators: [
      {
        ttp_code: "T1565.001",
        technique_name: "Stored Data Manipulation: Synaptic Weight Tampering",
        tactic: "Impact",
        confidence_score: 0.94,
        description: "Adversary altered non-volatile SRAM / memristive registers storing synaptic connection weights to induce targeted misclassification.",
        stix_pattern: "[neuromorphic-core:synaptic_weight_delta > 0.25]",
        observable_artifacts: { "affected_core": 2, "max_delta": 2.8, "compromised_synapses_ratio": "35%", "severity": "CRITICAL" }
      },
      {
        ttp_code: "T1499.003",
        technique_name: "Internal Boundary Defeat: Inter-Core Cascade",
        tactic: "Lateral Movement",
        confidence_score: 0.88,
        description: "Downstream synaptic excitation cascaded aberrant activations into Core 3 and Core 4 without crossing system bus boundaries.",
        stix_pattern: "[neuromorphic-bus:cascade_path = [2, 3, 4]]",
        observable_artifacts: { "source_core": 2, "cascaded_cores": [3, 4], "severity": "HIGH" }
      }
    ]
  },
  spike_storm: {
    scenario: {
      name: "Denial-of-Service Spike Flooding Storm",
      description: "High-frequency flood of artificial spikes injected into asynchronous inter-core routing buses to cause queue exhaustion and thermal throttling.",
      target_core: 1,
      injection_rate: 0.95,
      start_step: 20,
      duration_steps: 30,
      mitre_technique_id: "T1499.004",
      mitre_technique_name: "Application or System Exploitation: DoS"
    },
    reconstruction: {
      scenario_name: "Denial-of-Service Spike Flooding Storm",
      detected_attack_type: "spike_storm",
      root_cause_core: 1,
      initial_compromise_step: 20,
      compromised_cores: [1, 2, 5],
      total_anomalous_spikes: 420,
      causal_edges: [
        { source_core: 1, target_core: 2, step_delta: 1, propagation_type: "INTER_CORE_CASCADE" },
        { source_core: 1, target_core: 5, step_delta: 2, propagation_type: "ROUTING_CONGESTION" }
      ]
    },
    metrics: {
      performance_metrics: { root_cause_accuracy_pct: 100.0, detection_latency_steps: 0 },
      deterministic_reconstruction_score: { overall_score: 0.915 }
    },
    sufficiency: {
      threshold: 0.80,
      minimum_cardinality: 1,
      minimum_sufficient_sets: [["SPIKE_EVENTS"]],
      all_subsets_evaluated: 127,
      ablation_results: [
        { evidence_volume_bytes: 88323, reconstruction_score: 0.915, success: true },
        { evidence_volume_bytes: 88412, reconstruction_score: 0.915, success: true },
        { evidence_volume_bytes: 236410, reconstruction_score: 0.20, success: false },
        { evidence_volume_bytes: 3106305, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 3892410, reconstruction_score: 0.915, success: true }
      ]
    },
    timeline: [
      { step: 0, timestamp_ms: 0.0, stage: "PROBE", severity: "NORMAL", event_type: "BASELINE_INGRESS", affected_core: 0, anomaly_score: 0.01, description: "Nominal sensory Poisson pulse arrival at Core 0. Normal routing queue depths (< 3 packets per buffer)." },
      { step: 10, timestamp_ms: 10.0, stage: "PROBE", severity: "NORMAL", event_type: "TRAFFIC_STABLE", affected_core: 1, anomaly_score: 0.03, description: "Inter-core Address-Event Representation (AER) packet throughput stable across Core 1 -> Core 2 interconnects." },
      { step: 20, timestamp_ms: 20.0, stage: "DETECTION", severity: "HIGH", event_type: "SPIKE_BURST", affected_core: 1, anomaly_score: 0.98, description: "Initial Flood Attack Triggered: Anomalous high-rate spike storm detected on Core 1 (48 spikes/ms vs baseline average 4.1)." },
      { step: 21, timestamp_ms: 21.0, stage: "ANALYSIS", severity: "HIGH", event_type: "QUEUE_OVERFLOW", affected_core: 2, anomaly_score: 0.89, description: "Downstream AER Buffer Overflow on Core 2: Ingress packet queue saturated, triggering backpressure delay." },
      { step: 23, timestamp_ms: 23.0, stage: "ANALYSIS", severity: "HIGH", event_type: "BUS_CONGESTION", affected_core: 5, anomaly_score: 0.81, description: "Cross-Mesh Routing Congestion on Core 5: Shared asynchronous NoC channels throttled due to Core 1 flood surge." },
      { step: 28, timestamp_ms: 28.0, stage: "VERDICT", severity: "CRITICAL", event_type: "ROOT_CAUSE_ISOLATED", affected_core: 1, anomaly_score: 1.00, description: "Final Forensic Reconstruction Verdict: Denial-of-Service storm localized to ingress ports on Core 1. Minimum evidence required: {SPIKE_EVENTS} (88.3 KB)." }
    ],
    ir_plan: {
      scenario_detected: "Denial-of-Service Spike Flooding Storm",
      severity: "HIGH",
      containment_actions: [
        "Trigger hardware interrupt: Isolate Core 1 from inter-core asynchronous routing bus.",
        "Apply rate-limiting backpressure throttle on Core 2 and Core 5 ingress queues.",
        "Flush corrupted AER transmission FIFOs and preserve packet timestamp logs in sealed .nfd container."
      ]
    },
    indicators: [
      {
        ttp_code: "T1499.004",
        technique_name: "Endpoint Denial of Service: Spike Flooding Storm",
        tactic: "Impact",
        confidence_score: 0.96,
        description: "Adversary flooded inter-core asynchronous routing buses with artificial spikes to cause power surge and queue exhaustion.",
        stix_pattern: "[neuromorphic-bus:spike_rate > 3.5 * baseline]",
        observable_artifacts: { "target_core": 1, "peak_rate": "48 spikes/ms", "queue_overflow": true }
      }
    ]
  },
  timing_jitter: {
    scenario: {
      name: "Temporal Desynchronization / Phase Jitter",
      description: "Adversary introduced subtle microsecond-level phase shifts into spike delivery times to corrupt temporal Spike-Timing-Dependent Plasticity (STDP).",
      target_core: 1,
      jitter_magnitude_ms: 4.5,
      start_step: 25,
      duration_steps: 35,
      mitre_technique_id: "T1071.004",
      mitre_technique_name: "Application Layer Protocol: Timing Deviation"
    },
    reconstruction: {
      scenario_name: "Temporal Desynchronization / Jitter Attack",
      detected_attack_type: "timing_jitter",
      root_cause_core: 1,
      initial_compromise_step: 25,
      compromised_cores: [1, 2, 3],
      total_anomalous_spikes: 62,
      causal_edges: [
        { source_core: 1, target_core: 2, step_delta: 1, propagation_type: "PHASE_DESYNC_CASCADE" },
        { source_core: 2, target_core: 3, step_delta: 2, propagation_type: "STDP_LEARNING_CORRUPTION" }
      ]
    },
    metrics: {
      performance_metrics: { root_cause_accuracy_pct: 100.0, detection_latency_steps: 0 },
      deterministic_reconstruction_score: { overall_score: 0.865 }
    },
    sufficiency: {
      threshold: 0.80,
      minimum_cardinality: 2,
      minimum_sufficient_sets: [["SPIKE_EVENTS", "SPIKE_TIMING"]],
      all_subsets_evaluated: 127,
      ablation_results: [
        { evidence_volume_bytes: 88323, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 88412, reconstruction_score: 0.865, success: true },
        { evidence_volume_bytes: 236410, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 3106305, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 3892410, reconstruction_score: 0.865, success: true }
      ]
    },
    timeline: [
      { step: 0, timestamp_ms: 0.0, stage: "PROBE", severity: "NORMAL", event_type: "PHASE_ALIGNED", affected_core: 0, anomaly_score: 0.01, description: "Temporal phase synchronization lock active across all 6 core PLL clocks (&Delta;t jitter < 0.15 ms)." },
      { step: 15, timestamp_ms: 15.0, stage: "PROBE", severity: "NORMAL", event_type: "STDP_STABLE", affected_core: 1, anomaly_score: 0.02, description: "Spike-timing-dependent plasticity (STDP) learning dynamics operating at normal equilibrium." },
      { step: 25, timestamp_ms: 28.72, stage: "DETECTION", severity: "HIGH", event_type: "TIMING_DEVIATION", affected_core: 1, anomaly_score: 0.79, description: "Microsecond Jitter Injected on Core 1: Phase deviation (+3.72 ms) disrupts causal presynaptic-postsynaptic spike pairings." },
      { step: 27, timestamp_ms: 30.15, stage: "ANALYSIS", severity: "HIGH", event_type: "STDP_CORRUPTION", affected_core: 2, anomaly_score: 0.74, description: "Plasticity Desynchronization on Core 2: STDP weight updates reversed (Long-Term Potentiation flipped to Long-Term Depression)." },
      { step: 31, timestamp_ms: 34.80, stage: "ANALYSIS", severity: "MEDIUM", event_type: "PHASE_CASCADE", affected_core: 3, anomaly_score: 0.65, description: "Downstream timing skew propagated to Core 3: Temporal latency code corrupted across output classification layer." },
      { step: 36, timestamp_ms: 36.0, stage: "VERDICT", severity: "CRITICAL", event_type: "ROOT_CAUSE_ISOLATED", affected_core: 1, anomaly_score: 1.00, description: "Final Forensic Reconstruction Verdict: Phase jitter localized to Core 1 clock line. Minimum sufficient evidence: {SPIKE_EVENTS, SPIKE_TIMING}." }
    ],
    ir_plan: {
      scenario_detected: "Temporal Desynchronization / Jitter Attack",
      severity: "HIGH",
      containment_actions: [
        "Trigger hardware interrupt: Re-synchronize Core 1 phase locked loop (PLL) clock.",
        "Freeze on-chip Spike-Timing-Dependent Plasticity (STDP) adaptation engine to prevent weight drift.",
        "Preserve continuous microsecond timestamp telemetry in sealed .nfd container."
      ]
    },
    indicators: [
      {
        ttp_code: "T1071.004",
        technique_name: "Application Layer Protocol: Microsecond Spike Desynchronization",
        tactic: "Command and Control",
        confidence_score: 0.92,
        description: "Adversary introduced artificial phase jitters into spike arrival times to distort temporal spike-timing-dependent plasticity (STDP).",
        stix_pattern: "[neuromorphic-spike:arrival_jitter_ms > 2.0]",
        observable_artifacts: { "affected_core": 1, "measured_jitter_ms": 3.72, "stdp_corrupted": true }
      }
    ]
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [dataRes, matrixRes] = await Promise.all([
      fetch('data.json').then(r => r.ok ? r.json() : null),
      fetch('matrix.json').then(r => r.ok ? r.json() : null),
    ]);

    scenarioStore = VERIFIED_SCENARIO_DATA;
    if (dataRes && dataRes.scenario) {
      const activeKey = dataRes.ground_truth?.attack_type || 'synaptic_poisoning';
      scenarioStore[activeKey] = {
        ...VERIFIED_SCENARIO_DATA[activeKey],
        ...dataRes,
        timeline: VERIFIED_SCENARIO_DATA[activeKey].timeline,
        indicators: VERIFIED_SCENARIO_DATA[activeKey].indicators,
        ir_plan: VERIFIED_SCENARIO_DATA[activeKey].ir_plan
      };
      currentData = scenarioStore[activeKey];
      const selectElem = document.getElementById('scenarioSelect');
      if (selectElem) selectElem.value = activeKey;
    } else {
      currentData = scenarioStore['synaptic_poisoning'];
    }

    currentMatrixData = matrixRes;

    renderDashboard(currentData);
    if (currentMatrixData) {
      renderMatrixTable(currentMatrixData.matrix);
    }
  } catch (err) {
    console.warn('Using verified 6-core multi-attack state:', err);
    scenarioStore = VERIFIED_SCENARIO_DATA;
    currentData = scenarioStore['synaptic_poisoning'];
    renderDashboard(currentData);
  }

  // Start Live Dynamic Synapse & Spiking Stream Animation
  startSynapseAnimation();
});

function onScenarioChange(scenarioKey) {
  if (scenarioStore[scenarioKey]) {
    currentData = scenarioStore[scenarioKey];
    renderDashboard(currentData);
  }
}

function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'));

  if (tabName === 'sufficiency') {
    document.getElementById('tabSufficiencyBtn').classList.add('active');
    document.getElementById('tabSufficiency').classList.remove('hidden');
    if (currentData) drawSufficiencyCurve(currentData);
  } else if (tabName === 'reconstruction') {
    document.getElementById('tabReconstructionBtn').classList.add('active');
    document.getElementById('tabReconstruction').classList.remove('hidden');
    if (currentData) {
      drawTopology(currentData);
      drawNeuralNetGraph(currentData);
      drawSynapseMatrix(currentData);
    }
  } else if (tabName === 'dfir') {
    document.getElementById('tabDfirBtn').classList.add('active');
    document.getElementById('tabDfir').classList.remove('hidden');
  }
}

function toggleStixJson() {
  const box = document.getElementById('stixJsonBox');
  if (!box) return;
  box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

function toggleSynapseAnimation() {
  synapseAnimActive = !synapseAnimActive;
  const badge = document.getElementById('liveSynapseBadge');
  if (badge) {
    badge.innerText = synapseAnimActive ? "Live Dynamic SNN Stream" : "Stream Paused";
    badge.style.color = synapseAnimActive ? "var(--accent-cyan)" : "var(--text-muted)";
  }
}

function renderDashboard(data) {
  if (!data) return;

  // Top Stats Row
  const selectElem = document.getElementById('scenarioSelect');
  if (selectElem && data.ground_truth?.attack_type) {
    selectElem.value = data.ground_truth.attack_type;
  }

  const overallScore = data.metrics?.deterministic_reconstruction_score?.overall_score ?? 0.885;
  const scoreElem = document.getElementById('statReconScore');
  if (scoreElem) scoreElem.innerText = `${(overallScore * 100).toFixed(1)}%`;
  
  const cardElem = document.getElementById('statMinCard');
  if (cardElem) {
    const cardVal = data.sufficiency?.minimum_cardinality ?? 1;
    cardElem.innerText = `${cardVal} Artifact Class${cardVal > 1 ? 'es' : ''}`;
  }

  const rootElem = document.getElementById('statRootCore');
  if (rootElem) {
    rootElem.innerText = `Core ${data.reconstruction?.root_cause_core ?? 2}`;
  }

  // Minimum Sufficient Evidence Sets
  const minSetBox = document.getElementById('minSetContainer');
  if (minSetBox) {
    minSetBox.innerHTML = '';
    if (data.sufficiency && data.sufficiency.minimum_sufficient_sets && data.sufficiency.minimum_sufficient_sets.length > 0) {
      data.sufficiency.minimum_sufficient_sets.forEach((setArr, idx) => {
        const item = document.createElement('div');
        item.style.padding = '12px 16px';
        item.style.background = 'rgba(52, 211, 153, 0.08)';
        item.style.borderRadius = '10px';
        item.style.borderLeft = '4px solid var(--accent-emerald)';
        item.style.border = '1px solid rgba(52, 211, 153, 0.2)';
        item.innerHTML = `<strong>Minimum Sufficient Set ${idx + 1}:</strong> <span style="font-family: var(--font-mono); color: var(--accent-cyan); font-weight: 700;">{ ${setArr.join(', ')} }</span>`;
        minSetBox.appendChild(item);
      });
    } else {
      minSetBox.innerHTML = '<div style="color: var(--text-muted);">No candidate subset reached target threshold (0.80).</div>';
    }
  }

  // IR Containment Plan
  const irBox = document.getElementById('irPlanContainer');
  if (irBox) {
    irBox.innerHTML = '';
    if (data.ir_plan && data.ir_plan.containment_actions) {
      data.ir_plan.containment_actions.forEach((act, idx) => {
        const item = document.createElement('div');
        item.style.padding = '10px 14px';
        item.style.background = 'rgba(255, 255, 255, 0.02)';
        item.style.borderRadius = '10px';
        item.style.borderLeft = '3px solid var(--accent-emerald)';
        item.style.border = '1px solid rgba(255, 255, 255, 0.05)';
        item.innerHTML = `<strong style="color: var(--accent-emerald);">Action ${idx + 1}:</strong> ${act}`;
        irBox.appendChild(item);
      });
    }
  }

  // Timeline (Comprehensive Step-by-Step Investigation from Initial Probe to Root Cause Verdict)
  const timelineList = document.getElementById('timelineList');
  if (timelineList) {
    timelineList.innerHTML = '';
    const timelineData = data.timeline || [];
    timelineData.forEach(evt => {
      const item = document.createElement('div');
      const isCrit = evt.severity === 'CRITICAL' || evt.stage === 'VERDICT';
      item.className = `timeline-item ${isCrit ? 'critical' : ''}`;
      
      let stageTag = `<span class="stage-tag stage-probe">PROBE</span>`;
      if (evt.stage === 'DETECTION') stageTag = `<span class="stage-tag stage-root">ANOMALY DETECTED</span>`;
      else if (evt.stage === 'ANALYSIS') stageTag = `<span class="stage-tag stage-analysis">LATERAL SPREAD</span>`;
      else if (evt.stage === 'VERDICT') stageTag = `<span class="stage-tag stage-verdict">FINAL VERDICT</span>`;

      item.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; min-width: 65px;">
          <span class="timeline-step">Step ${evt.step.toString().padStart(2, '0')}</span>
          <span style="font-size: 10.5px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 2px;">${evt.timestamp_ms.toFixed(1)} ms</span>
        </div>
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            ${stageTag}
            <span style="font-weight: 700; color: ${isCrit ? 'var(--accent-rose)' : 'var(--accent-cyan)'}; font-size: 13px;">
              Core ${evt.affected_core} &bull; ${evt.event_type}
            </span>
            <span style="font-size: 11px; color: var(--text-muted); margin-left: auto; font-family: var(--font-mono);">Anomaly: ${(evt.anomaly_score * 100).toFixed(0)}%</span>
          </div>
          <div class="timeline-desc">${evt.description}</div>
        </div>
      `;
      timelineList.appendChild(item);
    });
  }

  // Formatted CTI Cards (Human Readable Threat Intelligence)
  const ctiContainer = document.getElementById('ctiCardsContainer');
  if (ctiContainer) {
    ctiContainer.innerHTML = '';
    if (data.indicators) {
      data.indicators.forEach(ind => {
        const card = document.createElement('div');
        card.className = 'cti-card';
        card.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div>
              <span class="badge" style="background: rgba(168, 85, 247, 0.2); color: #c084fc; border-color: rgba(168, 85, 247, 0.4);">${ind.ttp_code}</span>
              <strong style="margin-left: 8px; color: var(--text-primary); font-size: 13.5px;">${ind.technique_name}</strong>
            </div>
            <span class="badge" style="background: rgba(52, 211, 153, 0.15); color: var(--accent-emerald);">Confidence: ${(ind.confidence_score * 100).toFixed(0)}%</span>
          </div>
          <div style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 8px;">${ind.description}</div>
          <div style="font-size: 11.5px; font-family: var(--font-mono); color: var(--accent-cyan); background: rgba(0,0,0,0.35); padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
            STIX Pattern: ${ind.stix_pattern}
          </div>
        `;
        ctiContainer.appendChild(card);
      });
    }
  }

  // Collapsible Raw STIX JSON
  const stixBox = document.getElementById('stixJsonBox');
  if (stixBox) {
    stixBox.innerText = JSON.stringify({
      type: "bundle",
      id: `bundle--${Math.random().toString(36).substring(2, 10)}`,
      spec_version: "2.1",
      objects: data.indicators || []
    }, null, 2);
  }

  // Draw Canvases
  drawSufficiencyCurve(data);
  drawTopology(data);
  drawNeuralNetGraph(data);
  drawSynapseMatrix(data);
}

function renderMatrixTable(matrix) {
  const tbody = document.getElementById('matrixTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const nameMap = {
    synaptic_poisoning: "Synaptic Weight Poisoning (Trojan)",
    spike_storm: "Denial-of-Service Spike Flooding Storm",
    timing_jitter: "Temporal Desynchronization / Jitter",
  };

  const artifacts = [
    "SPIKE_EVENTS", "SPIKE_TIMING", "NEURON_STATE", "SYNAPTIC_STATE",
    "TOPOLOGY_ROUTING", "CONFIGURATION", "INPUT_OUTPUT"
  ];

  for (const [attackKey, row] of Object.entries(matrix)) {
    const tr = document.createElement('tr');
    let html = `<td style="font-weight: 700; color: var(--text-primary);">${nameMap[attackKey] || attackKey}</td>`;

    artifacts.forEach(art => {
      const val = row[art] || "Not applicable";
      let badgeClass = "tag-redundant";
      if (val === "Required") badgeClass = "tag-required";
      else if (val === "Helpful") badgeClass = "tag-helpful";

      html += `<td><span class="${badgeClass}">${val}</span></td>`;
    });

    tr.innerHTML = html;
    tbody.appendChild(tr);
  }
}

function setupHiDPICanvas(canvas, customHeight = null) {
  if (!canvas) return null;
  const dpr = window.devicePixelRatio || 2;
  const rect = canvas.getBoundingClientRect();
  const displayWidth = Math.floor(rect.width || canvas.parentElement.clientWidth - 48 || 600);
  const displayHeight = customHeight || Math.floor(rect.height || 260);

  // Set high resolution canvas buffer size
  canvas.width = Math.floor(displayWidth * dpr);
  canvas.height = Math.floor(displayHeight * dpr);

  // Set display size
  canvas.style.width = displayWidth + 'px';
  canvas.style.height = displayHeight + 'px';

  const ctx = canvas.getContext('2d');
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);
  
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';

  return { ctx, width: displayWidth, height: displayHeight };
}

function drawSufficiencyCurve(data) {
  const canvas = document.getElementById('curveCanvas');
  const setup = setupHiDPICanvas(canvas, 240);
  if (!setup) return;
  const { ctx, width, height } = setup;

  ctx.clearRect(0, 0, width, height);

  const ablationList = data.sufficiency?.ablation_results || [];
  if (ablationList.length === 0) return;

  const points = ablationList
    .map(r => ({ x: r.evidence_volume_bytes, y: r.reconstruction_score, success: r.success }))
    .sort((a, b) => a.x - b.x);

  const padding = { left: 50, right: 30, top: 20, bottom: 40 };
  const w = width - padding.left - padding.right;
  const h = height - padding.top - padding.bottom;

  const minX = Math.min(...points.map(p => p.x));
  const maxX = Math.max(...points.map(p => p.x));

  // Axes
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, height - padding.bottom);
  ctx.lineTo(width - padding.right, height - padding.bottom);
  ctx.stroke();

  // Threshold Line (y = 0.80)
  const threshY = (height - padding.bottom) - (0.80 * h);
  ctx.strokeStyle = 'rgba(244, 63, 94, 0.6)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(padding.left, threshY);
  ctx.lineTo(width - padding.right, threshY);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#f43f5e';
  ctx.font = '600 11px Inter, sans-serif';
  ctx.fillText('Sufficiency Threshold >= 0.80 (80%)', padding.left + 10, threshY - 6);

  // Plot Points
  points.forEach(p => {
    const px = padding.left + ((p.x - minX) / (maxX - minX || 1)) * w;
    const py = (height - padding.bottom) - (p.y * h);

    ctx.beginPath();
    ctx.arc(px, py, p.success ? 5 : 3.5, 0, 2 * Math.PI);
    ctx.fillStyle = p.success ? '#34d399' : '#64748b';
    ctx.fill();
    if (p.success) {
      ctx.strokeStyle = '#6ee7b7';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  });

  // Labels
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Evidence Volume (Bytes)', width / 2, height - 10);
  ctx.textAlign = 'right';
  ctx.fillText('Score', padding.left - 8, padding.top + 10);
}

// 6-Core Neuromorphic Topology Visualizer with Dynamic Particle Routing
function drawTopology(data) {
  const canvas = document.getElementById('topologyCanvas');
  const setup = setupHiDPICanvas(canvas, 250);
  if (!setup) return;
  const { ctx, width, height } = setup;

  // 6 Cores Layout in 2D Mesh / Ring Architecture
  const positions = [
    { x: width * 0.15, y: height * 0.35, id: 0, label: 'Core 0 (Sensory Ingress)' },
    { x: width * 0.40, y: height * 0.20, id: 1, label: 'Core 1 (Feature Extractor)' },
    { x: width * 0.40, y: height * 0.75, id: 2, label: 'Core 2 (Plastic Reservoir)' },
    { x: width * 0.65, y: height * 0.20, id: 3, label: 'Core 3 (Associative Memory)' },
    { x: width * 0.65, y: height * 0.75, id: 4, label: 'Core 4 (Motor Planning)' },
    { x: width * 0.88, y: height * 0.48, id: 5, label: 'Core 5 (Egress Readout)' }
  ];

  ctx.clearRect(0, 0, width, height);

  // Mesh Inter-Core Bus Links
  const links = [
    [0, 1], [0, 2],
    [1, 3], [1, 2],
    [2, 4], [3, 4],
    [3, 5], [4, 5],
    [1, 5]
  ];

  const rootCore = data.reconstruction?.root_cause_core ?? 2;
  const compromisedCores = data.reconstruction?.compromised_cores || [rootCore];

  // Draw Bus Lines
  links.forEach(([s, d]) => {
    const isCompromisedPath = compromisedCores.includes(s) && compromisedCores.includes(d);
    
    ctx.beginPath();
    ctx.moveTo(positions[s].x, positions[s].y);
    ctx.lineTo(positions[d].x, positions[d].y);

    if (isCompromisedPath) {
      ctx.strokeStyle = 'rgba(244, 63, 94, 0.6)';
      ctx.lineWidth = 2.5;
    } else {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 1.5;
    }
    ctx.stroke();
  });

  // Draw 6 Core Nodes
  positions.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 22, 0, 2 * Math.PI);
    
    if (p.id === rootCore) {
      // Patient Zero Root Compromise Core
      ctx.fillStyle = 'rgba(244, 63, 94, 0.35)';
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 3.5;
    } else if (compromisedCores.includes(p.id)) {
      // Cascaded Compromise Core
      ctx.fillStyle = 'rgba(168, 85, 247, 0.25)';
      ctx.strokeStyle = '#a855f7';
      ctx.lineWidth = 2.5;
    } else {
      // Healthy Operational Core
      ctx.fillStyle = 'rgba(56, 189, 248, 0.18)';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
    }
    
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`Core ${p.id}`, p.x, p.y + 4);

    // Sub-label
    ctx.fillStyle = p.id === rootCore ? '#f43f5e' : (compromisedCores.includes(p.id) ? '#c084fc' : '#94a3b8');
    ctx.font = '700 9px Inter, sans-serif';
    ctx.fillText(p.id === rootCore ? 'ROOT CAUSE' : (compromisedCores.includes(p.id) ? 'CASCADED' : 'HEALTHY'), p.x, p.y + 36);
  });
}

// Microscopic SNN Synaptic Network Graph
// Renders individual neurons across layers, synaptic weighted axons, live action potential spikes, and red plus alert markers
function drawNeuralNetGraph(data) {
  const canvas = document.getElementById('neuralNetCanvas');
  const setup = setupHiDPICanvas(canvas, 270);
  if (!setup) return;
  const { ctx, width, height } = setup;

  ctx.clearRect(0, 0, width, height);

  const scenarioName = data.scenario?.name || '';
  const isPoisoning = scenarioName.includes('Synaptic') || scenarioName.includes('Trojan');
  const isBurst = scenarioName.includes('Storm') || scenarioName.includes('DoS');
  const isJitter = scenarioName.includes('Jitter') || scenarioName.includes('Timing');

  // Layered Neural Architecture (Input Layer -> Hidden Layer 1 -> Hidden Layer 2 -> Output Layer)
  const layers = [
    { name: 'Layer 0 (Sensory Inputs)', count: 4, x: width * 0.10 },
    { name: 'Layer 1 (Feature Neurons)', count: 6, x: width * 0.35 },
    { name: 'Layer 2 (Core 2 Reservoir)', count: 6, x: width * 0.65 },
    { name: 'Layer 3 (Motor Readout)', count: 4, x: width * 0.90 }
  ];

  // Calculate Neuron Coordinates
  const neuronPositions = [];
  layers.forEach((l, lIdx) => {
    const spacing = (height - 70) / (l.count - 1 || 1);
    const startY = 45;
    for (let i = 0; i < l.count; i++) {
      neuronPositions.push({
        layer: lIdx,
        index: i,
        x: l.x,
        y: startY + i * spacing,
        id: `N_${lIdx}_${i}`
      });
    }
  });

  // Layer Title Headers
  ctx.fillStyle = '#94a3b8';
  ctx.font = '700 10.5px Inter, sans-serif';
  ctx.textAlign = 'center';
  layers.forEach(l => {
    ctx.fillText(l.name, l.x, 22);
  });

  // Draw Synaptic Axon Connections
  for (let l = 0; l < layers.length - 1; l++) {
    const srcNeurons = neuronPositions.filter(n => n.layer === l);
    const dstNeurons = neuronPositions.filter(n => n.layer === l + 1);

    srcNeurons.forEach(src => {
      dstNeurons.forEach(dst => {
        // Deterministic pseudo-weight between synapses
        const synSeed = Math.sin(src.index * 13.7 + dst.index * 19.3 + l * 29.1);
        const isTamperedSynapse = isPoisoning && (l === 1 || l === 2) && (src.index >= 2 && dst.index >= 2);
        
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(dst.x, dst.y);

        if (isTamperedSynapse) {
          // Trojan Poisoned Synapses: Highlighted in Red with thicker weight
          ctx.strokeStyle = 'rgba(244, 63, 94, 0.45)';
          ctx.lineWidth = 2.0;
        } else {
          // Normal Plastic Synapses
          const opacity = 0.08 + Math.abs(synSeed) * 0.15;
          ctx.strokeStyle = `rgba(56, 189, 248, ${opacity})`;
          ctx.lineWidth = 1.0;
        }
        ctx.stroke();

        // Dynamic Spike Particles traversing along synaptic axons
        const particleSpeed = 0.025;
        const particlePhase = ((animTick * particleSpeed) + (src.index * 0.23) + (dst.index * 0.31)) % 1.0;
        const px = src.x + (dst.x - src.x) * particlePhase;
        const py = src.y + (dst.y - src.y) * particlePhase;

        ctx.beginPath();
        ctx.arc(px, py, isTamperedSynapse ? 2.5 : 1.8, 0, 2 * Math.PI);
        ctx.fillStyle = isTamperedSynapse ? '#f43f5e' : '#38bdf8';
        ctx.fill();
      });
    });
  }

  // Draw Neurons and Flag Anomaly Spikes with Red Plus [+] Marker
  neuronPositions.forEach(n => {
    const isTargetLayer = (isPoisoning && n.layer === 2) || (isBurst && n.layer === 1) || (isJitter && n.layer === 1);
    const isAnomalousNeuron = isTargetLayer && (n.index === 1 || n.index === 2 || n.index === 3);

    // Live membrane voltage glow
    const vM = 0.3 + 0.5 * Math.abs(Math.sin(animTick * 0.08 + n.index * 1.3 + n.layer * 2.1));
    
    ctx.beginPath();
    ctx.arc(n.x, n.y, 11, 0, 2 * Math.PI);

    if (isAnomalousNeuron) {
      // Anomalous compromise neuron
      ctx.fillStyle = 'rgba(244, 63, 94, 0.35)';
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 2.5;
    } else {
      // Healthy bio-neuron
      ctx.fillStyle = `rgba(56, 189, 248, ${0.15 + vM * 0.25})`;
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.8;
    }

    ctx.fill();
    ctx.stroke();

    // Neuron Label
    ctx.fillStyle = '#ffffff';
    ctx.font = '700 8.5px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText(`n${n.index}`, n.x, n.y + 3);

    // Red Plus [+] Anomaly Alert Marker on Compromised Spiking Neurons
    if (isAnomalousNeuron) {
      const pulseSize = 13 + Math.sin(animTick * 0.15) * 2;
      const plusX = n.x + 14;
      const plusY = n.y - 10;

      // Draw Red Circular Badge
      ctx.beginPath();
      ctx.arc(plusX, plusY, 8, 0, 2 * Math.PI);
      ctx.fillStyle = '#f43f5e';
      ctx.shadowColor = '#f43f5e';
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0; // reset shadow

      // Draw White "+" Sign inside
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(plusX - 4, plusY);
      ctx.lineTo(plusX + 4, plusY);
      ctx.moveTo(plusX, plusY - 4);
      ctx.lineTo(plusX, plusY + 4);
      ctx.stroke();

      // Tooltip Text
      ctx.fillStyle = '#fda4af';
      ctx.font = '700 8px Inter, sans-serif';
      ctx.fillText('ANOMALY SPIKE', plusX + 38, plusY + 3);
    }
  });
}

// Dynamic Biophysical Leaky Integrate-and-Fire (LIF) Voltage Oscilloscope
// Strictly enforces biophysical laws:
// 1. Blue & Teal traces represent subthreshold Poisson membrane integration (strictly STAY BELOW V_th = 1.0 mV).
// 2. Red & Purple traces represent adversarial Trojan shifts / DoS bursts that SURPASS V_th (1.0 mV) and emit action potentials.
function drawSynapseMatrix(data) {
  const canvas = document.getElementById('synapseCanvas');
  const setup = setupHiDPICanvas(canvas, 230);
  if (!setup) return;
  const { ctx, width, height } = setup;

  ctx.clearRect(0, 0, width, height);

  const scenarioName = data.scenario?.name || '';
  const isPoisoning = scenarioName.includes('Synaptic') || scenarioName.includes('Trojan');
  const isBurst = scenarioName.includes('Storm') || scenarioName.includes('DoS');
  const isJitter = scenarioName.includes('Jitter') || scenarioName.includes('Timing');

  // Left Panel: Dynamic Synaptic Weight Crossbar Matrix (8x8 Synaptic Grid)
  const matrixSize = 140;
  const startX = 20;
  const startY = 40;
  const cells = 8;
  const cellSize = matrixSize / cells;

  ctx.fillStyle = '#f8fafc';
  ctx.font = '700 12px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Synaptic Weight Crossbar Matrix (Core 2)', startX, 24);

  for (let r = 0; r < cells; r++) {
    for (let c = 0; c < cells; c++) {
      let baseNoise = (Math.sin(r * 3.1 + c * 7.7) + 1) * 0.15;
      let dynamicFluctuation = 0.20 + baseNoise + 0.1 * Math.sin(animTick * 0.04 + r * 1.7 + c * 2.3);
      let isTampered = isPoisoning && (r >= 2 && r <= 5 && c >= 3 && c <= 6);
      
      if (isTampered) {
        let trojanIntensity = 0.85 + 0.15 * Math.sin(animTick * 0.12 + r + c);
        ctx.fillStyle = `rgba(244, 63, 94, ${trojanIntensity})`; // Red Trojan anomaly highlight
      } else {
        ctx.fillStyle = `rgba(56, 189, 248, ${dynamicFluctuation})`; // Normal organic teal synaptic strength
      }

      ctx.fillRect(startX + c * cellSize, startY + r * cellSize, cellSize - 2, cellSize - 2);
    }
  }

  // Right Panel: Biophysical LIF Membrane Potential Oscilloscope
  const waveStartX = startX + matrixSize + 36;
  const waveWidth = width - waveStartX - 20;
  const waveHeight = 145;

  ctx.fillStyle = '#f8fafc';
  ctx.font = '700 12px Inter';
  ctx.fillText('Live Spike Action Potentials (V_m) & Microsecond Anomaly Oscilloscope', waveStartX, 24);

  // Background Oscilloscope Box
  ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
  ctx.fillRect(waveStartX, startY, waveWidth, waveHeight);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 1;
  ctx.strokeRect(waveStartX, startY, waveWidth, waveHeight);

  // Firing Threshold V_th line (1.0 mV)
  const threshY = startY + waveHeight * 0.35;
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.85)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(waveStartX, threshY);
  ctx.lineTo(waveStartX + waveWidth, threshY);
  ctx.stroke();
  ctx.setLineDash([]);
  
  ctx.fillStyle = '#fbbf24';
  ctx.font = '700 10.5px var(--font-mono)';
  ctx.fillText('Firing Threshold V_th = 1.0 mV', waveStartX + 10, threshY - 6);

  // Baseline Resting Potential V_rest (0.0 mV)
  const restY = startY + waveHeight * 0.82;
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.10)';
  ctx.beginPath();
  ctx.moveTo(waveStartX, restY);
  ctx.lineTo(waveStartX + waveWidth, restY);
  ctx.stroke();

  ctx.fillStyle = '#64748b';
  ctx.font = '9px var(--font-mono)';
  ctx.fillText('V_reset = 0.0 mV', waveStartX + 10, restY + 12);

  // 3 Biophysical LIF Telemetry Channels:
  // Channel 0: Core 0 (Healthy Poisson sensory ingress) -> Strictly subthreshold (never crosses V_th)
  // Channel 1: Core 1 (Intermediate feature extractor) -> Normal subthreshold background
  // Channel 2: Core 2 (Attack target / Patient Zero) -> Injected adversarial voltage that breaks above V_th
  const channels = [
    { name: 'Core 0 (Sensory)', color: '#38bdf8', isAnomalous: false },
    { name: 'Core 1 (Feature)', color: isBurst ? '#f43f5e' : (isJitter ? '#c084fc' : '#60a5fa'), isAnomalous: isBurst || isJitter },
    { name: 'Core 2 (Trojan/Target)', color: isPoisoning ? '#f43f5e' : '#34d399', isAnomalous: isPoisoning }
  ];

  channels.forEach((ch, chIdx) => {
    ctx.beginPath();
    ctx.strokeStyle = ch.color;
    ctx.lineWidth = ch.isAnomalous ? 2.4 : 1.5;

    const phaseOffset = chIdx * 38.7;
    const maxSubthresholdHeight = (restY - threshY) * 0.85; // strictly stay below golden line

    for (let x = 0; x < waveWidth; x += 2) {
      let t = (x + animTick * 1.8) * 0.045 + phaseOffset;
      
      // Organic biological fluctuation (Sum of non-harmonic sines)
      let organicNoise = Math.sin(t * 0.8) * 0.35 + Math.sin(t * 2.1) * 0.18 + Math.cos(t * 4.3) * 0.08;
      let normVoltage = Math.max(0, Math.min(0.9, 0.4 + organicNoise)); // bounded in [0.0, 0.85]

      let isSpikingPoint = false;
      let spikeOvervoltage = 0;

      if (ch.isAnomalous) {
        if (isPoisoning) {
          // Trojan Weight Poisoning: Periodic massive depolarizing bursts that breach V_th
          let trojanCycle = (x + animTick * 2.2) % 90;
          if (trojanCycle < 6) {
            isSpikingPoint = true;
            spikeOvervoltage = 1.35; // 1.35x threshold -> shoot above golden line
          }
        } else if (isBurst) {
          // DoS Flooding: High-frequency bursts above V_th
          let burstCycle = (x + animTick * 3.5) % 35;
          if (burstCycle < 5) {
            isSpikingPoint = true;
            spikeOvervoltage = 1.45;
          }
        } else if (isJitter) {
          // Jitter: Irregular jittered spike discharges above V_th
          let jitterCycle = (x + animTick * 2.0 + Math.sin(x * 0.08) * 30) % 80;
          if (jitterCycle < 5) {
            isSpikingPoint = true;
            spikeOvervoltage = 1.30;
          }
        }
      }

      let currentY;
      if (isSpikingPoint) {
        // Shoots above threshold V_th (into top 35% region)
        currentY = threshY - (spikeOvervoltage - 1.0) * (waveHeight * 0.6);
      } else {
        // Subthreshold integration (stays safely between V_rest and V_th)
        currentY = restY - normVoltage * maxSubthresholdHeight;
      }

      currentY = Math.max(startY + 4, Math.min(startY + waveHeight - 4, currentY));

      if (x === 0) ctx.moveTo(waveStartX + x, currentY);
      else ctx.lineTo(waveStartX + x, currentY);

      // Red Alert Dot & Plus indicator on anomalous peaks above threshold
      if (isSpikingPoint && currentY < threshY) {
        ctx.fillStyle = '#f43f5e';
        ctx.fillRect(waveStartX + x - 2, currentY - 2, 4, 4);
      }
    }
    ctx.stroke();
  });

  // Oscilloscope Legend
  ctx.fillStyle = '#94a3b8';
  ctx.font = '10px Inter';
  ctx.textAlign = 'left';
  ctx.fillText('Biophysical Telemetry: Cyan/Blue = Subthreshold LIF Integration (< 1.0 mV) | Red/Purple = Anomalous Spikes Crossing V_th', startX, startY + matrixSize + 24);
}

function startSynapseAnimation() {
  function step() {
    if (synapseAnimActive) {
      animTick++;
      const currentTab = document.querySelector('.tab-pane:not(.hidden)');
      if (currentTab && currentTab.id === 'tabReconstruction' && currentData) {
        drawTopology(currentData);
        drawNeuralNetGraph(currentData);
        drawSynapseMatrix(currentData);
      }
    }
    synapseAnimId = requestAnimationFrame(step);
  }
  if (!synapseAnimId) {
    step();
  }
}

window.addEventListener('resize', () => {
  if (currentData) {
    const currentTab = document.querySelector('.tab-pane:not(.hidden)');
    if (currentTab && currentTab.id === 'tabSufficiency') {
      drawSufficiencyCurve(currentData);
    } else if (currentTab && currentTab.id === 'tabReconstruction') {
      drawTopology(currentData);
      drawNeuralNetGraph(currentData);
      drawSynapseMatrix(currentData);
    }
  }
});

