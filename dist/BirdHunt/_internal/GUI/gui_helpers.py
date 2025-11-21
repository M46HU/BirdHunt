"""
This module bridges the Tkinter GUI with the backend analysis scripts.
It calls the processing functions and returns the data/figures.
This is the "Controller" part of the application.
"""

import pandas as pd
from pathlib import Path
import tempfile
import os

from Analysis import log_converter
from Analysis import analysis
from Analysis import plotting
from Analysis import mapping
from Analysis import reporting
from Analysis import config

def process_log_file(tlog_file_path_str):
    """
    Runs the conversion and analysis steps.
    Returns the stats, timeline, and dataframe for plotting.
    """
    print(f"Processing {tlog_file_path_str}...")
    tlog_file = Path(tlog_file_path_str)
    
    temp_dir = tempfile.gettempdir()
    csv_path = Path(temp_dir) / f'{tlog_file.stem}_temp.csv'
    
    parser = log_converter.TlogParser(tlog_file)
    if not parser.to_csv(csv_path):
        raise Exception("Failed to convert .tlog to .csv")
    
    print("Analyzing data...")
    try:
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
        df = df.dropna(how='all', subset=df.columns.difference(['timestamp']))
        if df.empty: raise ValueError("No valid data in CSV")
    except Exception as e:
        raise Exception(f"Data Error: {e}")
    
    timeline = analysis.calculate_timeline_events(df)
    stats = analysis.calculate_summary_stats(df)
    
    os.remove(csv_path)
    
    print("Analysis complete.")
    return df, stats, timeline

def generate_plots(df):
    """
    Generates all plots and returns them as Figure objects.
    """
    print("Generating plots for GUI...")
    alt_fig = plotting.plot_altitude(df)
    rc_fig = plotting.plot_rc_channels(df)
    print("Plots generated.")
    return alt_fig, rc_fig

def generate_pdf_export(output_pdf_path, log_file_name, summary_stats, timeline_data,
                        df, alt_fig, rc_fig):
    """
    Saves the figures temporarily to disk, generates the PDF,
    and then cleans up the temp images.
    """
    print(f"Generating PDF at {output_pdf_path}...")
    
    config.PLOT_DIR.mkdir(parents=True, exist_ok=True)
    
    map_path = config.PLOT_DIR / 'temp_map.png'
    alt_path = config.PLOT_DIR / 'temp_alt.png'
    rc_path = config.PLOT_DIR / 'temp_rc.png'
    
    print("Generating map for export...")
    map_fig = mapping.create_flight_path_map(df)
    
    if map_fig: 
        mapping.add_basemap(map_fig)
        map_fig.savefig(map_path, bbox_inches='tight')
    if alt_fig: alt_fig.savefig(alt_path, bbox_inches='tight')
    if rc_fig: rc_fig.savefig(rc_path, bbox_inches='tight')
    
    reporting.generate_forensic_report(
        output_pdf_path=str(output_pdf_path),
        log_file_name=log_file_name,
        summary_stats=summary_stats,
        timeline_data=timeline_data,
        map_image_path=map_path,
        alt_plot_path=alt_path,
        rc_plot_path=rc_path
    )
    
    if map_path.exists(): os.remove(map_path)
    if alt_path.exists(): os.remove(alt_path)
    if rc_path.exists(): os.remove(rc_path)
    
    print(f"PDF generation complete.")
    return True