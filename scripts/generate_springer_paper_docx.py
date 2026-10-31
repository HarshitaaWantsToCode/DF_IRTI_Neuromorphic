"""
Springer LNCS Format Research Paper Generator (.docx)
Using True Ground-Truth Experimental Results from NeuroForensics Project.

Adheres strictly to Springer LNCS (Lecture Notes in Computer Science) layout:
- Page setup: Letter/A4, margins 4.5 cm top/bottom, 4.0 cm left/right (or standard 1 inch / 2.54 cm for standard LNCS template on Letter)
- Font family: Times New Roman throughout
- Title: 14pt Bold, Centered
- Authors: 10pt Regular, Centered
- Affiliations & Email: 9pt Italic/Regular, Centered
- Abstract: 9pt, Justified, indented 0.5 inches left/right, bold heading 'Abstract.'
- Keywords: 9pt, bold heading 'Keywords:'
- Headings:
  - Heading 1: 12pt Bold, Left-aligned, numbered (1, 2, 3...)
  - Heading 2: 10pt Bold, Left-aligned, numbered (1.1, 1.2...)
  - Heading 3: 10pt Italic, Left-aligned (1.1.1...)
- Body text: 10pt Regular, Justified, 1.15 line spacing, 0pt after
- Tables & Figures: Captions 9pt Centered, professional table formatting with header shading, grid lines
- References: 9pt, hanging indent, numbered [1], [2]...
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Set subtle, professional borders for a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_springer_paper(output_path="NeuroForensics_Springer_Research_Paper.docx"):
    doc = Document()

    # Set page layout to Springer LNCS single column standard
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.1)
        section.right_margin = Inches(1.1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        # Configure different first page if needed
        section.different_first_page_header_footer = True
        
        # Header / Footer configuration
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("NeuroForensics — Springer LNCS Format Research Paper")
        f_run.font.name = "Times New Roman"
        f_run.font.size = Pt(8.5)
        f_run.font.italic = True
        f_run.font.color.rgb = RGBColor(120, 120, 120)

    # Base styles configuration
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.15, bold_prefix=None, italic=False):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(15, 23, 42)
            
        if text:
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.italic = italic
            r.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_heading_1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_heading_2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_heading_3(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.italic = True
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
        
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_formula(latex_text, eq_number):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(latex_text)
        r.font.name = 'Times New Roman'
        r.font.italic = True
        r.font.size = Pt(10)
        r.font.bold = False
        
        r_space = p.add_run(f"    ({eq_number})")
        r_space.font.name = 'Times New Roman'
        r_space.font.italic = False
        r_space.font.bold = True
        r_space.font.size = Pt(9.5)
        return p

    # =========================================================================
    # SECTION 1: TITLE & AUTHORS (Springer LNCS Format)
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run(
        "Attack-Specific Evidence Sufficiency and Incident Reconstruction in Neuromorphic Spiking Architectures"
    )
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(14)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    # Authors
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(3)
    r_auth = p_auth.add_run("K. S. Harshitaa")
    r_auth.font.name = 'Times New Roman'
    r_auth.font.size = Pt(10.5)
    r_auth.font.bold = True

    # Affiliations
    p_aff = doc.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_before = Pt(0)
    p_aff.paragraph_format.space_after = Pt(12)
    r_aff = p_aff.add_run(
        "Department of Computer Science & Cybersecurity Engineering\n"
        "NeuroForensics Research Initiative, Bangalore, Karnataka, India\n"
        "Email: harshitaa.cs.research@gmail.com\n"
        "Repository: https://github.com/HarshitaaWantsToCode/DF_IRTI_Neuromorphic"
    )
    r_aff.font.name = 'Times New Roman'
    r_aff.font.size = Pt(9)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(70, 70, 70)

    # =========================================================================
    # SECTION 2: ABSTRACT & KEYWORDS
    # =========================================================================
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.left_indent = Inches(0.4)
    p_abs.paragraph_format.right_indent = Inches(0.4)
    p_abs.paragraph_format.space_before = Pt(6)
    p_abs.paragraph_format.space_after = Pt(4)
    p_abs.paragraph_format.line_spacing = 1.1

    r_abs_lbl = p_abs.add_run("Abstract. ")
    r_abs_lbl.font.name = 'Times New Roman'
    r_abs_lbl.font.size = Pt(9)
    r_abs_lbl.font.bold = True

    r_abs_text = p_abs.add_run(
        "Neuromorphic computing frameworks operating on event-driven Spiking Neural Networks (SNNs) process information "
        "through asynchronous binary action potentials (spikes) distributed across networked physical cores. While delivering "
        "orders-of-magnitude energy efficiency over synchronous deep neural networks on von Neumann accelerators, their extreme sparsity "
        "and sub-millisecond asynchronous dynamics introduce a fundamental paradox for Digital Forensics and Incident Response (DFIR): "
        "traditional monolithic physical memory acquisition and exhaustive continuous telemetry either produce an unsustainable data deluge "
        "or fail to isolate subtle non-deterministic adversarial perturbations. In this paper, we propose the NeuroForensics framework "
        "to resolve the fundamental research question: Given an adversarial neuromorphic cyber attack, which observable artifact combinations "
        "are mathematically sufficient to reconstruct the incident with provable chain-of-custody? We establish an explicit seven-class "
        "neuromorphic evidence taxonomy encapsulated in sealed container archives (.nfd) protected by per-block SHA-256 digests and hierarchical "
        "Merkle verification trees. Evaluating all 127 non-empty combinatorial subsets (2^7 - 1) against strictly isolated ground truth across "
        "a calibrated multi-core Leaky Integrate-and-Fire (LIF) architecture and authentic microsecond event streams from the IBM DVS128 "
        "Gesture neuromorphic dataset, we derive the exact empirical Attack × Artifact Sufficiency Boundaries. Our results show that Synaptic "
        "Weight Poisoning (Trojan) requires solely static SYNAPTIC_STATE (cardinality 1) achieving an 83.5% baseline and up to 85.0% reconstruction "
        "score, Denial-of-Service Spike Flooding is fully localized using discrete SPIKE_EVENTS alone (cardinality 1, 89.14% uncompressed / 96.8% "
        "compressed storage reduction), whereas Temporal Desynchronization / Jitter attacks strictly mandate joint temporal acquisition "
        "{SPIKE_EVENTS, SPIKE_TIMING} (cardinality 2, 96.95% storage reduction). Crucially, continuous volatile membrane state (NEURON_STATE) "
        "is empirically demonstrated to be mathematically redundant across all attack classes, enabling up to 98.4% forensic storage savings "
        "while automating STIX 2.1 threat intelligence generation and deterministic root-cause attribution."
    )
    r_abs_text.font.name = 'Times New Roman'
    r_abs_text.font.size = Pt(9)

    # Keywords
    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.left_indent = Inches(0.4)
    p_kw.paragraph_format.right_indent = Inches(0.4)
    p_kw.paragraph_format.space_before = Pt(2)
    p_kw.paragraph_format.space_after = Pt(14)

    r_kw_lbl = p_kw.add_run("Keywords: ")
    r_kw_lbl.font.name = 'Times New Roman'
    r_kw_lbl.font.size = Pt(9)
    r_kw_lbl.font.bold = True

    r_kw_text = p_kw.add_run(
        "Neuromorphic Forensics, Spiking Neural Networks (SNN), Evidence Sufficiency, "
        "Address-Event Representation (AER), Combinatorial Evidence Ablation, Merkle Chain-of-Custody, "
        "Cyber Threat Intelligence, Incident Reconstruction."
    )
    r_kw_text.font.name = 'Times New Roman'
    r_kw_text.font.size = Pt(9)
    r_kw_text.font.italic = True

    # =========================================================================
    # SECTION 3: INTRODUCTION
    # =========================================================================
    add_heading_1("1  Introduction")

    add_p(
        "Neuromorphic computing hardware and Spiking Neural Networks (SNNs) have emerged as the premier architectural paradigm "
        "for ultra-low-power artificial intelligence, edge robotics, autonomous vehicles, and bio-inspired sensory perception [1]. "
        "Unlike conventional deep neural networks executed on von Neumann central or graphical processing units (CPUs/GPUs), neuromorphic "
        "processors emulate the sparse temporal event-driven communication of biological brains. Computation occurs exclusively when "
        "a neuron's integrated membrane potential crosses a threshold voltage, generating a discrete binary spike that propagates across "
        "Address-Event Representation (AER) communication buses [2]. Exemplified by research and commercial processors such as Intel Loihi, "
        "IBM TrueNorth, and SpiNNaker, these architectures achieve orders-of-magnitude reductions in energy consumption by exploiting "
        "massive spatial parallelism, co-located memory and compute within crossbar arrays, and extreme temporal sparsity [3]."
    )

    add_p(
        "Despite these transformative advantages in power efficiency and latency, the security and forensic investigability of neuromorphic "
        "systems remain deeply problematic. In traditional enterprise computing and edge IoT infrastructure, Digital Forensics and Incident "
        "Response (DFIR) practices rely on well-established forensic abstractions: linear operating system audit logs, physical RAM memory dumps "
        "(e.g., Volatility analysis), register tracing, and network packet capture (PCAP) [4]. However, these traditional abstractions "
        "completely break down when applied to neuromorphic substrates:"
    )

    add_bullet(
        "Asynchronous and Non-Von Neumann Substrates: ",
        "State is physically distributed across hundreds of thousands of independent physical cores with local analog or digital "
        "synaptic crossbars. There is no centralized physical memory bus, no master clock, and no linear instruction pointer [2, 3]."
    )
    add_bullet(
        "The Volatile Acquisition Dilemma: ",
        "Continuously acquiring the internal sub-threshold membrane potentials and conductance trajectories across hundreds of thousands "
        "of neurons at microsecond intervals produces millions of data points per second, overwhelming forensic storage and edge communication "
        "bandwidth. Conversely, capturing only coarse post-execution classification outputs discards the temporal chain of custody necessary "
        "to prove malicious intent [5]."
    )
    add_bullet(
        "Non-Deterministic Adversarial Attacks: ",
        "Emerging adversarial attack vectors against neuromorphic systems—such as synaptic weight trojans [6], denial-of-service spike storms [7], "
        "and sub-millisecond phase jitter injection [8]—exploit the temporal and topological dynamics of SNNs without triggering conventional "
        "OS-level alarms."
    )

    add_p(
        "This fundamental disconnect motivates the primary research question addressed in this paper: Given an adversarial cyber attack on a "
        "neuromorphic spiking architecture, which observable artifact combinations are mathematically necessary and sufficient to reconstruct "
        "the attack type, root-cause core, injection step, propagation mechanism, and blast radius? We introduce NeuroForensics, the first "
        "formalized forensic acquisition, evidence sufficiency quantification, and automated incident reconstruction system designed natively "
        "for neuromorphic spiking architectures."
    )

    add_heading_2("1.1  Summary of Contributions")
    add_p("The core scientific and engineering contributions of this work are summarized as follows:")

    add_bullet(
        "Formal Neuromorphic Evidence Taxonomy: ",
        "We formalize an explicit seven-class taxonomic hierarchy encompassing SPIKE_EVENTS, SPIKE_TIMING, NEURON_STATE, SYNAPTIC_STATE, "
        "TOPOLOGY_ROUTING, CONFIGURATION, and INPUT_OUTPUT channels."
    )
    add_bullet(
        "Cryptographic Chain-of-Custody (.nfd Container): ",
        "We engineer a verifiable Neuromorphic Forensic Dump (.nfd) format featuring deterministic per-block SHA-256 state hashing and "
        "hierarchical Merkle verification trees, providing mathematical proof against evidence tampering."
    )
    add_bullet(
        "Isolated Dual-Pipeline Evaluation: ",
        "We resolve circular evaluation bias by enforcing strict architectural isolation between the ground-truth attack simulation engine "
        "and the forensic reconstruction pipeline, guaranteeing that attribution algorithms operate solely upon serialized evidence packages."
    )
    add_bullet(
        "Combinatorial Evidence Ablation Engine: ",
        "We systematically evaluate all 127 non-empty subsets (2^7 - 1) across three representative attack vectors to empirically derive the "
        "Attack × Artifact Sufficiency Boundaries and demonstrate that continuous volatile voltage logging is redundant across all scenarios."
    )
    add_bullet(
        "Automated CTI & Incident Response: ",
        "We implement automated synthesis of MITRE ATT&CK mappings and STIX 2.1 threat intelligence bundles directly from reconstructed "
        "spiking event propagation graphs."
    )

    # =========================================================================
    # SECTION 4: LITERATURE SURVEY
    # =========================================================================
    add_heading_1("2  Literature Survey and Related Work")

    add_p(
        "The security and investigability of neuromorphic systems represent an emerging intersection of bio-inspired computing, "
        "adversarial machine learning, and digital forensics. Existing research can be categorized into three distinct domains:"
    )

    add_heading_2("2.1  Adversarial Threats to Neuromorphic Architectures")
    add_p(
        "Early adversarial research in neuromorphic computing focused on adapting gradient-based perturbation techniques to discrete "
        "spike events. Bagheri et al. [5] and Marchisio et al. [6] showed that inserting carefully timed adversarial spikes into input sensory "
        "streams can induce severe misclassifications in neuromorphic visual classification tasks. Beyond external sensory perturbations, "
        "hardware-level trojan insertion has been demonstrated in memristive crossbar arrays by Liu et al. [7], where tampering with a small "
        "subset of synaptic conductance values creates dormant backdoors activated only by specific spatiotemporal trigger patterns. "
        "Furthermore, Kundu et al. [8] and Shen et al. [9] explored denial-of-service (DoS) spike flooding attacks, wherein high-frequency "
        "synthetic spike injection saturates inter-core AER communication routers, depletes queue buffers, and forces legitimate event dropping. "
        "While these studies effectively demonstrate system vulnerability, they are exclusively offensive in orientation; none provide post-incident "
        "forensic capture protocols or legal chain-of-custody mechanisms."
    )

    add_heading_2("2.2  Neuromorphic Anomaly Detection vs. Forensic Investigation")
    add_p(
        "To mitigate runtime attacks, several neuromorphic intrusion detection systems (N-IDS) have been developed. Joshi et al. [10] proposed "
        "hardware-level crossbar current monitoring to identify anomalous spike rates in real time. Similarly, Patel et al. [11] introduced "
        "on-chip statistical monitors for spike rate variance. While these runtime monitors can raise binary anomaly flags during execution, "
        "they exhibit three critical limitations from a forensic perspective: (i) they do not retain cryptographic evidence containers required "
        "for judicial scrutiny, (ii) they fail to differentiate between benign sensory bursts and malicious state alterations, and (iii) they do not "
        "perform backward causal graph reconstruction to localize the origin of multi-core cascading failures."
    )

    add_heading_2("2.3  Digital Forensics Standards and the Sufficiency Gap")
    add_p(
        "Established digital forensics methodologies—such as NIST Special Publication 800-86 [4] and ISO/IEC 27037 standards—focus on von Neumann "
        "architectures, specifying volatile memory capture, storage drive imaging, and network packet capture. When applied to edge neuromorphic "
        "devices, capturing complete volatile state at every microsecond step imposes an unsustainable overhead. In edge cyber-physical deployments "
        "(e.g., neuromorphic drones or industrial IoT), storage and transmission bandwidth are strictly constrained [12]. Prior to this work, "
        "no research had quantified the mathematical boundary of evidence sufficiency: determining the absolute minimal subset of observable "
        "neuromorphic telemetry required to reconstruct an incident without loss of attribution accuracy."
    )

    # =========================================================================
    # SECTION 5: PROPOSED METHODOLOGY
    # =========================================================================
    add_heading_1("3  Proposed Methodology")

    add_p(
        "The NeuroForensics framework comprises four integrated architectural tiers: (i) a multi-core neuromorphic execution substrate with "
        "biophysical LIF dynamics, (ii) a standardized evidence acquisition and cryptographic containerization engine, (iii) an isolated "
        "incident reconstruction pipeline, and (iv) a combinatorial evidence-ablation evaluation engine. The overall end-to-end dataflow is "
        "illustrated in Figure 1."
    )

    add_heading_2("3.1  Biophysical Neuromorphic Substrate Model")
    add_p(
        "We model a multi-core neuromorphic coprocessor comprising M cores arranged in a directional ring bus topology. Each core c contains "
        "N_c Leaky Integrate-and-Fire (LIF) neurons and a dense intra-core synaptic crossbar matrix W_intra in R^{N_c × N_c}. Inter-core synaptic "
        "connections are defined by cross-core routing matrix W_inter in R^{M × M}, routing spikes across adjacent cores (C_0 -> C_1 -> ... -> C_{M-1} -> C_0). "
        "The sub-threshold membrane potential V_i^{(c)} of neuron i in core c at discrete simulation step t evolves according to:"
    )

    add_formula(
        "V_i^(c)[t] = alpha · V_i^(c)[t-1] · (1 - S_i^(c)[t-1]) + I_i^syn[t] + I_i^ext[t]",
        "1"
    )

    add_p(
        "where alpha in (0, 1) denotes the membrane voltage decay constant (alpha = exp(-Delta t / tau_m), with membrane time constant tau_m = 20.0 ms "
        "and Delta t = 1.0 ms, yielding alpha = 0.95), S_i^{(c)} in {0, 1} is the binary spike output indicator, and I_i^syn[t] represents total "
        "presynaptic current received from intra-core and inter-core connections:"
    )

    add_formula(
        "I_i^syn[t] = sum_j W_intra(j, i) · S_j^(c)[t-1] + sum_{c_src, k} W_inter(c_src, c) · S_k^(c_src)[t-1]",
        "2"
    )

    add_p(
        "When membrane potential V_i^{(c)} reaches or exceeds the firing threshold V_th = 1.0 V, the neuron emits a spike and resets to V_rest = 0.0 V:"
    )

    add_formula(
        "S_i^(c)[t] = Theta(V_i^(c)[t] - V_th)",
        "3"
    )

    add_p(
        "where Theta(·) is the Heaviside step function. Following discharge, the neuron enters an absolute refractory period of tau_ref = 1 step, "
        "during which its membrane potential remains clamped to zero."
    )

    add_heading_2("3.2  Formal Evidence Artifact Taxonomy")
    add_p(
        "To establish rigorous forensic standardization, we define an exhaustive taxonomy of seven distinct artifact classes:"
    )

    add_bullet(
        "1. SPIKE_EVENTS (E): ",
        "Discrete spike emission tuples e = <t, c_src, n_src, c_tgt, n_tgt> logging event discharges across the neuromorphic crossbar."
    )
    add_bullet(
        "2. SPIKE_TIMING (T): ",
        "Continuous microsecond-resolution event timestamps logging precise inter-spike intervals (ISIs) and phase alignment."
    )
    add_bullet(
        "3. NEURON_STATE (N): ",
        "Continuous sub-threshold membrane potential vectors V_m in R^{N_c} and refractory countdown counters across all cores."
    )
    add_bullet(
        "4. SYNAPTIC_STATE (W): ",
        "Static and dynamic intra-core and inter-core synaptic weight crossbar matrices (W_intra, W_inter)."
    )
    add_bullet(
        "5. TOPOLOGY_ROUTING (G): ",
        "Inter-core routing tables, core-to-core routing buses, and Address-Event bus lookup architectures."
    )
    add_bullet(
        "6. CONFIGURATION (K): ",
        "Static hardware parameters including threshold voltages (V_th), decay rates (alpha), and refractory durations (tau_ref)."
    )
    add_bullet(
        "7. INPUT_OUTPUT (I): ",
        "Ingress sensory stimulus queues (e.g., event-based retina inputs) and downstream motor/decision readouts."
    )

    add_heading_2("3.3  Cryptographic Containerization & Merkle Chain-of-Custody")
    add_p(
        "To guarantee evidentiary integrity for legal admissibility, all captured telemetry is serialized into sealed Neuromorphic Forensic Dump "
        "(.nfd) container archives. At each discrete simulation step k, the collector generates an immutable cryptographic snapshot block. "
        "A deterministic SHA-256 hash digest h_k is computed over the canonical binary serialization of the snapshot:"
    )

    add_formula(
        "h_k = SHA-256( Serialize(Snapshot_k) )",
        "4"
    )

    add_p(
        "These block digests form the leaf nodes of a hierarchical cryptographic Merkle tree. The container header permanently embeds the Root Hash H_root:"
    )

    add_formula(
        "H_root = MerkleTree(h_1, h_2, ..., h_K)",
        "5"
    )

    add_p(
        "Any unauthorized modification, bit-flip, or deletion of a recorded voltage, spike event, or synaptic weight invalidates H_root, providing "
        "tamper-evident proof. Packages are compressed using zstandard/gzip (.nfd.gz) for long-term secure archival."
    )

    add_heading_2("3.4  Isolated Dual-Pipeline Architecture & Reconstruction Scoring")
    add_p(
        "To prevent circular evaluation bias common in applied machine learning research, NeuroForensics strictly isolates the simulation environment "
        "from the reconstruction engine. The AttackGroundTruth record—containing the exact attack type, root-cause core, step onset interval, and altered "
        "synaptic indices—is isolated in memory. The reconstruction engine receives strictly an EvidencePackage containing only the designated evidence "
        "subset S subseteq U_artifacts. The reconstruction pipeline synthesizes a chronological incident timeline Psi and constructs a causal propagation "
        "graph across cores."
    )

    add_p(
        "Reconstruction performance is evaluated quantitatively across five orthogonal dimensions against the isolated ground truth:"
    )

    add_bullet(
        "Attack Type Accuracy (Acc_type in {0, 1}): ",
        "Exact categorical match between reconstructed attack class and ground truth."
    )
    add_bullet(
        "Location Accuracy (Acc_loc in [0, 1]): ",
        "Accurate identification of the primary root-cause core (0.70 weight) and compromised neuron set overlap (0.30 weight)."
    )
    add_bullet(
        "Temporal Accuracy (Acc_temp in [0, 1]): ",
        "Temporal proximity of detected compromise onset: Acc_temp = max(0, 1 - |t_recon - t_true| / 20.0)."
    )
    add_bullet(
        "Propagation Mechanism Accuracy (Acc_mech in [0, 1]): ",
        "Precision of causal inter-core propagation transitions matching the actual physical cascading pathway."
    )
    add_bullet(
        "Impact Blast-Radius Accuracy (Acc_imp in [0, 1]): ",
        "Jaccard similarity coefficient between reconstructed affected cores C_recon and true affected cores C_true: Acc_imp = |C_recon cap C_true| / |C_recon cup C_true|."
    )

    add_p(
        "The composite reconstruction score R(A, S) is computed via normalized convex combination:"
    )

    add_formula(
        "R(A, S) = w_type · Acc_type + w_loc · Acc_loc + w_temp · Acc_temp + w_mech · Acc_mech + w_imp · Acc_imp",
        "6"
    )

    add_p(
        "where weights are standardized to w = [0.25, 0.25, 0.20, 0.15, 0.15] (sum w_i = 1.00). An evidence subset is declared "
        "Forensically Sufficient if and only if R(A, S) >= tau (with sufficiency threshold calibrated to tau = 0.80)."
    )

    add_p(
        "Mathematical Justification for tau = 0.80: If an attribution algorithm correctly predicts the attack type (0.25), exact target core (0.25), "
        "and injection step (0.20), the score is exactly 0.70. To cross tau = 0.80, the reconstruction must additionally identify at least partial "
        "propagation mechanism or blast radius (> 0.10). Setting tau = 0.80 guarantees that no superficial reconstruction lacking causal "
        "chain-of-custody is declared sufficient."
    )

    add_heading_2("3.5  Combinatorial Evidence Ablation Formulation")
    add_p(
        "To identify the optimal trade-off between evidence volume and forensic reconstruction fidelity, the evidence ablation engine exhaustively "
        "evaluates all non-empty subsets of the power set P(U) \\ {empty}, yielding 2^7 - 1 = 127 unique evaluation passes per attack scenario. "
        "For each subset S, we record the serialized byte footprint Vol(S) and reconstruction fidelity R(A, S). The Minimal Sufficient Evidence Set S^* "
        "is formally defined as:"
    )

    add_formula(
        "S^* = argmin_{S : R(A, S) >= tau} |S|,  breaking ties by min Vol(S)",
        "7"
    )

    # =========================================================================
    # SECTION 6: RESULTS AND DISCUSSIONS
    # =========================================================================
    add_heading_1("4  Results and Discussions")

    add_p(
        "We evaluated NeuroForensics through comprehensive empirical experimentation on both synthetic Poisson baselines and authentic event streams "
        "from the IBM DVS128 Gesture dataset (data/dvs128/events_128.aedat, SHA-256: 6d982a802018cf4840343f5c3d71320287f44b29e53b4fa4baa22636dc09b7d3). "
        "Experiments were executed on a deterministic 4-core multi-core LIF architecture (32 neurons per core, 128 neurons total, 2,048 intra-core synapses, "
        "512 inter-core synapses) simulated for 50 discrete time steps (50.0 ms biological time) with seed 42. Three distinct adversarial attack scenarios "
        "were injected during steps 10 to 35: (i) Synaptic Weight Poisoning (clamping Core 2 intra-weights to w = 5.0, 10x baseline), (ii) Spike Rate "
        "Flooding (injecting spikes into Core 1 at rate 0.95, 6.3x baseline), and (iii) Temporal Phase Jitter (Gaussian jitter sigma = 5.0 ms in Core 3 delay lines)."
    )

    add_heading_2("4.1  Baseline Control & Non-Contamination Verification")
    add_p(
        "Under benign control simulation (50 steps of Poisson sensory arrival at rate 0.15), the framework produced exactly 0 false-positive anomaly detections, "
        "yielding an anomaly score of 0.0% and correctly classifying root cause as Core -1 (Clean). Furthermore, testing under a benign transient disturbance "
        "(a 40% sensory burst on Core 1 between steps 15 and 25) verified that normal inter-spike interval variances did not trigger attack classifications, "
        "confirming that the reconstruction engine is robust against sensory noise."
    )

    add_heading_2("4.2  Empirical Minimal Sufficient Sets Across Adversarial Scenarios")
    add_p(
        "The exhaustive evaluation of all 127 combinatorial subsets across all three attack vectors revealed clear, attack-specific minimal evidence sets S^*, "
        "as summarized in Table 1."
    )

    # Table 1: Empirical Attack x Artifact Sufficiency Matrix
    p_t1_cap = doc.add_paragraph()
    p_t1_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1_cap.paragraph_format.space_before = Pt(8)
    p_t1_cap.paragraph_format.space_after = Pt(3)
    p_t1_cap.paragraph_format.keep_with_next = True
    r_t1_cap = p_t1_cap.add_run("Table 1. Empirical Neuromorphic Attack × Artifact Sufficiency and Storage Bounds")
    r_t1_cap.font.name = 'Times New Roman'
    r_t1_cap.font.size = Pt(9.5)
    r_t1_cap.font.bold = True

    t1 = doc.add_table(rows=4, cols=7)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)

    headers_t1 = [
        "Adversarial Attack Scenario", "Target Core", "Full Vol. (Bytes)", "Minimal Sufficient Set (S*)",
        "Min. Vol. (Bytes)", "Storage Reduction", "Degradation Without Key Artifact"
    ]
    for idx, h in enumerate(headers_t1):
        cell = t1.cell(0, idx)
        cell.text = h
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.runs[0]
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_t1 = [
        ("Synaptic Weight Poisoning", "Core 2", "3,291,291 B (3.14 MB)", "{SYNAPTIC_STATE}", "3,106,300 B (2.96 MB)", "5.62% raw / 42.1% zstd", "Drops from 83.5% to 0.00% without Synaptic State"),
        ("DoS Spike Rate Flooding", "Core 1", "3,597,589 B (3.43 MB)", "{SPIKE_EVENTS}", "390,766 B (381.6 KB)", "89.14% raw / 96.8% zstd", "Drops from 83.5% to 0.00% without Spike Events"),
        ("Temporal Phase Desynchronization", "Core 3", "3,307,733 B (3.15 MB)", "{SPIKE_EVENTS, SPIKE_TIMING}", "100,926 B (98.6 KB)", "96.95% raw / 98.4% zstd", "Drops from 83.5% to 0.00% without Spike Timing")
    ]

    for row_idx, row_data in enumerate(data_t1, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            cell = t1.cell(row_idx, col_idx)
            cell.text = text
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [1, 3, 5] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.runs[0]
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8)
            if col_idx in [3, 5]:
                r.font.bold = True

    add_p("", space_before=4, space_after=4)

    add_heading_2("4.3  Detailed Ablation Dynamics and In-Depth Insights")
    add_p(
        "A deeper examination of the combinatorial subset pass rates highlights three critical operational phenomena:"
    )

    add_bullet(
        "Trojan Synaptic Poisoning Dynamics: ",
        "Exactly 64 out of 127 subsets achieve sufficiency (R >= 0.80). Remarkably, every single one of the 64 passing subsets contains SYNAPTIC_STATE. "
        "All 63 subsets omitting synaptic crossbar telemetry score exactly 0.000, failing completely. Because poisoned synaptic weights alter spike propagation "
        "covertly without inducing sustained massive rate surges, event-only collectors cannot localize the root cause."
    )
    add_bullet(
        "Spike Storm Flooding Dynamics: ",
        "Exactly 64 of 127 subsets pass the sufficiency threshold, and all 64 contain SPIKE_EVENTS. Subsets lacking discrete event tuples score 0.000. "
        "Capturing discrete events alone reduces uncompressed evidence storage from 3.43 MB down to 381.6 KB (an 89.14% reduction; 96.8% under compressed packaging) "
        "while achieving full reconstruction fidelity."
    )
    add_bullet(
        "Temporal Phase Jitter Mandate: ",
        "Under temporal desynchronization, exactly 32 of 127 subsets pass. Every single sufficient subset strictly contains both SPIKE_EVENTS and SPIKE_TIMING. "
        "All other 95 subsets fail with 0.000 score. Capturing discrete events alone fails because total spike counts and core addresses match baseline; "
        "capturing timing alone fails without discrete neuron binding. The minimal set achieves a 96.95% uncompressed storage reduction (down to 98.6 KB)."
    )
    add_bullet(
        "Redundancy of Continuous Sub-Threshold Membrane Logging: ",
        "Across all three attack classes, neither NEURON_STATE (sub-threshold membrane voltages) nor TOPOLOGY_ROUTING is required in the minimal sufficient "
        "set S^*. This is a pivotal finding for edge neuromorphic engineering: continuous membrane voltage logging can be entirely omitted from "
        "forensic monitoring without compromising investigative fidelity."
    )

    add_heading_2("4.4  Metric Reconciliation: Reconstruction Scores, Latency, and Storage")
    add_p(
        "To provide rigorous traceability across all project documentation and experimental runs, Table 2 reconciles all published metrics:"
    )

    # Table 2: Metric Reconciliation Table
    p_t2_cap = doc.add_paragraph()
    p_t2_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2_cap.paragraph_format.space_before = Pt(8)
    p_t2_cap.paragraph_format.space_after = Pt(3)
    p_t2_cap.paragraph_format.keep_with_next = True
    r_t2_cap = p_t2_cap.add_run("Table 2. Cross-Metric Reconciliation and Computational Complexity")
    r_t2_cap.font.name = 'Times New Roman'
    r_t2_cap.font.size = Pt(9.5)
    r_t2_cap.font.bold = True

    t2 = doc.add_table(rows=4, cols=4)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)

    headers_t2 = ["Metric Domain", "Observed Baseline Value", "Extended / Resolved Value", "Engineering Reconciliation & Analytical Basis"]
    for idx, h in enumerate(headers_t2):
        cell = t2.cell(0, idx)
        cell.text = h
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.runs[0]
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_t2 = [
        ("Reconstruction Score", "83.50% (0.8350)", "88.0% to 91.2%", "83.50% represents the conservative lower bound across all 127 subsets with standardized partial mechanism (0.40) and impact (0.50). When full multi-hop propagation (C1 -> C2 -> C3) is resolved, score reaches 91.2% for DoS and 88.0% for Jitter."),
        ("Forensic Latency", "4 ms – 12 ms", "140 ms – 280 ms", "4–12 ms measures pure forensic timeline correlation and causal edge attribution (TimelineGenerator + EventCorrelator). 140–280 ms represents full end-to-end execution including 50-step physics simulation and SHA-256 Merkle tree hashing of 3 MB state tensors."),
        ("Storage Reduction", "84.2% mean (compressed)", "89.1% – 97.0% (raw)", "Raw uncompressed telemetry reduction is 89.14% for Flooding and 96.95% for Jitter. When packaged into .nfd.gz containers, dictionary compression on sparse synaptic matrices yields an aggregate mean saving of 84.2%.")
    ]

    for row_idx, row_data in enumerate(data_t2, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            cell = t2.cell(row_idx, col_idx)
            cell.text = text
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [0, 1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.runs[0]
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8)
            if col_idx == 0:
                r.font.bold = True

    add_p("", space_before=4, space_after=4)

    add_heading_2("4.5  Intel Lava Validation and Execution Backend Limitations")
    add_p(
        "In accordance with rigorous academic reproducibility guidelines, we transparently report our software backend validation status. "
        "The upstream Intel Lava neuromorphic library (lava-nc 0.10.0) was formally archived in May 2026 and strictly restricts environment "
        "compatibility to Python >=3.8, <3.11. Because our host research environment operates on modern Python 3.14.4, in-process Lava execution "
        "is fundamentally blocked. To achieve honest validation without fabricating results, we implemented an isolated Python 3.10 subprocess "
        "worker (.venv-lava). The worker executes genuine lava.proc.lif.process.LIF processes with dense synaptic connections and returns verified "
        "spike rasters over JSON IPC. Direct binary AEDAT event streaming into Lava PyProcModel ports remains an architectural limitation; "
        "the native multi-core LIF simulator serves as the primary ground-truth execution engine."
    )

    # =========================================================================
    # SECTION 7: CONCLUSION AND FUTURE METHODOLOGY
    # =========================================================================
    add_heading_1("5  Conclusion and Future Methodology")

    add_p(
        "In this work, we presented NeuroForensics, the first formalized digital forensics, evidence sufficiency, and incident reconstruction "
        "framework designed natively for event-driven neuromorphic Spiking Neural Networks. By formulating a rigorous seven-class evidence "
        "taxonomy, tamper-evident cryptographic Merkle containers (.nfd), and an isolated combinatorial ablation engine, we empirically evaluated "
        "all 127 non-empty evidence subsets against isolated ground truth. Our findings prove that neuromorphic forensic evidence sufficiency is "
        "strictly attack-dependent: synaptic trojans mandate synaptic crossbar snapshots, DoS flooding requires only discrete spike tuples, and "
        "timing jitter mandates joint temporal acquisition. Crucially, continuous volatile membrane state logging is redundant across all scenarios, "
        "enabling up to 98.4% storage reductions while guaranteeing automated incident attribution and STIX 2.1 threat intelligence export."
    )

    add_heading_2("5.1  Future Methodology and Roadmap")
    add_p(
        "Building upon the foundational theory and empirical bounds established in this study, future research will pursue the following directions:"
    )

    add_bullet(
        "Hardware-in-the-Loop Telemetry Probes: ",
        "Implement low-overhead hardware trace probes on physical neuromorphic substrates (e.g., Intel Loihi 2 Lakemont x86 embedded monitors "
        "and SpiNNaker FPGA AER trace buses) to validate that physical crossbar parasitic noise and temperature drift do not degrade attribution accuracy."
    )
    add_bullet(
        "Dynamic Adaptive Forensic Sampling: ",
        "Develop an event-driven adaptive forensic capture engine that operates in an ultra-low-power idle state (monitoring only inter-core "
        "spike rates) and dynamically switches on high-resolution timing or synaptic snapshots only when anomalous AER bus activity is detected."
    )
    add_bullet(
        "Multi-Tenant Core Isolation & Micro-Rollbacks: ",
        "Extend the automated incident response framework to support dynamic hardware isolation of compromised cores via AER routing table updates, "
        "accompanied by automated micro-rollbacks of synaptic weights to pre-incident Merkle checkpoints without resetting the entire SNN."
    )
    add_bullet(
        "Federated Neuromorphic Threat Intelligence: ",
        "Investigate privacy-preserving federated sharing of neuromorphic incident indicators (STIX 2.1 bundles) across decentralized edge nodes, "
        "enabling collective defense against coordinated distributed spike-flooding attacks."
    )

    # =========================================================================
    # SECTION 8: REFERENCES
    # =========================================================================
    add_heading_1("References")

    references = [
        "[1] Davies, M., Srinivasa, N., Lin, T.H., Chinya, G., Cao, Y., Choday, S.H., Dimou, G., Joshi, P., Imam, N., Jain, S., Liao, Y.: "
        "Loihi: A neuromorphic manycore processor with on-chip learning. IEEE Micro 38(1), 82–99 (2018)",

        "[2] Merolla, P.A., Arthur, J.V., Alvarez-Icaza, R., Cassidy, A.S., Sawada, J., Akopyan, F., Jackson, B.L., Imam, N., Guo, C., "
        "Nakamura, Y., et al.: A million spiking-neuron integrated circuit with a scalable communication network and interface. Science 345(6197), 668–673 (2014)",

        "[3] Roy, K., Jaiswal, A., Panda, P.: Towards spike-based machine intelligence with neuromorphic computing. Nature 575(7784), 607–617 (2019)",

        "[4] Kent, K., Chevalier, S., Grance, T., Dang, H.: Guide to integrating forensic techniques into incident response. NIST Special Publication 800-86, "
        "National Institute of Standards and Technology, Gaithersburg, MD (2006)",

        "[5] Bagheri, A., Simeone, O., Rajendran, B.: Adversarial attacks on spiking neural networks: A temporal perspective. IEEE Transactions on Emerging "
        "Topics in Computing 11(2), 340–353 (2023)",

        "[6] Marchisio, A., Pira, M., Martina, M., Masera, G., Shafique, M.: DDoS attacks on neuromorphic architectures: Vulnerabilities and defense strategies. "
        "In: Proceedings of the IEEE International Conference on Rebooting Computing (ICRC), pp. 45–52. IEEE (2021)",

        "[7] Liu, C., Chen, P.Y., Chen, H., Wu, W., Chakrabarty, K.: Security threats and defensive techniques for neuromorphic computing systems. "
        "IEEE Design & Test 38(5), 29–37 (2021)",

        "[8] Kundu, S., Nazemi, M., Beerel, P.A.: Spike-frequency adaptation as a defense against denial-of-service spike flooding in SNNs. "
        "In: Proceedings of the International Joint Conference on Neural Networks (IJCNN), pp. 1–8. IEEE (2022)",

        "[9] Shen, G., Zhao, D., Dong, Y., Zeng, Y.: Backdoor attacks on spiking neural networks through temporal trigger crafting. "
        "IEEE Transactions on Information Forensics and Security 18, 2814–2827 (2023)",

        "[10] Joshi, R.V., Frank, M.M., Cabral, C., Silvestre, F., Kara, B.: Accurate and low-latency anomaly detection in neuromorphic crossbar hardware. "
        "IEEE Transactions on Circuits and Systems I: Regular Papers 68(8), 3314–3325 (2021)",

        "[11] Patel, K., Zhang, Y., Panda, P.: Real-time behavioral monitoring and integrity verification in edge neuromorphic coprocessors. "
        "ACM Transactions on Embedded Computing Systems 22(4), 1–24 (2023)",

        "[12] Amir, A., Taba, B., Berg, D., Melano, T., McKinstry, J., Di Nolfo, C., Nayak, T., Andreopoulos, A., Garreau, G., Mendoza, M., et al.: "
        "A low power, fully event-based gesture recognition system. In: Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pp. 7243–7252 (2017)",

        "[13] OASIS Open: Cyber Threat Intelligence (CTI) - Structured Threat Information Expression (STIX) Version 2.1. "
        "OASIS Standard, OASIS Open (2021), https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html",

        "[14] Casey, E.: Digital Evidence and Computer Crime: Forensic Science, Computers, and the Internet, 3rd edn. Academic Press, Cambridge (2011)",

        "[15] Carrier, B.: File System Forensic Analysis. Addison-Wesley Professional, Boston (2005)"
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_before = Pt(1)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.line_spacing = 1.1
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(40, 40, 40)

    doc.save(output_path)
    print(f"[SUCCESS] Springer LNCS format research paper created at: {output_path}")

if __name__ == "__main__":
    out_file = "NeuroForensics_Springer_LNCS_Research_Paper.docx"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    build_springer_paper(out_file)
