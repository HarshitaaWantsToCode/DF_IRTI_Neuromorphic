"""
Base classes and abstractions for neuromorphic dataset ingestion.
All dataset loaders must implement the DatasetLoader interface.
Raw source data is treated as immutable; any transformations are logged.
"""
import hashlib
import os
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field


class EventPolarity(int, Enum):
    """Polarity of a neuromorphic event (ON/OFF or positive/negative)."""
    OFF = 0
    ON = 1


class NeuromorphicEvent(BaseModel):
    """
    A single neuromorphic event in a normalized representation.
    Supports both vision (DVS) and auditory (SHD) event streams.
    """
    timestamp: float               # Event time in seconds (canonical unit)
    timestamp_raw: Optional[float] = None  # Original timestamp before normalization (e.g. microseconds)
    relative_time_ms: Optional[float] = None  # Elapsed time in ms relative to first event in recording/sample
    channel_id: int                # Neuron/unit/channel ID (generic)
    x: Optional[int] = None       # X coordinate (vision sensors)
    y: Optional[int] = None       # Y coordinate (vision sensors)
    polarity: Optional[int] = None  # Event polarity (0=OFF, 1=ON) for vision sensors
    value: float = 1.0            # Event amplitude/weight (default: spike = 1.0)


class DatasetSplit(str, Enum):
    """Standard dataset split labels."""
    TRAIN = "train"
    TEST = "test"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class DatasetMetadata(BaseModel):
    """Provenance and integrity metadata for a registered dataset."""
    dataset_id: str                           # Unique identifier
    dataset_name: str                         # Human-readable name
    source_url: str = ""                      # Original download URL
    citation: str = ""                        # BibTeX or citation string
    license: str = ""                         # License identifier
    local_path: str                           # Absolute path on disk
    file_format: str                          # e.g., "hdf5", "aedat", "synthetic"
    file_size_bytes: Optional[int] = None     # File size on disk
    file_checksum_sha256: Optional[str] = None  # SHA-256 of the raw file
    num_samples: Optional[int] = None         # Total samples/recordings
    num_classes: Optional[int] = None         # Number of class labels
    num_channels: Optional[int] = None        # Input channels/neurons
    split: DatasetSplit = DatasetSplit.UNKNOWN
    time_unit: str = "seconds"                # Unit of timestamps in raw data
    spatial_resolution: Optional[Tuple[int, int]] = None  # (width, height) for vision
    registered_at: float = Field(default_factory=time.time)
    ingestion_time_seconds: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class DatasetSample(BaseModel):
    """A single sample (recording) from a dataset with its events and metadata."""
    sample_id: int                          # Index within the dataset
    label: Optional[int] = None             # Class label
    label_name: Optional[str] = None        # Human-readable label
    events: List[NeuromorphicEvent]         # Ordered event stream
    num_events: int = 0                     # Total event count
    duration_seconds: Optional[float] = None  # Recording duration
    dataset_id: str = ""                    # Reference to parent dataset
    split: DatasetSplit = DatasetSplit.UNKNOWN
    source_file: str = ""                   # Source file path
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransformationLog(BaseModel):
    """Records any transformation applied to raw events."""
    operation: str                    # e.g., "time_unit_conversion", "spatial_crop"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    events_before: int = 0
    events_after: int = 0
    events_dropped: int = 0
    drop_policy: str = ""            # Why events were dropped (if any)
    timestamp: float = Field(default_factory=time.time)


