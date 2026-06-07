"""Shim so older pip versions can perform an editable install.

All real metadata lives in pyproject.toml; this just delegates to setuptools.
"""

from setuptools import setup

setup()
