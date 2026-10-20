"""
Abstract Base Classes and Interfaces for Neuromorphic Execution Backends.
Supports multiple backends (LIF simulator, Lava CPU stub/adapter, physical hardware)
with explicit capability reporting, provenance labelling, and forensic observation hooks.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import time

from pydantic import BaseModel, Field


class BackendType(str, Enum):
    BUILTIN_SIMULATOR = "builtin_simulator"
    LAVA_CPU = "lava_cpu"
    LAVA_HARDWARE = "lava_hardware"
    PHYSICAL_HARDWARE = "physical_hardware"


class BackendCapability(BaseModel):
    """Explicit declaration of what an execution backend supports and observes."""
    backend_id: str
    backend_name: str
    backend_type: BackendType
    is_available: bool = True
    unavailability_reason: Optional[str] = None
    
    # Observable state capabilities
    observable_spikes: bool = True
    observable_potentials: bool = True
    observable_weights: bool = True
    observable_refractory: bool = True
    observable_hardware_telemetry: bool = False
    
    # Execution constraints
    max_cores: int = 16
    max_neurons_per_core: int = 1024
    supported_neuron_models: List[str] = Field(default_factory=lambda: ["LIF"])
    
    # Hardware/environment metadata
    device_name: str = "CPU (Software Emulation)"
    notes: str = ""


class StepObservation(BaseModel):
    """Snapshot of observable state captured at a single discrete simulation step."""
    step: int
    timestamp_s: float
    spike_events: List[Dict[str, Any]] = Field(default_factory=list)
    membrane_potentials: Dict[str, List[float]] = Field(default_factory=dict)
    refractory_states: Dict[str, List[int]] = Field(default_factory=dict)
    weights_summary: Optional[Dict[str, Any]] = None
    telemetry: Dict[str, Any] = Field(default_factory=dict)


class SNNBackendAdapter(ABC):
    """
    Abstract Interface for SNN backends.
    All simulation and neuromorphic backends must implement this adapter to ensure
    consistent, reproducible, and forensically sound execution.
    """

    @abstractmethod
    def get_capabilities(self) -> BackendCapability:
        """Report hardware/software capabilities and observability limits."""
        ...

    @abstractmethod
    def initialize_network(self, config: Dict[str, Any]) -> bool:
        """Initialize or reset network state with provided topology and parameters."""
        ...

    @abstractmethod
    def step(self, input_spikes: Optional[Dict[int, List[int]]] = None) -> StepObservation:
        """
        Advance simulation by one time-step (dt).
        Args:
            input_spikes: Optional mapping of core_id -> list of neuron_ids receiving external spikes.
        Returns:
            StepObservation containing observable states.
        """
        ...

    @abstractmethod
    def get_weights(self) -> Dict[str, Any]:
        """Return synaptic weight state across all cores."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset internal potential, refractory states, and counters."""
        ...
