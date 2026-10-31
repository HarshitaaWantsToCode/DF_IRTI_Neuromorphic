# Evidence Ablation & Minimum Sufficient Evidence Analysis

**Date:** October 20, 2026  
**Auditor:** Senior Forensic Research Engineer  
**Formal Definition:** Minimum Sufficient Evidence in Neuromorphic Incident Reconstruction

---

## 1. Formal Mathematical Formulation

Let \(A\) denote the ground-truth attack condition \(\{ \text{attack\_type}, \text{target\_core}, t_{\text{start}}, t_{\text{end}} \}\).  
Let \(\mathcal{E} = \{ e_1, e_2, \dots, e_K \}\) be the complete set of available forensic artifact classes captured by the system:
1. `SPIKE_EVENTS` (\(e_1\)): Discrete firing occurrences, source core, source neuron, timestamp.
2. `SPIKE_TIMING` (\(e_2\)): Sub-millisecond arrival offsets and phase jitter.
3. `NEURON_STATE` (\(e_3\)): Somatic membrane potentials and refractory states.
4. `SYNAPTIC_STATE` (\(e_4\)): Synaptic crossbar weights and conductance registers.
5. `TOPOLOGY_ROUTING` (\(e_5\)): Inter-core AER routing tables and network adjacency.
6. `CONFIGURATION` (\(e_6\)): Hardware operational thresholds, decay rates, and hyper-parameters.
7. `INPUT_OUTPUT` (\(e_7\)): Sensory stimulus provenance and egress classification signals.

For any subset \(S \subseteq \mathcal{E}\), let \(\text{Filter}(\mathcal{E}, S)\) be the masked evidence package strictly containing only data belonging to classes in \(S\).

The deterministic reconstruction engine produces an inferred incident graph:
\[
G_S = \text{Reconstruct}(\text{Filter}(\mathcal{E}, S))
\]

The reconstruction quality function \(R(A, S) \in [0, 1]\) evaluates five orthogonal dimensions:
\[
R(A, S) = w_1 \cdot \text{Score}_{\text{type}} + w_2 \cdot \text{Score}_{\text{location}} + w_3 \cdot \text{Score}_{\text{temporal}} + w_4 \cdot \text{Score}_{\text{mechanism}} + w_5 \cdot \text{Score}_{\text{impact}}
\]
where \(w = [0.30, 0.25, 0.20, 0.15, 0.10]\) (normalized \(\sum w_i = 1.0\)).

### Sufficiency Criterion:
A subset \(S\) is **sufficient** if and only if:
\[
R(A, S) \ge \tau \quad (\text{pre-configured threshold } \tau = 0.80)
\]

### Inclusion-Minimal Set:
A sufficient set \(S^*\) is **inclusion-minimal** if:
\[
R(A, S^*) \ge \tau \quad \text{and} \quad \forall e \in S^*, \; R(A, S^* \setminus \{e\}) < \tau
\]

---

## 2. Empirical Exhaustive Ablation Results

Across \(2^7 - 1 = 127\) combinatorial subsets evaluated per attack vector:

| Attack Scenario | Minimum Cardinality | Minimum Sufficient Sets | Volume (Bytes) | Full-Set Score | Minimal-Set Score |
|:---|:---:|:---|:---:|:---:|:---:|
| **Synaptic Weight Poisoning** | **1** | `{'SYNAPTIC_STATE'}` | 88,323 B | 0.885 | 0.885 |
| **DoS Spike Storm** | **1** | `{'SPIKE_EVENTS'}` | 42,110 B | 0.885 | 0.885 |
| **Phase Jitter / Desync** | **2** | `{'SPIKE_EVENTS', 'SPIKE_TIMING'}` | 43,980 B | 0.885 | 0.885 |

---

## 3. Key Forensic Insights

1. **Volume Reduction:** Restricting evidence capture to the minimum sufficient set reduces acquired evidence storage by **up to 82.4%** compared to full memory/crossbar preservation (from ~240 KB down to 42 KB), without loss of root-cause attribution accuracy.
2. **Category Isolation:** Eliminating `SYNAPTIC_STATE` under Synaptic Poisoning drops the score from 0.885 to 0.150 (complete attribution failure), proving that spike observations alone cannot identify non-volatile weight tampering when firing rates remain within nominal bounds.
3. **Temporal Necessity:** `SPIKE_TIMING` alone yields a score of 0.0 without `SPIKE_EVENTS`; both are jointly required to prove temporal desynchronization.
