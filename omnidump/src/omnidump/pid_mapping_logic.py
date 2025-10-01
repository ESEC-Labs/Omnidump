import string
import itertools
import sys
import re
import os
from datetime import datetime
import click

'''
Workflow:

dump_bytes_mem()  <-- This is the main entry point

    |
    |------> format_output_bytes()
    
                |
                |------> group_regions()  <-- First step: reads and sorts all memory regions
                |             |
                |             |------> process_lines()  <-- Helper to parse each line from the maps file
                |
                |
                |------> (Conditional Path based on user flags)
                |
                |------> IF user wants to print to console:
                |            read_bytes_show_sections()
                |                 |
                |                 |------> get_section_information() <-- Helper to get info for a region
                |                 |------> get_strings_from_bytes()  <-- Helper to extract strings from the data
                |
                |
                |------> IF user wants to save to a file (e.g., `--log-unclassified, --log-strings, --log-sections`):
                |            save_file_to_dir()
                |                 |
                |                 |------> get_section_information()
                |                 |------> get_strings_from_bytes()
'''

'''
---- Supporting Functions ----
'''

def get_strings_from_bytes(byte_data, length_out=None, default=4):
    """
    Extracts printable strings from a byte sequence, with user-specified length.

    This function is a generator that yields a string as soon as it finds a
    sequence of printable characters of a certain minimum length.

    Args:
        byte_data (bytes): The input byte sequence.
        length_out (int, optional): The minimum length of strings to yield,
                                    as specified by the user.
        default (int): The default minimum length if length_out is not provided.

    Yields:
        str: A string of printable characters.
    """

    '''
    if length_out: 
        min_length = length_out
    else: 
        min_length = default
    '''

    min_length = length_out if length_out else default
    
    current_string = []
    
    for byte in byte_data:
        char = chr(byte)
        if char in string.printable:
            current_string.append(char)
        else:
            if len(current_string) >= min_length:
                yield "".join(current_string)
            current_string = []
            
    # Yield any remaining string at the end of the data
    if len(current_string) >= min_length:
        yield "".join(current_string)


def get_section_information(section):
    """
    Extracts the address, permissions, and path from a single section dictionary.

    Args:
        section (dict): A dictionary representing a single memory section
                        parsed from the maps file.

    Returns:
        tuple: A tuple containing the address (str), permissions (str),
               path (str), inode (str), and major/minor ID (str).
    """
    address = section.get('address', 'N/A')
    permissions = section.get('permissions', 'N/A')
    path = section.get('file_path', 'N/A')
    inode = section.get('inode', 'N/A')
    maj_min_id = section.get('maj_min_id','N/A')
    return (address, permissions, path, inode, maj_min_id)


def process_lines(line):
    """
    Parses a single line from the /proc/PID/maps file using a regular expression.

    Args:
        line (str): A single line from the maps file.

    Returns:
        dict or None: A dictionary containing the parsed information (address,
                      permissions, etc.) or None if the line does not match
                      the expected format.
    """
    # Regex to capture address, permissions, offset, major/minor ID, inode, and file path.
    # The (.*) at the end is non-greedy to handle paths with spaces.
    match = re.match(r"(\w{0,16}+-\w{0,16})\s+(.{4})\s+(\w+)\s+(\w{2}:\w{2})\s+(\d[0-9]{0,8})\s*(.*)", line)

    if not match:
        click.secho(f"No match for: {line.strip()}", fg="yellow")
        return None 
 
    address, permissions, offsets, maj_min_id, inode, file_path= match.groups()

    return {
            "address": address,
            "permissions": permissions,
            "offsets": offsets,
            "maj_min_id": maj_min_id,
            "inode": inode,
            "file_path": file_path
            }

