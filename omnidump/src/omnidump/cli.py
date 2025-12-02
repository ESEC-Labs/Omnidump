import pwd
import os
import sys
import click
import psutil
from . import pid_mapping_logic
from .config_pid import CliAppConfig  

def pid_map_file(
        process_maps,
        process_mem,
        config: CliAppConfig 
        ):
    
    dict_to_pass = pid_mapping_logic.group_regions(process_maps)
    pid_mapping_logic.dump_bytes_mem(
            process_mem,
            dict_to_pass,
            config 
            )

def pid_pass_flags(config: CliAppConfig):
    """
    Validates arguments and handles the actual memory dumping logic.

    Args:
        pid (int): The process ID to dump memory from.
        flag_exec_sec (bool): True if the executable sections should be dumped.
        flag_slib_sec (bool): True if the shared library sections should be dumped.
        ... (and so on for all flags)
    """

    click.echo(f"Dumping memory segments for PID {config.pid}...\n")
    try:
        process_maps = f"/proc/{config.pid}/maps"
        process_mem = f"/proc/{config.pid}/mem"
        pid_map_file(
            process_maps,
            process_mem,
            config 
            )

    except PermissionError:
        click.echo("Permission denied. Please run as sudo.")
    except FileNotFoundError:
        click.echo("Process file not found. Run 'omnidump' show' to look for another process.")

@click.group()
def main():
    #pylint: disable=W0105
    ''' Omnidump CLI memory dumping tool'''


#Main dump command
@main.group(name="dump")
def dump():
    #pylint: disable=W0105
    ''' Dump memory regions/sections from different MCU and linux processes. '''



#PID: Show command
@main.command(name="show")
@click.option('--owner', 'user', type=str, help="Filter processes by the owner's name.")
@click.option('-sp', 'flag_sleeping', is_flag=True, help="Show only sleeping processes.")
@click.option('-id', 'flag_idle', is_flag=True, help="Show only idle processes.")
@click.option('-rn', 'flag_running', is_flag=True, help="Show only running processes.")
def show(user, flag_sleeping, flag_idle, flag_running):
    """
    Show running processes.
    """
    click.echo("Showing processes...")
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
            sys.exit(16)
    found_processes = 0

    for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
        proc_info = proc.info

        if user and proc_info['username'] != user:
            continue

        if proc_info['status'] not in statuses_to_show:
            continue
        found_processes += 1
        color = status_colors.get(proc_info['status'], "white")
        #pylint: disable=C0301
        final_output= f"PID: {proc_info['pid']} - Name: {proc_info['name']} - Status: {proc_info['status']} - Owner: {proc_info['username']}"
        click.secho(final_output, fg=color)
    if found_processes == 0:
        click.echo("No processes found matching the specified criteria.")

@dump.command(name="pid")
@click.argument('pid', type=int, required=False)
@click.option('--verbose', 'verbose_out', is_flag=True,
              help="Dump permissions, inode, and extracted strings.")
@click.option('--length', 'length_out', type=int,
              help="Set the minimum length for extracted strings (default is 4).")
@click.option('--self', 'dump_self', is_flag=True,
              help="Dump the current process.")
@click.option('--strings', 'strings_out', is_flag=True,
              help=("Dumps strings to the terminal. Strings by default are length 4. "
                    "Use '--length' to increase the length."))
@click.option('--save-dir', 'save_dir',
              type=click.Path(exists=False, dir_okay=True, file_okay=False),
              help="Path for directory to save data to.")
@click.option('--all', 'flag_all_sec', is_flag=True,
              help="Dump all memory sections.")
@click.option('--log-sections', 'flag_sec_log', is_flag=True,
              help=("Save a section and each individual region to bytes to a file."
                    "Provide a parent directory using '--save-dir'."))
@click.option('--unclassified', 'flag_none_sec', is_flag=True,
              help="Dump memory sections that cannot be mapped.")
@click.option('--log-unclassified', 'flag_none_log', is_flag=True,
              help=("Save uncategorized sections to a log file. Creates the directory "
                    "if it doesn't exist. See examples for more information."))
