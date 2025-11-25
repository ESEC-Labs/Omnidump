"""Test for Function get_strings_from_bytes (pid_mapping_logic)"""
import random
import pytest
from omnidump.pid_mapping_logic import get_strings_from_bytes
def test_gsfb_2_argument_missing():
    """
    No Arguments

    Goal: Verify that the function requires both the config object and byte data to process data. 

    Assertions: Assert that byte data and config object is needed with asserting the TypeError error message. 
    """
    with pytest.raises(TypeError) as excinfo:
        #The logic here is intentionally leaving out byte_data which is the goal of the test. 
        #pylint:disable=E1120
        get_strings_from_bytes()

    assert excinfo.type is TypeError
    expected_message = "missing 2 required positional argument"
    assert expected_message in str(excinfo.value)

def test_gsfb_1_argument_missing(mock_gsfb_1_argument_missing_config): 
    """
    No Byte data

    Goal: Verify that functions requires byte data to process data. 

    Assertions: Assert that byte data is needed with asserting the TypeError error message. 
    """
    with pytest.raises(TypeError) as excinfo:
        #The logic here is intentionally leaving out byte_data which is the goal of the test. 
        #pylint:disable=E1120
        get_strings_from_bytes(config=mock_gsfb_1_argument_missing_config)

    assert excinfo.type is TypeError
    expected_message = "missing 1 required positional argument"
    assert expected_message in str(excinfo.value) 

def test_gsfb_length_no_config():
    """
    No Byte data or Config

    Goal: Verify that the function requires byte data and the length configuration to process data. 

    Assertions: Assert that length_out isn't a valid argument. 
    """
    length_out=10
    with pytest.raises(TypeError) as excinfo:
        #The logic here is intentionally leaving out byte_data which is the goal of the test. 
        #pylint: disable=E1120, E1123
        get_strings_from_bytes(length_out=length_out)

    assert excinfo.type is TypeError
    expected_message = "got an unexpected keyword argument"
    assert expected_message in str(excinfo.value)

def test_gsfb_length_boundary(mock_gsfb_1_argument_missing_config):
    """
    Length Boundary Failure

    Goal: Assert that a string of length N - 1 is correctly filtered out. 

    Assertions: Assert that 3 char string is excluded (return ['4567']).
    """
    byte_data = b'123\x004567\x00'
    result = list(get_strings_from_bytes(byte_data, mock_gsfb_1_argument_missing_config))
    assert result == ['4567']

def test_gsfb_non_print(mock_gsfb_non_print_config):
    """
    All Non-Printable

    Goal: Verify that input consisting only of terminators/binary data yields nothing. 

    Assertions: Function returns empty list.
    """
    byte_data = b'\x00\xFF\x07\x00'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_non_print_config))
    assert not result 

def test_gsfb_non_print_sep(mock_gsfb_1_argument_missing_config):
    """
    Non-Printable Separator 

    Goal: Verify common terminators correctly break the string and reset the state. 

    Assertion: Assert ['StringA', 'StringB'] are returned. 
    """
    byte_data = b'StringA\x00StringB'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['StringA', 'StringB']

def test_gsfb_multi_sep(mock_gsfb_1_argument_missing_config):
    """
    Consecutive Separators 

    Goal: Verify that multiple terminators in a row are handled gracefully. 

    Assertions: Assert ['StringA', 'StringB'] are returned.  
    """
    byte_data = b'StringA\x00\x00\x00StringB'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['StringA', 'StringB']

def test_gsfb_empty_input(mock_gsfb_1_argument_missing_config):
    """
    Empty Input

    Goal: Verify handling of zero-byte input sequence. 

    Assertions: Result should be empty (empty list []).
    """
    byte_data = b''
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert not result  

def test_gsfb_print_before_bytes(mock_gsfb_1_argument_missing_config):
    """
    Zero/Negative Length 

    Goal: Verify that a length_out of 0 or less doesn't cause errors (CLI validates use for insurance). 

    Assertions: Should yield everything (code should use default length 4). 
    """
    byte_data = b'ABCD\x00'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['ABCD']

def test_gsfb_basic_extraction(mock_gsfb_1_argument_missing_config):
    """
    Basic Extraction

    Goal: verify default minimum length (4) is used and simple ASCII strings are found.

    Assertions: Assert that 4 cahr string is included (['ABCD', 'EFGH I J K']).
    """
    byte_data = b'ABCD\x00EFGH I J K\x00' 
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['ABCD', 'EFGH I J K']

def test_gsfb_custom_length(mock_gsfb_custom_length_config):
    """
    Custom Length

    Goal: Verify the length_out argument correctly enforces a higher minimum length. 

    Assertions: Assert that 4 char string is exclued and 5 char string is included (['56789']).
    """
    byte_data = b'1234\x0056789\x00'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_custom_length_config))
    assert result == ['56789']

def test_gsfb_printable_types(mock_gsfb_1_argument_missing_config):
    """
    All Printable Types

    Goal: Verify that letters, digits, whitespace, and punctuations are correctly included. 

    Assertions: Assert that the function returns ['A.B-1 2', 'C,D3']
    """
    byte_data = b'A.B-1 2\x00C,D3\x00'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['A.B-1 2', 'C,D3']

def test_gsfb_end_data(mock_gsfb_1_argument_missing_config):
    """
    End-of-Data Yield 

    Goal: Verify the function yields the last string even if the input ends without a non printable delimiter. 

    Assertions: Assert that the function returns 'FinalString'.
    """
    byte_data = b'FinalString'
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result == ['FinalString']

def test_gsfb_max_bytes(mock_gsfb_1_argument_missing_config):
    """
    Max Length String 

    Goal: Test with a very long string to ensure memory handling isn't an issue. 

    Assertion: Assert Full 1000 byte string
    """
    byte_data = random.randbytes(1000)
    result = list(get_strings_from_bytes(byte_data, config=mock_gsfb_1_argument_missing_config))
    assert result
