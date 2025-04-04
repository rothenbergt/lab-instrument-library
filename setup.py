"""
Setup script for the Lab Instrument Library package.

This file contains the package metadata and dependencies required for installation.
"""

from setuptools import setup, find_packages
import os

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from __init__.py
with open(os.path.join("lab_instrument_library", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("'\"")
            break
    else:
        version = "0.1.0"

setup(
    name="lab_instrument_library",
    version=version,
    author="Tyler Rothenberg",
    author_email="rothenbergt@gmail.com",
    description="A library for interfacing with laboratory instruments through VISA/GPIB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rothenbergt/lab-instrument-library",
    project_urls={
        "Bug Tracker": "https://github.com/rothenbergt/lab-instrument-library/issues",
        "Documentation": "https://github.com/rothenbergt/lab-instrument-library",
        "Source Code": "https://github.com/rothenbergt/lab-instrument-library",
    },
    packages=find_packages(),
    package_data={"lab_instrument_library": ["py.typed"]},
    install_requires=[
        "pyvisa>=1.11.0",
        "pyvisa-py>=0.5.2",
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "matplotlib>=3.3.0",
        "PySimpleGUI>=4.40.0",
        "Pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "sphinx>=3.0.0",
            "black>=20.8b1",
            "mypy>=0.800",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", # Added newer Python version
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lab-instrument-scan=lab_instrument_library.utils.utilities:scan_gpib_devices",
        ],
    },
)
