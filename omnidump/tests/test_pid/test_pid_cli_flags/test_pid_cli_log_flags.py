'''PID log flags test'''
import pytest 
from omnidump.cli import dump_pid

SECTION_FLAG_DATA = [
    "-e", "-sl", "--all", "-h", "-st", "-vv", "-vs", "-vd", 
    "--unclassified", "-an", "-gp", "-fb", "-ts", "-dm" 
]
def test_pid_none_log_save_dir_fail(cli_runner, self_base_args, save_dir_base_args):
    '''Self flag, Log unclassiied and save dir flag without section flags. Returns error code 15'''
    args = self_base_args + ['--unclassified'] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 15
    assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_length_none_log_save_dir_fail(cli_runner, self_base_args, flags, save_dir_base_args):
    '''Self flag, Strings out, log unclassified flag with section flags, and length flag with. Returns error code 3'''
    args = self_base_args + ['--strings', '--length', '-1', '--log-unclassified', flags] + save_dir_base_args
    expected_output = (
        "Error: The '--log-unclassified' flag"
        " cannot be used with any other section flags."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 3
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_strings_log_flags_save_dir_fail(cli_runner, save_dir_base_args, flags):
    """Log strings, section flags, and save dir without PID or self. Returns error code 2."""
    args = ["--log-strings", flags] + save_dir_base_args
    expected_output = (
        "Error: A PID or --self flag is required."
        "Please run omnidump dump pid --help for more information."
    )
    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

def test_strings_log_all_save_dir_fail(cli_runner, save_dir_base_args):
    """Log strings, all flag, and save dir without PID or --self. Returns error code 2."""
    args = ["--log-strings", "--all"] + save_dir_base_args
    expected_output = (
        "Error: A PID or --self flag is required." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_verbose_length_none_log_flags_save_dir_fail(self_base_args, flags, cli_runner, save_dir_base_args):
    '''Self flag, Verbose out, length out bad input, log unclassified, section flags, and save dir. Returns error code 3'''
    args = self_base_args + ["--verbose", "--length", "0", "--log-unclassified", flags] + save_dir_base_args
    expected_output = (
        "Error: The '--log-unclassified' flag"
        " cannot be used with any other section flags."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 3
    assert expected_output in result.output

def test_none_log_save_dir_fail(cli_runner, save_dir_base_args):
    """Log unclassified, and save dir without PID or self. Returns error code 2."""
    args = ["--log-unclassified"] + save_dir_base_args
    expected_output = (
        "Error: A PID or --self flag is required." 
        "Please run omnidump dump pid --help for more information."
    )
    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_sections_log_flags_save_dir_fail(cli_runner, flags, save_dir_base_args):
    """Log sections, section flags, and save dir without PID and self flag. Returns error code 2."""
    args = ["--log-sections", flags] + save_dir_base_args
    expected_output = (
        "Error: A PID or --self flag is required."
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 2
    assert expected_output in result.output

def test_pid_none_log_length_save_dir_fail(self_base_args, cli_runner, save_dir_base_args):
    """Self flag, Log unclassified, length valid input, and save dir flag. Returns error code 4."""
    args = self_base_args + ["--log-unclassified", "--length", "5"] + save_dir_base_args
    expected_output = (
        "Error: When using '--log-unclassified', the '--length'"
        " flag requires the '--verbose' flag." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 4
    assert expected_output in result.output

def test_pid_none_log_length_fail(self_base_args, cli_runner):
    """Self flag, Log unclassified, length valid input, and verbose flag. Returns error code 5"""
    args = self_base_args + ["--log-unclassified", "--length", "5", "--verbose"]
    expected_output = (
        "Error: When using '--log-unclassified', the '--save-dir' flag is required." 
        "Please run omnidump dump pid --help for more information."
    )
    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 5
    assert expected_output in result.output

def test_pid_sections_log_save_dir_fail(self_base_args, cli_runner, save_dir_base_args):
    """Self flag, Log sections, and save dir without section flags. Returns error code 6"""
    args = self_base_args + ["--log-sections"] + save_dir_base_args
    expected_output = (
        "Error: The '--log-sections' flag requires" 
        "at least one section flag (-e, -h, etc.) to be specified."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 6
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_sections_log_flags_fail(self_base_args, cli_runner, flags):
    """Self flag, Log sections, and section flags without save dir flag. Returns error code 7."""
    args = self_base_args + ["--log-sections", flags]
    expected_output = (
        "Error: When using '--log-sections', the '--save-dir' flag is required." 
        "Please run omnidump dump pid --help for more information."
    )

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 7
    assert expected_output in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_sections_log_flags_save_dir_verbose_fail(self_base_args, cli_runner, flags, save_dir_base_args):
    """Self flag, Log sections, section flags, verbose out, and save dir. Returns error code 8."""
    args = self_base_args + ["--log-sections", flags, "--verbose"] + save_dir_base_args
    expected_output = (
        "Error: When using '--log-sections'," 
        "please reframe from using other flags such as:"
        " '--length', and '--verbose'." 
        "Please run omnidump dump pid --help for more information."
    )
    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 8
    assert expected_output in result.output

def test_pid_strings_log_save_dir_fail(self_base_args, cli_runner, save_dir_base_args):
    """Self flag, log strings, and save dir without section flags. Returns error code 9."""
    args = self_base_args + ["--log-strings"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 9
    assert "Error: The '--log-strings' flag requires at least one section flag (-e, -h, etc.) to be specified." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_log_flags_fail(self_base_args, cli_runner, flags):
    """Self flag, log strings, and section flags without save dir flag. Returns error code 10."""
    args = self_base_args + ["--log-strings", flags]

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 10
    assert "Error: When using '--log-sections', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_log_flags_length_save_dir_11(self_base_args, cli_runner, flags, save_dir_base_args):
    """Log strings, legnth valid input, section flags, and save dir. Return error code 11."""
    args = self_base_args + ["--log-strings", "--length", "5" ,flags] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 11
    assert "Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information." in result.output

def test_pid_strings_log_flags_length_save_dir_12(self_base_args, cli_runner):
    """Self flag only without section flag. Return error code 12."""
    args = self_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 12
    assert "Error: The '--self' or 'pid' flag requires at least one section flag." in result.output

@pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
def test_pid_strings_log_flags_save_dir_pass(self_base_args, cli_runner, flags, save_dir_base_args):
    """Self flags, log strings, section flags, and save dir. Returns error code 0."""
    args = self_base_args + ["--log-strings", flags] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0

def test_pid_strings_log_none_out_save_dir_pass(self_base_args, cli_runner, save_dir_base_args):
    """Self flags, log strings, unclassified flag, and save dir. Returns error 0."""
    args = self_base_args + ["--log-strings", "--unclassified"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0


def test_pid_none_log_length_verbose_save_dir_pass(self_base_args, cli_runner, save_dir_base_args):
    """Self flags, log unclassified, length valid input, verbose out, and save dir. Returns error code 0."""
    args = self_base_args + ["--log-unclassified", "--length", "5", "--verbose"] + save_dir_base_args

    result = cli_runner.invoke(dump_pid, args)
    assert result.exit_code == 0


