"""
Handles the creation of 2D plots.
MODIFIED to return figure objects for Tkinter GUI.
FIXED to be thread-safe by avoiding pyplot.
"""

from matplotlib.figure import Figure
import matplotlib.dates as mdates
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def plot_altitude(df):
    try:
        fig = Figure(figsize=(10, 4))
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(df['timestamp'], df['GLOBAL_POSITION_INT.alt'] / 100.0, color='#2980b9', linewidth=2)
        ax.fill_between(df['timestamp'], df['GLOBAL_POSITION_INT.alt'] / 100.0, alpha=0.1, color='#2980b9')
        ax.set_title('Altitude Profile (MSL)', fontweight='bold')
        ax.set_xlabel('Flight Time (s)')
        ax.set_ylabel('Altitude (m)')
        ax.grid(True, linestyle='--', alpha=0.5)
        
        return fig
    except Exception as e:
        print(f"Altitude plot error: {e}")
        return None

def plot_rc_channels(df):
    try:
        fig = Figure(figsize=(10, 4))
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(df['timestamp'], df['RC_CHANNELS.chan1_raw'], label='Roll (Ch1)', alpha=0.7)
        ax.plot(df['timestamp'], df['RC_CHANNELS.chan2_raw'], label='Pitch (Ch2)', alpha=0.7)
        ax.plot(df['timestamp'], df['RC_CHANNELS.chan3_raw'], label='Throttle (Ch3)', linewidth=2, color='black')
        ax.plot(df['timestamp'], df['RC_CHANNELS.chan4_raw'], label='Yaw (Ch4)', alpha=0.7)
        ax.set_title('Pilot Inputs (RC Raw)', fontweight='bold')
        ax.set_xlabel('Flight Time (s)')
        ax.set_ylabel('PWM Value (1000-2000)')
        ax.legend(loc='upper right', ncol=4)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        return fig
    except Exception as e:
        print(f"RC plot error: {e}")
        return None