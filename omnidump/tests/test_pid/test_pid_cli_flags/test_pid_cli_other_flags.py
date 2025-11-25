"""PID Other flags tests (section flags, and output flags i.e. --length, --verbose, -e, and -sl"""
import pytest
from omnidump.cli import dump_pid

SECTION_FLAG_DATA = [
    "-e", "-sl", "--all", "-h", "-st", "-vv", "-vs", "-vd", 
    "--unclassified", "-an", "-gp", "-fb", "-ts", "-dm" 
]

def test_pid_verbose_length_none_out_save_dir_fail(cli_runner, self_base_args, save_dir_base_args):
    """Self flag, verbose out, length valid input, unclassified flag, and save dir flag. Returns error code 2."""
    args = self_base_args + ['--verbose', '--length', '5', '--unclassified', '--save-dir']

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert "Error: Option '--save-dir' requires an argument." in result.output

def test_save_dir_fail(cli_runner):
    """Save dir flag. Needs log flag/section flags. Returns error code 2."""
    args = ["--save-dir"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert "Error: Option '--save-dir' requires an argument." in result.output

def test_pid_verbose_length_none_out_zero(cli_runner, self_base_args):
    """Self flags, verbose out, length out, and unclassified flag. Returns error code 14."""
    args = self_base_args + ["--verbose", "--length" ,"0", "--unclassified"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 14
    assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

def test_pid_strings_length_all_save_dir_fail(cli_runner, self_base_args, save_dir_base_args):
    """Self flags, strings out, length invalid input, all flag, and save dir flag. Returns error code 14."""
    args = self_base_args + ["--strings", "--length", "-1", "--all"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 14
    assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

def test_pid_verbose_length_none_out_negative(cli_runner, self_base_args):
    """Self flags, verbose out, length invalid input, and unclassified flag. Returns error code 14."""
    args = self_base_args + ["--verbose", "--length", "-1", "--unclassified"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 14
    assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_sections_flags_save_dir_fail(cli_runner, save_dir_base_args, flags):
    """Log sections, legnth invalid input, and unclassified flag. Returns error code 2."""
    args = ["--log-sections", "--length", "-1", "--unclassified"]
    expected_output = (
        "Error: A PID or --self flag is required." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

def test_pid_verbose_length_all_save_dir_fail(self_base_args, cli_runner, save_dir_base_args):
    """Self flags, verbose out, length valid input, all flag and save dir flag. Returns error code 15."""
    args = self_base_args + ["--verbose", "--length", "5", "--all"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 15
    assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_length_flags_save_dir_fail(self_base_args, cli_runner, flags):
    """Self flags, length invalid input, section flags, and save dir flag. Returns error code 2."""
    args = self_base_args + ["--length", "0", flags, "--save-dir"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert "Error: Option '--save-dir' requires an argument." in result.output

def test_fail(cli_runner):
    """No input args. Needs PID or self flag. Returns error code 2."""
    args = []
    expected_output = (
        "Error: A PID or --self flag is required." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_verbose_length_flags_save_dir_14(self_base_args, cli_runner, flags, save_dir_base_args):
    """Self flags, verbose out, length invalid input, section flags, and save dir flag. Returns error code 14."""
    args = self_base_args + ["--verbose", "--length", "0", flags] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 14
    assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

def test_none_out_fail(cli_runner):
    """Unclassified flag only. Needs PID or self. Returns error code 2."""
    args = ["--unclassified"]
    expected_output = (
        "Error: A PID or --self flag is required." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_verbose_length_flags_save_dir_3(self_base_args, cli_runner, save_dir_base_args, flags):
    """Self flags, verbose out, length valid input, log unclassified, section flags and save dir. Returns error code 3."""
    args = self_base_args + ["--verbose", "--length", "5", "--log-unclassified", flags] + save_dir_base_args
    expected_output = (
        "Error: The '--log-unclassified' flag"
        " cannot be used with any other section flags."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 3
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_length_flags_save_dir_fail(self_base_args, cli_runner, flags):
    """Self flags, strings out, length invalid input, section flags, and save dir flag. Returns error code 2."""
    args = self_base_args + ["--strings", "--length", "-1", flags, "--save-dir"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert "Error: Option '--save-dir' requires an argument." in result.output

def test_pid_verbose_length_all_fail(self_base_args, cli_runner):
    """Self flags, verbose out, length invalid input, and all flag. Returns error code 14."""
    args = self_base_args + ["--verbose", "--length", "0", "--all"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 14
    assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

def test_pid_strings_length_none_out_save_dir_fail(self_base_args, cli_runner):
    """Self flags, strings out, length valid input, unclassified flag, and save dir flag. Returns error code 2."""
    args = self_base_args + ["--strings", "--length", "5", "--unclassified", "--save-dir"]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert "Error: Option '--save-dir' requires an argument." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_flags_length_fail(self_base_args, cli_runner, flags):
    """Self flags, length valid input, and section flags. Returns error code 13."""
    args = self_base_args + ["--length", "5", flags]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 13
    assert "Error: The '--length' flag requires the '--verbose' or the '--strings' flag. Please run omnidump dump pid --help for more information." in result.output

def test_pid_sections_none_out_save_dir_pass(self_base_args, cli_runner, save_dir_base_args):
    """Self flags, log sections, unclassified flag, and save dir flag. Returns error code 0."""
    args = self_base_args + ["--log-sections", "--unclassified"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_verbose_length_flags_save_dir_pass(self_base_args, cli_runner, flags):
    """Self flags, verbose out, length valid input, and section flags."""
    args = self_base_args + ["--verbose", "--length", "5", flags]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_flags_pass(cli_runner, self_base_args, flags):
    """Self flags, strings out, and section flags. Returns error code 0."""
    args = self_base_args + ['--strings', flags]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_verbose_flags_pass(cli_runner, self_base_args, flags):
    """Self flags, verbose out, and section flags. Returns error code 0."""
    args = self_base_args + ['--verbose', flags]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0

def test_pid_sections_all_save_dir_pass(self_base_args, cli_runner, save_dir_base_args):
    """Self flags, log sections, all flag, and save dir flag. Returns error code 0"""
    args = self_base_args + ["--log-sections", "--all"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0