def read_bytes_show_sections(mem_path, input_dict, sections_to_show, length_out, verbose_out, strings_out):
    """
    Reads the specified memory regions from /proc/PID/mem and prints them.

    This function iterates through a list of section categories, opens the
    memory file, reads the bytes for each region, and prints the formatted
    output to the console.

    Args:
        mem_path (str): Path to the /proc/PID/mem file.
        input_dict (dict): Dictionary of categorized memory regions.
        sections_to_show (list): List of section categories to process.
        length_out (int): Minimum string length to extract.
        verbose_out (bool): If True, prints additional information.
    """
    with open(mem_path, "rb") as mem:
        for category_name in sections_to_show:
            sections_list = input_dict.get(category_name, [])

            if not sections_list:
                click.secho(f"\n--- {category_name.upper()} SECTIONS (No entries) ---\n", fg="red")
                continue
                
            click.secho(f"\n--- {category_name.upper()} SECTIONS ---\n", fg="green")
            
            for line_num, section in enumerate(sections_list, 1):
                address, permissions, path, inode, maj_min_id = get_section_information(section)
                try:
                    start, end = [int(x, 16) for x in address.split("-")]
                except ValueError:
                    click.secho(f"Invalid address format for {address}", fg="yellow")
                    continue
                
                if "r" in permissions:
                    size = end - start
                    if size <= 0:
                        continue
                    try:
                        mem.seek(start)
                        chunk = mem.read(size)
                        string_list = list(itertools.islice(get_strings_from_bytes(chunk, length_out), 3))

                        if verbose_out is True:
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Major Minor Id: {maj_min_id}\n Extracted Strings: {string_list}\n")
                        elif strings_out is True:  
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n Extracted Strings: {string_list}\n")
                        else:
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n")
                    except OSError as e:
                        click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")

