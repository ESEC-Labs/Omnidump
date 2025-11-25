"""Test for Function process_lines (pid_mapping_logic)"""
from omnidump.pid_mapping_logic import process_lines
def test_pl_stack_pass():
    """
    Stack Success

    Goal: Verify that a given a line (which resembles /proc/PID/maps) 
          returns the processed line. 

    Assertions: Assert that the function returns a categorized line 
                with stack as file path.  
    """
    line = "7ffd91eca000-7ffd91eec000 rw-p 00000000 00:00 0                          [stack]"
    result = process_lines(line)
    assert result == {'address':'7ffd91eca000-7ffd91eec000', 'permissions':'rw-p', 'offsets': '00000000', 'maj_min_id':'00:00', 'inode':'0', 'file_path':'[stack]'}

def test_pl_file_backed_pass():
    """
    File Backed Success

    Goal: Verify that a given a line (which resembles /proc/PID/maps) 
          returns the processed line. 

    Assertions: Assert that the function returns a categorized line 
                with executable path as file path.  
    """
    line = "590f9dd2e000-590f9dd2f000 rw-p 00009000 08:02 12196053                   /usr/bin/cat"
    result = process_lines(line)
    assert result == {'address':'590f9dd2e000-590f9dd2f000', 'permissions':'rw-p', 'offsets': '00009000', 'maj_min_id':'08:02', 'inode':'12196053', 'file_path':'/usr/bin/cat'}

def test_pl_shared_lib_pass():
    """
    Shared Library Success 

    Goal: Verify that a given a line (which resembles /proc/PID/maps) 
          returns the processed line. 

    Assertions: Assert that the function returns a categorized line 
                with shared library path as the file path.
    """
    line = "785b11803000-785b11805000 rw-p 00202000 08:02 12190214                   /usr/lib/x86_64-linux-gnu/libc.so.6"
    result = process_lines(line)
    assert result == {'address':'785b11803000-785b11805000', 'permissions':'rw-p', 'offsets': '00202000', 'maj_min_id':'08:02', 'inode':'12190214', 'file_path':'/usr/lib/x86_64-linux-gnu/libc.so.6'}

def test_pl_vdso_pass():
    """
    VDSO Sucess 

    Goal: Verify that a given a line (which resembles /proc/PID/maps) 
          returns the processed line. 

    Assertions: Assert that the function returns a categorized line 
                with vdso as the file path.
    """
    line = "7ffd91fa1000-7ffd91fa3000 r-xp 00000000 00:00 0                          [vdso]"
    result = process_lines(line)
    assert result == {'address':'7ffd91fa1000-7ffd91fa3000', 'permissions':'r-xp', 'offsets': '00000000', 'maj_min_id':'00:00', 'inode':'0', 'file_path':'[vdso]'}
