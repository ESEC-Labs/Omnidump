import randomm
import getpass
import string
import pytest
from omnidump.cli import dump_pid, show

SECTION_FLAG_DATA = [
    "-e", "-sl", "--all", "-h", "-st", "-vv", "-vs", "-vd", 
    "--unclassified", "-an", "-gp", "-fb", "-ts", "-dm" 
]

class TestSelfFail:

    def test_pid_none_log_save_dir_fail(self, cli_runner, self_base_args, save_dir_base_args):
        args = self_base_args + ['--unclassified'] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 15
        assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output

    def test_pid_verbose_length_none_out_save_dir_fail(self, cli_runner, self_base_args, save_dir_base_args):
        args = self_base_args + ['--verbose', '--length', '5', '--unclassified', '--save-dir']

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_length_none_log_save_dir_fail(self, cli_runner, self_base_args, flags, save_dir_base_args):
        args = self_base_args + ['--strings', '--length', '-1', '--log-unclassified', flags] + save_dir_base_args
        expected_output = (
            "Error: The '--log-unclassified' flag"
            " cannot be used with any other section flags."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert expected_output in result.output
    
    def test_save_dir_fail(self, cli_runner):
        args = ["--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output

    def test_pid_verbose_length_none_out_zero(self, cli_runner, self_base_args):
        args = self_base_args + ["--verbose", "--length" ,"0", "--unclassified"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_strings_length_all_save_dir_fail(self, cli_runner, self_base_args, save_dir_base_args):
        args = self_base_args + ["--strings", "--length", "-1", "--all"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_verbose_length_none_out_negative(self, cli_runner, self_base_args):
        args = self_base_args + ["--verbose", "--length", "-1", "--unclassified"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_sections_flags_save_dir_fail(self, cli_runner, save_dir_base_args, flags):
        args = ["--log-sections", "--length", "-1", "--unclassified"]
        expected_output = (
            "Error: A PID or --self flag is required." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output

    def test_pid_verbose_length_all_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "5", "--all"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 15
        assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_strings_log_flags_save_dir_fail(self, cli_runner, save_dir_base_args, flags):
        args = ["--log-strings", flags] + save_dir_base_args
        expected_output = (
            "Error: A PID or --self flag is required."
            "Please run omnidump dump pid --help for more information."
        )
        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_length_flags_save_dir_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--length", "0", flags, "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output
    
    def test_fail(self, cli_runner):
        args = []
        expected_output = (
            "Error: A PID or --self flag is required." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output
   
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_flags_save_dir_14(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "0", flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    def test_none_out_fail(self, cli_runner):
        args = ["--unclassified"]
        expected_output = (
            "Error: A PID or --self flag is required." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_flags_save_dir_3(self, self_base_args, cli_runner, save_dir_base_args, flags):
        args = self_base_args + ["--verbose", "--length", "5", "--log-unclassified", flags] + save_dir_base_args
        expected_output = (
            "Error: The '--log-unclassified' flag"
            " cannot be used with any other section flags."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert expected_output in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_length_flags_save_dir_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--strings", "--length", "-1", flags, "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output

    def test_strings_log_all_save_dir_fail(self, cli_runner, save_dir_base_args):
        args = ["--log-strings", "--all"] + save_dir_base_args
        expected_output = (
            "Error: A PID or --self flag is required." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_none_log_flags_save_dir_fail(self, self_base_args, flags, cli_runner, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "0", "--log-unclassified", flags] + save_dir_base_args
        expected_output = (
            "Error: The '--log-unclassified' flag"
            " cannot be used with any other section flags."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert expected_output in result.output
    
    def test_pid_verbose_length_all_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--verbose", "--length", "0", "--all"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    def test_none_log_save_dir_fail(self, cli_runner, save_dir_base_args):
        args = ["--log-unclassified"] + save_dir_base_args
        expected_output = (
            "Error: A PID or --self flag is required." 
            "Please run omnidump dump pid --help for more information."
        )
        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_sections_log_flags_save_dir_fail(self, cli_runner, flags, save_dir_base_args):
        args = ["--log-sections", flags] + save_dir_base_args
        expected_output = (
            "Error: A PID or --self flag is required."
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert expected_output in result.output

    def test_pid_strings_length_none_out_save_dir_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--strings", "--length", "5", "--unclassified", "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output
    
    def test_pid_none_log_length_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-unclassified", "--length", "5"] + save_dir_base_args
        expected_output = (
            "Error: When using '--log-unclassified', the '--length'"
            " flag requires the '--verbose' flag." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 4
        assert expected_output in result.output
    
    def test_pid_none_log_length_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--log-unclassified", "--length", "5", "--verbose"]
        expected_output = (
            "Error: When using '--log-unclassified', the '--save-dir' flag is required." 
            "Please run omnidump dump pid --help for more information."
        )
        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 5
        assert expected_output in result.output
    
    def test_pid_sections_log_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-sections"] + save_dir_base_args
        expected_output = (
            "Error: The '--log-sections' flag requires" 
            "at least one section flag (-e, -h, etc.) to be specified."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 6
        assert expected_output in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_sections_log_flags_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--log-sections", flags]
        expected_output = (
            "Error: When using '--log-sections', the '--save-dir' flag is required." 
            "Please run omnidump dump pid --help for more information."
        )

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 7
        assert expected_output in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_sections_log_flags_save_dir_verbose_fail(self, self_base_args, cli_runner, flags, save_dir_base_args):
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
    
    def test_pid_strings_log_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-strings"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 9
        assert "Error: The '--log-strings' flag requires at least one section flag (-e, -h, etc.) to be specified." in result.output
   
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_log_flags_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--log-strings", flags]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 10
        assert "Error: When using '--log-sections', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_log_flags_length_save_dir_11(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--log-strings", "--length", "5" ,flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 11
        assert "Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_strings_log_flags_length_save_dir_12(self, self_base_args, cli_runner):
        args = self_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 12
        assert "Error: The '--self' or 'pid' flag requires at least one section flag." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_flags_length_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--length", "5", flags]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 13
        assert "Error: The '--length' flag requires the '--verbose' or the '--strings' flag. Please run omnidump dump pid --help for more information." in result.output

class TestSelfPass:

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_flags_pass(self, cli_runner, self_base_args, flags):
        args = self_base_args + ['--strings', flags]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_flags_pass(self, cli_runner, self_base_args, flags):
        args = self_base_args + ['--verbose', flags]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    def test_pid_sections_all_save_dir_pass(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-sections", "--all"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_log_flags_save_dir_pass(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--log-strings", flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0
        
    def test_pid_sections_none_out_save_dir_pass(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-sections", "--unclassified"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_flags_save_dir_pass(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--verbose", "--length", "5", flags]  

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    def test_pid_strings_log_none_out_save_dir_pass(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-strings", "--unclassified"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0

    
    def test_pid_none_log_length_verbose_save_dir_pass(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-unclassified", "--length", "5", "--verbose"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 0


class TestShowFail:

    def test_show_owner_2(self, cli_runner, owner_base_args):
        args = owner_base_args

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 2
        assert "Error: Option '--owner' requires an argument." in result.output
    
    def test_show_owner_16(self, cli_runner, owner_base_args):
        length = 8
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        args = owner_base_args + [random_string]

        result = cli_runner.invoke(show, args)
        error_message = f"Showing processes...\nError: The user '{random_string}' doesn't exist.\n"
        assert result.exit_code == 16
        assert error_message in result.output

class TestShowPass:

    def test_show_owner_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
    
    def test_show_owner_idle_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-id"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
    
    def test_show_owner_running_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-rn"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_idle_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp", "-id"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_owner_sleeping_idle_running_pass(self, cli_runner, owner_base_args):
        username = getpass.getuser()
        args = owner_base_args + [username, "-sp", "-id", "-rn"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_pass(self, cli_runner):
        args = ["-sp"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_running_pass(self, cli_runner):
        args = ["-sp", "-rn"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_sleeping_running_idle_pass(self, cli_runner):
        args = ["-sp", "-rn", "-id"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_idle_pass(self, cli_runner):
        args = ["-id"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_idle_running_pass(self, cli_runner):
        args = ["-id", "-rn"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0

    def test_show_running_pass(self, cli_runner):
        args = ["-rn"]

        result = cli_runner.invoke(show, args)
        assert result.exit_code == 0
