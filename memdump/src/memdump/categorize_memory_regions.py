import re
import click
import string
import itertools


'''
Workflow: 
    group_regions -> dump_bytes_mem
        process_lines -> groups_regions
            
        
        -Group regions gets the data from the /proc/id/maps file which contains: address, permissions, offsets, major and minor id, and file paths
'''

'''
---- Supporting Functions ----
'''

def get_strings_from_bytes(byte_data, min=4):
    result = ""
    for c in byte_data: 
        if chr(c) in string.printable:
            result += chr(c) 
            continue
        if len(result) >= min:
            yield result
        result = ""
    if len(result) >= min: 
        yield result


def get_section_information(section):
    """
    Extracts the address and permissions from a single section dictionary.

    Args:
        section (dict): A dictionary representing a single section.

    Returns:
        tuple: A tuple containing the address (str) and permissions (str).
    """
    address = section.get('address', 'N/A')
    permissions = section.get('permissions', 'N/A')
    path = section.get('file_path', 'N/A')
    inode = section.get('inode', 'N/A')
    return (address, permissions, path, inode)





def process_lines(line):
    match = re.match(r"(\w{0,16}+-\w{0,16})\s+(.{4})\s+(\w{8})\s+(\d{2}+:\d{2})\s+(\d[0-9]{0,8})\s*(.+)", line)
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

'''
---- Main Functions ----
'''
def group_regions(file_path):
    '''
    This dictionary contains the sections of data that match a certain condition.
    For example if the section has the stack label it's metadata (addresses, etc.) 
    would be stored in the stack list.
    '''

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

                # Check for specific identifiers
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

                # tmpfs or shared memory
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

def format_output_bytes(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out):

    
    sections_to_show = []

    # If the user chose to show all sections
    if flag_all_sec is True:
        sections_to_show = list(input_dict.keys())
    else:
        # Otherwise, build the list based on specific flags
        if flag_exec_sec:
            sections_to_show.append("executable")
        if flag_slib_sec:
            sections_to_show.append("shared_libs")
        if flag_he_sec:
            sections_to_show.append("heap")
        if flag_st_sec:
            sections_to_show.append("stack")
        if flag_vvar_sec:
            sections_to_show.append("vvar")
        if flag_vsys_sec:
            sections_to_show.append("vsyscall")
        if flag_vdso_sec:
            sections_to_show.append("vdso")
        if flag_anon_sec: 
            sections_to_show.append("anon")
        if flag_gp_sec:
            sections_to_show.append("gurad_pages")
        if flag_fb_sec: 
            sections_to_show.append("file_backed")
        if flag_ts_sec: 
            sections_to_show.append("tmpfs_shm")
        if flag_dm_sec:
            sections_to_show.append("device_mappings")
        if flag_none_sec:
            sections_to_show.append("none")

    with open(mem_path, "rb") as mem:
        for category_name in sections_to_show:
            # Access the list of sections for the current category
            sections_list = input_dict.get(category_name, [])

            if not sections_list:
                click.secho(f"\n--- {category_name.upper()} SECTIONS (No entries) ---\n", fg="red")
                continue
                
            click.secho(f"\n--- {category_name.upper()} SECTIONS ---\n", fg="green")
            
            for line_num, section in enumerate(sections_list, 1):
                # Call the helper function to get the data
                address, permissions, path, inode = get_section_information(section)
                start, end = [int(x, 16) for x in address.split("-")]

                if "r" in permissions: 
                    size = end - start
                    if size <= 0:
                        continue
                    try:
                        mem.seek(start)
                        chunk = mem.read(size)
                        string_list = list(itertools.islice(get_strings_from_bytes(chunk), 3))

                        if verbose_out is True: 
                             click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Permissions: {permissions}\n Inode: {inode}\n Address Range: ({hex(start)}-{hex(end)})\n Extracted Strings: {string_list}\n")
                        else: 
                            click.secho(f"{line_num}: Chunk Size: {len(chunk)} bytes\n Path: {path}\n Address Range: ({hex(start)}-{hex(end)})\n")

                    except OSError as e:
                        click.secho(f"Could not read region {hex(start)}-{hex(end)}: {e}")

def dump_bytes_mem(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out):

    '''
    Uses pattern matching get the detailed information from a line in the maps file
    from the group_regions file.

    Uses the format_output_bytes function to format the output
    '''

    format_output_bytes(mem_path, input_dict, flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, verbose_out)


