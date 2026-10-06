"""
Unit Tests for Evaluation and Pipeline Runner (Person 5).
"""
import pytest
from src.eval.runner import PipelineRunner


def test_pipeline_runner_end_to_end(tmp_path):
    runner = PipelineRunner()
    result = runner.run_experiment(
        scenario_key="synaptic_poisoning",
        output_dir=str(tmp_path),
    )
    assert "scenario" in result
    assert "reconstruction" in result
    assert "timeline" in result
    assert "ir_plan" in result
    assert "metrics" in result
    assert result["metrics"]["performance_metrics"]["root_cause_accuracy_pct"] == 100.0
