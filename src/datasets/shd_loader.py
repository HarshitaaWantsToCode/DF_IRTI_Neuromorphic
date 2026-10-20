"""
Spiking Heidelberg Digits (SHD) dataset loader.
Parses the HDF5 files published at https://zenkelab.org/resources/spiking-heidelberg-datasets-shd/

File structure (HDF5):
    /spikes/times[]  — VLArray of spike timestamps in seconds per sample
    /spikes/units[]  — VLArray of neuron/channel IDs (0-699) per sample
    /labels[]        — Integer class labels (0-19)
    /extra/          — Optional metadata (speaker, gender, etc.)

Requires: h5py or tables (PyTables). Falls back gracefully if unavailable.
"""
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .base import (
    DatasetLoader,
    DatasetMetadata,
    DatasetSample,
    DatasetSplit,
    NeuromorphicEvent,
    TransformationLog,
)

# SHD class labels: digits 0-9 in English (0-9) and German (10-19)
SHD_LABEL_NAMES = {
    0: "zero_en", 1: "one_en", 2: "two_en", 3: "three_en", 4: "four_en",
    5: "five_en", 6: "six_en", 7: "seven_en", 8: "eight_en", 9: "nine_en",
    10: "null_de", 11: "eins_de", 12: "zwei_de", 13: "drei_de", 14: "vier_de",
    15: "fünf_de", 16: "sechs_de", 17: "sieben_de", 18: "acht_de", 19: "neun_de",
}


def _check_h5py_available() -> bool:
    """Check if h5py is installed."""
    try:
        import h5py  # noqa: F401
        return True
    except ImportError:
        return False


def _check_tables_available() -> bool:
    """Check if PyTables (tables) is installed."""
    try:
        import tables  # noqa: F401
        return True
    except ImportError:
        return False


