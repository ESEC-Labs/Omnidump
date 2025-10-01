import pwd
import os
import sys
import click
import psutil
from . import pid_mapping_logic

'''
--- Supporting functions ---
'''

def pid_map_file(
        process_maps,
        process_mem,
        flag_exec_sec,
        flag_slib_sec,
        flag_all_sec,
        flag_he_sec,
        flag_st_sec,
        flag_vvar_sec,
        flag_vsys_sec,
        flag_vdso_sec,
        flag_none_sec,
        flag_none_log,
        flag_anon_sec,
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out,
        length_out,
        flag_sec_log,
        strings_out,
        save_dir,
        flag_strings_log
        ):
    """
    Given a PID, map the process's memory from the /proc file system.

    This function reads from the process's /proc/{id}/maps and /proc/{id}/mem files
    to identify memory regions and then dumps the raw bytes based on the flags provided.

    Args:
        process_maps (str): The path to the process's /proc/{id}/maps file.
        process_mem (str): The path to the process's /proc/{id}/mem file.
        flag_exec_sec (bool): True if the executable sections should be dumped.
        flag_slib_sec (bool): True if the shared library sections should be dumped.
        flag_all_sec (bool): True if all memory sections should be dumped.
        flag_he_sec (bool): True if the heap section should be dumped.
        flag_st_sec (bool): True if the stack section should be dumped.
        flag_vvar_sec (bool): True if the vvar sections should be dumped.
        flag_vsys_sec (bool): True if the vsys sections should be dumped.
        flag_vdso_sec (bool): True if the vdso sections should be dumped.
        flag_none_sec (bool): True if the unclassified sections should be dumped.
        flag_none_log (str): Path to a log file for unclassified sections, or None.
        flag_anon_sec (bool): True if anonymous memory sections should be dumped.
        flag_gp_sec (bool): True if guard page sections should be dumped.
        flag_fb_sec (bool): True if file-backed sections should be dumped.
        flag_ts_sec (bool): True if tmpfs or shared memory sections should be dumped.
        flag_dm_sec (bool): True if device-mapped sections should be dumped.
        verbose_out (bool): True if permissions, inodes, and extracted strings should be dumped.
        length_out (int): The length of strings to extract when in verbose mode.
    """


    dict_to_pass = pid_mapping_logic.group_regions(process_maps)
        

    pid_mapping_logic.dump_bytes_mem(
            process_mem,
            dict_to_pass,
            flag_exec_sec,
            flag_slib_sec,
            flag_all_sec,
            flag_he_sec,
            flag_st_sec,
            flag_vvar_sec,
            flag_vsys_sec,
            flag_vdso_sec,
            flag_none_sec,
            flag_none_log,
            flag_anon_sec,
            flag_gp_sec,
            flag_fb_sec,
            flag_ts_sec,
            flag_dm_sec,
            verbose_out,
            length_out,
            flag_sec_log,
            strings_out,
            save_dir,
            flag_strings_log
            )

def pid_pass_flags(
        pid,
        flag_exec_sec,
        flag_slib_sec,
        flag_all_sec,
        flag_he_sec,
        flag_st_sec,
        flag_vvar_sec,
        flag_vsys_sec,
        flag_vdso_sec,
        flag_none_sec,
        flag_none_log,
        flag_anon_sec,
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out,
        length_out,
        flag_sec_log,
        strings_out,
        save_dir,
        flag_strings_log
        ):
    """
    Validates arguments and handles the actual memory dumping logic.

    Args:
        pid (int): The process ID to dump memory from.
        flag_exec_sec (bool): True if the executable sections should be dumped.
        flag_slib_sec (bool): True if the shared library sections should be dumped.
        ... (and so on for all flags)
    """

    click.echo(f"Dumping memory segments for PID {pid}...\n")
    try:
        process_maps = f"/proc/{pid}/maps"
        process_mem = f"/proc/{pid}/mem"
 

        pid_map_file(
            process_maps,
            process_mem,
            flag_exec_sec,
            flag_slib_sec,
            flag_all_sec,
            flag_he_sec,
            flag_st_sec,
            flag_vvar_sec,
            flag_vsys_sec,
            flag_vdso_sec,
            flag_none_sec,
            flag_none_log,
            flag_anon_sec,
            flag_gp_sec,
            flag_fb_sec,
            flag_ts_sec,
            flag_dm_sec,
            verbose_out,
            length_out,
            flag_sec_log,
            strings_out,
            save_dir,
            flag_strings_log
            )

    except PermissionError:
        click.echo("Permission denied. Please run as sudo.")
    except FileNotFoundError:
        click.echo("Process file not found. Please run 'omnidump' show' to look for another process.")
'''
--- Commands ---
'''
@click.group()
def main():
    ''' Omnidump CLI memory dumping tool'''
    pass


'''
MAIN DUMP COMMAND
'''
@main.group(name="dump")
def dump():
    ''' Dump anything memory region from different architectures including processes. '''
    pass


