#!/usr/bin/env python3
"""
Setup script for the Gamaliel Prompts CLI tool.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gamaliel-prompts-cli",
    version="0.1.0",
    author="Gamaliel Team",
    description="CLI tool for testing and validating Gamaliel prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0",
        "jinja2>=3.0",
        "requests",
        "pyyaml",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "gamaliel-prompts=cli.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