@click.option('--log-strings', 'flag_strings_log', is_flag=True,
              help=("Save a section and each individual region's strings to a .txt file. "
                    "Use --save-dir to specify a parent directory."))
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
@click.option('-am', 'flag_anon_map_sec', is_flag=True, help="Dump only anon mapping sections.")
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
        flag_strings_log,
        flag_anon_map_sec
        ):
    ''' Dumps memory maps from a given process ID or the current process. '''
    # 1. Argument Validation (Fail-fast checks)
    if pid is not None and dump_self:
        click.echo("Error: Cannot provide both a PID and the --self flag."
                   "Please run omnidump dump pid --help for more information.")
        sys.exit(1)
    if not pid and not dump_self:
        click.echo("Error: A PID or --self flag is required."
                   "Please run omnidump dump pid --help for more information.")
        sys.exit(2)

    # 1.1 Validate log flags
    #Validate --log-unclassified and --verbose / --length flag combinations

    if flag_none_log:
        other_section_flags = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, flag_anon_map_sec
        ])
        if other_section_flags:
            click.echo("Error: The '--log-unclassified' flag"
                       " cannot be used with any other section flags.")
            sys.exit(3)
        if length_out is not None and not verbose_out:
            click.echo("Error: When using '--log-unclassified', the '--length'"
                       " flag requires the '--verbose' flag."
                       "Please run omnidump dump pid --help for more information.")
            sys.exit(4)

        if save_dir is None:
            click.echo("Error: When using '--log-unclassified', the '--save-dir' flag is required."
                       "Please run omnidump dump pid --help for more information.")
            sys.exit(5)
    if flag_sec_log:
        other_section_flags_2 = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, flag_anon_map_sec
        ])
        other_flags =any([
            length_out, verbose_out
        ])
        if not any([flag_exec_sec, flag_slib_sec, flag_all_sec,
                    flag_he_sec, flag_st_sec, flag_vvar_sec,
                    flag_vsys_sec, flag_vdso_sec, flag_none_sec,
                    flag_anon_sec, flag_gp_sec, flag_fb_sec,
                    flag_ts_sec, flag_dm_sec, flag_anon_map_sec
        ]):
            click.echo("Error: The '--log-sections' flag requires"
                       "at least one section flag (-e, -h, etc.) to be specified.")
            sys.exit(6)
        if save_dir is None:
            click.echo("Error: When using '--log-sections', the '--save-dir' flag is required."
                       "Please run omnidump dump pid --help for more information.")
            sys.exit(7)

        if save_dir and other_section_flags_2 and other_flags:
            click.echo("Error: When using '--log-sections',"
                       "please reframe from using other flags such as:"
                       " '--length', and '--verbose'."
                       "Please run omnidump dump pid --help for more information.")
            sys.exit(8)
    ''' Flag strings log'''
    if flag_strings_log:
        other_section_flags_3 = any([
            flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec,
            flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec,
            flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, flag_anon_map_sec
        
        ])

        other_flags_2 =any([
            length_out, verbose_out  
        ])
        if not any([flag_exec_sec, flag_slib_sec, flag_all_sec, flag_he_sec, flag_st_sec, flag_vvar_sec, flag_vsys_sec, flag_vdso_sec, flag_none_sec, flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, flag_anon_map_sec]):
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
        flag_anon_sec, flag_gp_sec, flag_fb_sec, flag_ts_sec, flag_dm_sec, flag_anon_map_sec
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
    
    if length_out is not None and length_out <= 0:
        click.secho("Error: Please provide a value greater than 0 for '--length'. Please run omnidump dump pid --help for more information.")
        sys.exit(14)

    if section_flags is not None and save_dir is not None:
        if log_flags is True: 
            pass
        else: 
            click.secho("Error: Section flags (-e, -h, --all, --unclassified, etc.) cannot be used with '--save-dir DIR' flag.")
            sys.exit(15)

    if length_out is not None and length_out >= 30: 
        click.echo("Error: Please refrain from entering a value greater than or equal to 30. Please run omnidump dump pid --help for more information.")
        sys.exit(16)

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
        flag_anon_map_sec = True

    if length_out is None:
        length_out = 4

    if save_dir is None and not log_flags:
        save_dir = ""


    config = CliAppConfig(
        pid=target_pid,
        dump_self=dump_self,
        save_dir=save_dir,
        length_out=length_out,
        verbose_out=verbose_out,
        strings_out=strings_out,
        
        # Log flags
        flag_none_log=flag_none_log,
        flag_sec_log=flag_sec_log,
        flag_strings_log=flag_strings_log,
        
        # Section flags
        flag_exec_sec=flag_exec_sec,
        flag_slib_sec=flag_slib_sec,
        flag_all_sec=flag_all_sec, 
        flag_he_sec=flag_he_sec, 
        flag_st_sec=flag_st_sec,
        flag_vvar_sec=flag_vvar_sec,
        flag_vdso_sec=flag_vdso_sec,
        flag_none_sec=flag_none_sec,
        flag_anon_sec=flag_anon_sec,
        flag_gp_sec=flag_gp_sec,
        flag_fb_sec=flag_fb_sec,
        flag_dm_sec=flag_dm_sec,
        flag_anon_map_sec=flag_anon_map_sec
    )

    pid_pass_flags(config)

if __name__ == "__main__":
    main()

