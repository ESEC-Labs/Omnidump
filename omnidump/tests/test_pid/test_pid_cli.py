import pytest
from click.testing import CliRunner
from omnidump.cli import dump_pid  


'''
Within each Test{PID, SELF}Argument There are three types of test. 

    1. Test Intended to fail.

    2. Test Intended to pass.

'''

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

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert "Error: The '--log-unclassified' flag cannot be used with any other section flags." in result.output
    
    def test_save_dir_fail(self, cli_runner):
        args = ["--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2
        assert "Error: Option '--save-dir' requires an argument." in result.output

    def test_pid_verbose_length_none_out_fail(self, cli_runner, self_base_args):
        args = self_base_args + ["--verbose", "--length" ,"0", "--unclassified"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_strings_length_all_save_dir_fail(self, cli_runner, self_base_args, save_dir_base_args):
        args = self_base_args + ["--strings", "--length", "-1", "--all"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_verbose_length_none_out_fail(self, cli_runner, self_base_args):
        args = self_base_args + ["--verbose", "--length", "-1", "--unclassified"] 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_sections_flags_save_dir_fail(self, cli_runner, save_dir_base_args, flags):
        args = ["--log-sections", "--length", "-1", "--unclassified"] 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_verbose_length_all_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "5", "--all"] + save_dir_base_args 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 15  
        assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output
   
    def test_pid_verbose_length_all_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "5", "--all"] + save_dir_base_args 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 15  
        assert "Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_strings_log_flags_save_dir_fail(self, cli_runner, save_dir_base_args, flags):
        args = ["--log-strings", flags] + save_dir_base_args 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_length_flags_save_dir_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--length", "0", flags, "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: Option '--save-dir' requires an argument." in result.output
    
    def test_fail(self, cli_runner):
        args = []

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output
   
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_flags_save_dir_fail(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "0", flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14 
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    def test_none_out_fail(self, cli_runner):
        args = ["--unclassified"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2 
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_flags_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args, flags):
        args = self_base_args + ["--verbose", "--length", "5", "--log-unclassified", flags] + save_dir_base_args  

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert "Error: The '--log-unclassified' flag cannot be used with any other section flags." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_strings_length_flags_save_dir_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--strings", "--length", "-1", flags, "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: Option '--save-dir' requires an argument." in result.output

    def test_strings_log_all_save_dir_fail(self, cli_runner, save_dir_base_args):
        args = ["--log-strings", "--all"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_verbose_length_none_log_flags_save_dir_fail(self, self_base_args, flags, cli_runner, save_dir_base_args):
        args = self_base_args + ["--verbose", "--length", "0", "--log-unclassified", flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 3
        assert "Error: The '--log-unclassified' flag cannot be used with any other section flags." in result.output
    
    def test_pid_verbose_length_all_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--verbose", "--length", "0", "--all"] 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 14
        assert "Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information." in result.output
    
    def test_none_log_save_dir_fail(self, cli_runner, save_dir_base_args):
        args = ["--log-unclassified"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output
    
    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_sections_log_flags_save_dir_fail(self, cli_runner, flags, save_dir_base_args):
        args = ["--log-sections", flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_strings_length_none_out_save_dir_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--strings", "--length", "5", "--unclassified", "--save-dir"]

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 2  
        assert "Error: Option '--save-dir' requires an argument." in result.output
    
    def test_pid_none_log_length_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-unclassified", "--length", "5"] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 4  
        assert "Error: When using '--log-unclassified', the '--length' flag requires the '--verbose' flag. Please run omnidump dump pid --help for more information." in result.output
    
    def test_pid_none_log_length_fail(self, self_base_args, cli_runner):
        args = self_base_args + ["--log-unclassified", "--length", "5", "--verbose"] 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 5 
        assert "Error: When using '--log-unclassified', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information." in result.output
    
    def test_pid_sections_log_save_dir_fail(self, self_base_args, cli_runner, save_dir_base_args):
        args = self_base_args + ["--log-sections"] + save_dir_base_args 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 6 
        assert "Error: The '--log-sections' flag requires at least one section flag (-e, -h, etc.) to be specified." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_sections_log_flags_fail(self, self_base_args, cli_runner, flags):
        args = self_base_args + ["--log-sections", flags] 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 7
        assert "Error: When using '--log-sections', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information." in result.output

    @pytest.mark.parametrize("flags", SECTION_FLAG_DATA)
    def test_pid_sections_log_flags_save_dir_verbose_fail(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--log-sections", flags, "--verbose"] + save_dir_base_args 

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 8
        assert "Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information." in result.output
    
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
    def test_pid_strings_log_flags_length_save_dir_fail(self, self_base_args, cli_runner, flags, save_dir_base_args):
        args = self_base_args + ["--log-strings", "--length", "5" ,flags] + save_dir_base_args

        result = cli_runner.invoke(dump_pid, args)
        assert result.exit_code == 11
        assert "Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information." in result.output

    def test_pid_strings_log_flags_length_save_dir_fail(self, self_base_args, cli_runner):
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
