from unittest import mock 
from datetime import datetime
import subprocess
import sys
import time
import pytest
import os
import psutil
from omnidump.pid_mapping_logic import get_section_information, get_strings_from_bytes, save_memory_none_bin_read, save_memory_none_seek_read, save_memory_strings_read_bin, process_lines, categorize_regions, save_memory_sections 
from click.testing import CliRunner
from omnidump.config_pid import CliAppConfig

'''
--- Mock Data Fixture ---
'''


'''
--- Filename Fixture For PID Mapping ---
'''

@pytest.fixture
def mock_file_name_sl():
    """Filename for Shared Library region."""
    return "region-0x7f0000000000-0x7f0000001000.bin"

@pytest.fixture
def mock_file_name_sections_basic_pass():
    return f"region-0x40000000-0x40001000.bin"

@pytest.fixture 
def mock_file_name_smn_setup(mock_datetime_now_basic):
    return f"omnidump-{mock_datetime_now_basic.now.return_value}-unclassified-regions.log"

'''
--- Chunk data fixture for PID Mapping ---
'''

@pytest.fixture
def mock_chunk_data_basic_pass():
    return b"A\x00chunk\x00of\x00memory\x00data"

@pytest.fixture
def mock_chunk_data_sl():
    """Mock chunk data for the shared library region"""
    return b"Shared\x00chunk\x00data"

'''
--- Region size for PID Mapping ---
'''

@pytest.fixture
def mock_region_size_basic_pass():
    return 0x1000

@pytest.fixture
def mock_region_size_sl():
    return 0x1000

'''
--- Save Memory None for PID Mapping ---
'''
@pytest.fixture
def mock_smnsr_verbose_log_config(): 
    return CliAppConfig (
        verbose_out=True,
        length_out=4
    )

@pytest.fixture
def mock_smnsr_basic_config(): 
    return CliAppConfig (
        verbose_out=False,
        length_out=4
    )

@pytest.fixture 
def mock_smn_setup_config(mock_output_path):
    return CliAppConfig(
        verbose_out=False,
        save_dir=mock_output_path
    )

@pytest.fixture 
def mock_smnbr_full_loop_config():
    return CliAppConfig(
        verbose_out=False,
        length_out=4
    )

@pytest.fixture 
def mock_smn_basic():
    with mock.patch('omnidump.pid_mapping_logic.save_memory_none', autospec=True) as mock_smn:
        yield mock_smn

@pytest.fixture
def mock_smnbr_basic(): 
    """Mocks the helper function that reads the binary file"""
    with mock.patch('omnidump.pid_mapping_logic.save_memory_none_bin_read', autospec=True) as mock_bin_read:

        yield mock_bin_read

@pytest.fixture
def mock_smnsr_basic():
    """Mocks the helper function that seeks addresses and reads the chunk of byte data"""
    with mock.patch ('omnidump.pid_mapping_logic.save_memory_none_seek_read', autospec=True) as mock_seek_read:
        yield mock_seek_read 
'''
--- Get Section Info for PID Mapping ---
'''

@pytest.fixture
def mock_get_section_info_basic_pass():
    """Mocks the helper function that parses section details."""
    #autospace for the mock signature matches the real function
    with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
        
        mock_info.return_value = (
            "40000000-40001000",   
            "r-xp",               
            "/path/to/file",      
            "123",                
            "08:02"               
        )
        yield mock_info

@pytest.fixture
def mock_get_section_info_invalid():
    """Mocks the helper function that parses section details."""
    #autospace for the mock signature matches the real function
    with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
        
        mock_info.return_value = (
            "invalid_address",   
            "r",               
            "unused",      
            "unused",                
            "unused"               
        )
        yield mock_info

@pytest.fixture
def mock_get_section_info_no_read():
    """Mocks the helper function that parses section details."""
    #autospace for the mock signature matches the real function
    with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
        
        mock_info.return_value = (
            "40000000-40001000",   
            "--xp",               
            "/path/to/file",      
            "123",                
            "08:02"               
        )
        yield mock_info

@pytest.fixture
def mock_get_section_info_zero_skip():
    """Mocks the helper function that parses section details."""
    #autospace for the mock signature matches the real function
    with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
        
        mock_info.return_value = (
            "1000-1000",   
            "r-xp",               
            "/path/to/file",      
            "123",                
            "08:02"               
        )
        yield mock_info

