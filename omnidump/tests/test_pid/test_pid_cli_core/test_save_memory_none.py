"""Test for Function save_memory_none, save_memory_none_bin_read, 
   and save_memory_none_seek_read (pid_mapping_logic)"""
from unittest import mock
from omnidump.pid_mapping_logic import save_memory_none, save_memory_none_bin_read, save_memory_none_seek_read
def test_smn_setup(
        mock_os_makedirs,
        mock_os_join_paths_smn,
        mock_datetime_now_basic,
        mock_mem_path,
        mock_region_full_smn,
        mock_chunk_data_basic_pass,
        mock_output_path,
        mock_file_name_sections_basic_pass,
        mock_smn_write_1_string,
        mock_dynamic_log_string,
        mock_click_secho,
        mock_region_size_basic_pass,
        mock_smn_setup_config,
        mock_get_section_info_basic_pass
):
    """
    Setup Success

    Goal: Verify the output directory, log filename, and log file header are correct. 

    Assertions: Assert os.makedirs is called. 
                Assert datetime.now() is called. 
                Assert os.path.join is called. 
                Assert open(log_file) is called with unique filename. 
                Assert final success message is printed with the correct path and count. 
    """
    mock_log_file_handle = mock.MagicMock()
    mock_log_file_object = mock_log_file_handle.__enter__.return_value
    mock_log_file_object.write.return_value = None

    mock_mem_file_handle = mock.MagicMock()
    mock_mem_file_object = mock_mem_file_handle.__enter__.return_value
    mock_mem_file_object.read.return_value = mock_chunk_data_basic_pass
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_open_call.side_effect = [mock_log_file_handle, mock_mem_file_handle]

        save_memory_none(
                mem_path=mock_mem_path,
                regions_dict=[mock_region_full_smn],
                config=mock_smn_setup_config
        )

        #Assert 1
        mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

        #Assert 2
        mock_datetime_now_basic.now.assert_called_once()

        #Assert 3
        expected_full_path = mock_os_join_paths_smn(mock_output_path, mock_file_name_sections_basic_pass)
        mock_open_call.assert_any_call(expected_full_path, 'w')
        #Second open call
        calls = [
            mock.call(expected_full_path, 'w'),
            mock.call(mock_mem_path, 'rb'),
        ]

        mock_open_call.assert_has_calls(calls, any_order=False)
        assert mock_open_call.call_count == 2

        mock_mem_file_object.seek.assert_any_call(0x40000000)
        mock_mem_file_object.read.assert_any_call(mock_region_size_basic_pass)
        #Assert 4
        expected_log_writes = [
            mock.call(mock_smn_write_1_string), 
            mock.call(mock_dynamic_log_string),
        ]

        mock_log_file_object.write.assert_has_calls(expected_log_writes, any_order=False)

        expected_success_msg = f"Successfully saved 1 unclassified region(s) to '{expected_full_path}'."
        mock_click_secho.assert_called_with(expected_success_msg, fg="green")

def test_smnbr_full_loop(
        mock_mem_path, 
        mock_region_full_smn,
        mock_get_section_info_multi_region,
        mock_smnsr_basic,
        mock_start_address_basic,
        mock_end_address_basic,
        mock_smnbr_full_loop_config,
        mock_smnsr_basic_config
):
    """
    Log File Header

    Goal: Verify the inital log file content is written correctly. 

    Assertions: Assert the log file handle's .write() method is called once with 
                "Unclassified Memory Regions:\n"
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        mock_mem_handle = mock_open_call.return_value.__enter__.return_value
        
        save_memory_none_bin_read(
            mem_path=mock_mem_path, 
            regions_dict=[mock_region_full_smn], 
            log_file=mock_open_call,
            config=mock_smnbr_full_loop_config
        )
        line_num = 1
        size = 4096

        #Assert 1
        mock_smnsr_basic.assert_called_once_with(
            mock_start_address_basic,
            mock_end_address_basic,
            line_num,
            'unusedpath1',
            'r-xp',
            '123',
            '08:02',
            mock_mem_handle,
            size,
            log_file=mock_open_call,
            config=mock_smnsr_basic_config
        )

def test_smnbr_invalid_address_skip (
        mock_mem_path,
        mock_invalid_region,
        mock_click_secho,
        mock_smnsr_basic,
        mock_get_section_info_invalid,
        mock_smnbr_full_loop_config
):
    """
    Invalid Address Skip 

    Goal: Verify the function catches ValueError during address parsing and skips the region. 

    Assertions: Assert click.secho is called with the yellow "Invalid address format" message. 
                Assert save_memory_none_seek_read is not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
        save_memory_none_bin_read(
            mem_path=mock_mem_path,
            regions_dict=[mock_invalid_region],
            log_file=mock_open_call,
            config=mock_smnbr_full_loop_config
        )

        #Assert 2
        error_message_printed = any(
                "Invalid address format for" in call[0][0]                     
                for call in mock_click_secho.call_args_list
        )
        assert error_message_printed is True
        #Assert 3
        mock_get_section_info_invalid.assert_called_once_with(mock_invalid_region)
        #Assert 4
        mock_smnsr_basic.assert_not_called()
