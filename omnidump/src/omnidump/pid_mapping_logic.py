import string
import itertools
import re
import os
from datetime import datetime
import click
from .config_pid import CliAppConfig, FLAG_TO_SECTION_MAP

def get_strings_from_bytes(byte_data, config: CliAppConfig):
    """
    Extracts printable strings from a byte sequence, with user-specified length.

    This function is a generator that yields a string as soon as it finds a
    sequence of printable characters of a certain minimum length.

    Args:
        byte_data (bytes): The input byte sequence.
        length_out (int, optional): The minimum length of strings to yield,
                                    as specified by the user.
    Yields:
        str: A string of printable characters.
    """

    fixed_default_min_length = 4
    try:
        min_length = config.length_out if config.length_out else fixed_default_min_length
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
    except TypeError as e:
        click.echo(f"Error: {e}")


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

def read_bytes_show_sections(mem_path, input_dict, sections_to_show, config: CliAppConfig):
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
        strings_out (bool): If True, prints only strings from region. 
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
                        string_list = list(itertools.islice(get_strings_from_bytes(chunk, config), 3))

                        if config.verbose_out is True:
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Major Minor Id: {maj_min_id}\n Extracted Strings: {string_list}\n")
                        elif config.strings_out is True:  
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n Extracted Strings: {string_list}\n")
                        else:
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n")
                    except OSError as e:
                        click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")

def save_memory_sections_bin_write(full_file_path, chunk, start, end):
    """
    Writes a chunk of memory data to a specified binary file. 

    Args: 
        full_file_path (str): The complete path to the output binary file.
        chunk (bytes): The memory data chunk to write. 
        start (int): The starting address of the memory region (for logging). 
        end (int): The ending address of the memory region (for logging).
    """

    try: 
        with open(full_file_path, 'wb') as bin_file: 
            bin_file.write(chunk)
    except OSError as e: 
        click.secho(f"Could not write chunk to binary file for region {hex(start)}-{hex(end)}: {e}")

def save_memory_sections(mem_path, regions_dict, output_path):
    """
    Reads specified memory regions from /proc/PID/mem and saves them as separate binary files. 

    Args:
        mem_path (str): Path to the /proc/PID/mem file. 
        regions_dict (list): A list of dictionaries where each dictionary a memory section to save.
        output_path (str): The dictionary where the binary files will be saved. 
    """
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
                    save_memory_sections_bin_write(full_file_path, chunk, start, end)
                except OSError as e:
                    click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")
        click.secho(f"Successfully saved {len(regions_dict)} region(s) to '{output_path}'.", fg="green") 



