"""Test for Function format_output_bytes_console_log (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import format_output_bytes_console_log

def test_fobcl_selected_selections_output(
    mock_mem_path,
    memory_map_exe,
    mock_rbss,
    mock_console_output_config_selections_output
):
    """
    Selected Selections ouput

    Goal: Verify delegation when specific flags are set.

    Assertions: read_bytes_show_sections is called with sections_to_show containing ["heap"]
    """
    section_flag_dict = {
        "flag_exec_sec": mock_console_output_config_selections_output.flag_exec_sec
    }


    format_output_bytes_console_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_exe,
        section_flag_dict=section_flag_dict,
        config=mock_console_output_config_selections_output
    )
    #Assert 1
    mock_rbss.assert_called_once_with (
        mock_mem_path,
        memory_map_exe,
        ['executable'],
        mock_console_output_config_selections_output
    )

def test_fobcl_all_sections_output(
    mock_mem_path,
    mock_rbss,
    mock_input_flag_options,
    mock_console_output_config_sections_output
):
    """
    All Sections Output

    Goal: Verify the error message when no flags are set and flag_all_sec is false

    Assertions: read_bytes_show_sections is not called. Assert click.secho is called once
                with the red "No memory regions were selected..." message.
    """
    section_flag_dict_multi = {
        "flag_exec_sec": mock_console_output_config_sections_output.flag_exec_sec,
        "flag_slib_sec": mock_console_output_config_sections_output.flag_exec_sec 
    }

    format_output_bytes_console_log(
        mem_path=mock_mem_path,
        input_dict=mock_input_flag_options,
        section_flag_dict=section_flag_dict_multi,
        config=mock_console_output_config_sections_output
    )
    #Assert 1
    mock_rbss.assert_called_once_with(
        mock_mem_path,
        mock_input_flag_options,
        ['executable', 'shared_libs'],
        mock_console_output_config_sections_output
    )

def test_fobcl_no_sections_selected(
    mock_mem_path,
    mock_flag_options_empty,
    mock_rbss,
    mock_input_flag_options_empty,
    mock_click_secho,
    mock_console_output_config_no_sections_selected
):
    """
    No Sections Selected 
    
    Goal: Verify the error message when no flags are set and flag_all_sec is false

    Assertions: read_bytes_show_sections is not called. Assert click.secho is called once
                with the red no memory regions were selected..." message.
    """
    format_output_bytes_console_log(
        mem_path=mock_mem_path,
        input_dict=mock_input_flag_options_empty,
        section_flag_dict=mock_flag_options_empty,
        config=mock_console_output_config_no_sections_selected
    )
    #Assert 1
    mock_rbss.assert_not_called()

    #Assert 2
    expected_msg = "No memory regions were selected for console output."
    mock_click_secho.assert_called_once_with(expected_msg, fg="red")
