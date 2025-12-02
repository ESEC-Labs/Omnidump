from click.testing import CliRunner
import pytest 
from omnidump.cli import dump_pid
from unittest import mock
from datetime import datetime


@pytest.fixture(scope="function")
def self_base_args():
    """Provides the base argument list for testing self-dumps."""
    return ['--self'] 


@pytest.fixture(scope="session")
def save_dir_base_args():
    """Provides the base argument list for testing save-dir."""
    return ["--save-dir", "/tmp/log"]

@pytest.fixture(scope="function")
def owner_base_args():
    """Provides the base argument list for testing owner"""
    return ['--owner']
