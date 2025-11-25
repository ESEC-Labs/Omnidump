import random 
import pytest 
import os
from unittest import mock
import unittest
from click.testing import CliRunner
from omnidump.pid_mapping_logic import get_strings_from_bytes, process_lines, read_bytes_show_sections, save_memory_sections, save_memory_sections_bin_write, save_memory_none, save_memory_none_bin_read, save_memory_none_seek_read, save_memory_strings_write, save_memory_strings_read_bin, save_memory_strings, get_region_category, categorize_regions, group_regions

'''
get_strings_from_bytes function test
'''

class TestGetBytes: 

    def test_gsfb(self):
        with pytest.raises(TypeError) as excinfo:
            get_strings_from_bytes()

        assert excinfo.type is TypeError
        expected_message = "missing 1 required positional argument"

        assert expected_message in str(excinfo.value)
    
    def test_gsfb_length(self):
        length_out = 10

        with pytest.raises(TypeError) as excinfo:
            get_strings_from_bytes(length_out=length_out)

        assert excinfo.type is TypeError
        expected_message = "missing 1 required positional argument"

        assert expected_message in str(excinfo.value)

    def test_gsfb_length_default(self):
        length_out = 10
        default = 1 
        
        with pytest.raises(TypeError) as excinfo:
            get_strings_from_bytes(length_out=length_out, default=default)

        assert excinfo.type is TypeError
        expected_message = "got an unexpected keyword argument"

        assert expected_message in str(excinfo.value)

    def test_gsfb_length_boundary(self):
        length_out = 4 
        byte_data = b'123\x004567\x00'
        
        result = list(get_strings_from_bytes(byte_data, length_out))

        assert result == ['4567']

    def test_gsfb_non_print(self):

        byte_data = b'\x00\xFF\x07\x00'

        result = list(get_strings_from_bytes(byte_data))

        assert result == []

    def test_gsfb_non_print_sep(self):

        byte_data = b'StringA\x00StringB'

        result = list(get_strings_from_bytes(byte_data))

        assert result == ['StringA', 'StringB']

    def test_gsfb_multi_sep(self):

        byte_data = b'StringA\x00\x00\x00StringB'

        result = list(get_strings_from_bytes(byte_data))

        assert result == ['StringA', 'StringB']
    
    def test_gsfb_empty_input(self):

        byte_data = b''

        result = list(get_strings_from_bytes(byte_data))

        assert result == []

    def test_gsfb_zero_length(self):

        byte_data = b'ABCD\x00'
        length_out=0

        result = list(get_strings_from_bytes(byte_data))

        assert result == ['ABCD']

    def test_gsfb_basic_extraction(self):
        byte_data = b'ABCD\x00EFGH I J K\x00' 
        
        result = list(get_strings_from_bytes(byte_data))

        assert result == ['ABCD', 'EFGH I J K']
    
    def test_gsfb_custom_length(self):
        byte_data = b'1234\x0056789\x00'
        length_out = 5 
        
        result = list(get_strings_from_bytes(byte_data, length_out))

        assert result == ['56789']
    
    def test_gsfb_printable_types(self):
        byte_data = b'A.B-1 2\x00C,D3\x00'
         
        
        result = list(get_strings_from_bytes(byte_data))

        assert result == ['A.B-1 2', 'C,D3']

    def test_gsfb_printable_types(self):
        byte_data = b'A.B-1 2\x00C,D3\x00'
         
        
        result = list(get_strings_from_bytes(byte_data))

        assert result == ['A.B-1 2', 'C,D3']

    def test_gsfb_end_data(self):
        byte_data = b'FinalString'
         
        
        result = list(get_strings_from_bytes(byte_data))

        assert result == ['FinalString']

    def test_gsfb_max_bytes(self):

        byte_data = random.randbytes(1000)

        result = list(get_strings_from_bytes(byte_data))

'''
process_lines test
'''