@pytest.fixture
def mock_get_section_info_multi_region():
    """
    Mocks get_section_information to return a sequence of tuples 
    for different regions using side_effect.
    """
    with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
        
        mock_info.side_effect = [
            #Executable
            ("40000000-40001000", "r-xp", "unusedpath1", "123", "08:02"), 
            
            #Shared Library
            ("7f0000000000-7f0000001000", "rw-p", "unusedpath2", "456", "08:02") 
        ]
        yield mock_info

@pytest.fixture
def mock_helpers():
        '''Use helper functions and configure return output'''
        with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_info:
            with mock.patch('omnidump.pid_mapping_logic.get_strings_from_bytes') as mock_strings:

                mock_info.return_value = (
                    "40000000-40001000", 
                    "r-xp",               
                    "/usr/bin/app",       
                    "123",                
                    "08:02"               
                )

                mock_strings.return_value = iter(['test strings 1', 'test strings 2'])

        yield  mock_strings

@pytest.fixture
def mock_invalid():
        '''Use helper functions and configure return output'''
        with mock.patch('omnidump.pid_mapping_logic.get_section_information', autospec=True) as mock_strings:
            mock_info.return_value = (
                    "40000000-40001000", 
                    "r-xp",               
                    "/usr/bin/app",       
                    "123",                
                    "08:02"               
                )


        yield  mock_strings

'''
--- Sections data for PID Mapping ---
'''

@pytest.fixture
def mock_sections_data():
    """Returns fake categorized memory regions dictionary."""
    return {
        "executable": [
            {
                "address": "40000000-40001000", 
                "permissions": "r-xp",        
                "file_path": "/usr/bin/app",
                "inode": "123",
                "maj_min_id": "08:02"
            }
        ],
        "shared_libs": [
            {
                "address": "7f0000000000-7f0000001000", 
                "permissions": "rw-p",        
                "file_path": "/lib/lib.so",
                "inode": "456",
                "maj_min_id": "08:02"
            }
        ],

        "heap": [
            {
                "address": "70001000000-7f0000001000", 
                "permissions": "---p",        
                "file_path": "[heap]",
                "inode": "456",
                "maj_min_id": "08:02"
            }
        ],
        "empty_section": [], 
    }

@pytest.fixture
def mock_regions_multi():
    return[
        {"address": "40000000-40001000", "permissions": "r-xp"},
        {"address": "7f0000000000-7f0000001000", "permissions": "rw-p"}
    ] 

'''
--- Paths for PID Mapping ---
'''

@pytest.fixture
def mock_maps_path():
    return "/proc/self/maps"

@pytest.fixture
def mock_mem_path():
    return "/proc/self/mem"

@pytest.fixture
def mock_output_path():
    return "/tmp/dump_dir"

'''
--- OS functions for PID Mapping ---
'''
@pytest.fixture
def mock_os_join_paths_smn():
    """Mocks the os.path.join call to prevent actual file system interaction."""
    with mock.patch("omnidump.pid_mapping_logic.os.path.join", autospec=True) as mock_os_join:
        mock_os_join.return_value = "/tmp/dump_dir/region-0x40000000-0x40001000.bin"
        yield mock_os_join

@pytest.fixture
def mock_os_join_paths_basic_pass():
    """Mocks the os.path.join call to prevent actual file system interaction."""
    with mock.patch("omnidump.pid_mapping_logic.os.path.join", autospec=True) as mock_os_join:
        mock_os_join.return_value = "/tmp/dump_dir/region-0x40000000-0x40001000.bin"
        yield mock_os_join

@pytest.fixture
def mock_os_makedirs():
    """Mocks the os.makedirs call to prevent actual file system interaction."""
    with mock.patch('omnidump.pid_mapping_logic.os.makedirs', autospec=True) as mock_makedirs:
        yield mock_makedirs

'''
--- Datetime functions for PID Mapping ---
'''

@pytest.fixture
def mock_datetime_now_basic():
    """Mocks the datetime.now() call to prevent actual date time generation."""
    with mock.patch("omnidump.pid_mapping_logic.datetime",autospec=True) as mock_datetime: 
        mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 30, 0)
        yield mock_datetime 

