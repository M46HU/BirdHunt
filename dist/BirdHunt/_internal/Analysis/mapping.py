"""
Handles all geospatial plotting using GeoPandas.
MODIFIED to only plot the path (no basemap).
The basemap will be added by the GUI in the main thread.
"""

import geopandas
import contextily as cx
from matplotlib.figure import Figure
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

        fig = Figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1)
        
        gdf_wm.plot(ax=ax, color='red', linewidth=3, alpha=0.7, zorder=2)
        
        minx, miny, maxx, maxy = gdf_wm.total_bounds
        x_buf = (maxx - minx) * 0.5
        y_buf = (maxy - miny) * 0.5
        ax.set_xlim(minx - x_buf, maxx + x_buf)
        ax.set_ylim(miny - y_buf, maxy + y_buf)
        
        start = gdf_wm.geometry.iloc[0]
        ax.scatter(start.x, start.y, color='#2ecc71', edgecolors='black', s=150, zorder=5)
        ax.text(start.x, start.y, " START", fontsize=12, fontweight='bold', color='white', 
                path_effects=[pe.withStroke(linewidth=3, foreground="black")], zorder=6)

        end = gdf_wm.geometry.iloc[-1]
        ax.scatter(end.x, end.y, color='#3498db', edgecolors='black', marker='X', s=150, zorder=5)
        ax.text(end.x, end.y, " END", fontsize=12, fontweight='bold', color='white', 
                path_effects=[pe.withStroke(linewidth=3, foreground="black")], zorder=6)
        
        ax.set_axis_off()
        ax.set_title('Flight Path Reconstruction', fontsize=14)
        
        print("Path plot generated.")
        return fig

    except Exception as e:
         print(f"Map Error: {e}")
         return None

def add_basemap(fig):
    """
    Adds the basemap to an existing figure. 
    Useful for PDF export where we need the background.
    """
    try:
        if fig is None or not fig.axes:
            return
        ax = fig.axes[0]
        cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
        print("Basemap added to figure for export.")
    except Exception as e:
        print(f"Failed to add basemap: {e}")