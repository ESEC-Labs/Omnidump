"""Test for Function format_output_bytes_section_log (pid_mapping_logic)"""
from unittest import mock
from omnidump.pid_mapping_logic import format_output_bytes_section_log

def test_fobsl_single_section_save(
        mock_mem_path,
        mock_output_path,
        memory_map_multi_exe_sl,
        mock_save_memory_sections,
        mock_os_join_paths_smn,
        mock_click_secho,
        mock_fobsl_single_section_save_config
):
    """
    Single Section Save 

    Goal: Verify correct delegation for a single enabled flag (executable)

    Assertions: Assert save_memory_sections is called once with section_dict=[r1]
                and the expected section_output_dir(os.path.join(save_dir, "executable")). 
                Assert click.secho is not called. 
    """
    section_flag_dict = {
        "flag_exec_sec": mock_fobsl_single_section_save_config.flag_exec_sec
    }

    format_output_bytes_section_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_multi_exe_sl,
        section_flag_dict=section_flag_dict,
        config=mock_fobsl_single_section_save_config
    )
    #Assert 1
    mock_save_memory_sections.assert_called_once_with(
            mock_mem_path,
            memory_map_multi_exe_sl['executable'],
            mock_os_join_paths_smn(mock_output_path, "executable")
    )
    #Assert 2
    mock_click_secho.assert_not_called()

def test_fobsl_multi_sect_save(
        mock_mem_path,
        mock_output_path,
        mock_save_memory_sections,
        mock_os_join_paths_smn,
        memory_map_multi_exe_sl,
        mock_fobsl_multi_sect_save_config
):
    """
    Multiple Sections Saved 

    Goal: Verify correct delegation for multiple enabled flags. 

    Assertions: Assert save_memory_sections is called twice, once
                for each section, with the correct dictionary and output 
                directory for each. 
    """
    section_flag_dict_multi={
        "flag_exec_sec": mock_fobsl_multi_sect_save_config.flag_exec_sec,
        "flag_slib_sec": mock_fobsl_multi_sect_save_config.flag_slib_sec
    }

    format_output_bytes_section_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_multi_exe_sl,
        section_flag_dict=section_flag_dict_multi,
        config=mock_fobsl_multi_sect_save_config
    )

    #Assert 1
    expected_calls = [
        mock.call(
            mock_mem_path,
            memory_map_multi_exe_sl['executable'],
            mock_os_join_paths_smn(mock_output_path, "executable")
        ),

        mock.call(
            mock_mem_path,
            memory_map_multi_exe_sl['shared_libs'],
            mock_os_join_paths_smn(mock_output_path, "shared_libs")
        )
    ]
    #Assert 2
    assert mock_save_memory_sections.call_count == 2
    #Assert 3
    mock_save_memory_sections.assert_has_calls(expected_calls, any_order=True)

def test_fobsl_section_empty(
        mock_mem_path,
        mock_save_memory_sections,
        memory_map_exe_e,
        mock_click_secho,
        mock_fobsl_single_section_save_config
):
    """
    Section Empty

    Goal: Verify message is printed when a required section is empty

    Assertions: Assert save_memory_sections is not called. 
                Assert click.secho is called once with the yellow message: 
                "No regions found for section 'executable'."
    """
    section_flag_dict = {
        "flag_exec_sec": mock_fobsl_single_section_save_config.flag_exec_sec
    }

    format_output_bytes_section_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_exe_e,
        section_flag_dict=section_flag_dict,
        config=mock_fobsl_single_section_save_config
    )
    #Assert 1
    mock_save_memory_sections.assert_not_called()

    #Assert 2
    expected_msg = "No regions found for section 'executable'."
    mock_click_secho.assert_called_once_with(expected_msg, fg="yellow")