'''
--- Data offsets for PID Mapping ---
'''

@pytest.fixture
def mock_sections_data_offsets():
    """Returns fake categorized memory regions offsets"""
    return {
            "executable": [{"offsets": "0x1000"}],
            "shared_libs": [{"offsets": 0x1000}]
            }
'''
--- Regions ---
'''
@pytest.fixture
def mock_region(): 
    return {
            "address": "40000000-40001000",
            "permissions": "r-xp"
    }

@pytest.fixture
def mock_invalid_region(): 
    return {
            "address": "50001000-50000000X",
            "permissions": "r-xp",
    }

@pytest.fixture
def mock_region_zero_skip(): 
    return {
            "address": "1000-1000",
            "permissions": "r-xp",
    }

@pytest.fixture
def mock_region_full_smn():
    return {"address": "40000000-40001000", "permissions": "r-xp"}
    
'''
--- Addresses -- 
'''

@pytest.fixture 
def mock_start_address_basic():
    start_add = 0x40000000 
    return start_add
    

@pytest.fixture 
def mock_end_address_basic():
    end_add = 0x40001000
    return end_add 

'''
--- Save Memory Sections ---
'''

@pytest.fixture
def mock_save_memory_sections():
    with mock.patch('omnidump.pid_mapping_logic.save_memory_sections') as mock_sms:
        yield mock_sms

'''
--- Save Memory None Write Strings ---
'''

@pytest.fixture
def mock_dynamic_log_string(mock_chunk_data_basic_pass):
    line_num = 1
    chunk = len(mock_chunk_data_basic_pass) 
    path = "/path/to/file" 
    start = 0x40000000
    end = 0x40001000
    final_string = f"{line_num}: Chunk Size: {chunk} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n" + "\n"
    return final_string

@pytest.fixture
def mock_dynamic_log_string_verbose(mock_chunk_data_basic_pass):
    line_num = 1
    chunk = len(mock_chunk_data_basic_pass) 
    path = "/path/to/file"
    permissions = 'r-xp'
    inode = '123'
    maj_min_id = '08:02'
    string_list = ['chunk', 'memory', 'data']
    start = 0x40000000
    end = 0x40001000
    final_string = f"{line_num}: Chunk Size: {chunk} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Major Minor Id: {maj_min_id}\n Extracted Strings: {string_list}\n" + "\n"
    return final_string

@pytest.fixture
def mock_smn_write_1_string():
    return "Unclassified Memory Regions:\n"

'''
--- Save Memory Strings Write Strings 
'''
@pytest.fixture
def mock_sms_config(mock_output_path): 
    return CliAppConfig (
        length_out=4
    )

@pytest.fixture 
def mock_smsw_log_string(mock_smsw_strings_list):
    final_string = f"\n--Extracted Strings --\n {mock_smsw_strings_list}" 
    return final_string

@pytest.fixture
def mock_smsw_strings_list():
    strings_list = ['a', 'b']
    return strings_list

@pytest.fixture
def mock_smst():
    """Mocks the helper function that seeks addresses and reads the chunk of byte data"""
    with mock.patch ('omnidump.pid_mapping_logic.save_memory_strings', autospec=True) as mock_strings:
        yield mock_strings

@pytest.fixture
def mock_smsw():
    """Mocks the helper function that seeks addresses and reads the chunk of byte data"""
    with mock.patch ('omnidump.pid_mapping_logic.save_memory_strings_write', autospec=True) as mock_strings_write:
        yield mock_strings_write

@pytest.fixture
def mock_smsrb():
    """Mocks the helper function that seeks addresses and reads the chunk of byte data
       and sets a side effect to simulate a successful save by updating the count."""
       
    # 1. Define the side effect logic
    def set_success_count_to_one(*args, **kwargs):
        successful_saves_count = args[1] 
        successful_saves_count[0] = 1 

    with mock.patch ('omnidump.pid_mapping_logic.save_memory_strings_read_bin', autospec=True) as mock_strings_read_bin:
        mock_strings_read_bin.side_effect = set_success_count_to_one
        yield mock_strings_read_bin