class SHDDatasetLoader(DatasetLoader):
    """
    Loader for the Spiking Heidelberg Digits (SHD) dataset.

    Citation:
        Cramer, B., Stradmann, Y., Schemmel, J., & Zenke, F. (2020).
        The Heidelberg Spiking Data Sets for the Systematic Evaluation of
        Spiking Neural Networks. IEEE Transactions on Neural Networks and
        Learning Systems, 33(7), 2744-2757.

    License: Creative Commons Attribution 4.0 International (CC BY 4.0)
    """

    SHD_CITATION = (
        "Cramer, B., Stradmann, Y., Schemmel, J., & Zenke, F. (2020). "
        "The Heidelberg Spiking Data Sets for the Systematic Evaluation of "
        "Spiking Neural Networks. IEEE TNNLS, 33(7), 2744-2757."
    )
    SHD_LICENSE = "CC BY 4.0"
    SHD_SOURCE_URL = "https://zenkelab.org/resources/spiking-heidelberg-datasets-shd/"
    SHD_NUM_CHANNELS = 700
    SHD_NUM_CLASSES = 20

    def get_name(self) -> str:
        return "Spiking Heidelberg Digits (SHD)"

    def validate_path(self, path: str) -> Tuple[bool, str]:
        """Validate that the path points to a valid SHD HDF5 file."""
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"
        if not path.endswith((".h5", ".hdf5")):
            return False, f"Expected .h5 or .hdf5 file, got: {path}"

        # Check HDF5 library availability
        if not _check_h5py_available() and not _check_tables_available():
            return False, (
                "Neither h5py nor PyTables is installed. "
                "Install one with: pip install h5py  or  pip install tables"
            )

        # Try opening the file
        try:
            if _check_h5py_available():
                import h5py
                with h5py.File(path, "r") as f:
                    if "spikes" not in f or "labels" not in f:
                        return False, (
                            f"HDF5 file does not contain expected groups. "
                            f"Found: {list(f.keys())}. Expected: 'spikes', 'labels'."
                        )
                    if "times" not in f["spikes"] or "units" not in f["spikes"]:
                        return False, (
                            f"spikes group does not contain 'times' and 'units'. "
                            f"Found: {list(f['spikes'].keys())}."
                        )
            elif _check_tables_available():
                import tables
                with tables.open_file(path, mode="r") as f:
                    if not hasattr(f.root, "spikes") or not hasattr(f.root, "labels"):
                        return False, "HDF5 file missing 'spikes' or 'labels' groups."
        except Exception as e:
            return False, f"Error reading HDF5 file: {e}"

        return True, "Valid SHD HDF5 file."

    def load_metadata(self, path: str, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetMetadata:
        """Load dataset-level metadata from the SHD HDF5 file."""
        valid, msg = self.validate_path(path)
        if not valid:
            raise ValueError(f"Invalid SHD dataset path: {msg}")

        t0 = time.time()
        file_size = os.path.getsize(path)
        warnings: List[str] = []

        # Infer split from filename
        if split == DatasetSplit.UNKNOWN:
            basename = os.path.basename(path).lower()
            if "train" in basename:
                split = DatasetSplit.TRAIN
            elif "test" in basename:
                split = DatasetSplit.TEST
            elif "val" in basename:
                split = DatasetSplit.VALIDATION

        num_samples = self.get_num_samples(path)

        # Compute checksum (may be slow for large files)
        checksum = None
        if file_size < 500_000_000:  # Skip for files > 500MB to avoid blocking
            checksum = self.compute_file_checksum(path)
        else:
            warnings.append(
                f"Skipped SHA-256 checksum for large file ({file_size / 1e9:.1f} GB). "
                f"Use compute_file_checksum() explicitly if needed."
            )

        ingestion_time = time.time() - t0

        return DatasetMetadata(
            dataset_id=f"shd_{split.value}_{os.path.basename(path)}",
            dataset_name=f"Spiking Heidelberg Digits ({split.value})",
            source_url=self.SHD_SOURCE_URL,
            citation=self.SHD_CITATION,
            license=self.SHD_LICENSE,
            local_path=os.path.abspath(path),
            file_format="hdf5",
            file_size_bytes=file_size,
            file_checksum_sha256=checksum,
            num_samples=num_samples,
            num_classes=self.SHD_NUM_CLASSES,
            num_channels=self.SHD_NUM_CHANNELS,
            split=split,
            time_unit="seconds",
            ingestion_time_seconds=round(ingestion_time, 3),
            warnings=warnings,
            extra={
                "label_names": SHD_LABEL_NAMES,
                "cochlear_channels": self.SHD_NUM_CHANNELS,
                "languages": ["English", "German"],
            },
        )

    def load_sample(self, path: str, sample_index: int, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetSample:
        """Load a single sample from the SHD dataset."""
        valid, msg = self.validate_path(path)
        if not valid:
            raise ValueError(f"Invalid SHD dataset path: {msg}")

        num_samples = self.get_num_samples(path)
        if sample_index < 0 or sample_index >= num_samples:
            raise IndexError(
                f"Sample index {sample_index} out of range [0, {num_samples - 1}] "
                f"for SHD file: {path}"
            )

        if _check_h5py_available():
            return self._load_sample_h5py(path, sample_index, split)
        elif _check_tables_available():
            return self._load_sample_tables(path, sample_index, split)
        else:
            raise ImportError("Neither h5py nor PyTables is available.")

    def _load_sample_h5py(self, path: str, sample_index: int, split: DatasetSplit) -> DatasetSample:
        """Load sample using h5py."""
        import h5py

        with h5py.File(path, "r") as f:
            spike_times = f["spikes"]["times"][sample_index]
            spike_units = f["spikes"]["units"][sample_index]
            label = int(f["labels"][sample_index])

            # Handle variable-length arrays
            if hasattr(spike_times, '__len__'):
                times_arr = np.array(spike_times, dtype=np.float64)
                units_arr = np.array(spike_units, dtype=np.int32)
            else:
                times_arr = np.array([spike_times], dtype=np.float64)
                units_arr = np.array([spike_units], dtype=np.int32)

        return self._build_sample(times_arr, units_arr, label, sample_index, path, split)

    def _load_sample_tables(self, path: str, sample_index: int, split: DatasetSplit) -> DatasetSample:
        """Load sample using PyTables."""
        import tables

        with tables.open_file(path, mode="r") as f:
            spike_times = np.array(f.root.spikes.times[sample_index], dtype=np.float64)
            spike_units = np.array(f.root.spikes.units[sample_index], dtype=np.int32)
            label = int(f.root.labels[sample_index])

        return self._build_sample(spike_times, spike_units, label, sample_index, path, split)

    def _build_sample(
        self,
        times: np.ndarray,
        units: np.ndarray,
        label: int,
        sample_index: int,
        path: str,
        split: DatasetSplit,
    ) -> DatasetSample:
        """Build a DatasetSample from raw spike times and units."""
        events: List[NeuromorphicEvent] = []

        for i in range(len(times)):
            events.append(
                NeuromorphicEvent(
                    timestamp=float(times[i]),     # SHD times are in seconds
                    timestamp_raw=float(times[i]),
                    channel_id=int(units[i]),
                    value=1.0,
                )
            )

        duration = float(times[-1] - times[0]) if len(times) > 0 else 0.0
        label_name = SHD_LABEL_NAMES.get(label, f"unknown_{label}")

        return DatasetSample(
            sample_id=sample_index,
            label=label,
            label_name=label_name,
            events=events,
            num_events=len(events),
            duration_seconds=duration,
            dataset_id=f"shd_{split.value}_{os.path.basename(path)}",
            split=split,
            source_file=os.path.abspath(path),
            metadata={
                "dataset": "SHD",
                "num_channels": self.SHD_NUM_CHANNELS,
                "time_unit": "seconds",
            },
        )

    def get_num_samples(self, path: str) -> int:
        """Return the number of samples in the SHD HDF5 file."""
        if _check_h5py_available():
            import h5py
            with h5py.File(path, "r") as f:
                return len(f["labels"])
        elif _check_tables_available():
            import tables
            with tables.open_file(path, mode="r") as f:
                return len(f.root.labels)
        else:
            raise ImportError("Neither h5py nor PyTables is available.")
