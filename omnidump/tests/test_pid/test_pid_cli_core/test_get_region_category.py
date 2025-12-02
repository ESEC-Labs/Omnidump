"""Test for Function get_region_category (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import  get_region_category
def test_grc_heap(
    mock_heap_region_data
):
    """
    Heap 

    Goal: Matches the explicit [heap] identifier.

    Assertions: Assert output returns expected category (heap).
    """
    result = get_region_category(mock_heap_region_data)

    expected_value = 'heap'

    assert result == expected_value

def test_grc_stack(
    mock_stack_region_data
):
    """
    Stack

    Goal: Matches the explicit [stack] identifier.

    Assertions: Assert output returns expected category (stack).
    """
    result = get_region_category(mock_stack_region_data)
    expected_value = 'stack'
    assert result == expected_value

def test_grc_anon(
    mock_anon_region_data
):
    """
    Anon 

    Goal: Matches the explicit [anon] identifier.

    Assertions: Assert output returns expected category (anon).
    """
    result = get_region_category(mock_anon_region_data)
    expected_value = 'anon'
    assert result == expected_value

def test_grc_vsyscall(
    mock_vsyscall_region_data
):
    """
    Vsyscall 

    Goal: Matches the explicit [vsyscall] identifier.

    Assertions: Assert output returns expected category (vsyscall).
    """
    result = get_region_category(mock_vsyscall_region_data)
    expected_value = 'vsyscall'
    assert result == expected_value

def test_grc_guard_pages(
    mock_gp_region_data
):
    """
    Guard Pages 

    Goal: Matches empty path and unreadable permissions (----).

    Assertions: Assert output returns expected category (guard_pages).
    """
    result = get_region_category(mock_gp_region_data)

    expected_value = 'guard_pages'

    assert result == expected_value

def test_grc_device_mappings(
    mock_dm_region_data
):
    """
    Device Mappings 

    Goal: Matches path starting with /dev/.

    Assertions: Assert output returns expected category (device_mappings).
    """
    result = get_region_category(mock_dm_region_data)
    expected_value = 'device_mappings'
    assert result == expected_value

def test_grc_tmpfs_shm(
    mock_ts_region_data
):
    """
    Tmps/Shm 

    Goal: Matches path starting with /dev/shm.

    Assertions: Assert output returns expected category (tmpfs_shm).
    """
    result = get_region_category(mock_ts_region_data)
    expected_value = 'tmpfs_shm'
    assert result == expected_value

def test_grc_anon_map(
    mock_am_region_data
):
    """
    Anon Map 

    Goal: Matches empty path but has rw-p permissions (not a guard page).

    Assertions: Assert output returns expected category (anon_map).
    """
    result = get_region_category(mock_am_region_data)
    expected_value = 'anon_map'
    assert result == expected_value

def test_grc_shared_libs(
    mock_sl_region_data
):
    """
    Shared Library 

    Goal: Matches .so(\.\d+)*$ regex for a library file (.so.1, or .so.6.expat).

    Assertions: Assert output returns expected category (shared_libs).
    """
    result = get_region_category(mock_sl_region_data)
    expected_value = 'shared_libs'
    assert result == expected_value

def test_grc_executable(
    mock_ex_region_data
):
    """
    Executable 

    Goal: Matches executable pattern (/path/to/file) and is not a shared library.

    Assertions: Assert output returns expected category (executable).
    """
    result = get_region_category(mock_ex_region_data)
    expected_value = 'executable'
    assert result == expected_value

def test_grc_file_backed(
    mock_fb_region_data
):
    """
    File Backed 

    Goal: File path that doesn't match the specific executable or shared library regex.

    Assertions: Assert output returns expected category (file_backed).
    """
    result = get_region_category(mock_fb_region_data)
    expected_value = 'file_backed'
    assert result == expected_value

def test_grc_none(
    mock_no_region_data
):
    """
    None 

    Goal: Default fallback case.

    Assertions: Assert output returns expected category (none).
    """
    result = get_region_category(mock_no_region_data)
    expected_value = 'none'
    assert result == expected_value
