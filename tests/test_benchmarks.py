"""
Automated regression tests for continuous benchmark runner.
Tests scripts/run_benchmarks.py.
"""

import os
import subprocess
import sys
import json
import pytest


def test_benchmark_runner_execution_and_artifacts():
    """Verify scripts/run_benchmarks.py runs cleanly and produces all publication artifacts."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(project_root, "scripts", "run_benchmarks.py")
    assert os.path.exists(script_path), f"Benchmark runner script not found at {script_path}"

    cmd = [sys.executable, script_path]
    proc = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, f"Benchmark runner failed: {proc.stderr}"

    output_dir = os.path.join(project_root, "results", "benchmarks")
    tex_file = os.path.join(output_dir, "comparative_evaluation_table.tex")
    png_file = os.path.join(output_dir, "evidence_sufficiency_tradeoff.png")
    pdf_file = os.path.join(output_dir, "evidence_sufficiency_tradeoff.pdf")
    summary_file = os.path.join(output_dir, "benchmark_summary.json")

    assert os.path.exists(tex_file), "comparative_evaluation_table.tex must exist"
    assert os.path.exists(png_file), "evidence_sufficiency_tradeoff.png must exist"
    assert os.path.exists(pdf_file), "evidence_sufficiency_tradeoff.pdf must exist"
    assert os.path.exists(summary_file), "benchmark_summary.json must exist"

    # Verify LaTeX table syntax
    with open(tex_file, "r", encoding="utf-8") as f:
        tex_content = f.read()
    assert r"\begin{table*}" in tex_content
    assert r"\end{table*}" in tex_content
    assert "Synaptic Weight Poisoning" in tex_content
    assert "DoS Spike Flooding Storm" in tex_content
    assert "83.5\\%" in tex_content

    # Verify PNG is non-empty
    assert os.path.getsize(png_file) > 10000, "Tradeoff plot image must not be empty"

    # Verify Summary JSON
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
    assert summary_data.get("status") == "success"
    assert "synaptic_poisoning" in summary_data.get("scenarios_benchmarked", [])