'''
--- Get Region Category regions ---
'''

@pytest.fixture
def mock_heap_region_data():
    return {'file_path': '[heap]', 'permissions': 'rw-p'}

@pytest.fixture
def mock_stack_region_data():
    return {'file_path': '[stack]', 'permissions': 'rw-p'}

@pytest.fixture
def mock_anon_region_data():
    return {'file_path': '[anon:something]', 'permissions': 'rw-p'}

@pytest.fixture
def mock_vsyscall_region_data():
    return {'file_path': '[vsyscall]', 'permissions': 'r-xp'}

@pytest.fixture
def mock_gp_region_data():
    return {'file_path': '', 'permissions': '---p'}

@pytest.fixture
def mock_dm_region_data():
    return {'file_path': '/dev/zero', 'permissions': 'r-xp'}

@pytest.fixture
def mock_ts_region_data():
    return {'file_path': '/dev/shm', 'permissions': 'rw-p'}

@pytest.fixture
def mock_am_region_data():
    return {'file_path': '', 'permissions': 'rw-p'}

@pytest.fixture
def mock_sl_region_data():
    return {'file_path': '/usr/lib/libc.so.6.1', 'permissions': 'r-xp'}

@pytest.fixture
def mock_ex_region_data():
    return {'file_path': '/usr/bin/myapp', 'permissions': 'r-xp'}

@pytest.fixture
def mock_fb_region_data():
    return {'file_path': '/tmp/data.log', 'permissions': 'rw-p'}

@pytest.fixture
def mock_no_region_data():
    return {'file_path': 'custom', 'permissions': 'r--p'}

'''
--- Categorize Region Mocks --- 
'''

@pytest.fixture 
def mock_process_lines():
    """Mocks process lines function used to for separating lines for the line data into categories."""
    with mock.patch('omnidump.pid_mapping_logic.process_lines') as mock_pl:
        yield mock_pl

@pytest.fixture 
def mock_get_region_category():
    """Mocks get_region_category function"""
    with mock.patch('omnidump.pid_mapping_logic.get_region_category') as mock_grc:
        yield mock_grc

@pytest.fixture
def mock_dict_data():
    return{
        "dict_a": {"id": "A", "start": "0x1000"},
        "dict_b": {"id": "B", "start": "0x2000"},
        "dict_c": {"id": "C", "start": "0x3000"}
    }

'''
--- Group Region Mocks ---
'''
@pytest.fixture 
def mock_expected_result_gr():
    expected_result = {"heap": 1}
    return expected_result

@pytest.fixture
def mock_gr_strings_list():
    strings_list = ['Line1\n', 'Line2\n']
    return strings_list

@pytest.fixture
def mock_categorize_regions(): 
    """Mocks the categorize regions function"""
    result = {"heap": 1}
    with mock.patch('omnidump.pid_mapping_logic.categorize_regions', return_value=result) as mock_cr: 
        yield mock_cr

'''
--- Format Output Bytes None Log ---
'''
@pytest.fixture 
def mock_fobnl_success_config(mock_output_path): 
    """CliAppConfig for none log test 1"""
    return CliAppConfig(
        verbose_out=True,
        length_out=3,
        save_dir=mock_output_path,
    
    )

@pytest.fixture 
def mock_fobnl_no_regions_config(mock_output_path): 
    """CliAppConfig for none log test 2"""
    return CliAppConfig(
        verbose_out=True,
        length_out=3,
        save_dir=mock_output_path, 
        flag_none_log=True
    )

@pytest.fixture 
def mock_fobnl_missing_cat_config(mock_output_path): 
    """CliAppConfig for none log test 3"""
    return CliAppConfig(
        verbose_out=True,
        length_out=3,
        save_dir=mock_output_path, 
    )

@pytest.fixture(name="memory_map_exe")
def mock_input_dict_exe():
    region1 = "..."
    input_dict = {"executable": [region1]}
    return input_dict

@pytest.fixture(name="memory_map_dict")
def mock_input_dict():
    region1 = "..."
    input_dict = {"none": [region1]}
    return input_dict

@pytest.fixture(name="memory_map_empty")
def mock_input_dict_empty():
    input_dict = {"none": []}
    return input_dict

