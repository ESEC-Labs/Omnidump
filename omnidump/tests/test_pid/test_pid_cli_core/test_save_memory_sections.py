"""
Test for Function categorize_region 

- save_memory_sections
- save_memeory_sections_bin_write

(pid_mapping_logic)
"""
from unittest import mock
from omnidump.pid_mapping_logic import save_memory_sections, save_memory_sections_bin_write
def test_sms_basic_pass(
    mock_click_secho,
    mock_get_section_info_basic_pass,
    mock_os_makedirs,
    mock_file_name_sections_basic_pass,
    mock_region_size_basic_pass,
    mock_chunk_data_basic_pass,
    mock_region,
    mock_output_path,
    mock_mem_path,
    mock_os_join_paths_basic_pass
):
    """
    Basic Success

    Goal: Verify successful reading and writing of a single valid region. 

    Assertions: Assert mem.seek, mem.read, and builtins.open 
                were called correctly. Asert the final success message 
                is printed. 
    """
    mock_get_section_info_basic_pass.return_value = ("40000000-40001000", "r-xp", "unusedpath", "unusedinode", "unusedmajminid")

    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        save_memory_sections(
            mem_path=mock_mem_path,
            regions_dict=[mock_region],
            output_path=mock_output_path
        )
        #Assert 1
        mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

        #Assert 2
        mock_open_call.assert_any_call(mock_mem_path, "rb")

        mock_mem_handle.seek.assert_called_once_with(0x40000000)
        mock_mem_handle.read.assert_called_once_with(mock_region_size_basic_pass)

        #Assert 3
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        mock_open_call.assert_any_call(expected_full_path, 'wb')
        mock_os_join_paths_basic_pass.assert_called_with(mock_output_path, mock_file_name_sections_basic_pass)
        #Second memory handle for writing bytes
        mock_bin_handle = mock_open_call.return_value.__enter__.return_value
        mock_bin_handle.write.assert_called_once_with(mock_chunk_data_basic_pass)

        #Assert 4
        success_message = f"Successfully saved 1 region(s) to '{mock_output_path}'."
        assert any(success_message in call[0][0] for call in mock_click_secho.call_args_list)

def test_sms_multi_regions_pass(
    mock_click_secho,
    mock_os_makedirs,
    mock_file_name_sections_basic_pass,
    mock_file_name_sl,
    mock_region_size_sl,
    mock_chunk_data_sl,
    mock_region_size_basic_pass,
    mock_regions_multi,
    mock_get_section_info_multi_region,
    mock_output_path,
    mock_os_join_paths_basic_pass,
    mock_chunk_data_basic_pass,
    mock_mem_path
):
    """
    Multiple Regions 

    Goal: Verify looping through and saving multiple regions works w/o issue

    Assertions: Assert the number of calls to mem.seek/mem.read matches the number of regions.
                Assert the sucess message shows the correct count. 
    """
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        #start both reads
        mock_mem_handle.read.side_effect = [
            mock_chunk_data_basic_pass,
            mock_chunk_data_sl
        ]

        save_memory_sections(
            mem_path=mock_mem_path,
            regions_dict=mock_regions_multi,
            output_path=mock_output_path
        )
        #assert 1
        mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

        #assert 2
        assert mock_mem_handle.seek.call_count == 2
        assert mock_mem_handle.read.call_count == 2

        mock_mem_handle.seek.assert_any_call(0x40000000)
        mock_mem_handle.read.assert_any_call(mock_region_size_basic_pass)

        mock_mem_handle.seek.assert_any_call(0x7f0000000000)
        mock_mem_handle.read.assert_any_call(mock_region_size_sl)

        #assert 3
        expected_full_path_1 = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        mock_open_call.assert_any_call(expected_full_path_1, 'wb')

        #check call for region 2
        #assume join mock only return first filename
        #check second write's content

        mock_bin_handle = mock_open_call.return_value.__enter__.return_value
        assert mock_bin_handle.write.call_count == 2
        mock_bin_handle.write.assert_any_call(mock_chunk_data_basic_pass)
        mock_bin_handle.write.assert_any_call(mock_chunk_data_sl)

        #assert 4
        success_message = f"Successfully saved 2 region(s) to '{mock_output_path}'."
        assert any (success_message in call[0][0] for call in mock_click_secho.call_args_list)

