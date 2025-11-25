"""Testing PID general CLI usage"""
from omnidump.cli import main

def test_help_message(cli_runner):
    """Test opening help meassage 'omnidump --help'"""
    # Test that the --help flag works and provides a zero exit code
    result = cli_runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "Omnidump CLI memory dumping tool" in result.output
