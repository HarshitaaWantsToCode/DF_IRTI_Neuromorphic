"""
STIX 2.1 Threat Intelligence Exporter (Person 4).
Exports neuromorphic forensic findings and TTPs as standardized STIX 2.1 JSON intelligence bundles.
"""
import json
import uuid
import datetime
from typing import List, Dict, Any
from src.core.schemas import AttackReconstructionGraph, ThreatIndicator


class STIXExporter:
    """Creates standards-compliant STIX 2.1 bundles from neuromorphic forensic artifacts."""

    @staticmethod
    def generate_stix_bundle(
        reconstruction: AttackReconstructionGraph,
        indicators: List[ThreatIndicator],
        org_name: str = "NeuroForensics-Lab",
    ) -> Dict[str, Any]:
        """Builds a full STIX 2.1 JSON Bundle with Identity, Attack-Pattern, and Indicator objects."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        bundle_id = f"bundle--{uuid.uuid4()}"

        identity_id = f"identity--{uuid.uuid4()}"
        identity_obj = {
            "type": "identity",
            "spec_version": "2.1",
            "id": identity_id,
            "created": now_iso,
            "modified": now_iso,
            "name": org_name,
            "identity_class": "organization",
        }

        objects = [identity_obj]

        for ind in indicators:
            attack_pattern_id = f"attack-pattern--{uuid.uuid4()}"
            attack_pattern_obj = {
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": attack_pattern_id,
                "created": now_iso,
                "modified": now_iso,
                "name": ind.technique_name,
                "description": ind.description,
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": ind.ttp_code,
                    }
                ],
                "kill_chain_phases": [
                    {
                        "kill_chain_name": "mitre-attack",
                        "phase_name": ind.tactic.lower().replace(" ", "-"),
                    }
                ],
            }

            indicator_obj = {
                "type": "indicator",
                "spec_version": "2.1",
                "id": ind.indicator_id,
                "created": now_iso,
                "modified": now_iso,
                "name": f"Neuromorphic Indicator: {ind.technique_name}",
                "description": ind.description,
                "pattern_type": "stix",
                "pattern": ind.stix_pattern,
                "valid_from": now_iso,
                "confidence": int(ind.confidence_score * 100),
                "custom_properties": {
                    "x_neuromorphic_artifacts": ind.observable_artifacts,
                    "x_scenario_context": reconstruction.scenario_name,
                },
            }

            rel_obj = {
                "type": "relationship",
                "spec_version": "2.1",
                "id": f"relationship--{uuid.uuid4()}",
                "created": now_iso,
                "modified": now_iso,
                "relationship_type": "indicates",
                "source_ref": ind.indicator_id,
                "target_ref": attack_pattern_id,
            }

            objects.extend([attack_pattern_obj, indicator_obj, rel_obj])

        return {
            "type": "bundle",
            "id": bundle_id,
            "objects": objects,
        }

    @classmethod
    def export_to_file(cls, bundle: Dict[str, Any], file_path: str) -> str:
        """Writes the STIX 2.1 bundle to disk."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        return file_path
