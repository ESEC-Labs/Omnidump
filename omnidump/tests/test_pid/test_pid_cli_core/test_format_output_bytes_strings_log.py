"""Test for Function test_format_output_bytes_strings_log (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import format_output_bytes_strings_log
def test_fobstl_single_section_strings_saved(
    memory_map_exe,
    mock_mem_path,
    mock_output_path,
    mock_smst,
    mock_os_join_paths_smn,
    mock_click_secho,
    mock_fobstl_single_section_strings_saved_config
):
    """
    Single Section Strings Saved

    Goal: Verify correct delegation to save_memory_strings. 

    Assertions: Assert save_memory_strings is called once with section_dict=[r1],
                the correct section_output_dir, and length_out. 
                Assert click.secho is not called. 
    """
    section_flag_dict = {
        "executable": mock_fobstl_single_section_strings_saved_config.flag_exec_sec
    }

    format_output_bytes_strings_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_exe,
        section_flag_dict=section_flag_dict,
        config=mock_fobstl_single_section_strings_saved_config
    )

    #Assert 1
    mock_smst.assert_called_once_with(
        mock_mem_path,
        memory_map_exe["executable"],
        mock_os_join_paths_smn(mock_output_path, "executable"),
        mock_fobstl_single_section_strings_saved_config
    )

    #Assert 2
    mock_click_secho.assert_not_called()

def test_fobstl_invalid_output_path(
    mock_mem_path,
    memory_map_exe,
    mock_click_secho,
    section_flag_dict_empty,
    mock_smst,
    mock_fobstl_invalid_output_path_config
):
    """
    Invalid save_dir type

    Goal: Verify the guard clause at the top handles non-string save_dir. 

    Assertions: Assert click.secho is called once with the "Internal Error"
                message. Assert the function returns immediately. 
    """
    format_output_bytes_strings_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_exe,
        section_flag_dict=section_flag_dict_empty,
        config=mock_fobstl_invalid_output_path_config
    )
    #Assert 1
    expected_msg = "Internal Error: save_dir is not a valid path string (None)."
    mock_click_secho.assert_called_once_with(expected_msg)

    #Assert 2
    mock_smst.assert_not_called()
