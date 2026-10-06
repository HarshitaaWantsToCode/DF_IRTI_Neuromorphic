"""
Unit Tests for DFIR Playbook & STIX 2.1 Threat Intel (Person 4).
"""
import pytest
from src.core.schemas import AttackReconstructionGraph, TimelineEvent
from src.dfir_cti.ir_playbook import IncidentResponseEngine
from src.dfir_cti.ttp_mapper import NeuromorphicTTPMapper
from src.dfir_cti.stix_exporter import STIXExporter


def test_dfir_and_stix_generation():
    evt = TimelineEvent(
        step=10,
        timestamp_ms=10.0,
        event_type="SYNAPSE_ANOMALY",
        affected_core=2,
        affected_neurons=[0, 1],
        severity="CRITICAL",
        description="Synaptic anomaly",
        evidence_ref="snap_10",
        anomaly_score=0.9,
    )
    reconstruction = AttackReconstructionGraph(
        scenario_name="Synaptic Poisoning / Weight Trojan",
        root_cause_core=2,
        initial_compromise_step=10,
        progression_steps=[evt],
        compromised_cores=[2],
        total_anomalous_spikes=12,
        causal_edges=[],
    )

    plan = IncidentResponseEngine.formulate_response(reconstruction)
    assert 2 in plan.isolated_cores
    assert plan.severity == "CRITICAL"

    indicators = NeuromorphicTTPMapper.map_threats(reconstruction)
    assert len(indicators) == 1
    assert indicators[0].ttp_code == "T1565.001"

    stix_bundle = STIXExporter.generate_stix_bundle(reconstruction, indicators)
    assert stix_bundle["type"] == "bundle"
    assert len(stix_bundle["objects"]) >= 4
