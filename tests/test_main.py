"""
Module containing test cases for a FastAPI application.

This module uses the FastAPI TestClient to perform unit tests on endpoints
defined in the `main` FastAPI app. The tests include checking responses for
various endpoints under normal and edge-case scenarios.
"""

# pylint: disable=wrong-import-position

import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the system path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # Adjust the import if your file is named differently

client = TestClient(app)