class DatasetLoader(ABC):
    """
    Abstract base class for neuromorphic dataset loaders.
    Implementations must parse specific file formats into normalized events.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return the dataset name."""
        ...

    @abstractmethod
    def validate_path(self, path: str) -> Tuple[bool, str]:
        """
        Check whether the given path points to a valid dataset file.
        Returns (is_valid, message).
        """
        ...

    @abstractmethod
    def load_metadata(self, path: str, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetMetadata:
        """
        Load dataset-level metadata without reading all events.
        """
        ...

    @abstractmethod
    def load_sample(self, path: str, sample_index: int, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetSample:
        """
        Load a single sample by index.
        """
        ...

    @abstractmethod
    def get_num_samples(self, path: str) -> int:
        """
        Return the number of samples in the dataset file.
        """
        ...

    def load_recording(self, path: str, sample_index: int = 0, split: DatasetSplit = DatasetSplit.UNKNOWN, **kwargs) -> DatasetSample:
        """Common interface to load a recording/sample."""
        return self.load_sample(path, sample_index=sample_index, split=split, **kwargs)

    def get_events(self, path: str, sample_index: int = 0, **kwargs) -> List[NeuromorphicEvent]:
        """Extract only events for a recording."""
        sample = self.load_recording(path, sample_index=sample_index, **kwargs)
        return sample.events

    def get_labels(self, path: str, sample_index: int = 0) -> Tuple[Optional[int], Optional[str]]:
        """Extract label id and name for a recording."""
        sample = self.load_recording(path, sample_index=sample_index)
        return sample.label, sample.label_name

    def get_metadata(self, path: str, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetMetadata:
        """Alias for load_metadata."""
        return self.load_metadata(path, split=split)

    def get_source_provenance(self, path: str) -> Dict[str, Any]:
        """Extract source provenance and checksum."""
        meta = self.load_metadata(path)
        return {
            "dataset_id": meta.dataset_id,
            "dataset_name": meta.dataset_name,
            "source_url": meta.source_url,
            "citation": meta.citation,
            "license": meta.license,
            "file_checksum_sha256": meta.file_checksum_sha256,
            "file_size_bytes": meta.file_size_bytes,
            "split": meta.split.value,
        }

    def validate_integrity(self, path: str, expected_sha256: Optional[str] = None) -> Tuple[bool, str]:
        """Validate raw file integrity via SHA-256."""
        if not os.path.isfile(path):
            return False, f"File not found: {path}"
        actual_hash = self.compute_file_checksum(path, "sha256")
        if expected_sha256 and actual_hash.lower() != expected_sha256.lower():
            return False, f"Checksum mismatch: expected {expected_sha256}, got {actual_hash}"
        return True, actual_hash

    def compute_file_checksum(self, path: str, algorithm: str = "sha256") -> str:
        """Compute a cryptographic hash of the raw file. Reads in 64KB chunks."""
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def validate_events(self, events: List[NeuromorphicEvent]) -> Tuple[List[NeuromorphicEvent], List[str]]:
        """
        Validate a list of events for timestamp ordering, missing values, etc.
        Returns (validated_events, warning_messages).
        Does NOT silently drop events — reports issues.
        """
        warnings = []
        if not events:
            warnings.append("Empty event list.")
            return events, warnings

        # Check timestamp ordering
        out_of_order = 0
        prev_t = -float("inf")
        for i, evt in enumerate(events):
            if evt.timestamp < prev_t:
                out_of_order += 1
            prev_t = evt.timestamp

        if out_of_order > 0:
            warnings.append(
                f"Found {out_of_order} out-of-order timestamps "
                f"({out_of_order / len(events) * 100:.1f}% of events). "
                f"Events are preserved as-is (not reordered)."
            )

        # Check for NaN/inf timestamps
        nan_count = sum(1 for e in events if np.isnan(e.timestamp) or np.isinf(e.timestamp))
        if nan_count > 0:
            warnings.append(f"Found {nan_count} events with NaN/inf timestamps.")

        # Check for negative timestamps
        neg_count = sum(1 for e in events if e.timestamp < 0)
        if neg_count > 0:
            warnings.append(f"Found {neg_count} events with negative timestamps.")

        return events, warnings


class DatasetRegistry:
    """
    In-memory registry of available datasets.
    Tracks loaded datasets and their metadata for the API and dashboard.
    """

    def __init__(self):
        self._datasets: Dict[str, DatasetMetadata] = {}
        self._loaders: Dict[str, DatasetLoader] = {}

    def register_loader(self, format_name: str, loader: DatasetLoader):
        """Register a loader for a specific file format."""
        self._loaders[format_name] = loader

    def get_loader(self, format_name: str) -> Optional[DatasetLoader]:
        """Get the registered loader for a format."""
        return self._loaders.get(format_name)

    def register_dataset(self, metadata: DatasetMetadata) -> str:
        """
        Register a dataset with its metadata.
        Returns the dataset_id.
        """
        self._datasets[metadata.dataset_id] = metadata
        return metadata.dataset_id

    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Retrieve metadata for a registered dataset."""
        return self._datasets.get(dataset_id)

    def list_datasets(self) -> List[DatasetMetadata]:
        """List all registered datasets."""
        return list(self._datasets.values())

    def remove_dataset(self, dataset_id: str) -> bool:
        """Remove a dataset registration."""
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False

    def to_dict(self) -> List[Dict[str, Any]]:
        """Serialize all dataset metadata for API responses."""
        return [d.model_dump() for d in self._datasets.values()]