class TestProcessLines: 

    def test_pl_stack_pass(self):

        line = "7ffd91eca000-7ffd91eec000 rw-p 00000000 00:00 0                          [stack]"
    
        result = process_lines(line)

        assert result == {'address':'7ffd91eca000-7ffd91eec000', 'permissions':'rw-p', 'offsets': '00000000', 'maj_min_id':'00:00', 'inode':'0', 'file_path':'[stack]'}     

    def test_pl_file_backed_pass(self):

        line = "590f9dd2e000-590f9dd2f000 rw-p 00009000 08:02 12196053                   /usr/bin/cat"
    
        result = process_lines(line)

        assert result == {'address':'590f9dd2e000-590f9dd2f000', 'permissions':'rw-p', 'offsets': '00009000', 'maj_min_id':'08:02', 'inode':'12196053', 'file_path':'/usr/bin/cat'}

    def test_pl_shared_lib_pass(self):

        line = "785b11803000-785b11805000 rw-p 00202000 08:02 12190214                   /usr/lib/x86_64-linux-gnu/libc.so.6"
    
        result = process_lines(line)

        assert result == {'address':'785b11803000-785b11805000', 'permissions':'rw-p', 'offsets': '00202000', 'maj_min_id':'08:02', 'inode':'12190214', 'file_path':'/usr/lib/x86_64-linux-gnu/libc.so.6'}

    def test_pl_vdso_pass(self):

        line = "7ffd91fa1000-7ffd91fa3000 r-xp 00000000 00:00 0                          [vdso]"
    
        result = process_lines(line)

        assert result == {'address':'7ffd91fa1000-7ffd91fa3000', 'permissions':'r-xp', 'offsets': '00000000', 'maj_min_id':'00:00', 'inode':'0', 'file_path':'[vdso]'}

'''
read_bytes_show_section test 
'''

class TestReadBytesShowSections: 

    @mock.patch('omnidump.pid_mapping_logic.click.secho')
    def test_rbss_verbose_pass(self, mock_secho, mock_sections_data):
        with mock.patch("builtins.open", mock.mock_open(read_data=b"I am a string")) as mock_file:
            read_bytes_show_sections(
                    mem_path="/proc/self/mem",
                    input_dict=mock_sections_data, 
                    sections_to_show=["executable"],
                    length_out=4, 
                    verbose_out=True,
                    strings_out=False
            )
            
            #Assert 1
            mock_file.assert_called_once_with("/proc/self/mem", "rb")
            mock_file().seek.assert_called_once_with(0x40000000)
            mock_file().read.assert_called_once_with(0x1000) 

            #Assert 2
            assert mock_secho.call_count > 1

            last_call_args = mock_secho.call_args_list[-1][0][0]
            assert "Permissions: r-xp" in last_call_args
            assert "Inode: 123" in last_call_args
            assert "Extracted Strings: ['I am a string']" in last_call_args

    def test_rbss_non_readable_heap_pass(self, mock_sections_data):
        with mock.patch("builtins.open", mock.mock_open(read_data=b"")) as mock_file:
            read_bytes_show_sections(
                    mem_path="/proc/self/mem",
                    input_dict=mock_sections_data, 
                    sections_to_show=["heap"],
                    length_out=4, 
                    verbose_out=True,
                    strings_out=False
            )
            
            #Assert 1
            mock_file().seek.assert_not_called()
            mock_file().read.assert_not_called()

    def test_rbss_oserror_handled_pass(self, mock_click_secho, mock_sections_data):
        mock_file_handle = mock.MagicMock()
        mock_file_handle.read.side_effect = OSError("Permission denied") 
        
        with mock.patch('builtins.open', return_value=mock.MagicMock(__enter__=lambda self: mock_file_handle, __exit__=lambda self, *args: None)):
            
            read_bytes_show_sections(
                mem_path="/proc/self/mem",
                input_dict=mock_sections_data,
                sections_to_show=["executable"],
                length_out=4,
                verbose_out=False,
                strings_out=False
            )

            # Check that the error message was printed to the console
            error_message_printed = any("Could not read region" in call[0][0] for call in mock_click_secho.call_args_list)
            assert error_message_printed is True

