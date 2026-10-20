"""
DVS128 Gesture dataset loader.
Parses AEDAT files from the IBM DVS128 Gesture dataset.

AEDAT 3.1 file structure:
    - ASCII header lines starting with '#', ending with '#!END-HEADER\\r\\n'
    - Binary event packets containing:
        - Event type header (event_type, event_size, event_number)
        - Polarity events: (data: 32-bit, timestamp: 32-bit) per event
            - data[0]: polarity (1=ON, 0=OFF)
            - data[1:12]: Y address (11 bits)
            - data[12:23]: X address (11 bits, but DVS128 only uses 0-127)
            - data[23]: validity flag
            - timestamp: microseconds

Source: IBM Research, available at https://ibm.ent.box.com/
Resolution: 128x128 pixels
11 gesture classes + 1 'other' class

Requires: numpy (always available). No external library needed for basic parsing.
"""
import os
import struct
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .base import (
    DatasetLoader,
    DatasetMetadata,
    DatasetSample,
    DatasetSplit,
    NeuromorphicEvent,
)

DVS128_GESTURE_LABELS = {
    0: "hand_clapping",
    1: "right_hand_wave",
    2: "left_hand_wave",
    3: "right_arm_cw",
    4: "right_arm_ccw",
    5: "left_arm_cw",
    6: "left_arm_ccw",
    7: "arm_roll",
    8: "air_drums",
    9: "air_guitar",
    10: "other_gestures",
}

# AEDAT 3.1 constants
AEDAT_HEADER_END = b"#!END-HEADER\r\n"
POLARITY_EVENT_TYPE = 1