'''
--- Format Output Bytes Section Log ---
'''
@pytest.fixture 
def mock_fobsl_single_section_save_config(mock_output_path): 
    """CliAppConfig for sections log tests 1"""
    return CliAppConfig(
        save_dir=mock_output_path,
        flag_exec_sec=True,
        flag_slib_sec=False
    )

@pytest.fixture 
def mock_fobsl_multi_sect_save_config(mock_output_path): 
    """CliAppConfig for sections log tests 2"""
    return CliAppConfig(
        save_dir=mock_output_path,
        flag_exec_sec=True,
        flag_slib_sec=True
    )


@pytest.fixture(name="section_flag_dict_multi_true")
def mock_section_flag_dict_true():
    section_flag_dict = {"executable": True, "shared_libs": True}
    return section_flag_dict

@pytest.fixture(name="memory_map_exe_e")
def mock_input_dict_exe_e():
    input_dict = {"executable": []}
    return input_dict


@pytest.fixture(name="memory_map_multi_exe_sl")
def mock_input_dict_multi():
    r1 = "region1"
    r2 = "region2"

    input_dict = {"executable": [r1], "shared_libs": [r2]}
    return input_dict

@pytest.fixture(name="section_flag_dict_empty")
def mock_section_flag_dict_empty():
    section_flag_dict = {}
    return section_flag_dict

@pytest.fixture(name="section_flag_dict_multi")
def mock_section_flag_dict():
    section_flag_dict = {"executable": True, "shared_libs": False}
    return section_flag_dict

'''
--- Format Output Bytes Console Log ---
'''

@pytest.fixture 
def mock_console_output_config_selections_output(): 
    """CliAppConfig for console output tests 1"""
    return CliAppConfig(
        strings_out=True, 
        verbose_out=False,
        length_out=5,
        flag_all_sec=False,
        flag_exec_sec=True
    )

@pytest.fixture 
def mock_console_output_config_sections_output(): 
    """CliAppConfig for console output test 2"""
    return CliAppConfig(
        strings_out=True, 
        verbose_out=False,
        length_out=5,
        flag_all_sec=True,
        flag_exec_sec=True,
        flag_slib_sec=True
    )

@pytest.fixture 
def mock_console_output_config_no_sections_selected(): 
    """CliAppConfig for console output test 3"""
    return CliAppConfig(
        strings_out=True, 
        verbose_out=False,
        length_out=5,
        flag_all_sec=True,
        flag_slib_sec=False, 
        flag_exec_sec=False
    )

@pytest.fixture
def mock_flag_options():
    flag_options_all = {"executable": True, "shared_libs": True, "none": True}
    return flag_options_all

@pytest.fixture
def mock_input_flag_options():
    r1 = "r1"
    r2 = "r2"
    r3 = "r3"

    flag_options_all = {"executable": [r1], "shared_libs": [r2], "none": [r3]}
    return flag_options_all

@pytest.fixture 
def mock_flag_options_empty(): 
    flag_options_all = {"executable": False, "shared_libs": False, "none": False}
    return flag_options_all

@pytest.fixture
def mock_input_flag_options_empty():
    flag_options_all = {}
    return flag_options_all

'''
--- Format Output Bytes String ---
'''
@pytest.fixture 
def mock_fobstl_single_section_strings_saved_config(mock_output_path): 
    """CliAppConfig for strings log tests 1"""
    return CliAppConfig(
        length_out=3,
        flag_exec_sec=True,
        flag_slib_sec=False,
        save_dir=mock_output_path, 
    )

@pytest.fixture 
def mock_fobstl_invalid_output_path_config(mock_output_path): 
    """CliAppConfig for strings log tests 1"""
    return CliAppConfig(
        length_out=3,
        save_dir=None, 
    )


'''
--- Format Output Bytes --- 
'''

@pytest.fixture 
def mock_fobnl():
    with mock.patch('omnidump.pid_mapping_logic.format_output_bytes_none_log') as mock_fobnl:
        yield mock_fobnl

@pytest.fixture 
def mock_fobsl():
    with mock.patch('omnidump.pid_mapping_logic.format_output_bytes_section_log') as mock_fobsl:
        yield mock_fobsl

