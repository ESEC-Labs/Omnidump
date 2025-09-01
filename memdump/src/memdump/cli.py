import os
import sys
import click
import psutil
from . import categorize_memory_regions

'''
--- Supporting functions ---
'''

def map_file(
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
        flag_anon_sec, 
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out
        ):
        '''Given a file name match a regex expression and get each readable string from a mmapped file'''  
    

        dict_to_pass = categorize_memory_regions.group_regions(process_maps) 
        
        categorize_memory_regions.dump_bytes_mem(
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
                flag_anon_sec,
                flag_gp_sec,
                flag_fb_sec,
                flag_ts_sec,
                flag_dm_sec,
                verbose_out)

def dump_memory(
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
        flag_anon_sec,
        flag_gp_sec,
        flag_fb_sec,
        flag_ts_sec,
        flag_dm_sec,
        verbose_out
        ):
    """Handles the actual memory dumping logic."""

    click.echo(f"Dumping memory segments for PID {pid}...\n")
    try:
        process_maps = f"/proc/{pid}/maps"
        process_mem = f"/proc/{pid}/mem"

        map_file(
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
                flag_anon_sec,
                flag_gp_sec,
                flag_fb_sec,
                flag_ts_sec,
                flag_dm_sec,
                verbose_out)
        click.echo("Memory map has been dumped!\n")
    except PermissionError:
        click.echo("Permission denied. Please run as sudo.")
    except FileNotFoundError:
        click.echo("Process file not found. Please run 'memdump show' to look for another process.")

'''
--- Commands ---
'''
@click.group()
def main():
    ''' Memdump CLI memory dumping tool'''
    pass

@main.group(name="dump")
def dump():
    ''' Dump memory maps from a process ID or self. '''
    pass

@main.command(name="show")
@click.option('--owner', help="Filter by the owner name.")
def show(owner):
    ''' 
    Show running processes. Shows in the order of pid, name 
    '''

    click.echo("Showing process...")
    for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
        pid = proc.info['pid']
        name = proc.info['name']
        status = proc.info['status']
        owner = proc.info['username']

        if status == "running":
            color = "green"
        elif status == "idle":
            color = "yellow"
        elif status == "sleeping":
            color = "blue"
        else:
            color = "white"  

        click.secho(f"PID: {pid} - Name: {name} - Status: {status} - Owner: {owner}", fg=color)


@dump.command(name="pid")
@click.argument('pid', type=int, required=False)
@click.option('--self', 'dump_self', is_flag=True, help="Dump the current process.")
@click.option('--all', 'flag_all_sec', is_flag=True, help="Dump all memory sections.")
@click.option('--verbose', 'verbose_out', is_flag=True, help="Dump permissions, inode, and extracted strings.")
@click.option('-e', 'flag_exec_sec', is_flag=True, help="Dump only executable sections.")
@click.option('-sl', 'flag_slib_sec', is_flag=True, help="Dump only shared library sections.")
@click.option('-h', 'flag_he_sec', is_flag=True, help="Dump only heap sections.")
@click.option('-st', 'flag_st_sec', is_flag=True, help="Dump only stack sections.")
@click.option('-vv', 'flag_vvar_sec', is_flag=True, help="Dump only vvar sections.")
@click.option('-vs', 'flag_vsys_sec', is_flag=True, help="Dump only vsys sections.")
@click.option('-vd', 'flag_vdso_sec', is_flag=True, help="Dump only vdso sections.")
@click.option('-no', 'flag_none_sec', is_flag=True, help="Dump only none sections.")
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
        verbose_out
        ):
    ''' Dumps memory maps from a given process ID or the current process. '''
    # Check if a flag has been provided
    if not dump_self and not pid and not any([
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
        flag_dm_sec 
        ]):
        click.echo("Error: Please provide a flag or a PID. Use --help for more.")
        sys.exit(1)
    
    if dump_self and not pid and not any([
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
        flag_dm_sec]):
        click.echo("Error: Please provide a flag or a PID. Use --help for more.")
        sys.exit(1)
 
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
    elif flag_exec_sec or flag_slib_sec or flag_he_sec or flag_st_sec or flag_vvar_sec or flag_vsys_sec or flag_vdso_sec or flag_none_sec or flag_gp_sec or flag_fb_sec or flag_ts_sec or flag_dm_sec:
        all_sec = False

    if pid is not None and dump_self:
        click.echo("Error: Cannot provide both a PID and the --self flag. Use --help for more information.")
        sys.exit(1)

    # Determine the target PID
    if dump_self:
        target_pid = os.getpid()
    elif pid is not None:
        target_pid = pid
    else:
        click.echo("Error: A PID or --self flag is required for this command.")
        sys.exit(1)

    dump_memory(
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
            flag_anon_sec,
            flag_gp_sec, 
            flag_fb_sec, 
            flag_ts_sec,
            flag_dm_sec,
            verbose_out
            )

if __name__ == "__main__":
    main()
