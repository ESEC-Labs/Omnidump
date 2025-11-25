"""Test for Function format_output_bytes (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import format_output_bytes

def test_fob_priority_none_log(
    mock_fobnl,
    mock_fobsl,
    mock_fobstl,
    mock_fobcl,
    mock_input_flag_fob_none,
    mock_click_secho,
    mock_fob_priority_none_log_config,
    mock_mem_path
):
    """
    Priority None Log

    Goal: Verify flag_none_log takes the highest priority. 

    Assertions: Assert fobnl is called. Assert fobsl, fobstl, and fobcl are not called.
                Assert the final summary block is skipped (flag_none_log is true).
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_none, 
        'config': mock_fob_priority_none_log_config 
    }

    format_output_bytes(**all_args)

    #Assert 1
    mock_fobnl.assert_called_once()
    #Assert 2
    mock_fobsl.assert_not_called()
    #Assert 3
    mock_fobstl.assert_not_called()
    #Assert 4
    mock_fobcl.assert_not_called()
    #Assert 5
    mock_click_secho.assert_not_called()

def test_fob_priority_sections_log(
    mock_fobstl,
    mock_fobsl,
    mock_fobcl,
    mock_input_flag_fob_exe,
    mock_click_secho,
    mock_fob_priority_sections_log_config,
    mock_mem_path
):
    """
    Priority Sections Log 

    Goal: Verify flag_sec_log takes priority over string/console output

    Assertions: Assert fobsl is called. Assert fobstl and fobcl are not called.
                Assert the final summary block is skipped (flag_none_log is True). 
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_exe,
        'config': mock_fob_priority_sections_log_config 
    }

    format_output_bytes(**all_args)

    #Assert 1
    mock_fobsl.assert_called_once()

    #Assert 2
    mock_fobstl.assert_not_called()

    #Assert 3
    mock_fobcl.assert_not_called()
    #Assert 4
    mock_click_secho.assert_not_called()

def test_fob_priority_strings_log(
    mock_fobstl,
    mock_fobcl,
    mock_input_flag_fob_exe,
    mock_click_secho,
    mock_fob_priority_strings_log_config,
    mock_mem_path
):
    """
    Priority Strings Log

    Goal: Verify flag_strings_log takes priority over console output. 

    Assertions: Assert format_output_bytes_strings_log is called. 
                Assert format_output_bytes_console_log is not called.
                Assert the final summary block is executed 
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_exe,
        'config': mock_fob_priority_strings_log_config 
    }

    format_output_bytes(**all_args)

    #Assert 1
    mock_fobstl.assert_called_once()

    #Assert 2
    mock_fobcl.assert_not_called()

    #Assert 3
    mock_click_secho.assert_not_called()

def test_fob_priority_console_log(
    mock_input_flag_fob_exe,
    mock_click_secho,
    mock_fobcl,
    mock_fob_priority_console_log_config,
    mock_mem_path
):
    """
    Priority Console Log

    Goal: Verify console output is the default when no logging flags are set. 

    Assertions: Assert fobstl is called. Assert fobcl is not called. 
                Assert the final summary block is executed. 
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_exe, 
        'config': mock_fob_priority_console_log_config
    }

    format_output_bytes(**all_args)

    #Assert 1
    mock_fobcl.assert_called_once()

    #Assert 2
    mock_click_secho.assert_not_called()

def test_fob_summary_block(
    mock_input_flag_fob_none,
    mock_click_secho,
    mock_mem_path,
    mock_fob_priority_console_log_config
):
    """
    Final Summary Block (Executed)

    Goal: Verify the summary for unclassified regions is printed when neither flag_none_log 
          nor flag_sec_log are set. 

    Assertions: Assert click.secho is called with the 
                yellow summary messages about unclassified regions
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_none, 
        'config': mock_fob_priority_console_log_config
    }

    format_output_bytes(**all_args)

    #Assert 1
    expected_msg = "Use '--log-unclassified' command to save them to a log file."
    mock_click_secho.assert_called_with(expected_msg, fg="yellow")

def test_fob_summary_block_skipped(
    mock_input_flag_fob_none_empty,
    mock_click_secho,
    mock_mem_path,
    mock_fob_priority_console_log_config
):
    """
    Final Summary Block (Skipped)

    Goal: Verify the summary is skipped when the "none" category is empty. 

    Assertions: Assert click.secho is not called with the summary messages.  
    """
    all_args = {
        'mem_path': mock_mem_path,
        'input_dict': mock_input_flag_fob_none_empty, 
        'config': mock_fob_priority_console_log_config
    }

    format_output_bytes(**all_args)

    #Assert 1
    expected_msg = "No memory regions were selected for console output."
    mock_click_secho.assert_called_with(expected_msg, fg="red")