def test_smnbr_permission_skip(
        mock_get_section_info_no_read,
        mock_mem_path,
        mock_region,
        mock_smnsr_basic,
        mock_smnbr_full_loop_config
    ):
    """
    Permission Skip 

    Goal: Verify the function skips regions without read permission. 

    Assertions: Assert save_memory_none_seek_read is not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

        save_memory_none_bin_read(
                mem_path=mock_mem_path,
                regions_dict=[mock_region],
                log_file=mock_open_call,
                config=mock_smnbr_full_loop_config
        )

        #Assert 1
        mock_smnsr_basic.assert_not_called()

def test_smnbr_size_skip(
        mock_mem_path,
        mock_region,
        mock_get_section_info_zero_skip,
        mock_smnsr_basic,
        mock_smnbr_full_loop_config
):
    """
    Zero/Negative Size Skip 

    Goal: Verify the function skips regions where end <= start. 

    Assertions: Assert save_memory_none_seek_read is not called. 
    """
    with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

        save_memory_none_bin_read(
                mem_path=mock_mem_path,
                regions_dict=[mock_region],
                log_file=mock_open_call,
                config=mock_smnbr_full_loop_config
        )

        #Assert 1
        mock_smnsr_basic.assert_not_called()

def test_smnsr_log_write(
        mock_start_address_basic,
        mock_end_address_basic,
        mock_chunk_data_basic_pass,
        mock_region_size_basic_pass,
        mock_dynamic_log_string,
        mock_smnsr_basic_config
):
    """
    Basic Log Write 

    Goal: Verify sucessful memory read and log file write in the 
          non-verbose mode. 

    Assertions: Assert mock_mem.seek() and .read() are called.
                Assert mock_log_file.write() is called with the correct non-verbose string. 
    """
    mock_log_file_handle = mock.MagicMock()
    mock_log_file_object =  mock_log_file_handle.__enter__.return_value

    mock_mem_handle = mock.MagicMock()
    mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

    with mock.patch('builtins.open', new_callable=mock.mock_open):
        line_num = 1
        size = 4096

        save_memory_none_seek_read(
            mock_start_address_basic,
            mock_end_address_basic,
            line_num,
            '/path/to/file',
            'r-xp',
            '123',
            '08:02',
            mock_mem_handle,
            size,
            log_file=mock_log_file_object,
            config=mock_smnsr_basic_config
        )
        #Assert 1
        mock_mem_handle.seek.assert_any_call(0x40000000)
        mock_mem_handle.read.assert_any_call(mock_region_size_basic_pass)

        #Assert 2
        expected_log_writes = [
            mock.call(mock_dynamic_log_string),
        ]

        mock_log_file_object.write.assert_has_calls(expected_log_writes, any_order=False)

def test_smnsr_verbose_log_write(
        mock_start_address_basic,
        mock_end_address_basic,
        mock_chunk_data_basic_pass,
        mock_region_size_basic_pass,
        mock_dynamic_log_string_verbose,
        mock_smnsr_verbose_log_config
):
    """
    Verbose Log Write 

    Goal: Verify the detailed logging path is taken when verbose_out is True. 

    Assertions: Assert mock_log_file.write() is called with the full verbose string
                (including Permissions, Inode, etc.).
    """
    mock_log_file_handle = mock.MagicMock()
    mock_log_file_object =  mock_log_file_handle.__enter__.return_value

    mock_mem_handle = mock.MagicMock()
    mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

    with mock.patch('builtins.open', new_callable=mock.mock_open):
        line_num = 1
        size = 4096

        save_memory_none_seek_read(
            mock_start_address_basic,
            mock_end_address_basic,
            line_num,
            '/path/to/file',
            'r-xp',
            '123',
            '08:02',
            mock_mem_handle,
            size,
            log_file=mock_log_file_object,
            config=mock_smnsr_verbose_log_config
        )
        #Assert 1
        mock_mem_handle.seek.assert_any_call(0x40000000)
        mock_mem_handle.read.assert_any_call(mock_region_size_basic_pass)

        #Assert 2
        expected_log_writes = [
            mock.call(mock_dynamic_log_string_verbose),
        ]

        mock_log_file_object.write.assert_has_calls(expected_log_writes, any_order=False)

def test_smnsr_os_error(
        mock_start_address_basic,
        mock_end_address_basic,
        mock_region_size_basic_pass,
        mock_click_secho,
        mock_smnsr_verbose_log_config
):
    """
    Read Error Handling

    Goal: Verify I/O error is caught and a message is printed. 

    Assertions: Assert click.secho is called with the "Could not read region" error message.
                Assert mock_log_file.write() is not called with region data. 
    """
    test_os_error = OSError(13, "Permission denied")

    mock_log_file_handle = mock.MagicMock()
    mock_log_file_object = mock_log_file_handle.__enter__.return_value

    mock_mem_handle = mock.MagicMock()

    mock_mem_handle.read.side_effect = test_os_error
    line_num = 1
    size = 4096
    save_memory_none_seek_read(
        mock_start_address_basic,
        mock_end_address_basic,
        line_num,
        '/path/to/file',
        'r-xp',
        '123',
        '08:02',
        mock_mem_handle,
        size,
        log_file=mock_log_file_object,
        config=mock_smnsr_verbose_log_config
    )
    # Assert 1
    mock_mem_handle.seek.assert_any_call(0x40000000)
    # Assert 2
    mock_mem_handle.read.assert_any_call(mock_region_size_basic_pass)

    # Assert 3
    mock_log_file_object.write.assert_not_called()

    # Assert 4
    error_message_printed = any(
        "Could not read region" in call[0][0] 
        for call in mock_click_secho.call_args_list
    )

    assert error_message_printed is True
