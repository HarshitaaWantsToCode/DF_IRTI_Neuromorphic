"""
Generator for NeuroForensics Comprehensive Architecture, FAQ, and Guide PDF.
Answers:
1. Spikes to Logs pipeline (how spike events become forensic containers and timeline logs)
2. User Input & Stimulus encoding in SNNs (Poisson encoding, sensory channels, injection)
3. Lava Neuromorphic Simulation framework integration & execution model
4. What the website / dashboard actually represents and demonstrates
5. Neuromorphic Spikes fundamentals & SNN security / DFIR concepts
"""
import os
import sys
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Header on pages 2+
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor('#0F172A'))
            self.drawString(54, 750, "NEUROFORENSICS: TECHNICAL GUIDE & ARCHITECTURAL FAQ")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor('#64748B'))
            self.drawRightString(558, 750, "Spikes to Logs | User Input | Lava | SNN Forensics")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)

        # Footer on all pages
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#64748B'))
        self.drawString(54, 36, "NeuroForensics Research Project | Digital Forensics & Incident Response for Neuromorphic Systems")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.75)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def build_faq_pdf(output_filename="NeuroForensics_Technical_Architecture_and_FAQ.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom palette
    NAVY = colors.HexColor('#0F172A')
    CYAN = colors.HexColor('#0284C7')
    DARK_BLUE = colors.HexColor('#1E293B')
    LIGHT_BG = colors.HexColor('#F8FAFC')
    BORDER_COLOR = colors.HexColor('#E2E8F0')
    MUTED = colors.HexColor('#64748B')
    ACCENT_EMERALD = colors.HexColor('#059669')
    ACCENT_AMBER = colors.HexColor('#D97706')

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=NAVY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=CYAN,
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=MUTED
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=DARK_BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_BLUE,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=DARK_BLUE,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=NAVY
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_body = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=DARK_BLUE
    )

    story = []

    # ==================== COVER / TITLE SECTION ====================
    story.append(Paragraph("NeuroForensics Technical Guide", title_style))
    story.append(Paragraph("From Spikes to Forensic Logs, Lava SNN Simulation, User Stimuli, & System Architecture", subtitle_style))
    story.append(Paragraph("<b>Author:</b> DF+IRTI Research Project | <b>Classification:</b> Research Reference & FAQ Guide | <b>Framework:</b> NeuroForensics SNN DFIR", meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CYAN, spaceAfter=14))

    # Executive Overview Box
    exec_text = (
        "<b>Executive Summary:</b> Neuromorphic systems compute using asynchronous, event-driven action potentials (spikes) "
        "rather than synchronous matrix multiplications. This document clarifies the exact end-to-end pipeline: how raw bio-inspired "
        "spikes are captured and converted into immutable digital forensic logs, how external sensory user input is fed into the network, "
        "how Intel's Lava neuromorphic framework fits into this architecture, and what the accompanying interactive research dashboard presents."
    )
    exec_table = Table([[Paragraph(exec_text, callout_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, CYAN),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 14))

    # ==================== QUESTION 1: WHAT ARE SPIKES? ====================
    story.append(Paragraph("1. What Are Spikes in Neuromorphic Systems?", h1_style))
    story.append(Paragraph(
        "In biological brains and Spiking Neural Networks (SNNs), neurons do not continuously broadcast continuous floating-point activations. "
        "Instead, a neuron integrates incoming electrical currents over time into an internal state called its <b>membrane potential</b> (<i>V_m</i>). "
        "When this potential crosses a critical threshold (<i>V_th</i>), the neuron fires an instantaneous, discrete electrical pulse called an <b>action potential</b> or <b>spike</b> (represented mathematically as a binary event: 1 = fired, 0 = silent). "
        "Immediately after firing, the membrane potential is reset, and the neuron enters a brief refractory period.",
        body_style
    ))
    story.append(Paragraph("<b>Core Properties of Spikes:</b>", h2_style))
    story.append(Paragraph("• <b>Sparsity:</b> 90–99% of neurons are silent at any discrete millisecond, consuming virtually zero static dynamic power.", bullet_style))
    story.append(Paragraph("• <b>Asynchronous Timing:</b> Information is encoded in <i>when</i> spikes occur (temporal phase, latency, inter-spike intervals), not just overall firing rates.", bullet_style))
    story.append(Paragraph("• <b>Address Event Representation (AER):</b> When transmitted over hardware routing buses, spikes are packaged as tuples containing the source core ID, source neuron ID, and timestamp.", bullet_style))
    story.append(Spacer(1, 10))

    # ==================== QUESTION 2: SPIKES TO LOGS ====================
    story.append(Paragraph("2. How Do We Get from Spikes to Forensic Logs?", h1_style))
    story.append(Paragraph(
        "In conventional IT, servers generate syslog or SIEM text logs. In neuromorphic hardware (or SNN software simulations), "
        "spikes are fleeting microsecond voltage changes. To perform digital forensics and incident response (DFIR), "
        "NeuroForensics implements an <b>Acquisition and Serialization Pipeline</b>:",
        body_style
    ))

    # Pipeline Steps Table
    pipeline_data = [
        [Paragraph("Pipeline Stage", table_header), Paragraph("Mechanism & Processing", table_header), Paragraph("Forensic Output Artifact", table_header)],
        [
            Paragraph("<b>1. Spike Tap & Probe</b>", table_body),
            Paragraph("Non-intrusive probe attached to the SNN inter-core routing fabric intercepts Address-Event-Representation (AER) packets.", table_body),
            Paragraph("Raw discrete events: <code>(core_src, neuron_idx, step, timestamp_ms)</code>", table_body)
        ],
        [
            Paragraph("<b>2. State Snapshotting</b>", table_body),
            Paragraph("Periodic and anomaly-triggered state acquisition records membrane voltages (<i>V_m</i>), synaptic weight matrices (<i>W</i>), and refractory counters.", table_body),
            Paragraph("Volatile memory vectors (<code>NEURON_STATE</code>, <code>SYNAPTIC_STATE</code>)", table_body)
        ],
        [
            Paragraph("<b>3. Normalization & Log Structuring</b>", table_body),
            Paragraph("The acquisition engine serializes events into standardized, structured JSON / binary log streams with causal step counters.", table_body),
            Paragraph("Standardized forensic log entries with high-resolution timestamps", table_body)
        ],
        [
            Paragraph("<b>4. Cryptographic Sealing</b>", table_body),
            Paragraph("Evidence is packaged into sealed <code>.nfd</code> (NeuroForensics Data) containers. Each block is hashed with SHA-256 and anchored in a Merkle Tree.", table_body),
            Paragraph("Tamper-evident forensic archive with verifiable Chain of Custody", table_body)
        ],
    ]
    t_pipe = Table(pipeline_data, colWidths=[120, 240, 144])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 12))

    # ==================== QUESTION 3: USER INPUT & SENSORY STIMULI ====================
    story.append(Paragraph("3. How Is User Input / External Data Fed into SNNs?", h1_style))
    story.append(Paragraph(
        "Standard machine learning networks accept normalized matrices of continuous pixel values or token embeddings directly. "
        "Because SNN neurons only process discrete electrical pulses over time, user input must be <b>rate-coded or temporally encoded</b> into spike trains:",
        body_style
    ))
    story.append(Paragraph("• <b>Poisson Rate Encoding:</b> A continuous user input value (e.g., audio sensor level, pixel intensity between 0.0 and 1.0) is converted into a stochastic spike train where the firing probability per millisecond is proportional to the input magnitude.", bullet_style))
    story.append(Paragraph("• <b>Direct Event Sensors (DVS / Neuromorphic Audio):</b> Event-based vision cameras (silicon retinas) output asynchronous per-pixel contrast-change spikes directly as user/environment input without needing frame buffers.", bullet_style))
    story.append(Paragraph("• <b>In the NeuroForensics Pipeline:</b> Input channels (<code>INPUT_OUTPUT</code> artifact class) represent the sensory spike stream entering Core 0. Attacker-controlled malicious input injections or DoS spike bursts enter through these designated sensory stimulus channels.", bullet_style))
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ==================== QUESTION 4: HOW TO USE LAVA SIMULATION ====================
    story.append(Paragraph("4. How Lava Neuromorphic Simulation Fits into the Architecture", h1_style))
    story.append(Paragraph(
        "<b>Lava</b> is an open-source, hardware-agnostic neuromorphic computing framework developed by Intel. "
        "It provides modular software abstractions (Processes, Ports, and Channels) that execute seamlessly on both conventional CPUs/GPUs and physical neuromorphic hardware (e.g., Intel Loihi 2).",
        body_style
    ))

    story.append(Paragraph("<b>How Lava Is Structured & How NeuroForensics Integrates It:</b>", h2_style))
    story.append(Paragraph("• <b>Lava Processes & SubProcess Hierarchy:</b> In Lava, every SNN layer or neuromorphic core is modeled as an independent <code>AbstractProcess</code> with incoming and outgoing <code>InPort</code> / <code>OutPort</code> connections. Synaptic connections use <code>Dense</code> or <code>Sparse</code> connection processes.", bullet_style))
    story.append(Paragraph("• <b>Execution Model:</b> Lava's synchronous execution runtime steps the network forward across time-steps. At each step, neurons receive input currents, update potentials, fire spikes across ports, and decay.", bullet_style))
    story.append(Paragraph("• <b>Forensic Tap Integration:</b> In this project, NeuroForensics provides a native multi-core LIF backend simulator and defines the architectural interface for attaching forensic probes directly to Lava's channel monitors (<code>VarMonitor</code> and <code>PortMonitor</code>). This allows researchers to capture live spike trains and state matrices without disrupting execution speed.", bullet_style))
    story.append(Paragraph("• <b>Attack Simulation in Lava:</b> Attacks like synaptic weight poisoning are injected by manipulating weight parameters (<code>process.weights.set(...)</code>) or sending out-of-band high-frequency spike trains into specific input ports during configured time-windows.", bullet_style))
    story.append(Spacer(1, 10))

    # Lava Architecture Comparison Table
    lava_comp_data = [
        [Paragraph("Component", table_header), Paragraph("Lava Framework Concept", table_header), Paragraph("NeuroForensics Forensic Implementation", table_header)],
        [
            Paragraph("<b>Core / Neurons</b>", table_body),
            Paragraph("<code>LIF</code> / <code>Dense</code> Processes with state variables (<code>v</code>, <code>u</code>)", table_body),
            Paragraph("Multi-core LIF Network with <code>NEURON_STATE</code> acquisition", table_body)
        ],
        [
            Paragraph("<b>Inter-Core Fabric</b>", table_body),
            Paragraph("<code>OutPort</code> &harr; <code>InPort</code> message passing channels", table_body),
            Paragraph("Ring-bus routing topology with <code>SPIKE_EVENTS</code> probing", table_body)
        ],
        [
            Paragraph("<b>Sensory Stimulus</b>", table_body),
            Paragraph("<code>IO.DataLoader</code> / <code>ArrayProcess</code> spike generators", table_body),
            Paragraph("Poisson input stimulus generator (<code>INPUT_OUTPUT</code> artifact)", table_body)
        ],
        [
            Paragraph("<b>Forensics & DFIR</b>", table_body),
            Paragraph("<code>VarMonitor</code> (passive research telemetry)", table_body),
            Paragraph("Cryptographic <code>.nfd</code> Evidence Container & Ablation Engine", table_body)
        ]
    ]
    t_lava = Table(lava_comp_data, colWidths=[110, 194, 200])
    t_lava.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_lava)
    story.append(Spacer(1, 12))

    # ==================== QUESTION 5: WHAT IS THE WEBSITE ABOUT? ====================
    story.append(Paragraph("5. What Is the Website / Dashboard Actually About?", h1_style))
    story.append(Paragraph(
        "The web dashboard (launched via <code>python main.py serve-dashboard</code>) is the <b>Interactive DFIR & Research Intelligence Console</b> for neuromorphic cybersecurity investigations. It solves a crucial question in digital forensics: <i>'What is the minimum evidence required to prove an attack on an SNN without recording terabytes of unnecessary telemetry?'</i>",
        body_style
    ))

    story.append(Paragraph("<b>The Dashboard Features 3 Primary Modules:</b>", h2_style))
    story.append(Paragraph("<b>1. Evidence Sufficiency & Ablation Hub:</b> Displays empirical curves of Reconstruction Score vs. Evidence Volume (in bytes). It proves mathematically which artifact combinations achieve $\\ge 80\\%$ forensic accuracy with minimum storage overhead.", bullet_style))
    story.append(Paragraph("<b>2. Multi-Core SNN Attack Reconstruction & Topology:</b> Shows an interactive graph of the 4 neuromorphic cores (Core 0 to Core 3). It visualizes root-cause attack localization, cascading compromise blast radius, and chronological incident response timelines.", bullet_style))
    story.append(Paragraph("<b>3. DFIR Playbook & CTI (Threat Intelligence):</b> Provides step-by-step incident response playbooks for neuromorphic threats (Synaptic Weight Poisoning, DoS Spike Flooding, Timing Jitter), complete with SHA-256 Merkle root verification for court-admissible chain of custody.", bullet_style))
    story.append(Spacer(1, 14))

    # Summary Callout Table
    summary_text = (
        "<b>Key Takeaway for Researchers & Engineers:</b><br/>"
        "1. <b>Spikes</b> are discrete, asynchronous microsecond events communicating neuron firing.<br/>"
        "2. <b>Forensic Logs</b> capture spikes and membrane states into tamper-proof <code>.nfd</code> containers.<br/>"
        "3. <b>User Input</b> is Poisson rate-encoded before reaching the input cores.<br/>"
        "4. <b>Lava</b> provides the process-based computing foundation for deploying SNNs onto neuromorphic chips like Loihi 2.<br/>"
        "5. <b>The Web Dashboard</b> visualizes evidence sufficiency ablation, attack localization, and DFIR response playbooks."
    )
    sum_table = Table([[Paragraph(summary_text, body_style)]], colWidths=[504])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LINELEFT', (0, 0), (0, -1), 3.5, ACCENT_EMERALD),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(sum_table)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated: {output_filename}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "NeuroForensics_Technical_Architecture_and_FAQ.pdf"
    build_faq_pdf(out_file)