'''
save_memory_sections test
'''

class TestSaveMemSections: 
        
    def test_sms_basic_pass(self,
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
    
    def test_sms_multi_regions_pass(self,
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
    
    def test_sms_output_dir(self,
                            mock_click_secho,
                            mock_get_section_info_basic_pass,
                            mock_os_makedirs, 
                            mock_chunk_data_basic_pass, 
                            mock_region, 
                            mock_output_path, 
                            mock_mem_path,
                        ):

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

    def test_sms_invalid_address(self, 
                                 mock_mem_path, 
                                 mock_invalid_region, 
                                 mock_output_path, 
                                 mock_os_makedirs, 
                                 mock_click_secho,
                                 mock_get_section_info_invalid
                                 ): 
         

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
            self, 
            mock_get_section_info_no_read, 
            mock_chunk_data_basic_pass, 
            mock_mem_path, 
            mock_region, 
            mock_output_path,
            mock_os_makedirs, 
            mock_click_secho
    ):

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

    def test_sms_zero_size_skip(
            self, 
            mock_get_section_info_zero_skip, 
            mock_chunk_data_basic_pass, 
            mock_mem_path, 
            mock_region_zero_skip, 
            mock_os_makedirs, 
            mock_output_path):

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
    
    '''
    testing supporting function: save_memory_sections_bin_write
    '''

    def test_smsbw_os_error(
            self,                      
            mock_output_path, 
            mock_click_secho,
            mock_end_address_basic,
            mock_start_address_basic,
            mock_chunk_data_basic_pass,
            mock_os_join_paths_basic_pass, 
            mock_file_name_sections_basic_pass
        ): 
         
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

class TestSaveMemoryNone: 
    
    def test_smn_setup(
            self,
            mock_os_makedirs,
            mock_os_join_paths_smn,
            mock_datetime_now_basic,
            mock_mem_path, 
            mock_region_full_smn,
            mock_chunk_data_basic_pass, 
            mock_output_path,
            mock_get_section_info_basic_pass,
            mock_file_name_sections_basic_pass,
            mock_smn_write_1_string, 
            mock_dynamic_log_string,
            mock_click_secho,
            mock_region_size_basic_pass
    ):
        
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
                    output_path=mock_output_path,
                    verbose_out=False
            )

            #Assert 1 
            mock_os_makedirs.assert_called_once_with(mock_output_path, exist_ok=True)

            #Assert 2
            mock_datetime_now_basic

            #Assert 3
            #First open call 
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

    ):
        
        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
            mock_mem_handle = mock_open_call.return_value.__enter__.return_value
            
            save_memory_none_bin_read(
                mem_path=mock_mem_path, 
                regions_dict=[mock_region_full_smn], 
                verbose_out=False,
                log_file=mock_open_call 
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
                verbose_out=False,
                length_out=4
            )

    def test_smnbr_invalid_address_skip (
            self, 
            mock_mem_path, 
            mock_invalid_region, 
            mock_output_path, 
            mock_os_makedirs,
            mock_click_secho,
            mock_smnsr_basic,
            mock_get_section_info_invalid
    ): 
         

        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:
           
            save_memory_none_bin_read(
                mem_path=mock_mem_path,
                regions_dict=[mock_invalid_region],
                verbose_out=False, 
                log_file=mock_open_call
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
            self, 
            mock_get_section_info_no_read, 
            mock_mem_path, 
            mock_region,
            mock_smnsr_basic
        ):


        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

            save_memory_none_bin_read(
                    mem_path=mock_mem_path, 
                    regions_dict=[mock_region],
                    verbose_out=False, 
                    log_file=mock_open_call
            )

            #Assert 1
            mock_smnsr_basic.assert_not_called()
    
    def test_smnbr_size_skip(
            self,                              
            mock_get_section_info_zero_skip, 
            mock_chunk_data_basic_pass, 
            mock_mem_path, 
            mock_region_zero_skip,
            mock_region,
            mock_smnsr_basic
            ):

        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call:

            save_memory_none_bin_read(
                    mem_path=mock_mem_path, 
                    regions_dict=[mock_region],
                    verbose_out=False, 
                    log_file=mock_open_call
            )

            #Assert 1
            mock_smnsr_basic.assert_not_called()
    
    def test_smnsr_log_write(
            self,
            mock_start_address_basic, 
            mock_end_address_basic, 
            mock_chunk_data_basic_pass,
            mock_region_size_basic_pass,
            mock_dynamic_log_string,
            mock_click_secho
    ):
        mock_log_file_handle = mock.MagicMock()
        mock_log_file_object =  mock_log_file_handle.__enter__.return_value

        mock_mem_handle = mock.MagicMock()
        mock_mem_object = mock_mem_handle.__enter__.return_value

        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call: 
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
                verbose_out=False,
                length_out=4
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
            self,
            mock_start_address_basic, 
            mock_end_address_basic, 
            mock_chunk_data_basic_pass,
            mock_region_size_basic_pass,
            mock_click_secho,
            mock_dynamic_log_string_verbose
    ):
        mock_log_file_handle = mock.MagicMock()
        mock_log_file_object =  mock_log_file_handle.__enter__.return_value

        mock_mem_handle = mock.MagicMock()
        mock_mem_object = mock_mem_handle.__enter__.return_value

        mock_mem_handle.read.return_value = mock_chunk_data_basic_pass

        with mock.patch('builtins.open', new_callable=mock.mock_open) as mock_open_call: 
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
                verbose_out=True,
                length_out=4
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
            self,
            mock_start_address_basic, 
            mock_end_address_basic, 
            mock_chunk_data_basic_pass,
            mock_region_size_basic_pass,
            mock_click_secho,
            mock_dynamic_log_string_verbose
            ): 
    
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
            verbose_out=True,
            length_out=4
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

