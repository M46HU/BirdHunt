"""
Handles all geospatial plotting using GeoPandas.
MODIFIED to only plot the path (no basemap).
The basemap will be added by the GUI in the main thread.
"""

import geopandas
import contextily as cx
from matplotlib.figure import Figure # <-- MODIFIED
import matplotlib.patheffects as pe
import tempfile
import os

def create_flight_path_map(df):
    print("Generating flight path (lines only)...")
    gps_df = df.dropna(subset=['GLOBAL_POSITION_INT.lat', 'GLOBAL_POSITION_INT.lon']).copy()
    
    if gps_df.empty:
        print("Warning: No GPS data found.")
        return None

    gps_df['lat'] = gps_df['GLOBAL_POSITION_INT.lat'] / 1e7
    gps_df['lon'] = gps_df['GLOBAL_POSITION_INT.lon'] / 1e7
    
    try:
        gdf = geopandas.GeoDataFrame(
            gps_df, geometry=geopandas.points_from_xy(gps_df.lon, gps_df.lat), crs='EPSG:4326'
        )
        gdf_wm = gdf.to_crs(epsg=3857) 

        # --- Create figure in a thread-safe way ---
        fig = Figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1)
        
        # Plot Path
        gdf_wm.plot(ax=ax, color='red', linewidth=3, alpha=0.7, zorder=2)
        
        # Start Point & Label
        start = gdf_wm.geometry.iloc[0]
        ax.scatter(start.x, start.y, color='#2ecc71', edgecolors='black', s=150, zorder=5)
        ax.text(start.x, start.y, " START", fontsize=12, fontweight='bold', color='white', 
                path_effects=[pe.withStroke(linewidth=3, foreground="black")], zorder=6)

        # End Point & Label
        end = gdf_wm.geometry.iloc[-1]
        ax.scatter(end.x, end.y, color='#3498db', edgecolors='black', marker='X', s=150, zorder=5)
        ax.text(end.x, end.y, " END", fontsize=12, fontweight='bold', color='white', 
                path_effects=[pe.withStroke(linewidth=3, foreground="black")], zorder=6)
        
        # --- REMOVED CONTEXTILY ---
        # The main GUI thread will handle the basemap.
        
        ax.set_axis_off()
        ax.set_title('Flight Path Reconstruction', fontsize=14)
        
        print("Path plot generated.")
        return fig # Return the Figure object

    except Exception as e:
         print(f"Map Error: {e}")
         return None