def test_sms_output_dir(
    mock_get_section_info_basic_pass,
    mock_os_makedirs,
    mock_chunk_data_basic_pass,
    mock_region,
    mock_output_path,
    mock_mem_path,
):
    """
    Output Directory Creation 

    Goal: Verify os.makedirs(exist_ok=True) is called correctly. 

    Assertions: Assert os.makedirs is called with output_path and 
                exist_ok=True. 
    """
    mock_get_section_info_basic_pass.return_value = ("40000000-40001000", "r-xp", "unusedpath", "unusedinode", "unusedmajminid")

    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        save_memory_sections(
            mem_path=mock_mem_path,
            regions_dict=[mock_region],
            output_path=mock_output_path
        )
        #Assert 1
        mock_os_makedirs.assert_any_call(mock_output_path, exist_ok=True)

def test_sms_invalid_address(
    mock_mem_path,
    mock_invalid_region,
    mock_output_path,
    mock_os_makedirs,
    mock_click_secho,
    mock_get_section_info_invalid
):
    """
    Invalid Address 

    Goal: Verify the ValueError from int(x, 16) is caught logged, 
          and the loop continues. 

    Assertions: Assert mem.seek() and mem.read() were not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open):
        save_memory_sections(
            mem_path=mock_mem_path,
            regions_dict=[mock_invalid_region],
            output_path=mock_output_path
        )
        #Assert 1
        mock_os_makedirs.assert_any_call(mock_output_path, exist_ok=True)
        #Assert 2
        error_message_printed = any(
                "" in call[0][0]                     
                for call in mock_click_secho.call_args_list
        )
        assert error_message_printed is True
        #Assert 3
        mock_get_section_info_invalid.assert_called_once_with(mock_invalid_region)
        #Assert 4
        success_message_printed = any(
                "Successfully saved 1 region(s)" in call[0][0]
                for call in mock_click_secho.call_args_list
        )

        assert success_message_printed is True

def test_sms_permissions_skip(
        mock_get_section_info_no_read, 
        mock_chunk_data_basic_pass,
        mock_mem_path,
        mock_region,
        mock_output_path,
        mock_os_makedirs,
        mock_click_secho
):
    """
    Permission Skip 

    Goal: Verify the entire I/O block is skipped if read permission 
          ("r") is missing. 

    Assertions: Assert mem.seek() and mem.read() were not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        save_memory_sections(
                mem_path=mock_mem_path,
                regions_dict=[mock_region],
                output_path=mock_output_path
        )

        #Assert 1
        mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

        #Assert 2
        mock_open_call.assert_any_call(mock_mem_path, "rb")
        mock_mem_handle.seek.assert_not_called()
        mock_mem_handle.read.assert_not_called()
        #Assert 3
        success_message_printed = any(
            "Successfully saved 1 region(s)" in call[0][0] 
            for call in mock_click_secho.call_args_list
        )
        assert success_message_printed is True

def test_sms_zero_size_skip (
        mock_chunk_data_basic_pass,
        mock_mem_path,
        mock_region_zero_skip,
        mock_os_makedirs,
        mock_output_path
):
    """
    Zero/Negative Size Skip 

    Goal: Verify regions where end <= start are skipped. 

    Assertions: Assert mem.seek() and mem.read() were not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        save_memory_sections(
                mem_path=mock_mem_path,
                regions_dict=[mock_region_zero_skip],
                output_path=mock_output_path
        )

        #Assert 1
        mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

        #Assert 2
        mock_open_call.assert_any_call(mock_mem_path, "rb")
        mock_mem_handle.seek.assert_not_called()
        mock_mem_handle.read.assert_not_called()

def test_smsbw_os_error(
        mock_output_path,
        mock_click_secho,
        mock_end_address_basic,
        mock_start_address_basic,
        mock_chunk_data_basic_pass,
        mock_os_join_paths_basic_pass,
        mock_file_name_sections_basic_pass
    ):
    """
    Read Error (OS error)

    Goal: Verify an OSError that occurs when saving the file is caught 
          gracefully. 

    Assertions: Assert the os error in the macro. 
    """
    test_os_error  = OSError(13, "Permission denied")

    with mock.patch('builtins.open', side_effect=test_os_error) as mock_open_call:
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)

        save_memory_sections_bin_write(
            full_file_path=expected_full_path,
            chunk=mock_chunk_data_basic_pass,
            start=mock_start_address_basic,
            end=mock_end_address_basic
        )

        #Assert 1
        mock_open_call.assert_called_once_with(expected_full_path, 'wb')

        #Assert 2
        error_message_printed = any(
                "Could not write chunk to binary file for region" in call[0][0] 
                for call in mock_click_secho.call_args_list
        )

        assert error_message_printed is True
