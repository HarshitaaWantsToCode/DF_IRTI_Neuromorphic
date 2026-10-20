"""
Synthetic dataset loader.
Wraps the existing Poisson-noise generator as an explicitly labelled test fixture.
Not a substitute for real neuromorphic data.
"""
import time
import uuid
from typing import Dict, List, Optional, Tuple

import numpy as np

from .base import (
    DatasetLoader,
    DatasetMetadata,
    DatasetSample,
    DatasetSplit,
    NeuromorphicEvent,
)


class SyntheticDatasetLoader(DatasetLoader):
    """
    Generates synthetic spike-event streams using a Poisson process.
    Explicitly labelled as SYNTHETIC — never presented as real data.
    """

    def __init__(
        self,
        num_channels: int = 128,
        num_samples: int = 10,
        duration_seconds: float = 1.0,
        firing_rate_hz: float = 50.0,
        seed: int = 42,
    ):
        self.num_channels = num_channels
        self.num_samples = num_samples
        self.duration_seconds = duration_seconds
        self.firing_rate_hz = firing_rate_hz
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def get_name(self) -> str:
        return "Synthetic Poisson Spike Generator"

    def validate_path(self, path: str) -> Tuple[bool, str]:
        """Synthetic data does not require a file path."""
        return True, "Synthetic dataset does not use file paths."

    def load_metadata(self, path: str = "", split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetMetadata:
        return DatasetMetadata(
            dataset_id=f"synthetic_{self.seed}",
            dataset_name="Synthetic Poisson Spike Generator",
            source_url="",
            citation="Generated internally by NeuroForensics for testing purposes.",
            license="Internal test fixture",
            local_path="(in-memory)",
            file_format="synthetic",
            num_samples=self.num_samples,
            num_classes=0,
            num_channels=self.num_channels,
            split=split,
            time_unit="seconds",
            extra={
                "duration_seconds": self.duration_seconds,
                "firing_rate_hz": self.firing_rate_hz,
                "seed": self.seed,
                "is_synthetic": True,
                "warning": "This is synthetic data generated via Poisson process. "
                           "It is NOT a substitute for real neuromorphic recordings.",
            },
        )

    def load_sample(self, path: str = "", sample_index: int = 0, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetSample:
        if sample_index < 0 or sample_index >= self.num_samples:
            raise IndexError(
                f"Sample index {sample_index} out of range [0, {self.num_samples - 1}]."
            )

        # Deterministic per-sample RNG
        sample_rng = np.random.RandomState(self.seed + sample_index)

        events: List[NeuromorphicEvent] = []
        dt = 1.0 / (self.firing_rate_hz * self.num_channels)
        t = 0.0

        while t < self.duration_seconds:
            for ch in range(self.num_channels):
                if sample_rng.rand() < self.firing_rate_hz * dt:
                    events.append(
                        NeuromorphicEvent(
                            timestamp=t,
                            channel_id=ch,
                            value=1.0,
                        )
                    )
            t += dt

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        return DatasetSample(
            sample_id=sample_index,
            label=sample_index % max(1, self.num_samples),
            label_name=f"synthetic_class_{sample_index % max(1, self.num_samples)}",
            events=events,
            num_events=len(events),
            duration_seconds=self.duration_seconds,
            dataset_id=f"synthetic_{self.seed}",
            split=split,
            source_file="(in-memory)",
            metadata={
                "is_synthetic": True,
                "seed": self.seed + sample_index,
                "firing_rate_hz": self.firing_rate_hz,
                "num_channels": self.num_channels,
            },
        )

    def get_num_samples(self, path: str = "") -> int:
        return self.num_samples
