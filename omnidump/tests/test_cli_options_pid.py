import pytest
from click.testing import CliRunner
from omnidump.cli import main  

class TestGeneralCli:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help_message(self):
        # Test that the --help flag works and provides a zero exit code
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Omnidump CLI memory dumping tool" in result.output
