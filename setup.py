from setuptools import setup, find_packages

setup(
    name="neuroforensics",
    version="0.1.0",
    description="A Framework for Forensic Acquisition and Reconstruction of Computational State in Neuromorphic Systems",
    author="NeuroForensics Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "networkx>=3.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "stix2>=3.0.1",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "neuroforensics=main:cli",
        ],
    },
)