def save_memory_none_seek_read(start, end, line_num, path, permissions, inode, maj_min_id, mem, size, log_file, config: CliAppConfig):
    """
    Reads a memory chunk, extracts strings, and writes the summary to a log file (for unclassified regions).

    Args: 
        start (int): The starting address of the memory region. 
        end (int): The ending address of the memory region. 
        line_num (int): The line number/index of the region being processed.
        path (str): The file path associated with the region. 
        permissions (str): The read/write/execute/private permissions. 
        inode (str): The inode number.
        maj_min_id (str): The major:minor device ID.
        mem (file object): The open /proc/PID/mem file handle.
        size (int): The size of the region to read.
        log_file (file object): The file handle to write the log output to..
        verbose_out (bool, optional): If True, includes more details to log. Default is false. 
        length_out (int, optional): Minimum string length to extract. Defaults to 4.
    """
    try:
        mem.seek(start)
        chunk = mem.read(size)
        string_list = list(itertools.islice(get_strings_from_bytes(chunk, config), 3))

        if config.verbose_out is True:
            log_file.write(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Major Minor Id: {maj_min_id}\n Extracted Strings: {string_list}\n" + "\n")
        else:
            log_file.write(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n" + "\n")
    except OSError as e:
        click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")

def save_memory_none_bin_read(mem_path, regions_dict, log_file, config: CliAppConfig):
    """
    Reads all unclassified (none category) memory regions from /proc/PID/mem and logs details/strings.

    Args: 
        mem_path (str): Path to the /proc/PID/mem file. 
        regions_dict (list): List of unclassified memory section dictionaries. 
        log_file (file object): The file handle to write the log output to. 
        length_out (int, optional): Minimum string length to extract. Defaults to 4.
        verbose_out (boolean, optional): If True, includes more details to log. Default is false. 
    """
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

                save_memory_none_seek_read(start, end, line_num, path, permissions, inode, maj_min_id, mem, size, log_file=log_file, config=config) 

def save_memory_none(mem_path, regions_dict, config: CliAppConfig):
    """
    Handles saving unclassified memory regions to a timestamped log file. 

    Args:
        mem_path (str): The path to the /proc/PID/mem file. 
        regions_dict (list): List of the unclassified memory sections dictionaries.
        output_path (str): The dictionary where the log file will be saved. 
        length_out (int, optional): Minimum string length to extract. Defaults to 4.
        verbose_out (boolean, optional): If True, includes more details to log. Default is false.
    """

    # Create the user-specified directory if it doesn't exist
    os.makedirs(config.save_dir, exist_ok=True)
        
    # Construct the log file path with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"omnidump-{timestamp}-unclassified-regions.log"
    full_file_path = os.path.join(config.save_dir, filename)

    with open(full_file_path, 'w') as log_file:
        log_file.write("Unclassified Memory Regions:\n")
        save_memory_none_bin_read(mem_path, regions_dict, log_file, config)
    click.secho(f"Successfully saved {len(regions_dict)} unclassified region(s) to '{full_file_path}'.", fg="green")


def save_memory_strings_write(full_file_path, string_list, successful_saves_count):
    """
    Writes extracted strings from a memory region to a text file.

    Args:
        full_file_path (str): The complete path to the output strings file. 
        string_list (list of str): The list of strings extracted from a region. 
        successful_saves_count (list of int): A list used to track the count of successful saves (mutable object)
    """
    try:
        with open(full_file_path, "w") as strings_file:
            strings_file.write(f"\n--Extracted Strings --\n {string_list}")
        successful_saves_count[0] += 1
    except OSError as e: 
        click.secho(f"Could not write strings to file: {e}")

def save_memory_strings_read_bin(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, config: CliAppConfig): 
    """
    Reads specified memory regions from /proc/PID/mem, extract strings, and writes them to separate files.

    Args:
        full_file_path (str or None): This parameter is used to hold the path of the *last* file written, which is then returned. 
        successful_saves_count (list of int): A list used to track the count of successful saves (mutable object)
        mem_path (str): The path to the /proc/PID/mem file. 
        regions_dict (list): List of the unclassified memory sections dictionaries.
        output_path (str): The dictionary where the log file will be saved. 
        length_out (int, optional): Minimum string length to extract. Defaults to 4.
    
    Returns: 
        str or None: The full path of the last successfully processed file, or None if no regions were processed.
    """
    with open(mem_path, "rb") as mem:
        for line_num, region_dict in enumerate(regions_dict, 1):
            address, permissions, _, _, _ = get_section_information(region_dict)
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
                    string_list = list(get_strings_from_bytes(chunk, config))
                    filename = f"region-{hex(start)}-{hex(end)}-strings.txt"
                    full_file_path = os.path.join(output_path, filename)
                    
                    save_memory_strings_write(full_file_path, string_list, successful_saves_count)
                except OSError as e: 
                    click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")
        
    return full_file_path

def save_memory_strings(mem_path, regions_dict, output_path, config: CliAppConfig):
    """
    Orchestrates the process of extracting and saving strings from memory regions. 

    Args:
        mem_path (str): The path to the /proc/PID/mem file. 
        regions_dict (list): List of the unclassified memory sections dictionaries.
        output_path (str): The dictionary where the log file will be saved. 
        length_out (int, optional): Minimum string length to extract. Defaults to 4. 
    """ 
    full_file_path = None
    successful_saves_count = [0] 
    
    # Create the user-specified directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    full_file_path = save_memory_strings_read_bin(full_file_path, successful_saves_count, mem_path, regions_dict, output_path, config)
    
    if successful_saves_count[0] > 0: 
        if full_file_path is not None: 
            click.secho(f"Successfully saved strings of {len(regions_dict)} region(s) '{full_file_path}'.", fg="green")

def get_region_category(region_data):

    """
    Determines the category (heap, stack, etc.) for a single memory region

    Args: 
        region_data (dict): Dictionary representing a single memory region line 

    Returns: 
        str: The category name
    """

    file_path = region_data.get("file_path", "")
    permissions = region_data["permissions"]

    f_path_target_char = "/"
    h_target_char = "[heap]"
    s_target_char = "[stack]"
    vvar_target_char = "[vvar]"
    vsyscall_target_char = "[vsyscall]"
    anon_target_char = "[anon"
    vdso_target_char = "[vdso]"

    # Check for specific identifiers to categorize the section
    if h_target_char in file_path:
        return "heap"
    if s_target_char in file_path:
        return "stack"
    if vvar_target_char in file_path:
        return "vvar"
    if vsyscall_target_char in file_path:
        return "vsyscall"
    if vdso_target_char in file_path:
        return "vdso"
    if file_path.startswith(anon_target_char):
        return "anon"
    if file_path.strip() == "" and permissions.startswith("---"):
        return "guard_pages"
    if file_path.startswith("/dev/shm") or "tmpfs" in file_path:
        return "tmpfs_shm"
    if file_path.startswith("/dev/"):
        return "device_mappings"
    # Check for tmpfs or shared memory
    if file_path.strip() == "":
        return "anon_map"

    if file_path and f_path_target_char in file_path:
        # The (?:\.\d+)* handles zero or more version numbers
        if re.search(r"\.so(\.\d+)*$", file_path):
            return "shared_libs"
        if re.search(r"/(?:[a-zA-Z0-9_-]+)$", file_path) or "firefox" in file_path:
            # Check if the path is not a shared library and is a potential executable
            if not re.search(r"\.so", file_path):
                return "executable"
            return "shared_libs"
        return "file_backed"
    return "none"

def categorize_regions(file_content):

    """
    Processes map file lines and categorizes memory regions into a dictionary
        
    Args: 
        file_content (list of str): lines read from the /proc/pid/maps file 

    Returns: 
        dict: Categorized memory regions.
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
        "anon_map": [],
        "none": []
    }

    for line in file_content:
        result = process_lines(line)

        # Check if a match was successfully made
        if result:
            category = get_region_category(result)
            section_categories[category].append(result)

    return section_categories
def group_regions(file_path):

    """
    Reads a /proc/PID/maps file and categorizes memory regions/

    Args: 
        file_path (str): The path to the /proc/PID/maps file. 

    Returns: 
        dict or None: A dictionary of categorized memory regions, or None if the file is not found. 
    """

    try: 
        with open(file_path, 'r') as file: 
            file_content= file.readlines()
    except FileNotFoundError: 
        return None

    return categorize_regions(file_content)

def format_output_bytes_none_log(mem_path, input_dict, config: CliAppConfig):
    """
    Formats and saves unclassified (none) memory regions to a log file. 

    Args:
        mem_path (str): The path to the /proc/PID/mem file. 
        input_dict (dict): Dictionary of categorized memory regions.  
        verbose_out (boolean, optional): If True, includes more details to log. Default is false.
        length_out (int, optional): Minimum string length to extract. 
        save_dir (str): The dictionary where the log file will be saved. 
    """
    none_dict = input_dict.get("none", {})
    if none_dict:
        save_memory_none(mem_path, none_dict, config)
    else:
        click.secho("No unclassified regions found to save.", fg="yellow")


def format_output_bytes_section_log(mem_path, input_dict, section_flag_dict, config):
    """
    Formats and saves from specified memory sections (by flag) to separate binary files. 

    Args:
        mem_path (str): The path to the /proc/PID/mem file. 
        input_dict (dict): Dictionary of categorized memory regions.  
        save_dir (str): The dictionary where the log file will be saved.
        section_flag_dict (dict): Dictionary mapping section names to boolean flags 
    """
    
    sections_to_save = []
    for flag, is_true in section_flag_dict.items():
        if is_true: 
            section_name = FLAG_TO_SECTION_MAP.get(flag)
            if section_name: 
                sections_to_save.append(section_name)

    for section_name in sections_to_save: 
        section_dict = input_dict.get(section_name, {})
        if section_dict: 
            section_output_dir = os.path.join(config.save_dir, section_name)
            save_memory_sections(mem_path, section_dict, section_output_dir)
        else: 
            click.secho(f"No regions found for section '{section_name}'.", fg="yellow")


def format_output_bytes_strings_log(mem_path, input_dict, section_flag_dict, config: CliAppConfig):
    """
    Formats and saves extracted strings from specified memory sections to separate text files.

    Args:
        mem_path (str): The path to the /proc/PID/mem file. 
        input_dict (dict): Dictionary of categorized memory regions.  
        length_out (int, optional): Minimum string length to extract. 
        save_dir (str): The dictionary where the log file will be saved.
        section_flag_dict (dict): Dictionary mapping section names to boolean flags
    """
    if not isinstance(config.save_dir, str):
        click.secho(f"Internal Error: save_dir is not a valid path string ({config.save_dir}).")
        return

    sections_to_save = []
    for flag, is_true in section_flag_dict.items():
        if is_true: 
            section_name = FLAG_TO_SECTION_MAP.get(flag)
            if section_name: 
                sections_to_save.append(section_name)

    for section_name in sections_to_save: 
        section_dict = input_dict.get(section_name, {})
        if section_dict: 
            section_output_dir = os.path.join(config.save_dir, section_name)
            save_memory_strings(mem_path, section_dict, section_output_dir, config)
        else: 
            click.secho(f"No regions found for section '{section_name}'.", fg="yellow")

def format_output_bytes_console_log(mem_path, input_dict, section_flag_dict, config: CliAppConfig):
    """
    Formats and saves specified memory sections (by flag) to the console

    Args: 
        mem_path (str): The path to the /proc/PID/mem file. 
        input_dict (dict): Dictionary of categorized memory regions. 
        length_out (int, optional): Minimum string length to extract. 
        verbose_out (boolean, optional): If True, includes more details to log. Default is false.
        strings_out (bool, optional): If True, includes strings from specified memory sections  
    """
    
    # If the user chose to show all sections
    sections_to_show = []

    if config.flag_all_sec is True:
        for key in input_dict.keys():
            if key != "none":
                sections_to_show.append(key)
    else:
        for flag, is_true in section_flag_dict.items():
            if is_true:
                section_key = FLAG_TO_SECTION_MAP.get(flag)
                if section_key: 
                    sections_to_show.append(section_key)
    
    # Use the helper function to read bytes and print sections to the console
    if sections_to_show:
        read_bytes_show_sections(mem_path, input_dict, sections_to_show, config)
    else: 
        click.secho("No memory regions were selected for console output.", fg="red")


def format_output_bytes(mem_path, input_dict, config: CliAppConfig):
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

    
    print_to_console = True
    
    flag_options_all = {
        flag_name: getattr(config, flag_name)
        for flag_name in FLAG_TO_SECTION_MAP.keys()
    }
    

    sections_to_log_dict = {
        key: value for key, value in flag_options_all.items() if key != "none"
    }

    print_to_console = True 

    if config.flag_none_log:
        print_to_console = False
        format_output_bytes_none_log(mem_path, input_dict, config)
    
    elif config.flag_sec_log:
        print_to_console = False
        format_output_bytes_section_log(mem_path, input_dict, sections_to_log_dict, config)

    elif config.flag_strings_log:
        print_to_console = False
        format_output_bytes_strings_log(mem_path, input_dict, sections_to_log_dict, config)

    if print_to_console: 
        format_output_bytes_console_log(mem_path, input_dict, flag_options_all, config)
    
    none_dict = input_dict.get("none", {})
    none_dict_length = len(none_dict)

    # Provide a summary of unclassified regions if they were not logged
    if not config.flag_none_log and not config.flag_sec_log:
        if none_dict_length > 0: 
            click.secho(f"{none_dict_length} unclassified memory regions found", fg="yellow")
            click.secho("Use '--unclassified' command to print them.", fg="yellow")
            click.secho("Use '--log-unclassified' command to save them to a log file.", fg="yellow")


def dump_bytes_mem(mem_path, input_dict, config: CliAppConfig):
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
    format_output_bytes(mem_path, input_dict, config)