'''
SHOW COMMAND
'''

@main.command(name="show")
@click.option('--owner', 'user', type=str, help="Filter processes by the owner's name.")
@click.option('-sp', 'flag_sleeping', is_flag=True, help="Filter the output of the show command. Show only sleeping processes.")
@click.option('-id', 'flag_idle', is_flag=True, help="Filter the output of the show command. Show only idle processes.")
@click.option('-rn', 'flag_running', is_flag=True, help="Filter the output of the show command. Show only running processes.")
def show(user, flag_sleeping, flag_idle, flag_running):
    """
    Show running processes.
    """
    click.echo("Showing processes...")

    sections_to_show = []

    # Define a color map for process statuses
    status_colors = {
        "running": "green",
        "idle": "yellow",
        "sleeping": "blue",
    }

    flag_options= {
        "sleeping": flag_sleeping, 
        "running": flag_running,
        "idle": flag_idle
    }

    # Determine which statuses to show based on the flags
    statuses_to_show = []
    for status, is_set in flag_options.items():
        if is_set:
            statuses_to_show.append(status)

    # If no flags are set, show all statuses
    if not statuses_to_show:
        statuses_to_show = list(flag_options.keys())
    
    # Check if a user filter is provided and validate it
    if user:
        try:
            pwd.getpwnam(user)
        except KeyError:
            click.echo(f"Error: The user '{user}' doesn't exist.", err=True)
            sys.exit(1)
    
    found_processes = 0

    for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
        proc_info = proc.info

        if user and proc_info['username'] != user:
            continue

        if proc_info['status'] not in statuses_to_show:
            continue
        
        found_processes += 1

        color = status_colors.get(proc_info['status'], "white")
        
        click.secho(
            f"PID: {proc_info['pid']} - Name: {proc_info['name']} - Status: {proc_info['status']} - Owner: {proc_info['username']}",
            fg=color
        )
    if found_processes == 0:
        click.echo("No processes found matching the specified criteria.")
