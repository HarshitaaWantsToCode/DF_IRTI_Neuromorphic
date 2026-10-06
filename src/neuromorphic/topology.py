"""
Topology and Core inter-connectivity for Spiking Neural Networks (Person 1).
"""
import numpy as np
from typing import Dict, List, Tuple


class NeuromorphicTopology:
    """Manages the network graph and synaptic connection weights between cores and neurons."""

    def __init__(self, num_cores: int = 4, neurons_per_core: int = 32, seed: int = 42):
        self.num_cores = num_cores
        self.neurons_per_core = neurons_per_core
        self.rng = np.random.RandomState(seed)
        
        # Intra-core synaptic weight matrices: core_id -> (N x N)
        self.intra_weights: Dict[int, np.ndarray] = {}
        for c in range(num_cores):
            # Sparse intra-core connectivity with balanced weights
            mask = self.rng.rand(neurons_per_core, neurons_per_core) < 0.15
            weights = self.rng.uniform(0.05, 0.20, (neurons_per_core, neurons_per_core)) * mask
            np.fill_diagonal(weights, 0.0)
            self.intra_weights[c] = weights

        # Inter-core routing table: (src_core, dst_core) -> (N_src x N_dst)
        self.inter_weights: Dict[Tuple[int, int], np.ndarray] = {}
        for src in range(num_cores):
            for dst in range(num_cores):
                if src != dst and (dst == (src + 1) % num_cores):
                    # Feedforward ring routing bus
                    mask = self.rng.rand(neurons_per_core, neurons_per_core) < 0.10
                    weights = self.rng.uniform(0.08, 0.25, (neurons_per_core, neurons_per_core)) * mask
                    self.inter_weights[(src, dst)] = weights

    def get_synaptic_weights(self, core_id: int) -> np.ndarray:
        """Returns the intra-core synaptic weight matrix for a given core."""
        return self.intra_weights[core_id].copy()

    def set_synaptic_weights(self, core_id: int, weights: np.ndarray):
        """Updates the synaptic weight matrix for a core (used in attacks or reset)."""
        self.intra_weights[core_id] = weights.copy()
