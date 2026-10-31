"""
Unit and integration tests for neuromorphic dataset loaders.
Tests parsing, validation, provenance, metadata, and error handling for:
- Synthetic dataset fixture
- SHD dataset loader
- DVS128 Gesture loader
- Dataset registry
"""
import os
import struct
import tempfile
import pytest
import numpy as np

from src.datasets.base import (
    NeuromorphicEvent,
    DatasetMetadata,
    DatasetSample,
    DatasetRegistry,
    DatasetSplit,
)
from src.datasets.synthetic import SyntheticDatasetLoader
from src.datasets.dvs128_loader import DVS128GestureLoader
from src.datasets.shd_loader import SHDDatasetLoader, _check_h5py_available


def test_synthetic_dataset_loader():
    loader = SyntheticDatasetLoader(num_samples=3, num_channels=10, duration_seconds=0.1)
    meta = loader.load_metadata()
    assert meta.dataset_name == "Synthetic Poisson Spike Generator"
    assert meta.extra.get("is_synthetic") is True

    assert loader.get_num_samples() == 3

    sample0 = loader.load_sample(sample_index=0)
    assert sample0.sample_id == 0
    assert len(sample0.events) > 0
    assert sample0.duration_seconds == 0.1

    # Verify monotonic ordering
    events = sample0.events
    for i in range(1, len(events)):
        assert events[i].timestamp >= events[i-1].timestamp

    # Validate events via base loader validator
    validated_events, warnings = loader.validate_events(events)
    assert len(validated_events) == len(events)
    assert len(warnings) == 0


def test_dvs128_aedat_parser_valid():
    """Create a minimal valid AEDAT 3.1 file and parse it with DVS128GestureLoader."""
    with tempfile.TemporaryDirectory() as tmpdir:
        aedat_path = os.path.join(tmpdir, "user01_natural_light.aedat")
        
        # Build AEDAT 3.1 binary
        header = (
            b"#!AER-DAT3.1\r\n"
            b"#Data format: EVT2\r\n"
            b"#Source: DVS128\r\n"
            b"#!END-HEADER\r\n"
        )
        
        # Packet header: 28 bytes
        # [0:2] event_type=1 (uint16)
        # [2:4] event_source=0 (uint16)
        # [4:8] event_size=8 (uint32)
        # [8:12] event_ts_offset=0 (uint32)
        # [12:16] event_ts_overflow=0 (uint32)
        # [16:20] event_capacity=2 (uint32)
        # [20:24] event_number=2 (uint32)
        # [24:28] event_valid=2 (uint32)
        pkt_hdr = struct.pack("<HHIIIIII", 1, 0, 8, 0, 0, 2, 2, 2)

        # Polarity Event: 8 bytes -> uint32 data_word, int32 timestamp_raw
        # data_word:
        # bit 0: polarity
        # bits 1-11: y
        # bits 12-22: x
        # bit 23: valid (1)
        # Event 1: x=10, y=20, pol=1, ts=1000 us (0.001 s)
        dw1 = (1 & 0x1) | ((20 & 0x7FF) << 1) | ((10 & 0x7FF) << 12) | (1 << 23)
        ts1 = 1000
        e1 = struct.pack("<Ii", dw1, ts1)

        # Event 2: x=15, y=25, pol=0, ts=2500 us (0.0025 s)
        dw2 = (0 & 0x1) | ((25 & 0x7FF) << 1) | ((15 & 0x7FF) << 12) | (1 << 23)
        ts2 = 2500
        e2 = struct.pack("<Ii", dw2, ts2)

        with open(aedat_path, "wb") as f:
            f.write(header + pkt_hdr + e1 + e2)

        loader = DVS128GestureLoader()
        is_valid, msg = loader.validate_path(aedat_path)
        assert is_valid, msg

        meta = loader.load_metadata(aedat_path)
        assert "DVS128 Gesture" in meta.dataset_name
        assert meta.file_format == "aedat"

        sample = loader.load_sample(aedat_path, sample_index=0)
        assert len(sample.events) == 2
        assert sample.events[0].x == 10
        assert sample.events[0].y == 20
        assert sample.events[0].polarity == 1
        assert pytest.approx(sample.events[0].timestamp, rel=1e-5) == 0.001

        assert sample.events[1].x == 15
        assert sample.events[1].y == 25
        assert sample.events[1].polarity == 0
        assert pytest.approx(sample.events[1].timestamp, rel=1e-5) == 0.0025


def test_dvs128_invalid_file():
    loader = DVS128GestureLoader()
    is_valid, msg = loader.validate_path("non_existent_file.aedat")
    assert not is_valid
    assert "not found" in msg.lower()


def test_shd_loader_without_h5py():
    """Verify clean validation failure or loading behavior."""
    loader = SHDDatasetLoader()
    is_valid, msg = loader.validate_path("non_existent.h5")
    assert not is_valid


def test_shd_h5py_parser_valid():
    """Verify parsing a valid mock SHD HDF5 file structure with SHDDatasetLoader."""
    try:
        import h5py
    except ImportError:
        pytest.skip("h5py is not installed in the current environment")

    with tempfile.TemporaryDirectory() as tmpdir:
        h5_path = os.path.join(tmpdir, "shd_train.h5")
        with h5py.File(h5_path, "w") as f:
            spikes = f.create_group("spikes")
            dt = h5py.special_dtype(vlen=np.dtype("float64"))
            dt_units = h5py.special_dtype(vlen=np.dtype("int32"))
            
            times_dset = spikes.create_dataset("times", (2,), dtype=dt)
            units_dset = spikes.create_dataset("units", (2,), dtype=dt_units)
            
            times_dset[0] = np.array([0.01, 0.05, 0.12], dtype=np.float64)
            units_dset[0] = np.array([12, 45, 108], dtype=np.int32)
            
            times_dset[1] = np.array([0.02, 0.08], dtype=np.float64)
            units_dset[1] = np.array([7, 89], dtype=np.int32)
            
            f.create_dataset("labels", data=np.array([3, 15], dtype=np.int64))

        loader = SHDDatasetLoader()
        is_valid, msg = loader.validate_path(h5_path)
        assert is_valid, msg

        meta = loader.load_metadata(h5_path)
        assert "Spiking Heidelberg Digits" in meta.dataset_name
        assert meta.file_format == "hdf5"
        assert meta.num_samples == 2

        sample0 = loader.load_sample(h5_path, sample_index=0)
        assert sample0.sample_id == 0
        assert sample0.label == 3
        assert sample0.label_name == "three_en"
        assert sample0.num_events == 3
        assert sample0.events[0].channel_id == 12
        assert pytest.approx(sample0.events[0].timestamp, rel=1e-5) == 0.01
        assert sample0.events[1].channel_id == 45
        assert sample0.events[2].channel_id == 108

        sample1 = loader.load_sample(h5_path, sample_index=1)
        assert sample1.sample_id == 1
        assert sample1.label == 15
        assert sample1.label_name == "fünf_de"
        assert sample1.num_events == 2



def test_dataset_registry():
    registry = DatasetRegistry()
    synth = SyntheticDatasetLoader(num_samples=2)
    meta = synth.load_metadata()
    registry.register_dataset(meta)

    listed = registry.list_datasets()
    assert len(listed) == 1
    assert listed[0].dataset_id == meta.dataset_id

    retrieved = registry.get_dataset(meta.dataset_id)
    assert retrieved is not None
    assert retrieved.dataset_name == "Synthetic Poisson Spike Generator"

    removed = registry.remove_dataset(meta.dataset_id)
    assert removed is True
    assert len(registry.list_datasets()) == 0
