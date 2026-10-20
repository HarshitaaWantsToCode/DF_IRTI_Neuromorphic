"""
Neuromorphic Execution Backends package.
Provides an abstract SNNBackendAdapter interface, built-in simulator adapter,
and a diagnostic Lava CPU adapter.
"""
from .base import BackendCapability, BackendType, SNNBackendAdapter, StepObservation
from .simulator_adapter import BuiltinSimulatorAdapter
from .lava_adapter import LavaCPUAdapter

__all__ = [
    "BackendCapability",
    "BackendType",
    "SNNBackendAdapter",
    "StepObservation",
    "BuiltinSimulatorAdapter",
    "LavaCPUAdapter",
]