class DVS128GestureLoader(DatasetLoader):
    """
    Loader for the IBM DVS128 Gesture dataset (AEDAT 3.1 format).

    Citation:
        Amir, A., Taba, B., Berg, D., et al. (2017).
        A Low Power, Fully Event-Based Gesture Recognition System.
        CVPR 2017.

    License: Research use (IBM Research)
    """

    DVS128_CITATION = (
        "Amir, A., Taba, B., Berg, D., et al. (2017). "
        "A Low Power, Fully Event-Based Gesture Recognition System. "
        "CVPR 2017."
    )
    DVS128_SOURCE_URL = "https://ibm.ent.box.com/s/3hiq58ww1pbbjrinh367ykfdf60xsfm8"
    DVS128_RESOLUTION = (128, 128)
    DVS128_NUM_CLASSES = 11

    def get_name(self) -> str:
        return "DVS128 Gesture"

    def validate_path(self, path: str) -> Tuple[bool, str]:
        """Validate that the path points to a valid AEDAT file."""
        if not os.path.exists(path):
            return False, f"File not found: {path}"
        if not os.path.isfile(path):
            return False, f"Path is not a file: {path}"

        # Accept .aedat files
        if not path.lower().endswith(".aedat"):
            return False, f"Expected .aedat file, got: {os.path.basename(path)}"

        # Try reading the header
        try:
            with open(path, "rb") as f:
                first_line = f.readline()
                if not first_line.startswith(b"#"):
                    return False, "File does not start with AEDAT header (expected '#')."
        except Exception as e:
            return False, f"Error reading file: {e}"

        return True, "Valid AEDAT file."

    def validate_directory(self, dir_path: str) -> Tuple[bool, str]:
        """
        Validate a directory that may contain the DVS128 Gesture dataset structure.
        The dataset is typically organized as:
            dir/user01_fluorescent.aedat
            dir/user01_fluorescent_labels.csv
            ...
        """
        if not os.path.isdir(dir_path):
            return False, f"Not a directory: {dir_path}"

        aedat_files = [f for f in os.listdir(dir_path) if f.endswith(".aedat")]
        if not aedat_files:
            return False, f"No .aedat files found in: {dir_path}"

        return True, f"Found {len(aedat_files)} .aedat files."

    def load_metadata(self, path: str, split: DatasetSplit = DatasetSplit.UNKNOWN) -> DatasetMetadata:
        """Load metadata for a single AEDAT recording file."""
        valid, msg = self.validate_path(path)
        if not valid:
            raise ValueError(f"Invalid DVS128 file: {msg}")

        t0 = time.time()
        file_size = os.path.getsize(path)
        warnings: List[str] = []

        # Read header to extract version info
        header_info = self._read_header(path)

        # Compute checksum for smaller files
        checksum = None
        if file_size < 200_000_000:  # Skip for > 200MB
            checksum = self.compute_file_checksum(path)
        else:
            warnings.append(
                f"Skipped SHA-256 checksum for large file ({file_size / 1e6:.1f} MB)."
            )

        ingestion_time = time.time() - t0

        return DatasetMetadata(
            dataset_id=f"dvs128_{os.path.basename(path)}",
            dataset_name=f"DVS128 Gesture ({os.path.basename(path)})",
            source_url=self.DVS128_SOURCE_URL,
            citation=self.DVS128_CITATION,
            license="Research use (IBM Research)",
            local_path=os.path.abspath(path),
            file_format="aedat",
            file_size_bytes=file_size,
            file_checksum_sha256=checksum,
            num_samples=1,  # Each .aedat file is one continuous recording
            num_classes=self.DVS128_NUM_CLASSES,
            num_channels=128 * 128,  # 128x128 pixel grid
            split=split,
            time_unit="microseconds (raw), seconds (normalized)",
            spatial_resolution=self.DVS128_RESOLUTION,
            ingestion_time_seconds=round(ingestion_time, 3),
            warnings=warnings,
            extra={
                "header": header_info,
                "resolution": "128x128",
                "sensor": "DVS128",
            },
        )

    def load_sample(
        self,
        path: str,
        sample_index: int = 0,
        split: DatasetSplit = DatasetSplit.UNKNOWN,
        max_events: Optional[int] = None,
    ) -> DatasetSample:
        """
        Load events from an AEDAT file.
        Each .aedat file is treated as one sample (one continuous recording).
        Use max_events to limit memory usage for very large files.
        """
        valid, msg = self.validate_path(path)
        if not valid:
            raise ValueError(f"Invalid DVS128 file: {msg}")

        if sample_index != 0:
            raise IndexError(
                "Each AEDAT file contains a single recording. Use sample_index=0."
            )

        events = self._parse_aedat_events(path, max_events=max_events)
        duration = 0.0
        if events:
            t0 = events[0].timestamp
            duration = events[-1].timestamp - t0
            for ev in events:
                ev.relative_time_ms = round((ev.timestamp - t0) * 1000.0, 3)

        return DatasetSample(
            sample_id=0,
            label=None,  # Label comes from separate CSV file
            events=events,
            num_events=len(events),
            duration_seconds=duration,
            dataset_id=f"dvs128_{os.path.basename(path)}",
            split=split,
            source_file=os.path.abspath(path),
            metadata={
                "dataset": "DVS128 Gesture",
                "resolution": "128x128",
                "time_unit": "seconds (normalized from microseconds)",
                "max_events_applied": max_events,
            },
        )

    def get_num_samples(self, path: str) -> int:
        """Each AEDAT file is one recording/sample."""
        return 1

    def _read_header(self, path: str) -> Dict[str, Any]:
        """Read and parse the AEDAT header."""
        header_lines = []
        with open(path, "rb") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line == AEDAT_HEADER_END:
                    break
                if line.startswith(b"#"):
                    header_lines.append(line.decode("ascii", errors="replace").strip())
        return {
            "lines": header_lines,
            "num_header_lines": len(header_lines),
        }

    def _detect_version(self, path: str) -> str:
        """Detect AEDAT format version from header line."""
        with open(path, "rb") as f:
            first_line = f.readline().decode("ascii", errors="replace")
            if "2.0" in first_line:
                return "2.0"
            elif "3.1" in first_line:
                return "3.1"
            elif "1.0" in first_line:
                return "1.0"
        return "3.1"

    def _parse_aedat_events(
        self,
        path: str,
        max_events: Optional[int] = None,
    ) -> List[NeuromorphicEvent]:
        """
        Parse AEDAT events from a binary file.
        Supports AEDAT 2.0 (jAER raw stream) and AEDAT 3.1 (packetized).
        """
        version = self._detect_version(path)
        if version == "2.0":
            return self._parse_aedat_2_events(path, max_events=max_events)
        else:
            return self._parse_aedat_3_events(path, max_events=max_events)

    def _parse_aedat_2_events(
        self,
        path: str,
        max_events: Optional[int] = None,
    ) -> List[NeuromorphicEvent]:
        """
        Parse AEDAT 2.0 binary events (8 bytes each: Big-endian uint32 address, uint32 timestamp_us).
        DVS128 bit mapping in AEDAT 2.0:
            bit 0: polarity (0=OFF, 1=ON)
            bits 1..7: x coordinate (0..127)
            bits 8..14: y coordinate (0..127)
        """
        events: List[NeuromorphicEvent] = []
        with open(path, "rb") as f:
            # Skip all header lines starting with '#'
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    break
                if not line.startswith(b"#"):
                    f.seek(pos)
                    break

            raw = f.read()

        total_records = len(raw) // 8
        limit = total_records if max_events is None else min(total_records, max_events)

        for i in range(limit):
            addr, ts_raw = struct.unpack(">II", raw[i * 8 : (i + 1) * 8])
            polarity = addr & 0x1
            x = (addr >> 1) & 0x7F
            y = (addr >> 8) & 0x7F

            timestamp_sec = float(ts_raw) / 1_000_000.0
            events.append(
                NeuromorphicEvent(
                    timestamp=timestamp_sec,
                    timestamp_raw=float(ts_raw),
                    channel_id=y * 128 + x,
                    x=x,
                    y=y,
                    polarity=polarity,
                    value=1.0,
                )
            )
        return events

    def _parse_aedat_3_events(
        self,
        path: str,
        max_events: Optional[int] = None,
    ) -> List[NeuromorphicEvent]:
        """
        Parse AEDAT 3.1 polarity events from a binary file.
        Each polarity event is 8 bytes inside a 28-byte packet header.
        """
        events: List[NeuromorphicEvent] = []

        with open(path, "rb") as f:
            # Skip header
            while True:
                line = f.readline()
                if not line or line == AEDAT_HEADER_END:
                    break

            # Read event packets
            total_read = 0
            while True:
                if max_events is not None and total_read >= max_events:
                    break

                # Read event packet header (28 bytes)
                pkt_header = f.read(28)
                if len(pkt_header) < 28:
                    break

                # Parse packet header
                event_type = struct.unpack("<H", pkt_header[0:2])[0]
                event_size = struct.unpack("<I", pkt_header[4:8])[0]
                event_ts_overflow = struct.unpack("<I", pkt_header[8:12])[0]
                event_capacity = struct.unpack("<I", pkt_header[16:20])[0]
                event_number = struct.unpack("<I", pkt_header[20:24])[0]

                if event_number == 0:
                    continue

                # Read all events in this packet
                packet_data_size = event_number * event_size
                raw_data = f.read(packet_data_size)
                if len(raw_data) < packet_data_size:
                    break

                if event_type != POLARITY_EVENT_TYPE:
                    # Skip non-polarity event packets
                    continue

                # Parse polarity events (8 bytes each: 4 data + 4 timestamp)
                for i in range(event_number):
                    if max_events is not None and total_read >= max_events:
                        break

                    offset = i * event_size
                    if offset + 8 > len(raw_data):
                        break

                    data_word = struct.unpack("<I", raw_data[offset:offset + 4])[0]
                    ts_raw = struct.unpack("<i", raw_data[offset + 4:offset + 8])[0]

                    # Decode polarity event
                    polarity = data_word & 0x1          # bit 0
                    y = (data_word >> 1) & 0x7FF        # bits 1-11
                    x = (data_word >> 12) & 0x7FF       # bits 12-22
                    valid = (data_word >> 23) & 0x1     # bit 23 (validity)

                    if not valid:
                        continue

                    # Convert microseconds to seconds
                    timestamp_sec = float(ts_raw) / 1_000_000.0

                    events.append(
                        NeuromorphicEvent(
                            timestamp=timestamp_sec,
                            timestamp_raw=float(ts_raw),
                            channel_id=y * 128 + x,  # Flatten 2D to 1D channel
                            x=x,
                            y=y,
                            polarity=polarity,
                            value=1.0,
                        )
                    )
                    total_read += 1

        return events
