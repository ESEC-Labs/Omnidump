"""
Test for Functions

- save_memory_strings_read_bin 
- save_memory_strings 
- save_memory_strings_write 

(pid_mapping_logic)
"""
from unittest import mock
from omnidump.pid_mapping_logic import save_memory_strings_read_bin, save_memory_strings, save_memory_strings_write
def test_smsw_write(
        mock_smsw_strings_list,
        mock_os_join_paths_basic_pass,
        mock_output_path,
        mock_file_name_sections_basic_pass,
        mock_smsw_log_string
):
    """
    Sucessful Write 

    Goal: Verify the strings are written to the file in the correct format
          and the counter is incremented. 

    Assertions: Assert mock_file_handle.write() is called with a string containing: 
                '\n--Extracted Strings --\n ['a', 'b']'. Assert that 
                successful_saves_count is incremented by 1 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_write_handle = mock_open_call.return_value.__enter__.return_value
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_write(
            full_file_path=expected_full_path,
            string_list=mock_smsw_strings_list,
            successful_saves_count=count
        )

        expected_log_writes = [
            mock.call(mock_smsw_log_string),
        ]

        mock_write_handle.write.assert_has_calls(expected_log_writes, any_order=False)

        assert count[0] == 1

def test_smsw_os_error(
    mock_click_secho,
    mock_file_name_sections_basic_pass,
    mock_output_path,
    mock_os_join_paths_basic_pass,
    mock_smsw_strings_list
):
    """
    Write Error

    Goal: Verify OSError is caught and handled. 

    Assertions: Assert click.secho is called with the error message (Could not write strings...). 
    """
    test_os_error  = OSError(13, "Permission denied")

    with mock.patch('builtins.open', side_effect=test_os_error) as mock_open_call:
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_write(
            full_file_path=expected_full_path,
            string_list=mock_smsw_strings_list,
            successful_saves_count=count
        )

        #Assert 1
        mock_open_call.assert_called_once_with(expected_full_path, 'w')

        #Assert 2
        error_message_printed = any(
                "Could not write strings to file" in call[0][0]
                for call in mock_click_secho.call_args_list
        )

        assert error_message_printed is True

def test_smsrb_success(
    mock_get_section_info_basic_pass,
    mock_os_join_paths_basic_pass,
    mock_output_path,
    mock_file_name_sections_basic_pass,
    mock_region_size_basic_pass,
    mock_mem_path,
    mock_region,
    mock_sms_config
):
    """
    Full Success 

    Goal: Verify the function iterates, reads, memory, extracts strings, and calls
          save_memory_strings_write once per region. 

    Assertions: Assert mem.seek() and mem.read() are called correctly. Assert get_strings_from_bytes() is called.
                Assert save_memory_strings_write is called with the correct filename (region-*-strings.txt)
                and extracted strings. 
    """
    mock_get_section_info_basic_pass.return_value = ("40000000-40001000", "r-xp", "unusedpath", "unusedinode", "unusedmajminid")

    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_rb_handle = mock_open_call.return_value.__enter__.return_value
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_read_bin(
            full_file_path=expected_full_path,
            successful_saves_count=count,
            mem_path=mock_mem_path,
            regions_dict=[mock_region],
            output_path=mock_output_path,
            config=mock_sms_config
        )

        # Assert 1
        mock_rb_handle.seek.assert_any_call(0x40000000)
        # Assert 2
        mock_rb_handle.read.assert_any_call(mock_region_size_basic_pass)

def test_smsrb_multi_region_success(
    mock_smsw,
    mock_chunk_data_basic_pass,
    mock_chunk_data_sl,
    mock_regions_multi,
    mock_mem_path,
    mock_output_path,
    mock_os_join_paths_basic_pass,
    mock_file_name_sections_basic_pass,
    mock_sms_config
):
    """
    Multi-Region Success 

    Goal: Verify it correctly handles two regions in the loop 

    Assertions: Assert save_memory_strings_write is called twice, once for each expected filename. 
    """
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open_call:

        mock_mem_handle = mock_open_call.return_value.__enter__.return_value

        #start both reads

        mock_mem_handle.read.side_effect = [
            mock_chunk_data_basic_pass,
            mock_chunk_data_sl
        ]

        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_read_bin(
            full_file_path=expected_full_path,
            successful_saves_count=count,
            mem_path=mock_mem_path,
            regions_dict=mock_regions_multi,
            output_path=mock_output_path,
            config=mock_sms_config
        )
        #assert 1
        assert mock_mem_handle.seek.call_count == 2
        assert mock_mem_handle.read.call_count == 2

        #assert 2
        assert mock_smsw.call_count == 2

def test_smsrb_read_error(
    mock_click_secho,
    mock_output_path,
    mock_file_name_sections_basic_pass,
    mock_os_join_paths_basic_pass,
    mock_mem_path,
    mock_region,
    mock_smsw,
    mock_sms_config
):
    """
    Read Error

    Goal: Verify I/O error during memory read is caught 

    Assertions: Assert click.secho is called with the "Could not read region"
                error message. Assert save_memory_strings_write is not called 
                for that region. 
    """
    test_os_error  = OSError(13, "Permission denied")

    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        mock_mem_handle.seek.side_effect = test_os_error

        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_read_bin(
            full_file_path=expected_full_path,
            successful_saves_count=count,
            mem_path=mock_mem_path,
            regions_dict=[mock_region],
            output_path=mock_output_path,
            config=mock_sms_config
        )

        #Assert 1
        mock_open_call.assert_called_once_with(mock_mem_path, 'rb')
        #Assert 2
        mock_mem_handle.seek.assert_called_once()
        assert mock_smsw.call_count == 0

        #Assert 3
        error_message_printed = any(
                "Could not read region" in call[0][0] 
                for call in mock_click_secho.call_args_list
        )

        assert error_message_printed is True

def test_smsrb_value_error(
    mock_os_join_paths_basic_pass,
    mock_output_path,
    mock_file_name_sections_basic_pass,
    mock_mem_path,
    mock_invalid_region,
    mock_click_secho,
    mock_sms_config
):
    """
    Invalid Address Skipp 

    Goal: Verify ValueError during parsing is caught. 

    Assertions: Assert click.secho is called with the yellow "Invalid address format" message. 
                Assert mem.seek/read are not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        count = [0]

        save_memory_strings_read_bin(
            full_file_path=expected_full_path,
            successful_saves_count=count,
            mem_path=mock_mem_path,
            regions_dict=[mock_invalid_region],
            output_path=mock_output_path,
            config=mock_sms_config
        )

        #Assert 2
        error_message_printed = any(
                "Invalid address format for" in call[0][0]                     
                for call in mock_click_secho.call_args_list
        )
        assert error_message_printed is True

        #Assert 3
        mock_mem_handle.seek.assert_not_called()
        mock_mem_handle.read.assert_not_called()

