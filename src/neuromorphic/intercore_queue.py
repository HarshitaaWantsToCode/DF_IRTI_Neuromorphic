"""
Bounded Inter-core Queue and Event Scheduler for Neuromorphic Routing.
Models physical FIFO queuing, buffer overflow (event dropping), arrival/service rates,
and timestamp-aware event scheduling with microsecond accuracy.
"""
from dataclasses import dataclass, field
import heapq
from typing import List, Optional, Tuple, Dict, Any
from src.core.schemas import SpikeEvent


@dataclass(order=True)
class ScheduledSpike:
    """Spike scheduled in priority queue by absolute arrival time in milliseconds."""
    delivery_time_ms: float
    event_id: str = field(compare=False)
    spike: SpikeEvent = field(compare=False)


class IntercoreQueue:
    """
    Finite FIFO queue modeling an inter-core routing crossbar or router input buffer.
    Tracks arrival rate, service rate, occupancy, dropped packets, and latency.
    """

    def __init__(self, capacity: int = 50, service_rate_per_ms: float = 10.0):
        self.capacity = capacity
        self.service_rate_per_ms = service_rate_per_ms
        self.queue: List[Tuple[float, SpikeEvent]] = []  # (arrival_time_ms, spike)
        self.total_arrived: int = 0
        self.total_dropped: int = 0
        self.total_serviced: int = 0
        self.peak_occupancy: int = 0
        self.latency_history_ms: List[float] = []

    def enqueue(self, spike: SpikeEvent, current_time_ms: float) -> bool:
        """
        Attempts to enqueue a spike at current_time_ms.
        Returns True if accepted, False if dropped due to buffer saturation.
        """
        self.total_arrived += 1
        if len(self.queue) >= self.capacity:
            self.total_dropped += 1
            return False

        self.queue.append((current_time_ms, spike))
        self.peak_occupancy = max(self.peak_occupancy, len(self.queue))
        return True

    def service_step(self, current_time_ms: float, dt_ms: float = 1.0) -> List[SpikeEvent]:
        """
        Services events up to (service_rate_per_ms * dt_ms) capacity.
        Returns serviced SpikeEvents with updated delivery times.
        """
        max_serviceable = int(self.service_rate_per_ms * dt_ms)
        serviced_spikes: List[SpikeEvent] = []

        while self.queue and len(serviced_spikes) < max_serviceable:
            arrival_time, spike = self.queue.pop(0)
            queue_latency = max(0.0, current_time_ms - arrival_time)
            self.latency_history_ms.append(queue_latency)
            self.total_serviced += 1
            # Service and deliver spike
            serviced_spikes.append(spike)

        return serviced_spikes

    def get_metrics(self) -> Dict[str, Any]:
        """Returns diagnostic metrics for evaluating Denial-of-Service conditions."""
        avg_latency = float(sum(self.latency_history_ms) / len(self.latency_history_ms)) if self.latency_history_ms else 0.0
        drop_rate = (self.total_dropped / self.total_arrived) if self.total_arrived > 0 else 0.0
        return {
            "capacity": self.capacity,
            "total_arrived": self.total_arrived,
            "total_serviced": self.total_serviced,
            "total_dropped": self.total_dropped,
            "drop_rate": drop_rate,
            "peak_occupancy": self.peak_occupancy,
            "current_occupancy": len(self.queue),
            "avg_latency_ms": avg_latency,
            "queue_utilization": self.peak_occupancy / float(self.capacity) if self.capacity > 0 else 0.0,
        }


class TimestampEventScheduler:
    """
    Priority-queue event scheduler. Replaces step-index scheduling with true
    millisecond-accurate timestamp scheduling.
    """

    def __init__(self):
        self._heap: List[ScheduledSpike] = []

    def schedule(self, spike: SpikeEvent, delivery_time_ms: float) -> None:
        """Schedule a spike to arrive at delivery_time_ms."""
        heapq.heappush(self._heap, ScheduledSpike(delivery_time_ms=delivery_time_ms, event_id=spike.event_id, spike=spike))

    def pop_due_events(self, up_to_time_ms: float) -> List[SpikeEvent]:
        """Pop all events scheduled up to or at up_to_time_ms."""
        due: List[SpikeEvent] = []
        while self._heap and self._heap[0].delivery_time_ms <= up_to_time_ms:
            item = heapq.heappop(self._heap)
            due.append(item.spike)
        return due

    def __len__(self) -> int:
        return len(self._heap)
