"""Test for Function group_regions (pid_mapping_logic)"""
from unittest import mock
from omnidump.pid_mapping_logic import group_regions
def test_gr_success(
        mock_maps_path,
        mock_categorize_regions,
        mock_gr_strings_list,
        mock_expected_result_gr
):
    """
    Read and Delegate Success

    Goal: Verify the file is opened in read mode, lines are read, and passed to the categorization function. 

    Assertions: Assert open(file_path, 'r') is called. Assert categorize_regions
                is called with the list of lines: ["Line1\n, "Line2\n"].
                Assert the returned value matches the mock categorization result. 
    """
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
        mock_maps_path
):
    """
    File Not Found

    Goal: Verify FileNotFoundError is caught and None is returned. 

    Assertions: Assert the function returns none
    """
    test_fnfe  = FileNotFoundError()

    with mock.patch('builtins.open', side_effect=test_fnfe) as mock_open_call:
        actual = group_regions(file_path=mock_maps_path)
        #Assert 1
        mock_open_call.assert_any_call(mock_maps_path, "r")
        #Assert 2
        assert actual is None

def test_gr_empty_file(
    mock_maps_path,
    mock_categorize_regions
):
    """
    Empty File

    Goal: Verify that an empty file is processed (ex: 
            passed as an empty list to the next function) 

    Assertions: Assert cateogrize_regions is called with []. 
    """
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
