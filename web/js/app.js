// Dashboard UI Controller, Sufficiency Curve Renderer & Canvas Visualizer

let currentData = null;
let currentMatrixData = null;

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [dataRes, matrixRes] = await Promise.all([
      fetch('data.json').then(r => r.ok ? r.json() : null),
      fetch('matrix.json').then(r => r.ok ? r.json() : null),
    ]);

    currentData = dataRes || getDemoData();
    currentMatrixData = matrixRes;

    renderDashboard(currentData);
    if (currentMatrixData) {
      renderMatrixTable(currentMatrixData.matrix);
    }
  } catch (err) {
    console.warn('Using default demo state:', err);
    currentData = getDemoData();
    renderDashboard(currentData);
  }
});

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
    if (currentData) drawTopology(currentData);
  } else if (tabName === 'dfir') {
    document.getElementById('tabDfirBtn').classList.add('active');
    document.getElementById('tabDfir').classList.remove('hidden');
  }
}

function renderDashboard(data) {
  // Top Stats
  document.getElementById('statScenario').innerText = data.scenario?.name || 'Synaptic Poisoning';
  const overallScore = data.metrics?.deterministic_reconstruction_score?.overall_score ?? 0.835;
  document.getElementById('statReconScore').innerText = `${(overallScore * 100).toFixed(1)}%`;
  document.getElementById('statMinCard').innerText = data.sufficiency?.minimum_cardinality ? `${data.sufficiency.minimum_cardinality} Artifact(s)` : 'N/A';
  document.getElementById('statRootCore').innerText = `Core ${data.reconstruction?.root_cause_core ?? 2}`;

  // Render Min Sufficient Sets
  const minSetBox = document.getElementById('minSetContainer');
  minSetBox.innerHTML = '';
  if (data.sufficiency && data.sufficiency.minimum_sufficient_sets && data.sufficiency.minimum_sufficient_sets.length > 0) {
    data.sufficiency.minimum_sufficient_sets.forEach((setArr, idx) => {
      const item = document.createElement('div');
      item.style.padding = '10px 14px';
      item.style.background = 'rgba(16, 185, 129, 0.08)';
      item.style.borderRadius = '8px';
      item.style.borderLeft = '3px solid var(--accent-emerald)';
      item.innerHTML = `<strong>Minimum Sufficient Set ${idx + 1}:</strong> <span style="font-family: var(--font-mono); color: var(--accent-cyan);">{ ${setArr.join(', ')} }</span>`;
      minSetBox.appendChild(item);
    });
  } else {
    minSetBox.innerHTML = '<div style="color: var(--text-muted);">No candidate subset reached target threshold (0.80).</div>';
  }

  // IR Plan
  const irBox = document.getElementById('irPlanContainer');
  irBox.innerHTML = '';
  if (data.ir_plan && data.ir_plan.containment_actions) {
    data.ir_plan.containment_actions.forEach((act, idx) => {
      const item = document.createElement('div');
      item.style.padding = '8px 12px';
      item.style.background = 'rgba(255, 255, 255, 0.03)';
      item.style.borderRadius = '8px';
      item.style.borderLeft = '3px solid var(--accent-emerald)';
      item.innerHTML = `<strong>Action ${idx + 1}:</strong> ${act}`;
      irBox.appendChild(item);
    });
  }

  // Timeline
  const timelineList = document.getElementById('timelineList');
  timelineList.innerHTML = '';
  if (data.timeline) {
    data.timeline.forEach(evt => {
      const item = document.createElement('div');
      item.className = `timeline-item ${evt.severity === 'CRITICAL' ? 'critical' : ''}`;
      item.innerHTML = `
        <span class="timeline-step">Step ${evt.step}</span>
        <div>
          <div style="font-weight: 600; color: ${evt.severity === 'CRITICAL' ? 'var(--accent-rose)' : 'var(--accent-cyan)'}">
            [${evt.event_type}] Core ${evt.affected_core} (Score: ${evt.anomaly_score.toFixed(2)})
          </div>
          <div class="timeline-desc">${evt.description}</div>
        </div>
      `;
      timelineList.appendChild(item);
    });
  }

  // CTI & STIX
  const indList = document.getElementById('indicatorList');
  indList.innerHTML = '';
  if (data.indicators) {
    data.indicators.forEach(ind => {
      const tag = document.createElement('div');
      tag.style.marginBottom = '6px';
      tag.innerHTML = `<span class="badge" style="background: rgba(139, 92, 246, 0.2); color: #c084fc; border-color: #8b5cf6;">${ind.ttp_code}</span> <strong>${ind.technique_name}</strong> (Confidence: ${(ind.confidence_score * 100).toFixed(0)}%)`;
      indList.appendChild(tag);
    });
  }

  const stixBox = document.getElementById('stixJsonBox');
  stixBox.innerText = JSON.stringify(data.indicators || {}, null, 2);

  // Draw Sufficiency Curve
  drawSufficiencyCurve(data);
  // Draw Topology
  drawTopology(data);
}

