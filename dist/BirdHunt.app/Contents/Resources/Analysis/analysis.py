"""
Handles all data analysis from the CSV.
"""

import datetime
import numpy as np
from . import config

def calculate_summary_stats(df):
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    duration = end_time - start_time
    return {'start_time': start_time, 'end_time': end_time, 'duration_sec': duration}

def calculate_timeline_events(df):
    timeline = []
    
    if 'SYSTEM_TIME.time_unix_usec' in df.columns:
        valid_times = df['SYSTEM_TIME.time_unix_usec'].dropna()
        first_unix_time = valid_times.iloc[0] / 1000000 if not valid_times.empty else None
    else:
        first_unix_time = None
    
    if first_unix_time is None:
        print("Warning: No SYSTEM_TIME found. Timeline will be relative.")
        first_log_timestamp = df['timestamp'].dropna().iloc[0]
        def get_real_time(log_ts):
            return "N/A (No GPS Time)"
    else:
        first_log_timestamp = df['timestamp'].dropna().iloc[0]
        unix_offset = first_unix_time - first_log_timestamp
        def get_real_time(log_ts):
            try:
                return datetime.datetime.fromtimestamp(log_ts + unix_offset).strftime('%H:%M:%S')
            except Exception:
                return "Time Error"

    timeline.append({
        'Event': 'Log Start',
        'Time (s)': f"{first_log_timestamp:.1f}",
        'Real Time (UTC)': get_real_time(first_log_timestamp)
    })

    if 'GLOBAL_POSITION_INT.lat' in df.columns:
        gps_data = df.dropna(subset=['GLOBAL_POSITION_INT.lat'])
        if not gps_data.empty:
             ts = gps_data.iloc[0]['timestamp']
             timeline.append({'Event': 'GPS Lock', 'Time (s)': f"{ts:.1f}", 'Real Time (UTC)': get_real_time(ts)})

    if 'GLOBAL_POSITION_INT.alt' in df.columns:
        alts = (df['GLOBAL_POSITION_INT.alt'].fillna(0) / 100.0)
        takeoff_idx = np.where(alts >= config.ALT_THRESHOLD)[0]
        
        if takeoff_idx.size > 0:
            ts = df['timestamp'].iloc[takeoff_idx[0]]
            timeline.append({'Event': 'Takeoff', 'Time (s)': f"{ts:.1f}", 'Real Time (UTC)': get_real_time(ts)})

        landing_idx = np.where(alts >= config.ALT_THRESHOLD)[0]
        if landing_idx.size > 0:
            data_after = df.iloc[landing_idx[-1] + 1:] 
            if not data_after.empty:
                ts = df['timestamp'].iloc[-1]
                timeline.append({'Event': 'Landing/End', 'Time (s)': f"{ts:.1f}", 'Real Time (UTC)': get_real_time(ts)})

    if 'HEARTBEAT.custom_mode' in df.columns:
        mode_changes = df.dropna(subset=['HEARTBEAT.custom_mode']).copy()
        mode_changes['Mode_Change'] = mode_changes['HEARTBEAT.custom_mode'].diff().fillna(0).astype(int)
        for _, row in mode_changes[mode_changes['Mode_Change'] != 0].iterrows():
            ts = row['timestamp']
            timeline.append({'Event': f"Mode: {int(row['HEARTBEAT.custom_mode'])}", 'Time (s)': f"{ts:.1f}", 'Real Time (UTC)': get_real_time(ts)})

    timeline.sort(key=lambda x: float(x['Time (s)']))
    return timeline