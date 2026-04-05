"""
Conftest for utils tests — no external service mocking needed.
Validators and error helpers are pure Python with no I/O.
"""
import os
import pytest

# Minimal env setup
os.environ.setdefault("ENV_MODE", "test")
os.environ.setdefault("TESTING", "true")