'''
MAIN PID COMMAND
'''
@dump.command(name="pid")
@click.argument('pid', type=int, required=False)
@click.option('--verbose', 'verbose_out', is_flag=True, help="Dump permissions, inode, and extracted strings.")
@click.option('--length', 'length_out', type=int, help="Set the strings to length N (default is length 4).")
@click.option('--self', 'dump_self', is_flag=True, help="Dump the current process.")
@click.option('--strings', 'strings_out', is_flag=True, help="Dumps strings to the terminal. Strings by default are length 4. Use '--length' to increase the length.")
@click.option('--save-dir', 'save_dir', type=click.Path(exists=False, dir_okay=True, file_okay=False), help="Path for directory to save data to.")
@click.option('--all', 'flag_all_sec', is_flag=True, help="Dump all memory sections.")
@click.option('--log-sections', 'flag_sec_log', is_flag=True, help="Save a section and each individual region to bytes to a file. Give a parent directory to save information to. Use section flags to save data.")
@click.option('--unclassified', 'flag_none_sec', is_flag=True, help="Dump sections that can't be mapped.")
@click.option('--log-unclassified', 'flag_none_log', is_flag=True, help="Save uncategorized sections to a log file. If given directory doesn't exist the command will create it.If no section flags are specified then command will look for unclassified regions throughout each section. Please see examples for more information.")
@click.option('--log-strings', 'flag_strings_log', is_flag=True, help="Save a section and each individaul regions strings to a txt file. Use --save-dir and give a parent directory to save data to. Use section flags to save data.")
@click.option('-e', 'flag_exec_sec', is_flag=True, help="Dump only executable sections.")
@click.option('-sl', 'flag_slib_sec', is_flag=True, help="Dump only shared library sections.")
@click.option('-h', 'flag_he_sec', is_flag=True, help="Dump only heap sections.")
@click.option('-st', 'flag_st_sec', is_flag=True, help="Dump only stack sections.")
@click.option('-vv', 'flag_vvar_sec', is_flag=True, help="Dump only vvar sections.")
@click.option('-vs', 'flag_vsys_sec', is_flag=True, help="Dump only vsys sections.")
@click.option('-vd', 'flag_vdso_sec', is_flag=True, help="Dump only vdso sections.")
@click.option('-an', 'flag_anon_sec', is_flag=True, help="Dump only anon sections.")
@click.option('-gp', 'flag_gp_sec', is_flag=True, help="Dump only guard page sections.")
@click.option('-fb', 'flag_fb_sec', is_flag=True, help="Dump only file backed sections.")
@click.option('-ts', 'flag_ts_sec', is_flag=True, help="Dump only tmpfs or shared memory sections.")
@click.option('-dm', 'flag_dm_sec', is_flag=True, help="Dump only device mapped sections.")
def dump_pid(
        pid,
        dump_self,
        flag_exec_sec,
        flag_slib_sec,
        flag_all_sec,
        flag_he_sec,
        flag_st_sec,
        flag_vvar_sec,
        flag_vsys_sec,
        flag_vdso_sec,
        flag_none_sec,
        flag_anon_sec,
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out,
        length_out,
        flag_none_log,
        flag_sec_log,
        strings_out,
        save_dir,
        flag_strings_log
        ):
    ''' Dumps memory maps from a given process ID or the current process. '''

    
    # 1. Argument Validation (Fail-fast checks)
    if pid is not None and dump_self:
        click.echo("Error: Cannot provide both a PID and the --self flag. Please run omnidump dump pid --help for more information.")
        sys.exit(1)

    if not pid and not dump_self:
        click.echo("Error: A PID or --self flag is required. Please run omnidump dump pid --help for more information.")
        sys.exit(2)

    # 1.1 Validate log flags 
    #Validate --log-unclassified and --verbose / --length flag combinations

    if flag_none_log:
        other_section_flags = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, 
        
        ])
        if other_section_flags:  
            click.echo("Error: The '--log-unclassified' flag cannot be used with any other section flags.")
            sys.exit(3)
        
        if length_out is not None and not verbose_out:
            click.echo("Error: When using '--log-unclassified', the '--length' flag requires the '--verbose' flag. Please run omnidump dump pid --help for more information.")
            sys.exit(4)

        if save_dir is None: 
            click.echo("Error: When using '--log-unclassified', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information.")
            sys.exit(5) 
    
    #Validate --log-sections  
    if flag_sec_log:
        other_section_flags_2 = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec,
        
        ])
        
        other_flags =any([
            length_out, verbose_out  
        ])
        if not any([flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec]):   
            click.echo("Error: The '--log-sections' flag requires at least one section flag (-e, -h, etc.) to be specified.")
            sys.exit(6)
        
        if save_dir is None: 
            click.echo("Error: When using '--log-sections', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information.")
            sys.exit(7)

        if save_dir and other_section_flags_2 and other_flags: 
            click.echo("Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information.")
            sys.exit(8)
    

    #Validate --log-strings  
    if flag_strings_log:
        
        other_section_flags_3 = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec,
        
        ])

        other_flags_2 =any([
            length_out, verbose_out  
        ])
        if not any([flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec]):
            click.echo("Error: The '--log-strings' flag requires at least one section flag (-e, -h, etc.) to be specified.")
            sys.exit(9)
        
        if save_dir is None: 
            click.echo("Error: When using '--log-sections', the '--save-dir' flag is required. Please run omnidump dump pid --help for more information.")
            sys.exit(10)
        
        if save_dir and other_section_flags_3 and other_flags_2: 
            click.echo("Error: When using '--log-sections', please reframe from using other flags such as: '--length', and '--verbose'. Please run omnidump dump pid --help for more information.")
            sys.exit(11)

    
    section_flags = any([
        flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
        flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
        flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec,
    ])

    log_flags = any([flag_none_log, flag_sec_log, flag_strings_log]) 

    if length_out is not None and not (verbose_out or strings_out):
        click.echo("Error: The '--length' flag requires the '--verbose' or the '--strings' flag. Please run omnidump dump pid --help for more information.")
        sys.exit(13)

    if (dump_self or pid) and not section_flags:
        if log_flags is True: 
            pass
        else:
            click.echo("Error: The '--self' or 'pid' flag requires at least one section flag.")
            sys.exit(12)
    
    '''
    if strings_out and not section_flags: 
        click.echo("Error: The '--strings' flag requires at least one section flag.")
        sys.exit(13)
    '''

    if length_out is not None and length_out <= 0:
        click.secho("Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information.")
        sys.exit(14)

    if section_flags is not None and save_dir is not None:
        if log_flags is True: 
            pass
        else: 
            click.secho("Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag.")
            sys.exit(15)

    # 2. Determine Target PID
    if dump_self:
        target_pid = os.getpid()
    else:
        target_pid = pid 
        
    if flag_all_sec:
        flag_exec_sec = True
        flag_slib_sec = True
        flag_he_sec = True
        flag_st_sec = True
        flag_vvar_sec = True
        flag_vsys_sec = True
        flag_vdso_sec = True
        flag_none_sec = True
        flag_gp_sec = True
        flag_fb_sec = True
        flag_ts_sec = True
        flag_dm_sec = True

    if length_out is None:
        length_out = 4
   
    # 4. Passes flags and PID to be mapped.
    pid_pass_flags(
        target_pid,
        flag_exec_sec,
        flag_slib_sec,
        flag_all_sec,
        flag_he_sec,
        flag_st_sec,
        flag_vvar_sec,
        flag_vsys_sec,
        flag_vdso_sec,
        flag_none_sec,
        flag_none_log,
        flag_anon_sec,
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out,
        length_out,
        flag_sec_log,
        strings_out,
        save_dir,
        flag_strings_log
    )
if __name__ == "__main__":
    main()

