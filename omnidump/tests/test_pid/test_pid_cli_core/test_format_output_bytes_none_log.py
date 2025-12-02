"""Test for Function format_output_bytes_none_log (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import format_output_bytes_none_log

def test_fobnl_success(
        mock_mem_path,
        memory_map_dict,
        mock_click_secho,
        mock_smn_basic,
        mock_fobnl_success_config
):
    """ 
    Success Path 

    Goal: verify save_memory_none is called when "none" regions exist. 

    Assertions: Assert save_memory_none is called exactly once with the correct arguments: 
                mem_path, [region1], save_dir, length_out, and verbose_out. Assert 
                click.secho is not called. 
    """
    format_output_bytes_none_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_dict,
        config=mock_fobnl_success_config
    )

    mock_smn_basic.assert_called_once_with(
            mock_mem_path,
            memory_map_dict['none'],
            mock_fobnl_success_config
    )

    mock_click_secho.assert_not_called()

def test_fobnl_no_regions(
        mock_mem_path,
        memory_map_empty,
        mock_click_secho,
        mock_smn_basic,
        mock_fobnl_no_regions_config
):
    """
    No Regions Found

    Goal: Verify the user is informed when the "none" category is empty.

    Assertions: Assert save_memory_none is not called. Assert click.secho
                is called once with the yellow message: 
                "No unclassified regions found to save."
    """
    format_output_bytes_none_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_empty,
        config=mock_fobnl_no_regions_config
    )

    mock_smn_basic.assert_not_called()

    expected_msg = "No unclassified regions found to save."
    mock_click_secho.assert_called_once_with(expected_msg, fg="yellow")

def test_fobnl_missing_cat(
        mock_mem_path,
        memory_map_exe,
        mock_click_secho,
        mock_smn_basic,
        mock_fobnl_missing_cat_config
):
    """
    Category Missing

    Goal: Verify handling when the "none" key is missing entirely from input_dict.

    Assertions: Assert save_memory_none is not called. Assert click.secho is called 
                once with the yellow message. 
    """
    format_output_bytes_none_log(
        mem_path=mock_mem_path,
        input_dict=memory_map_exe,
        config=mock_fobnl_missing_cat_config
    )

    mock_smn_basic.assert_not_called()

    expected_msg = "No unclassified regions found to save."
    mock_click_secho.assert_called_once_with(expected_msg, fg="yellow")
