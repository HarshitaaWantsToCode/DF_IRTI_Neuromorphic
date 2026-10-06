"""
NeuroForensics CLI Application (Person 5 / Framework).
Provides commands to run simulations, acquisition, reconstruction, DFIR+CTI, ablation studies, and start the Web Dashboard.
"""
import click
import os
import http.server
import socketserver
import webbrowser
from src.eval.runner import PipelineRunner
from src.eval.metrics import ForensicEvaluator
from src.core.utils import load_yaml_config


@click.group()
def cli():
    """NeuroForensics: Forensic Acquisition & Incident Reconstruction Framework."""
    pass


@cli.command("run-pipeline")
@click.option(
    "--scenario",
    "-s",
    default="synaptic_poisoning",
    type=click.Choice(["synaptic_poisoning", "spike_storm", "timing_jitter"]),
    help="Attack scenario to inject and investigate.",
)
@click.option(
    "--output-dir",
    "-o",
    default="data/outputs",
    help="Directory to save .nfd dumps, STIX bundles, and metric reports.",
)
@click.option(
    "--config",
    "-c",
    default="config/default_config.yaml",
    help="Path to default configuration YAML.",
)
def run_pipeline(scenario, output_dir, config):
    """Executes the full end-to-end NeuroForensics research pipeline."""
    runner = PipelineRunner(config_path=config)
    runner.run_experiment(scenario_key=scenario, output_dir=output_dir)


@cli.command("run-ablation")
@click.option(
    "--output-dir",
    "-o",
    default="results/ablation",
    help="Directory to export JSON/CSV ablation study results.",
)
def run_ablation(output_dir):
    """Runs exhaustive evidence ablation study across all attacks and generates Attack × Artifact Matrix."""
    runner = PipelineRunner()
    runner.run_multi_attack_sufficiency_study(output_dir=output_dir)


@cli.command("serve-dashboard")
@click.option("--port", "-p", default=8080, help="Port to host the dashboard.")
@click.option("--open-browser/--no-open-browser", default=True, help="Open browser on start.")
def serve_dashboard(port, open_browser):
    """Starts the local web dashboard server for visualizing attack topology and timelines."""
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    os.chdir(web_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        click.echo(f"[+] NeuroForensics Web Dashboard running at: {url}")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nServer stopped.")


@cli.command("evaluate")
@click.option("--benchmark", is_flag=True, help="Run all attack scenarios and produce comparative evaluation.")
def evaluate(benchmark):
    """Runs automated benchmarks across all attack scenarios."""
    scenarios = ["synaptic_poisoning", "spike_storm", "timing_jitter"]
    runner = PipelineRunner()
    for s in scenarios:
        click.echo(f"\n================ Running Benchmark: {s} ================")
        runner.run_experiment(scenario_key=s)


if __name__ == "__main__":
    cli()