def test_smstrings_setup(
    mock_os_makedirs,
    mock_mem_path,
    mock_region,
    mock_output_path,
    mock_smsrb,
    mock_click_secho,
    mock_os_join_paths_basic_pass,
    mock_file_name_sections_basic_pass,
    mock_sms_config
):
    """
    Setup and Success Output 

    Goal: Verify setup is correct and the success message is printed when strings were saved. 

    Assertions: Assert os.makedirs is called. Assert save_memory_strings_read_bin is called.
                Assert click.secho is called with teh green "Successfully save strings..."
                message. 
    """
    expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
    mock_smsrb.return_value = expected_full_path
    
    #pylint: disable=unused-argument
    def mock_side_effect(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, mock_sms_config):
        successful_saves_count[0] = 1
        return expected_full_path

    mock_smsrb.side_effect = mock_side_effect

    save_memory_strings(
        mem_path=mock_mem_path,
        regions_dict=[mock_region],
        output_path=mock_output_path,
        config=mock_sms_config
    )
    #Assert 1
    mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

    #Assert 2
    mock_smsrb.assert_called_once()
    #Assert 3
    success_message_printed = any(
                "Successfully saved strings of" in call[0][0]                     
                for call in mock_click_secho.call_args_list
        )

    assert success_message_printed is True

def test_smstrings_count_0(
    mock_os_makedirs,
    mock_mem_path,
    mock_region,
    mock_output_path,
    mock_smsrb,
    mock_click_secho,
    mock_os_join_paths_basic_pass,
    mock_file_name_sections_basic_pass,
    mock_sms_config
):
    """
    No Save Output 

    Goal: Verify the sucess message is skipped when no strings were save (count=0)

    Assertions: Assert save_memory_strings_read_bin is called. Assert click.secho is 
                not called with the success message. 
    """
    expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
    mock_smsrb.return_value = expected_full_path
    
    #pylint: disable=unused-argument
    def mock_side_effect(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, length_out=4):
        successful_saves_count[0] = 0
        return expected_full_path

    mock_smsrb.side_effect = mock_side_effect

    save_memory_strings(
        mem_path=mock_mem_path,
        regions_dict=[mock_region],
        output_path=mock_output_path,
        config=mock_sms_config
    )
    #Assert 1
    mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

    #Assert 2
    mock_smsrb.assert_called_once()
    
    #Assert 3
    success_message_printed = any(
                "Successfully saved strings of" in call[0][0]                     
                for call in mock_click_secho.call_args_list
        )

    assert success_message_printed is False
