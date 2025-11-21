"""
BirdHunt Forensic Analyzer GUI
This file contains the main Tkinter application class (the "View").
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from pathlib import Path
import threading
import sys
import os
import pandas as pd
from PIL import Image, ImageTk, ImageDraw


from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

import contextily as cx 
import tkintermapview
from . import gui_helpers

class ConsoleRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')
    
    def flush(self):
        pass

class BirdHuntApp(ThemedTk):

    def __init__(self):
        super().__init__()
        
        self.set_theme("equilux") 
        
        self.title("BirdHunt Forensic Analyzer")
        
        try:
            self.state('zoomed')
        except:
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")
        
        self.log_file_name = None
        self.log_file_path = None
        self.summary_stats = None
        self.timeline_data = None
        
        self.map_fig = None
        self.map_widget = None
        self.drone_marker = None
        self.path_line = None
        self.alt_fig = None
        self.rc_fig = None
        
        self.create_widgets()

    def create_widgets(self):
        branding_frame = ttk.Frame(self, padding=5)
        branding_frame.pack(fill='x', side='top')
        
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open("logo.png")
            logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            ttk.Label(branding_frame, image=self.logo_photo).pack(side='left', padx=10)
        except Exception as e:
            print(f"Logo load error: {e}")
            ttk.Label(branding_frame, text="[LOGO]").pack(side='left', padx=10)
            
        ttk.Label(branding_frame, text="BirdHunt Forensics", font=("Arial", 16, "bold")).pack(side='left')
        
        footer_frame = ttk.Frame(self, padding=5)
        footer_frame.pack(fill='x', side='bottom')
        ttk.Label(footer_frame, text="BirdHunt Forensics | Contact: support@birdhunt.com | Confidential Report", 
                  font=("Arial", 8), foreground="gray").pack(side='bottom')

        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill='x')
        
        self.load_button = ttk.Button(header_frame, text="Load .tlog File", command=self.load_log, style="Accent.TButton")
        self.load_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(header_frame, text="Export to PDF", command=self.export_pdf, state='disabled')
        self.export_button.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(header_frame, text="Ready. Please load a .tlog file.")
        self.status_label.pack(side='left', padx=10, fill='x', expand=True)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tab_summary = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_summary, text='Summary & Timeline')
        self.create_summary_tab()
        
        self.tab_map = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_map, text='Flight Path')
        
        self.tab_alt = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_alt, text='Altitude')
        
        self.tab_rc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rc, text='RC Inputs')

        self.tab_console = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_console, text='Console')
        self.create_console_tab()

    def create_summary_tab(self):
        stats_frame = ttk.Labelframe(self.tab_summary, text="Summary", padding=10)
        stats_frame.pack(fill='x', pady=5)
        
        self.summary_text = tk.StringVar(value="File: N/A\nDuration: N/A")
        ttk.Label(stats_frame, textvariable=self.summary_text, font=("Arial", 12)).pack(anchor='w')
        
        timeline_frame = ttk.Labelframe(self.tab_summary, text="Timeline", padding=10)
        timeline_frame.pack(fill='both', expand=True, pady=5)
        
        cols = ('Real Time (UTC)', 'Log Time', 'Event')
        self.timeline_tree = ttk.Treeview(timeline_frame, columns=cols, show='headings')
        
        for col in cols:
            self.timeline_tree.heading(col, text=col)
            self.timeline_tree.column(col, width=150)
            
        self.timeline_tree.pack(fill='both', expand=True)

    def create_console_tab(self):
        console_text = tk.Text(self.tab_console, wrap='word', height=10, state='disabled')
        console_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        sys.stdout = ConsoleRedirector(console_text)
        sys.stderr = ConsoleRedirector(console_text)
        print("Application ready. Console initialized.")

    def load_log(self):
        file_path = filedialog.askopenfilename(
            title="Select .tlog file",
            filetypes=[("MAVLink Logs", "*.tlog"), ("All Files", "*.*")],
            initialdir="Logs/"
        )
        if not file_path:
            return
            
        self.log_file_name = Path(file_path).name
        self.log_file_path = file_path
        self.status_label.config(text=f"Processing {self.log_file_name}...")
        
        self.load_button.config(state='disabled')
        self.export_button.config(state='disabled')
        
        self.notebook.select(self.tab_console)
        
        threading.Thread(target=self.run_processing_thread, args=(file_path,), daemon=True).start()

    def run_processing_thread(self, file_path):
        try:
            df, self.summary_stats, self.timeline_data = gui_helpers.process_log_file(file_path)
            self.df = df
            
            self.alt_fig, self.rc_fig = gui_helpers.generate_plots(df)
            
            self.after(0, self.update_gui_with_data)
            
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Failed to process log: {e}"))

    def update_gui_with_data(self):
        self.summary_text.set(
            f"File: {self.log_file_name}\n"
            f"Duration: {self.summary_stats.get('duration_sec', 0):.2f} seconds"
        )
        
        for i in self.timeline_tree.get_children():
            self.timeline_tree.delete(i)
        
        for row in self.timeline_data:
            self.timeline_tree.insert("", "end", values=(
                row['Real Time (UTC)'],
                f"T+{float(row['Time (s)']):.1f}s",
                row['Event']
            ))
            
        self.embed_map_plot(self.tab_map)
        self.embed_plot(self.alt_fig, self.tab_alt)
        self.embed_plot(self.rc_fig, self.tab_rc)
        
        self.export_button.config(state='normal')
        self.load_button.config(state='normal')
        self.status_label.config(text=f"Successfully loaded {self.log_file_name}")
        self.notebook.select(self.tab_summary)

    def embed_map_plot(self, tab_frame):
        """
        Embeds the LIVE MAP using tkintermapview.
        """
        for widget in tab_frame.winfo_children():
            widget.destroy()
            
        self.map_widget = tkintermapview.TkinterMapView(tab_frame, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        
        if not hasattr(self, 'df') or self.df is None:
            return

        path_coords = []
        lats = self.df['GLOBAL_POSITION_INT.lat'] / 1e7
        lons = self.df['GLOBAL_POSITION_INT.lon'] / 1e7
        
        self.all_path_coords = [] 
        for lat, lon in zip(lats, lons):
            if pd.notna(lat) and pd.notna(lon) and lat != 0 and lon != 0:
                self.all_path_coords.append((lat, lon))
        
        if self.all_path_coords:
            self.map_widget.set_path(self.all_path_coords, color="red", width=2)
            
            start_lat, start_lon = self.all_path_coords[0]
            self.map_widget.set_marker(start_lat, start_lon, text="Start")
            
            end_lat, end_lon = self.all_path_coords[-1]
            self.map_widget.set_marker(end_lat, end_lon, text="End")
            
            min_lat = min(p[0] for p in self.all_path_coords)
            max_lat = max(p[0] for p in self.all_path_coords)
            min_lon = min(p[1] for p in self.all_path_coords)
            max_lon = max(p[1] for p in self.all_path_coords)
            
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2
            self.map_widget.set_position(center_lat, center_lon)
            self.map_widget.set_zoom(18)

    def embed_plot(self, fig, tab_frame):
        """Embeds a standard Matplotlib Figure object into a Tkinter tab."""
        for widget in tab_frame.winfo_children():
            widget.destroy()
            
        if fig is None:
            ttk.Label(tab_frame, text="Plot unavailable.").pack(padx=20, pady=20)
            return
            
        canvas = FigureCanvasTkAgg(fig, master=tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, tab_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

    def export_pdf(self):
        save_path = filedialog.asksaveasfilename(
            title="Save PDF Report",
            defaultextension=".pdf",
            initialfile=self.log_file_name.replace(".tlog", ".forensic.pdf"),
            filetypes=[("PDF Documents", "*.pdf")],
            initialdir="Exports/"
        )
        if not save_path:
            return
            
        self.status_label.config(text=f"Exporting PDF to {save_path}...")
        self.notebook.select(self.tab_console)
        
        threading.Thread(target=self.run_export_thread, args=(save_path,), daemon=True).start()

    def run_export_thread(self, save_path):
        try:
            gui_helpers.generate_pdf_export(
                output_pdf_path=save_path,
                log_file_name=self.log_file_name,
                summary_stats=self.summary_stats,
                timeline_data=self.timeline_data,
                df=self.df, 
                alt_fig=self.alt_fig,
                rc_fig=self.rc_fig
            )
            self.after(0, lambda: self.status_label.config(text="PDF Exported Successfully."))
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Failed to export PDF: {e}"))

    def show_error(self, message):
        print(f"ERROR: {message}")
        self.status_label.config(text="An error occurred. Check console tab.")
        self.load_button.config(state='normal')
        messagebox.showerror("Error", str(message))