"""
Dataset ingestion base classes and registry for NeuroForensics.
Provides an abstract interface for loading neuromorphic event datasets
and a registry for managing dataset registrations.
"""
from .base import (
    NeuromorphicEvent,
    DatasetMetadata,
    DatasetSample,
    DatasetLoader,
    DatasetRegistry,
)
from .synthetic import SyntheticDatasetLoader
from .shd_loader import SHDDatasetLoader
from .dvs128_loader import DVS128GestureLoader

__all__ = [
    "NeuromorphicEvent",
    "DatasetMetadata",
    "DatasetSample",
    "DatasetLoader",
    "DatasetRegistry",
    "SyntheticDatasetLoader",
    "SHDDatasetLoader",
    "DVS128GestureLoader",
]
