"""
Evidence Subset Generator and Filter.
Filters an EvidencePackage to strictly contain a specified subset of ArtifactClasses.
"""
import copy
import json
from typing import Set, List, Optional
from src.core.schemas import EvidencePackage, ArtifactClass, SystemStateSnapshot, CoreStateSnapshot, SpikeEvent


class EvidenceFilter:
    """Filters an EvidencePackage according to allowed artifact classes and computes evidence size."""

    @classmethod
    def filter_evidence(
        cls,
        evidence: EvidencePackage,
        allowed_artifacts: Set[ArtifactClass],
    ) -> EvidencePackage:
        """
        Creates a new EvidencePackage containing only the requested ArtifactClasses.
        """
        has_spikes = ArtifactClass.SPIKE_EVENTS in allowed_artifacts
        has_timing = ArtifactClass.SPIKE_TIMING in allowed_artifacts
        has_neuron = ArtifactClass.NEURON_STATE in allowed_artifacts
        has_synapse = ArtifactClass.SYNAPTIC_STATE in allowed_artifacts
        has_topology = ArtifactClass.TOPOLOGY_ROUTING in allowed_artifacts
        has_config = ArtifactClass.CONFIGURATION in allowed_artifacts
        has_io = ArtifactClass.INPUT_OUTPUT in allowed_artifacts

        # Deep copy header
        new_header = evidence.header.model_copy()
        new_header.included_artifacts = [a for a in allowed_artifacts]

        new_snapshots: List[SystemStateSnapshot] = []

        for snap in evidence.snapshots:
            # Filter core state
            new_cores = {}
            for c_id, core_st in snap.cores.items():
                new_cores[c_id] = CoreStateSnapshot(
                    core_id=c_id,
                    membrane_potentials=core_st.membrane_potentials if has_neuron else None,
                    synaptic_weights=core_st.synaptic_weights if has_synapse else None,
                    refractory_counters=core_st.refractory_counters if has_neuron else None,
                    active_spikes_count=core_st.active_spikes_count if has_spikes else 0,
                )

            # Filter spikes
            filtered_spikes: List[SpikeEvent] = []
            if has_spikes:
                for spk in snap.recent_spikes:
                    spk_copy = spk.model_copy()
                    if not has_timing:
                        # Coarsen or zero out continuous timing
                        spk_copy.timestamp_ms = float(spk.timestamp_step * 1.0)
                    filtered_spikes.append(spk_copy)

            new_snapshots.append(
                SystemStateSnapshot(
                    step=snap.step,
                    timestamp_epoch=snap.timestamp_epoch,
                    cores=new_cores,
                    recent_spikes=filtered_spikes,
                    sensory_inputs=snap.sensory_inputs if has_io else None,
                )
            )

        # Global spike stream
        new_spike_stream: List[SpikeEvent] = []
        if has_spikes:
            for spk in evidence.spike_stream:
                spk_copy = spk.model_copy()
                if not has_timing:
                    spk_copy.timestamp_ms = float(spk.timestamp_step * 1.0)
                new_spike_stream.append(spk_copy)

        return EvidencePackage(
            header=new_header,
            snapshots=new_snapshots,
            spike_stream=new_spike_stream,
            block_hashes=evidence.block_hashes,
            topology=evidence.topology if has_topology else None,
            configuration=evidence.configuration if has_config else None,
        )

    @classmethod
    def calculate_evidence_volume_bytes(cls, package: EvidencePackage) -> int:
        """Calculates serialized evidence volume in bytes."""
        serialized = json.dumps(package.model_dump(), sort_keys=True)
        return len(serialized.encode("utf-8"))
