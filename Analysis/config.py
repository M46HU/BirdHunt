"""
Configuration file for the BirdHunt forensic tool.
Holds all constants, paths, and settings.
"""

from pathlib import Path

# --- File Paths ---
# Directory for temporary plot/map images
PLOT_DIR = Path('plots_temp') 

# --- MAVLink Settings ---
DEFAULT_DIALECT = 'ardupilotmega'

# --- Analysis Settings ---
ALT_THRESHOLD = 5.0 # Altitude in meters for takeoff/land detection

# --- Data Extraction ---
# This dictionary defines the *only* fields we will extract.
FORENSIC_FIELDS = {
    # === Tier 1: Time & Location ===
    "SYSTEM_TIME": ["time_unix_usec", "time_boot_ms"],
    "GLOBAL_POSITION_INT": ["time_boot_ms", "lat", "lon", "alt", "relative_alt", "vx", "vy", "vz", "hdg"],
    "GPS_RAW_INT": ["time_usec", "lat", "lon", "alt", "vel", "cog"],
    "HOME_POSITION": ["latitude", "longitude", "altitude"],

    # === Tier 2: Pilot Intent & Mission ===
    "RC_CHANNELS": ["time_boot_ms", "chan1_raw", "chan2_raw", "chan3_raw", "chan4_raw"],
    "MISSION_ITEM_INT": ["seq", "frame", "command", "x", "y", "z"],
    "HEARTBEAT": ["base_mode", "custom_mode", "system_status"],
    "ATTITUDE": ["time_boot_ms", "roll", "pitch", "yaw"],
    "VFR_HUD": ["groundspeed", "heading", "throttle", "alt", "climb"],

    # === Tier 3: System Status & Events ===
    "STATUSTEXT": ["text"],
    "COMMAND_ACK": ["command", "result"],

    # === Tier 4: Hardware & Simulation Check ===
    "PARAM_VALUE": ["param_id", "param_value"],
    "SIMSTATE": ["lat", "lng", "roll", "pitch", "yaw"]
}