class TestSaveMemoryStrings: 

    def test_smsw_write(
            self, 
            mock_smsw_strings_list,
            mock_os_join_paths_basic_pass, 
            mock_output_path, 
            mock_file_name_sections_basic_pass,
            mock_smsw_log_string
    ):
        
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
        self, 
        mock_click_secho,
        mock_file_name_sections_basic_pass,
        mock_output_path,
        mock_os_join_paths_basic_pass,
        mock_smsw_strings_list
    ):
        test_os_error  = OSError(13, "Permission denied")

        with mock.patch('builtins.open', side_effect=test_os_error) as mock_open_call:
            mock_write_handle = mock_open_call.return_value.__enter__.return_value
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
        self, 
        mock_smsw,
        mock_get_section_info_basic_pass,
        mock_os_join_paths_basic_pass, 
        mock_output_path, 
        mock_file_name_sections_basic_pass,
        mock_region_size_basic_pass,
        mock_mem_path,
        mock_region
    ): 
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
                length_out=4
            )

            # Assert 1
            mock_rb_handle.seek.assert_any_call(0x40000000)
        
            # Assert 2
            mock_rb_handle.read.assert_any_call(mock_region_size_basic_pass)

    def test_smsrb_multi_region_success(
        self,
        mock_smsw,
        mock_chunk_data_basic_pass, 
        mock_chunk_data_sl,
        mock_regions_multi,
        mock_mem_path, 
        mock_output_path, 
        mock_os_join_paths_basic_pass, 
        mock_file_name_sections_basic_pass
    ):

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
                length_out=4
            )
            
            #assert 1
            assert mock_mem_handle.seek.call_count == 2
            assert mock_mem_handle.read.call_count == 2

            #assert 2
            assert mock_smsw.call_count == 2
    
    def test_smsrb_read_error(
        self,
        mock_click_secho,
        mock_output_path, 
        mock_file_name_sections_basic_pass, 
        mock_os_join_paths_basic_pass,
        mock_mem_path, 
        mock_region,
        mock_smsw
    ):
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
                length_out=4
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
        self,
        mock_os_join_paths_basic_pass, 
        mock_output_path,
        mock_file_name_sections_basic_pass, 
        mock_mem_path, 
        mock_invalid_region,
        mock_click_secho
    ):

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
                length_out=4
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
        self,
        mock_os_makedirs,
        mock_mem_path,
        mock_region,
        mock_output_path,
        mock_smsrb,
        mock_click_secho,
        mock_os_join_paths_basic_pass,
        mock_file_name_sections_basic_pass
    ):
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        
        mock_smsrb.return_value = expected_full_path

        def mock_side_effect(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, length_out=4):
            successful_saves_count[0] = 1
            return expected_full_path

        mock_smsrb.side_effect = mock_side_effect 

        save_memory_strings(
            mem_path=mock_mem_path, 
            regions_dict=[mock_region],
            output_path=mock_output_path,
            length_out=4
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
        self,
        mock_os_makedirs,
        mock_mem_path,
        mock_region,
        mock_output_path,
        mock_smsrb,
        mock_click_secho,
        mock_os_join_paths_basic_pass,
        mock_file_name_sections_basic_pass
    ):
        expected_full_path = mock_os_join_paths_basic_pass(mock_output_path, mock_file_name_sections_basic_pass)
        
        mock_smsrb.return_value = expected_full_path

        def mock_side_effect(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, length_out=4):
            successful_saves_count[0] = 0 
            return expected_full_path

        mock_smsrb.side_effect = mock_side_effect 

        save_memory_strings(
            mem_path=mock_mem_path, 
            regions_dict=[mock_region],
            output_path=mock_output_path,
            length_out=4
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

class TestGetRegionCategory:

    def test_grc_heap(
        self,
        mock_heap_region_data
    ): 

        result = get_region_category(mock_heap_region_data)

        expected_value = 'heap'  

        assert result == expected_value

    def test_grc_stack(
        self,
        mock_stack_region_data
    ): 

        result = get_region_category(mock_stack_region_data)

        expected_value = 'stack'  

        assert result == expected_value

    def test_grc_anon(
        self,
        mock_anon_region_data
    ): 

        result = get_region_category(mock_anon_region_data)

        expected_value = 'anon'  

        assert result == expected_value

    def test_grc_vsyscall(
        self,
        mock_vsyscall_region_data
    ): 

        result = get_region_category(mock_vsyscall_region_data)

        expected_value = 'vsyscall'  

        assert result == expected_value
    
    def test_grc_guard_pages(
        self,
        mock_gp_region_data
    ): 

        result = get_region_category(mock_gp_region_data)

        expected_value = 'guard_pages'  

        assert result == expected_value

    def test_grc_device_mappings(
        self,
        mock_dm_region_data
    ): 

        result = get_region_category(mock_dm_region_data)

        expected_value = 'device_mappings'  

        assert result == expected_value

    def test_grc_tmpfs_shm(
        self,
        mock_ts_region_data
    ): 

        result = get_region_category(mock_ts_region_data)

        expected_value = 'tmpfs_shm'  

        assert result == expected_value

    def test_grc_anon_map(
        self,
        mock_am_region_data
    ): 

        result = get_region_category(mock_am_region_data)

        expected_value = 'anon_map'  

        assert result == expected_value
    
    def test_grc_shared_libs(
        self,
        mock_sl_region_data
    ): 

        result = get_region_category(mock_sl_region_data)

        expected_value = 'shared_libs'  

        assert result == expected_value

    def test_grc_executable(
        self,
        mock_ex_region_data
    ): 

        result = get_region_category(mock_ex_region_data)

        expected_value = 'executable'  

        assert result == expected_value

    def test_grc_file_backed(
        self,
        mock_fb_region_data
    ): 

        result = get_region_category(mock_fb_region_data)

        expected_value = 'file_backed'  

        assert result == expected_value
    
    def test_grc_none(
        self,
        mock_no_region_data
    ): 

        result = get_region_category(mock_no_region_data)

        expected_value = 'none'  

        assert result == expected_value

class TestCategorizeRegion: 
    
    def test_cr_success(
            self,
            mock_process_lines,
            mock_get_region_category,
            mock_dict_data
    ):
        dict_A = mock_dict_data["dict_A"] 
        dict_B = mock_dict_data["dict_B"] 
        dict_C = mock_dict_data["dict_C"]

        file_content = ["line1", "line2", "line3"]
        mock_process_lines.side_effect = [dict_A, dict_B, dict_C]
        mock_get_region_category.side_effect = ["executable", "heap", "executable"]
        
        result = categorize_regions(file_content) 

        #Assert 1 
        mock_process_lines.assert_any_call("line1")
        mock_process_lines.assert_any_call("line2")
        mock_process_lines.assert_any_call("line3")
        assert mock_process_lines.call_count == 3

        #Assert 2
        mock_get_region_category.assert_any_call(dict_A)
        mock_get_region_category.assert_any_call(dict_B)
        mock_get_region_category.assert_any_call(dict_C)
        assert mock_get_region_category.call_count == 3

        #Assert 3
        assert result["executable"] == [dict_A, dict_C]

        assert result["heap"] == [dict_B]

    def test_cr_empty_input(
            self,
            mock_process_lines,
            mock_get_region_category 
    ):


        file_content = []
        
        result = categorize_regions(file_content) 

        mock_process_lines.assert_not_called()
        mock_get_region_category.assert_not_called()

        for category_list in result.values():
            assert category_list == []

    def test_cr_invalid_line(
        self, 
        mock_dict_data, 
        mock_process_lines, 
        mock_get_region_category
    ):
        dict_A = mock_dict_data["dict_A"] 


        file_content = ["line1", "bad_line"]
        mock_process_lines.side_effect = [dict_A, None]
        mock_get_region_category.side_effect = ["heap", "stack" ]
        
        result = categorize_regions(file_content) 

        #Assert 1 
        mock_process_lines.assert_any_call("line1")
        mock_process_lines.assert_any_call("bad_line")
        assert mock_process_lines.call_count == 2 

        #Assert 2
        mock_get_region_category.assert_any_call(dict_A)
        assert mock_get_region_category.call_count == 1

        #Assert 3
        assert result["heap"] == [dict_A]

        assert result["stack"] == []

class TestGroupRegions: 

    def test_gr_success(
            self,
            mock_maps_path,
            mock_categorize_regions,
            mock_gr_strings_list,
            mock_expected_result_gr
    ):
        read_data = "".join(mock_gr_strings_list)
        m_open = mock.mock_open(read_data=read_data)

        m_open.return_value.readlines.return_value = mock_gr_strings_list 

        with mock.patch('builtins.open', m_open) as mock_open_call:
            actual = group_regions(file_path=mock_maps_path)
            
            #Assert 1
            mock_open_call.assert_any_call(mock_maps_path, "r")
            
            #Assert 2
            mock_categorize_regions.assert_called_once_with(mock_gr_strings_list)
            
            #Assert 3
            assert actual == mock_expected_result_gr 

    def test_gr_file_not_found(
            self,
            mock_maps_path
    ):
        test_fnfe  = FileNotFoundError()

        with mock.patch('builtins.open', side_effect=test_fnfe) as mock_open_call:

            actual = group_regions(file_path=mock_maps_path)

            #Assert 1
            mock_open_call.assert_any_call(mock_maps_path, "r")

            #Assert 2
            assert actual is None 

    def test_gr_empty_file(
        self,
        mock_maps_path,
        mock_categorize_regions
    ):
        empty = []

        read_data = "" 
        m_open = mock.mock_open(read_data=read_data)

        m_open.return_value.readlines.return_value = empty 

        with mock.patch('builtins.open', m_open) as mock_open_call:
            group_regions(file_path=mock_maps_path)
            
            #Assert 1
            mock_open_call.assert_any_call(mock_maps_path, "r")
            
            #Assert 2
            mock_categorize_regions.assert_called_once_with(empty)

    