@pytest.fixture 
def mock_fobstl():
    with mock.patch('omnidump.pid_mapping_logic.format_output_bytes_strings_log') as mock_fobstl:
        yield mock_fobstl

@pytest.fixture 
def mock_fobcl():
    with mock.patch('omnidump.pid_mapping_logic.format_output_bytes_console_log') as mock_fobcl:
        yield mock_fobcl

@pytest.fixture
def mock_flags(): 
    
    flags = {
        'flag_exec_sec': False,
        'flag_slib_sec': False,
        'flag_all_sec': False,
        'flag_he_sec': False,
        'flag_st_sec': False,
        'flag_vvar_sec': False,
        'flag_vsys_sec': False,
        'flag_vdso_sec': False,
        'flag_none_sec': False,
        'flag_none_log': False,
        'flag_anon_sec': False,
        'flag_gp_sec': False,
        'flag_fb_sec': False,
        'flag_ts_sec': False,
        'flag_dm_sec': False,
        'flag_sec_log': False,
        'flag_strings_log': False,
        'flag_anon_map_sec': False,
    }

    return flags

@pytest.fixture
def mock_fob_priority_none_log_config():
    return CliAppConfig (
        flag_none_log=True,
        flag_sec_log=True,
        length_out=5,
        verbose_out=True, 
        save_dir=None
    )

@pytest.fixture
def mock_fob_priority_sections_log_config():
    return CliAppConfig (
        flag_strings_log=True,
        flag_sec_log=True,
        flag_exec_sec=True,
        length_out=5,
        verbose_out=True, 
        save_dir=None
    )

@pytest.fixture
def mock_fob_priority_strings_log_config():
    return CliAppConfig (
        flag_strings_log=True,
        length_out=5,
        verbose_out=True, 
        save_dir=None
    )

@pytest.fixture
def mock_fob_priority_console_log_config():
    return CliAppConfig (
        length_out=5,
        verbose_out=True, 
        save_dir=None
    )

@pytest.fixture
def mock_fob_summary_block_config():
    return CliAppConfig (
        flag_exec_sec=True,
        length_out=5,
        verbose_out=True, 
        save_dir=None
    )


@pytest.fixture
def mock_input_flag_fob_exe(): 
    r1 = "r1"
    flag_options_all = {"executable": [r1]}
    return flag_options_all

@pytest.fixture
def mock_input_flag_fob_none(): 
    r1 = "r1"
    flag_options_all = {"none": [r1]}
    return flag_options_all

@pytest.fixture
def mock_input_flag_fob_none_empty(): 
    flag_options_all = {"none": []}
    return flag_options_all

'''
--- Read Bytes Show Sections ---
'''

@pytest.fixture 
def mock_rbss_verbose_pass_config():
    """CliAppConfig for read bytes show sections tests: verbose pass, readable heap pass"""
    return CliAppConfig (
        length_out=4, 
        verbose_out=True, 
        strings_out=False
    )

@pytest.fixture 
def mock_rbss_oserror_handled_pass_config(): 
    """CliAppConfig for read bytes show sections tests: os error""" 
    return CliAppConfig (
        length_out=4, 
        verbose_out=False, 
        strings_out=False 
    )

@pytest.fixture
def mock_rbss(): 
    with mock.patch('omnidump.pid_mapping_logic.read_bytes_show_sections') as mock_rbss: 
        yield mock_rbss
'''
--- Get String From Bytes ---
'''

@pytest.fixture
def mock_gsfb_1_argument_missing_config():
    """CliAppConfig for get strings from bytes tests: one argument missing"""
    return CliAppConfig(
        length_out=4,
    )

@pytest.fixture
def mock_gsfb_non_print_config():
    """CliAppConfig for get strings from bytes tests: non print"""
    return CliAppConfig(
        length_out=None,
    )
@pytest.fixture 
def mock_gsfb_custom_length_config():
    """CliAppConfig for get strings from bytes tests: custom length"""
    return CliAppConfig(
        length_out=5,
    )

'''
--- Other ---
'''

@pytest.fixture
def mock_click_secho():
    """Mocks printing function used for all the console output."""
    with mock.patch('omnidump.pid_mapping_logic.click.secho') as mock_secho:
        yield mock_secho
