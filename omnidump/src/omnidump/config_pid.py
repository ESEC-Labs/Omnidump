"""Configuration file used to minimize flag declarations in logic functions."""
from dataclasses import dataclass
from typing import Optional, List

ALL_SECTIONS_FLAGS = [
    'flag_exec_sec', 'flag_slib_sec', 'flag_all_sec', 'flag_he_sec', 
    'flag_st_sec', 'flag_vvar_sec', 'flag_vsys_sec', 'flag_vdso_sec', 
    'flag_none_sec', 'flag_anon_sec', 'flag_gp_sec', 'flag_fb_sec', 
    'flag_ts_sec', 'flag_dm_sec', 'flag_anon_map_sec'
]

FLAG_TO_SECTION_MAP = {
    'flag_exec_sec': 'executable',
    'flag_slib_sec': 'shared_libs',
    'flag_he_sec': 'heap',
    'flag_st_sec': 'stack',
    'flag_vvar_sec': 'vvar',
    'flag_vsys_sec': 'vsyscall', 
    'flag_vdso_sec': 'vdso',
    'flag_none_sec': 'none',
    'flag_anon_sec': 'anon',
    'flag_gp_sec': 'guard_pages', 
    'flag_fb_sec': 'file_backed',
    'flag_ts_sec': 'tmpfs_shm',
    'flag_dm_sec': 'device_mappings',
    'flag_anon_map_sec': 'anon_map',
}

@dataclass(frozen=True)
class CliAppConfig:
    """Holds all config and input parameters for PID dumping logic."""

    pid: Optional[int] = None
    dump_self: bool = False

    #Logging
    save_dir: Optional[str] = None
    verbose_out: bool = False
    length_out: int = None
    strings_out: bool = False
    flag_none_log: bool = False
    flag_sec_log: bool = False
    flag_strings_log: bool = False

    #Section flags
    flag_exec_sec: bool = False
    flag_slib_sec: bool = False
    flag_all_sec: bool = False
    flag_he_sec: bool = False
    flag_st_sec: bool = False
    flag_vvar_sec: bool = False
    flag_vsys_sec: bool = False
    flag_vdso_sec: bool = False
    flag_none_sec: bool = False
    flag_anon_sec: bool = False
    flag_gp_sec: bool = False
    flag_fb_sec: bool = False
    flag_ts_sec: bool = False
    flag_dm_sec: bool = False
    flag_anon_map_sec: bool = False

    def section_flags_active(self) -> List [str]:
        """Returns list of section flags that are set to True."""
        active_flags = []
        for flag_name in ALL_SECTIONS_FLAGS:
            if getattr(self, flag_name):
                active_flags.append(flag_name)
        return active_flags
