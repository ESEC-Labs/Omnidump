from click.testing import CliRunner
from omnidump.cli import dump_pid
import subprocess
import sys
import time
import pytest
import os
import psutil
'''
---- Shared Resources ----
'''

@pytest.fixture(scope="function")
def cli_runner(): 
    return CliRunner()

@pytest.fixture(scope="function")
def self_base_args():
    """Provides the base argument list for testing self-dumps."""
    return ['--self'] 


@pytest.fixture(scope="session")
def save_dir_base_args():
    """Provides the base argument list for testing save-dir."""
    return ["--save-dir", "/tmp/log"]
'''
--- Data Fixtures ---
'''

@pytest.fixture(scope="session")
def section_flags():
    return [
        "-e", "-sl", "--all", "-h", "-st", "-vv", "-vs", "-vd", "--unclassified", "-an", "-gp", "-fb", "-ts", "-dm" 
    ]


