"""Test for Function read_bytes_show_sections (pid_mapping_logic)"""
from unittest import mock
from omnidump.pid_mapping_logic import read_bytes_show_sections
def test_rbss_verbose_pass(
        mock_click_secho,
        mock_sections_data,
        mock_rbss_verbose_pass_config
):
    """
    Test Console Output (Verbose Mode)

    Goal: Verify the function correctly mocks the file I/O and formats 
          the output based on verbose_out=True. 

    Assertions: Assert open(file_path. "rb").
                Assert print function was called multiple times.
                Assert verbose specific information is included. 
    """
    with mock.patch("builtins.open", mock.mock_open(read_data=b"I am a string")) as mock_file:
        read_bytes_show_sections(
                mem_path="/proc/self/mem",
                input_dict=mock_sections_data,
                sections_to_show=["executable"],
                config=mock_rbss_verbose_pass_config
        )
        #Assert 1
        mock_file.assert_called_once_with("/proc/self/mem", "rb")
        mock_file().seek.assert_called_once_with(0x40000000)
        mock_file().read.assert_called_once_with(0x1000)
        #Assert 2
        assert mock_click_secho.call_count > 1

        last_call_args = mock_click_secho.call_args_list[-1][0][0]
        assert "Permissions: r-xp" in last_call_args
        assert "Inode: 123" in last_call_args
        assert "Extracted Strings: ['I am a string']" in last_call_args

def test_rbss_non_readable_heap_pass(
        mock_sections_data,
        mock_rbss_verbose_pass_config
):
    """
    Empty/Non-Readable Sections

    Goal: Verify the logic for sections that are empty or not readable. 

    Assertions: Assert no mem.read() and mem.seek() were not called for non-readable sections. 
    """
    with mock.patch("builtins.open", mock.mock_open(read_data=b"")) as mock_file:
        read_bytes_show_sections(
                mem_path="/proc/self/mem",
                input_dict=mock_sections_data,
                sections_to_show=["heap"],
                config=mock_rbss_verbose_pass_config
        )
        #Assert 1
        mock_file().seek.assert_not_called()
        mock_file().read.assert_not_called()

def test_rbss_oserror_handled_pass(
        mock_click_secho,
        mock_sections_data,
        mock_rbss_oserror_handled_pass_config
):
    """
    Error Handling (OS Error) 

    Goal: Ensures functions hanles an OSError (Permission denied) during memory read operation gracefully.

    Assertions: Assert that the error message was printed to the console. 
    """
    mock_file_handle = mock.MagicMock()
    mock_file_handle.read.side_effect = OSError("Permission denied")
    with mock.patch('builtins.open', return_value=mock.MagicMock(__enter__=lambda self: mock_file_handle, __exit__=lambda self, *args: None)):
        read_bytes_show_sections(
            mem_path="/proc/self/mem",
            input_dict=mock_sections_data,
            sections_to_show=["executable"],
            config=mock_rbss_oserror_handled_pass_config
        )
        # Check that the error message was printed to the console
        error_message_printed = any("Could not read region" in call[0][0] for call in mock_click_secho.call_args_list)
        assert error_message_printed is True
