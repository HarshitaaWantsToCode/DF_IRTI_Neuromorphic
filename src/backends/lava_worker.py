"""
Lava Subprocess Worker for NeuroForensics.
Executes genuine Lava LIF network simulation within the Python 3.10 virtual environment
using official Lava processes (LIF, RingBuffer Source, RingBuffer Sink).
"""
import sys
import json
import numpy as np

def run_lava_simulation(
    num_neurons: int = 4,
    num_steps: int = 10,
    vth: float = 10.0,
    inject_spikes: bool = True
):
    try:
        from lava.proc.io.source import RingBuffer as SourceRingBuffer
        from lava.proc.io.sink import RingBuffer as SinkRingBuffer
        from lava.proc.lif.process import LIF
        from lava.magma.core.run_conditions import RunSteps
        from lava.magma.core.run_configs import Loihi1SimCfg

        # Construct input stimulation
        input_data = np.zeros((num_neurons, num_steps), dtype=np.float32)
        if inject_spikes:
            # Inject inputs within bounds of num_steps
            if num_steps > 0 and num_neurons > 0:
                input_data[0, 0] = 50.0
            if num_steps > 1 and num_neurons > 1:
                input_data[1, 1] = 50.0
            if num_steps > 2 and num_neurons > 0:
                input_data[0, 2] = 50.0
            if num_steps > 3 and num_neurons > 2:
                input_data[2, 3] = 50.0

        src = SourceRingBuffer(data=input_data)
        lif = LIF(shape=(num_neurons,), vth=vth)
        sink = SinkRingBuffer(shape=(num_neurons,), buffer=num_steps)

        # Wire topology
        src.s_out.connect(lif.a_in)
        lif.s_out.connect(sink.a_in)

        # Execute using Loihi1 simulation configuration with floating point CPU execution
        run_cfg = Loihi1SimCfg(select_tag="floating_pt")
        lif.run(condition=RunSteps(num_steps=num_steps), run_cfg=run_cfg)

        # Retrieve ground-truth spikes from Lava sink buffer
        captured_spikes = sink.data.get().tolist()  # shape (num_neurons, num_steps)
        final_v = lif.v.get().tolist() if hasattr(lif.v, "get") else []

        lif.stop()

        # Format events
        events = []
        for n_idx, neuron_spikes in enumerate(captured_spikes):
            for t_step, spike_val in enumerate(neuron_spikes):
                if spike_val > 0.0:
                    events.append({
                        "step": t_step,
                        "neuron_id": n_idx,
                        "core_id": 0,
                        "value": float(spike_val)
                    })

        result = {
            "status": "success",
            "backend": "Intel Lava CPU Adapter (Subprocess Worker)",
            "num_steps": num_steps,
            "num_neurons": num_neurons,
            "spike_events": events,
            "total_spikes": len(events),
            "final_voltages": final_v,
            "error": None
        }
        print(json.dumps(result))
        return 0

    except Exception as e:
        import traceback
        result = {
            "status": "error",
            "backend": "Intel Lava CPU Adapter (Subprocess Worker)",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(result))
        return 1

if __name__ == "__main__":
    # Optional JSON payload from stdin
    kwargs = {}
    if len(sys.argv) > 1:
        try:
            kwargs = json.loads(sys.argv[1])
        except Exception:
            pass
    sys.exit(run_lava_simulation(**kwargs))
