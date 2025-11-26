from click.testing import CliRunner
from omnidump.cli import dump_pid
from unittest import mock 
from datetime import datetime
import pytest

@pytest.fixture(scope="function")
def cli_runner(): 
    return CliRunner()

