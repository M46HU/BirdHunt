"""
Configuration file for the BirdHunt forensic tool.
Holds all constants, paths, and settings.
"""

from pathlib import Path

PLOT_DIR = Path('plots_temp') 

DEFAULT_DIALECT = 'ardupilotmega'

ALT_THRESHOLD = 5.0

FORENSIC_FIELDS = {
    "SYSTEM_TIME": ["time_unix_usec", "time_boot_ms"],
    "GLOBAL_POSITION_INT": ["time_boot_ms", "lat", "lon", "alt", "relative_alt", "vx", "vy", "vz", "hdg"],
    "GPS_RAW_INT": ["time_usec", "lat", "lon", "alt", "vel", "cog"],
    "HOME_POSITION": ["latitude", "longitude", "altitude"],

    "RC_CHANNELS": ["time_boot_ms", "chan1_raw", "chan2_raw", "chan3_raw", "chan4_raw"],
    "MISSION_ITEM_INT": ["seq", "frame", "command", "x", "y", "z"],
    "HEARTBEAT": ["base_mode", "custom_mode", "system_status"],
    "ATTITUDE": ["time_boot_ms", "roll", "pitch", "yaw"],
    "VFR_HUD": ["groundspeed", "heading", "throttle", "alt", "climb"],

    "STATUSTEXT": ["text"],
    "COMMAND_ACK": ["command", "result"],

    "PARAM_VALUE": ["param_id", "param_value"],
    "SIMSTATE": ["lat", "lng", "roll", "pitch", "yaw"]
}