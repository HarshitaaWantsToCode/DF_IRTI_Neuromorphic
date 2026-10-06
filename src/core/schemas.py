"""
Core Data Schemas, Explicit Artifact Taxonomies, and Ground Truth Models.
Supports research into attack-specific evidence sufficiency and forensic reconstruction.
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
import time
import uuid


class ArtifactClass(str, Enum):
    """Formal taxonomic artifact classes for neuromorphic evidence."""
    SPIKE_EVENTS = "SPIKE_EVENTS"           # Discrete inter/intra core spikes (source, target neuron/core)
    SPIKE_TIMING = "SPIKE_TIMING"           # High-precision continuous/microsecond timestamps (timestamp_ms)
    NEURON_STATE = "NEURON_STATE"           # Volatile neuron dynamics (membrane potential V_m, refractory state)
    SYNAPTIC_STATE = "SYNAPTIC_STATE"       # Plastic/programmable synaptic weight matrices
    TOPOLOGY_ROUTING = "TOPOLOGY_ROUTING"   # Core connectivity graph, routing tables, and static architecture
    CONFIGURATION = "CONFIGURATION"         # Hyperparameters (decay factor, firing threshold, refractory duration)
    INPUT_OUTPUT = "INPUT_OUTPUT"           # Sensory Poisson input channels and downstream motor/readout activations


class EvidenceRecord(BaseModel):
    """Generic structured forensic record with provenance."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp_step: int
    timestamp_ms: Optional[float] = None
    artifact_type: ArtifactClass
    core_id: Optional[int] = None
    neuron_id: Optional[int] = None
    synapse_id: Optional[str] = None
    value_state: Any = None
    provenance: Dict[str, Any] = Field(default_factory=dict)


class SpikeEvent(BaseModel):
    """Represents a single spike communication event between neurons/cores."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp_step: int
    timestamp_ms: float
    source_core: int
    source_neuron: int
    target_core: int
    target_neuron: int
    voltage_mv: float = 1.0


class CoreStateSnapshot(BaseModel):
    """Represents the volatile state of an individual Neuromorphic Core at a specific step."""
    core_id: int
    membrane_potentials: Optional[List[float]] = None
    synaptic_weights: Optional[List[List[float]]] = None
    refractory_counters: Optional[List[int]] = None
    active_spikes_count: int = 0


class SystemStateSnapshot(BaseModel):
    """Represents the global system state at a discrete acquisition time step."""
    step: int
    timestamp_epoch: float = Field(default_factory=time.time)
    cores: Dict[int, CoreStateSnapshot]
    recent_spikes: List[SpikeEvent] = Field(default_factory=list)
    sensory_inputs: Optional[List[int]] = None


class NFDHeader(BaseModel):
    """Header information for Neuromorphic Forensic Dump (.nfd) container."""
    format_version: str = "NFD-v2.0"
    dump_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at_epoch: float = Field(default_factory=time.time)
    total_steps: int
    num_cores: int
    neurons_per_core: int
    root_merkle_hash: str
    collector_signature: str
    included_artifacts: List[ArtifactClass] = Field(default_factory=lambda: list(ArtifactClass))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidencePackage(BaseModel):
    """Full forensic evidence package bundled in .nfd container."""
    header: NFDHeader
    snapshots: List[SystemStateSnapshot]
    spike_stream: List[SpikeEvent]
    block_hashes: List[str]
    topology: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None


class AttackGroundTruth(BaseModel):
    """
    Logically isolated ground truth representing the true physical attack injection.
    NEVER passed directly into the forensic reconstruction engine to prevent circular evaluation.
    """
    attack_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    attack_type: str                         # e.g., 'synaptic_poisoning', 'spike_storm', 'timing_jitter'
    attack_category: str                     # e.g., 'integrity', 'dos', 'temporal'
    target_core: int
    affected_cores: List[int]
    start_step: int
    end_step: int
    duration_steps: int
    target_neurons: List[int] = Field(default_factory=list)
    target_synapses: List[str] = Field(default_factory=list)
    modified_parameters: Dict[str, Any] = Field(default_factory=dict)
    true_propagation_path: List[int] = Field(default_factory=list)
    true_impact: Dict[str, Any] = Field(default_factory=dict)


class TimelineEvent(BaseModel):
    """An event reconstructed chronologically from forensic evidence."""
    step: int
    timestamp_ms: float
    event_type: str  # e.g., 'NORMAL_DISCHARGE', 'SYNAPSE_ANOMALY', 'SPIKE_BURST', 'TIMING_DEVIATION'
    affected_core: int
    affected_neurons: List[int]
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    description: str
    evidence_ref: str
    anomaly_score: float


class AttackReconstructionGraph(BaseModel):
    """Reconstructed causal sequence and topological propagation of an attack from evidence."""
    scenario_name: str
    detected_attack_type: Optional[str] = None
    root_cause_core: int
    initial_compromise_step: int
    progression_steps: List[TimelineEvent]
    compromised_cores: List[int]
    total_anomalous_spikes: int
    causal_edges: List[Dict[str, Any]]
    confidence: float = 0.0


class ReconstructionScore(BaseModel):
    """
    Deterministic quantitative evaluation comparing forensic reconstruction against Ground Truth.
    Score breakdown in range [0.0, 1.0].
    """
    attack_type_score: float      # Did the reconstruction identify the correct attack type/category?
    location_score: float         # Did it locate the exact root-cause core and affected components?
    temporal_score: float         # Accuracy of initial compromise step and timeline ordering
    mechanism_score: float        # Did it reconstruct the correct causal propagation edges?
    impact_score: float           # Accuracy of affected core blast radius estimation
    overall_score: float          # Weighted aggregate score [0.0 - 1.0]
    weights_used: Dict[str, float]
    passed_threshold: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class IncidentResponsePlan(BaseModel):
    """Automated containment and remediation instructions."""
    incident_id: str = Field(default_factory=lambda: f"INC-{str(uuid.uuid4())[:8].upper()}")
    scenario_detected: str
    severity: str
    containment_actions: List[str]
    isolated_cores: List[int]
    recalibration_targets: Dict[int, str]
    preservation_status: str


class ThreatIndicator(BaseModel):
    """Cyber Threat Intelligence (CTI) mapping of neuromorphic anomalies."""
    indicator_id: str = Field(default_factory=lambda: f"indicator--{uuid.uuid4()}")
    ttp_code: str
    technique_name: str
    tactic: str
    confidence_score: float
    description: str
    stix_pattern: str
    observable_artifacts: Dict[str, Any]
