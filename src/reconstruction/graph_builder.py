"""
Attack Graph and Topological Visualizer (Person 3 / Person 5).
Generates networkx-compatible and D3.js-compatible graphs of attack propagation across neuromorphic cores.
"""
import networkx as nx
from typing import Dict, Any
from src.core.schemas import AttackReconstructionGraph


class AttackGraphBuilder:
    """Builds interactive topological and temporal graphs for forensic inspection."""

    @staticmethod
    def build_networkx_graph(reconstruction: AttackReconstructionGraph) -> nx.DiGraph:
        """Constructs a Directed Graph of the attack propagation flow."""
        G = nx.DiGraph()
        G.add_node(reconstruction.root_cause_core, role="Root Cause / Patient Zero", status="COMPROMISED")

        for core_id in reconstruction.compromised_cores:
            if core_id != reconstruction.root_cause_core:
                G.add_node(core_id, role="Cascaded Core", status="AFFECTED")

        for edge in reconstruction.causal_edges:
            G.add_edge(
                edge["source_core"],
                edge["target_core"],
                step_delta=edge["step_delta"],
                type=edge["propagation_type"],
            )

        return G

    @staticmethod
    def to_d3_json(reconstruction: AttackReconstructionGraph) -> Dict[str, Any]:
        """Exports graph in D3.js force-directed / node-link format for the Web Dashboard."""
        nodes = []
        for c in range(4):  # Standard 4 cores
            status = "HEALTHY"
            if c == reconstruction.root_cause_core and reconstruction.progression_steps:
                status = "ROOT_COMPROMISE"
            elif c in reconstruction.compromised_cores:
                status = "PROPAGATED_IMPACT"
            nodes.append({"id": f"Core_{c}", "core_id": c, "status": status})

        links = []
        for edge in reconstruction.causal_edges:
            links.append({
                "source": f"Core_{edge['source_core']}",
                "target": f"Core_{edge['target_core']}",
                "type": edge["propagation_type"],
            })

        return {"nodes": nodes, "links": links, "scenario": reconstruction.scenario_name}
