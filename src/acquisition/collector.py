"""
Forensic Evidence Collector for Neuromorphic Computing Systems (Person 2).
Gathers volatile computational state (membrane potentials, synaptic weights, spike streams) and builds verifiable evidence packages.
"""
from typing import List, Dict, Any, Optional
from src.core.schemas import (
    SystemStateSnapshot,
    SpikeEvent,
    NFDHeader,
    EvidencePackage,
    ArtifactClass,
)
from .integrity import ChainOfCustodyVerifier
from .dump_format import NFDSerializer


class ForensicCollector:
    """Acquires live snapshots from the Neuromorphic SNN and seals them into tamper-evident .nfd containers."""

    def __init__(self, num_cores: int = 4, neurons_per_core: int = 32):
        self.num_cores = num_cores
        self.neurons_per_core = neurons_per_core
        self.snapshots: List[SystemStateSnapshot] = []
        self.spike_stream: List[SpikeEvent] = []
        self.topology_metadata: Optional[Dict[str, Any]] = None
        self.config_metadata: Optional[Dict[str, Any]] = None

    def record_step(self, snapshot: SystemStateSnapshot, spikes: List[SpikeEvent]):
        """Ingests a live state snapshot and spike stream from the simulation step."""
        self.snapshots.append(snapshot)
        self.spike_stream.extend(spikes)

    def attach_system_context(self, topology: Optional[Dict[str, Any]] = None, configuration: Optional[Dict[str, Any]] = None):
        """Attaches system architecture and configuration evidence."""
        self.topology_metadata = topology
        self.config_metadata = configuration

    def seal_evidence(self, metadata: Optional[Dict[str, Any]] = None) -> EvidencePackage:
        """
        Calculates block hashes for all recorded snapshots, computes the Merkle Root,
        and packages the full evidence into an immutable container.
        """
        if metadata is None:
            metadata = {}

        # 1. Compute SHA-256 for each snapshot block
        block_hashes = [
            ChainOfCustodyVerifier.hash_data(s.model_dump()) for s in self.snapshots
        ]

        # 2. Compute Merkle Root
        merkle_root = ChainOfCustodyVerifier.compute_merkle_root(block_hashes)

        # 3. Create NFD Header
        header = NFDHeader(
            total_steps=len(self.snapshots),
            num_cores=self.num_cores,
            neurons_per_core=self.neurons_per_core,
            root_merkle_hash=merkle_root,
            collector_signature=f"ECDSA-SIG-{merkle_root[:16]}",
            included_artifacts=list(ArtifactClass),
            metadata=metadata,
        )

        return EvidencePackage(
            header=header,
            snapshots=self.snapshots,
            spike_stream=self.spike_stream,
            block_hashes=block_hashes,
            topology=self.topology_metadata,
            configuration=self.config_metadata,
        )

    def export_dump(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, compress: bool = True) -> str:
        """Seals evidence and writes it to a .nfd / .nfd.gz container on disk."""
        package = self.seal_evidence(metadata)
        return NFDSerializer.save_dump(package, file_path, compress=compress)