function renderMatrixTable(matrix) {
  const tbody = document.getElementById('matrixTableBody');
  tbody.innerHTML = '';

  const nameMap = {
    synaptic_poisoning: "Synaptic Weight Poisoning / Trojan",
    spike_storm: "Denial-of-Service Spike Flooding Storm",
    timing_jitter: "Temporal Desynchronization / Jitter Attack",
  };

  const artifacts = [
    "SPIKE_EVENTS", "SPIKE_TIMING", "NEURON_STATE", "SYNAPTIC_STATE",
    "TOPOLOGY_ROUTING", "CONFIGURATION", "INPUT_OUTPUT"
  ];

  for (const [attackKey, row] of Object.entries(matrix)) {
    const tr = document.createElement('tr');
    let html = `<td style="font-weight: 600;">${nameMap[attackKey] || attackKey}</td>`;

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

function drawSufficiencyCurve(data) {
  const canvas = document.getElementById('curveCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth - 40;
  canvas.height = 240;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const ablationList = data.sufficiency?.ablation_results || [];
  if (ablationList.length === 0) return;

  // Sort points by volume
  const points = ablationList
    .map(r => ({ x: r.evidence_volume_bytes, y: r.reconstruction_score, success: r.success }))
    .sort((a, b) => a.x - b.x);

  const padding = { left: 50, right: 30, top: 20, bottom: 40 };
  const w = canvas.width - padding.left - padding.right;
  const h = canvas.height - padding.top - padding.bottom;

  const minX = Math.min(...points.map(p => p.x));
  const maxX = Math.max(...points.map(p => p.x));

  // Axes
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, canvas.height - padding.bottom);
  ctx.lineTo(canvas.width - padding.right, canvas.height - padding.bottom);
  ctx.stroke();

  // Threshold Line (y = 0.80)
  const threshY = (canvas.height - padding.bottom) - (0.80 * h);
  ctx.strokeStyle = 'rgba(244, 63, 94, 0.5)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(padding.left, threshY);
  ctx.lineTo(canvas.width - padding.right, threshY);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#f43f5e';
  ctx.font = '10px Inter';
  ctx.fillText('Threshold &ge; 0.80', padding.left + 10, threshY - 6);

  // Plot Data Points
  points.forEach(p => {
    const px = padding.left + ((p.x - minX) / (maxX - minX || 1)) * w;
    const py = (canvas.height - padding.bottom) - (p.y * h);

    ctx.beginPath();
    ctx.arc(px, py, p.success ? 4 : 2.5, 0, 2 * Math.PI);
    ctx.fillStyle = p.success ? '#10b981' : '#6b7280';
    ctx.fill();
    if (p.success) {
      ctx.strokeStyle = '#34d399';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  });

  // Labels
  ctx.fillStyle = '#9ca3af';
  ctx.font = '11px Inter';
  ctx.textAlign = 'center';
  ctx.fillText('Evidence Volume (Bytes)', canvas.width / 2, canvas.height - 10);
  ctx.textAlign = 'right';
  ctx.fillText('Score', padding.left - 8, padding.top + 10);
}

function drawTopology(data) {
  const canvas = document.getElementById('topologyCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth - 40;
  canvas.height = 240;

  const positions = [
    { x: canvas.width * 0.2, y: canvas.height * 0.35, id: 0, label: 'Core 0 (Sensory)' },
    { x: canvas.width * 0.45, y: canvas.height * 0.2, id: 1, label: 'Core 1 (Intermediate)' },
    { x: canvas.width * 0.45, y: canvas.height * 0.7, id: 2, label: 'Core 2 (Target/Trojan)' },
    { x: canvas.width * 0.8, y: canvas.height * 0.5, id: 3, label: 'Core 3 (Motor Output)' }
  ];

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw Bus lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.lineWidth = 2;
  const links = [[0, 1], [0, 2], [1, 3], [2, 3], [1, 2]];
  links.forEach(([s, d]) => {
    ctx.beginPath();
    ctx.moveTo(positions[s].x, positions[s].y);
    ctx.lineTo(positions[d].x, positions[d].y);
    ctx.stroke();
  });

  // Draw Cores
  const rootCore = data.reconstruction?.root_cause_core ?? 2;
  positions.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 24, 0, 2 * Math.PI);
    
    if (p.id === rootCore) {
      ctx.fillStyle = 'rgba(244, 63, 94, 0.3)';
      ctx.strokeStyle = '#f43f5e';
    } else {
      ctx.fillStyle = 'rgba(6, 182, 212, 0.2)';
      ctx.strokeStyle = '#06b6d4';
    }
    ctx.lineWidth = 3;
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#f9fafb';
    ctx.font = '11px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(`Core ${p.id}`, p.x, p.y + 4);
  });
}

function getDemoData() {
  return {
    scenario: { name: "Synaptic Weight Poisoning (Trojan)" },
    reconstruction: { root_cause_core: 2 },
    metrics: { deterministic_reconstruction_score: { overall_score: 0.835 } },
    sufficiency: {
      threshold: 0.80,
      minimum_cardinality: 1,
      minimum_sufficient_sets: [["SYNAPTIC_STATE"]],
      ablation_results: [
        { evidence_volume_bytes: 88323, reconstruction_score: 0.0, success: false },
        { evidence_volume_bytes: 3106305, reconstruction_score: 0.835, success: true }
      ]
    },
    timeline: [
      { step: 30, severity: "CRITICAL", event_type: "SYNAPSE_ANOMALY", affected_core: 2, anomaly_score: 0.94, description: "Synaptic weight deviation detected on Core 2 (max delta: 2.800)" }
    ],
    ir_plan: {
      severity: "CRITICAL",
      containment_actions: [
        "Trigger hardware interrupt: Isolate Core 2 from inter-core routing bus.",
        "Initiate non-volatile SRAM backup and cryptographic seal of corrupted synaptic registers."
      ]
    },
    indicators: [
      { ttp_code: "T1565.001", technique_name: "Stored Data Manipulation: Synaptic Weight Tampering", confidence_score: 0.95 }
    ]
  };
}