def save_memory_regions(mem_path, regions_dict, output_path, is_binary=False, length_out=4, verbose_out=False, is_strings=False):
    """
    Saves the specified memory regions to a log file.

    This function is specifically designed to handle the logging of unclassified
    memory regions when the `--log-unclassified` flag is used. It writes the
    extracted information and strings to a timestamped file.

    Args:
        full_file_path (str): The full path to the log file to be created.
        mem_path (str): Path to the /proc/PID/mem file.
        regions_dict (dict): Dictionary of unclassified memory regions.
        length_out (int): Minimum string length to extract.
        verbose_out (bool): If True, prints additional information.
    """
    try:
        if is_binary:
            os.makedirs(output_path, exist_ok=True)
            with open(mem_path, "rb") as mem:
                for line_num, section in enumerate(regions_dict, 1):
                    address, permissions, _, _, _ = get_section_information(section)
                    try:
                        start, end = [int(x, 16) for x in address.split("-")]
                    except ValueError:
                        click.secho(f"Invalid address format for {address}", fg="yellow")
                        continue
                        
                    if "r" in permissions and (end - start) > 0:
                        try:
                            mem.seek(start)
                            chunk = mem.read(end - start)
                            filename = f"region-{hex(start)}-{hex(end)}.bin"
                            full_file_path = os.path.join(output_path, filename)
                            with open(full_file_path, 'wb') as bin_file:
                                bin_file.write(chunk)
                        except OSError as e:
                            click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")
            click.secho(f"Successfully saved {len(regions_dict)} region(s) to '{output_path}'.", fg="green")
        else:
            if is_binary is False and is_strings is False: 

                # Create the user-specified directory if it doesn't exist
                os.makedirs(output_path, exist_ok=True)
                
                # Construct the log file path with a timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"omnidump-{timestamp}-unclassified-regions.log"
                full_file_path = os.path.join(output_path, filename)

                with open(full_file_path, 'w') as log_file:
                    log_file.write("Unclassified Memory Regions:\n")

                    with open(mem_path, "rb") as mem:
                        for line_num, section in enumerate(regions_dict, 1):
                            address, permissions, path, inode, maj_min_id = get_section_information(section)
                            try:
                                start, end = [int(x, 16) for x in address.split("-")]
                            except ValueError:
                                click.secho(f"Invalid address format for {address}", fg="yellow")
                                continue
                            
                            if "r" in permissions:
                                size = end - start
                                if size <= 0:
                                    continue
                                try:
                                    mem.seek(start)
                                    chunk = mem.read(size)
                                    string_list = list(itertools.islice(get_strings_from_bytes(chunk, length_out), 3))

                                    if verbose_out is True:
                                        log_file.write(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Major Minor Id: {maj_min_id}\n Extracted Strings: {string_list}\n" + "\n")
                                    else:
                                        log_file.write(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n" + "\n")
                                except OSError as e:
                                    click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")
                click.secho(f"Successfully saved {len(regions_dict)} unclassified region(s) to '{full_file_path}'.", fg="green")

            elif is_binary is False and is_strings is True:
                    # Create the user-specified directory if it doesn't exist
                    os.makedirs(output_path, exist_ok=True)

                    with open(mem_path, "rb") as mem:
                        for line_num, section in enumerate(regions_dict, 1):
                            address, permissions, _, _, _ = get_section_information(section)
                            try:
                                start, end = [int(x, 16) for x in address.split("-")]
                            except ValueError:
                                click.secho(f"Invalid address format for {address}", fg="yellow")
                                continue
                            
                            if "r" in permissions:
                                size = end - start
                                if size <= 0:
                                    continue
                                try:
                                    mem.seek(start)
                                    chunk = mem.read(size)
                                    string_list = list(get_strings_from_bytes(chunk, length_out))
                                    filename = f"region-{hex(start)}-{hex(end)}-strings.txt"
                                    full_file_path = os.path.join(output_path, filename)
                                    
                                    with open(full_file_path, "w") as strings_file:
                                        strings_file.write(f"\n--Extracted Stirngs --\n {string_list}") 

                                except OSError as e:
                                    click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")
                    click.secho(f"Successfully saved strings of {len(regions_dict)} region(s) '{full_file_path}'.", fg="green")

    except Exception as e:
        click.secho(f"Error saving memory regions: {e}", fg="red")
'''
---- Main Functions ----
'''
def group_regions(file_path):
    """
    Reads a /proc/PID/maps file and categorizes memory regions into a dictionary.

    This function iterates through each line of the maps file, parses it, and
    assigns the memory region to a specific category (e.g., heap, stack, shared libs)
    based on the file path and permissions.

    Args:
        file_path (str): The path to the /proc/PID/maps file.

    Returns:
        dict: A dictionary where keys are category names and values are lists of
              dictionaries, each representing a memory region.
    """
    section_categories = {
        "executable": [],
        "shared_libs": [],
        "heap":[], 
        "stack": [],
        "vvar": [],
        "vsyscall": [],
        "vdso": [],
        "anon": [],
        "guard_pages": [],
        "file_backed": [],
        "tmpfs_shm": [],
        "device_mappings": [],
        "none": []
    }

    f_path_target_char = "/"
    h_target_char = "[heap]"
    s_target_char = "[stack]"
    vvar_target_char = "[vvar]"
    vsyscall_target_char = "[vsyscall]"
    anon_target_char = "[anon"
    vdso_target_char = "[vdso]"

    with open(file_path, 'r') as file:
        file_content = file.readlines()

        for line in file_content:
            result = process_lines(line)

            # Check if a match was successfully made
            if result:
                file_path = result.get("file_path", "")

                # Check for specific identifiers to categorize the section
                if h_target_char in file_path:
                    section_categories["heap"].append(result)
                elif s_target_char in file_path:
                    section_categories["stack"].append(result)
                elif vvar_target_char in file_path:
                    section_categories["vvar"].append(result)
                elif vsyscall_target_char in file_path:
                    section_categories["vsyscall"].append(result)
                elif vdso_target_char in file_path:
                    section_categories["vdso"].append(result)
                elif file_path.startswith(anon_target_char): 
                    section_categories["anon"].append(result)
                elif file_path.strip() == "" and result["permissions"].startswith("---"):
                    section_categories["guard_pages"].append(result)
                elif file_path.startswith("/dev/"):
                    section_categories["device_mappings"].append(result)
                # Check for tmpfs or shared memory
                elif file_path.startswith("/dev/shm") or "tmpfs" in file_path:
                    section_categories["tmpfs_shm"].append(result)
                elif file_path and f_path_target_char in file_path:
                    
                    # The (?:\.\d+)* handles zero or more version numbers
                    if re.search(r"\.so(\.\d+)*$", file_path):
                        section_categories["shared_libs"].append(result)
                    
                    elif re.search(r"/(?:[a-zA-Z0-9_-]+)$", file_path) or "firefox" in file_path:
                        # Check if the path is not a shared library and is a potential executable
                        if not re.search(r"\.so", file_path):
                            section_categories["executable"].append(result)
                        else:
                            section_categories["shared_libs"].append(result)
                    else:
                        section_categories["file_backed"].append(result)
                else:
                    section_categories["none"].append(result)
        return section_categories

def format_output_bytes(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_none_log, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out, length_out, flag_sec_log, strings_out, save_dir, flag_strings_log):
    """
    Main orchestration function for formatting and printing memory dump output.

    This function acts as a controller, examining the provided flags to determine
    which memory regions to process. It either logs unclassified regions to a file
    or prints them to the console.

    Args:
        mem_path (str): The path to the /proc/PID/mem file.
        input_dict (dict): The dictionary of categorized memory regions.
        ... (and so on for all flags, as defined in cli.py)
        verbose_out (bool): If True, prints additional information like permissions and strings.
        length_out (int): The length of strings to extract when in verbose mode.
    """
    
    #control if print to console
    print_to_console = True
    
    flag_options_all = {
        "executable": flag_exec_sec,
        "shared_libs": flag_slib_sec,
        "heap": flag_he_sec,
        "stack": flag_st_sec,
        "vvar": flag_vvar_sec,
        "vsyscall": flag_vsys_sec,
        "vdso": flag_vdso_sec,
        "anon": flag_anon_sec,
        "guard_pages": flag_gp_sec,
        "file_backed": flag_fb_sec,
        "tmpfs_shm": flag_ts_sec,
        "device_mappings": flag_dm_sec,
        "none": flag_none_sec
    }

    if flag_none_log:
        print_to_console = False
        none_dict = input_dict.get("none", {})
        if none_dict:
            save_memory_regions(mem_path, none_dict, save_dir, is_binary=False, length_out=length_out, verbose_out=verbose_out)
        else:
            click.secho("No unclassified regions found to save.", fg="yellow")
    
    elif flag_sec_log:
        print_to_console = False
        sections_to_save = []
        for flag, is_true in flag_options_all.items():
            if is_true: 
                sections_to_save.append(flag)

        for section_name in sections_to_save: 
            section_dict = input_dict.get(section_name, {})
            if section_dict: 
                section_output_dir = os.path.join(save_dir, section_name)
                save_memory_regions(mem_path, section_dict, section_output_dir, is_binary=True)
            else: 
                click.secho(f"No regions found for section '{section_name}'.", fg="yellow")
    
    elif flag_strings_log: 
        sections_to_save = []
        print_to_console = False

        for flag, is_true in flag_options_all.items():
            if is_true: 
                sections_to_save.append(flag)

        for section_name in sections_to_save: 
            section_dict = input_dict.get(section_name, {})
            if section_dict: 
                section_output_dir = os.path.join(save_dir, section_name)
                save_memory_regions(mem_path, section_dict, section_output_dir, is_binary=False, is_strings=True)
            else: 
                click.secho(f"No regions found for section '{section_name}'.", fg="yellow")
    
    if print_to_console: 
        # If the user chose to show all sections
        sections_to_show = []

        if flag_all_sec is True:
            for key in input_dict.keys():
                if key != "none":
                    sections_to_show.append(key)
        else:
            for flag, is_true in flag_options_all.items():
                if is_true: 
                    sections_to_show.append(flag)
        
        # Use the helper function to read bytes and print sections to the console
        read_bytes_show_sections(mem_path, input_dict, sections_to_show, length_out, verbose_out, strings_out)
    
    none_dict = input_dict.get("none", {})
    none_dict_length = len(none_dict) 
    # Provide a summary of unclassified regions if they were not logged
    if not flag_none_log or not flag_sec_log:
        click.secho(f"{none_dict_length} unclassified memory regions found", fg="yellow")
        click.secho(f"Use '--unclassified' command to print them.", fg="yellow")
        click.secho(f"Use '--log-unclassified' command to save them to a log file.", fg="yellow")


def dump_bytes_mem(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_none_log, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out, length_out, flag_sec_log, strings_out, save_dir, flag_strings_log):
    """
    Main orchestration function for dumping memory bytes from a process.

    This function acts as a wrapper, taking all the user-provided flags and
    passing them to the `format_output_bytes` function to handle the actual
    reading and formatting.

    Args:
        mem_path (str): The path to the /proc/PID/mem file.
        input_dict (dict): The dictionary of categorized memory regions.
        ... (and so on for all flags, as defined in cli.py)
        verbose_out (bool): If True, prints additional information like permissions and strings.
        length_out (int): The length of strings to extract when in verbose mode.
    """
    format_output_bytes(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_none_log, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out, length_out, flag_sec_log, strings_out, save_dir, flag_strings_log)

