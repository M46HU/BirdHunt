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

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

import contextily as cx # <-- Critical Import for the map fix
from . import gui_helpers

class ConsoleRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END) # Auto-scroll
        self.widget.configure(state='disabled')
    
    def flush(self):
        pass

class BirdHuntApp(ThemedTk):

    def __init__(self):
        super().__init__()
        
        self.set_theme("equilux") 
        
        self.title("BirdHunt Forensic Analyzer")
        self.geometry("1100x800")
        
        # --- Data Storage ---
        self.log_file_name = None
        self.log_file_path = None
        self.summary_stats = None
        self.timeline_data = None
        
        self.map_fig = None # Will store the map + basemap
        self.alt_fig = None
        self.rc_fig = None
        
        self.create_widgets()

    def create_widgets(self):
        # --- Top Frame (Header) ---
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill='x')
        
        self.load_button = ttk.Button(header_frame, text="Load .tlog File", command=self.load_log, style="Accent.TButton")
        self.load_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(header_frame, text="Export to PDF", command=self.export_pdf, state='disabled')
        self.export_button.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(header_frame, text="Ready. Please load a .tlog file.")
        self.status_label.pack(side='left', padx=10, fill='x', expand=True)
        
        # --- Main Data Area (Notebook for Tabs) ---
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
            
            # Store all 3 figures (map has no background yet)
            self.map_fig, self.alt_fig, self.rc_fig = gui_helpers.generate_plots(df)
            
            self.after(0, self.update_gui_with_data)
            
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Failed to process log: {e}"))

    def update_gui_with_data(self):
        # --- 1. Update Summary Tab ---
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
            
        # --- 2. Embed Plots ---
        # We use a special function for the map to download the baselayer safely
        self.embed_map_plot(self.map_fig, self.tab_map)
        self.embed_plot(self.alt_fig, self.tab_alt)
        self.embed_plot(self.rc_fig, self.tab_rc)
        
        # --- 3. Finalize ---
        self.export_button.config(state='normal')
        self.load_button.config(state='normal')
        self.status_label.config(text=f"Successfully loaded {self.log_file_name}")
        self.notebook.select(self.tab_summary)

    # --- SPECIAL MAP FUNCTION ---
    def embed_map_plot(self, fig, tab_frame):
        """
        Embeds the map plot and ADDS THE BASEMAP in the main thread.
        This prevents threading/SSL crashes.
        """
        for widget in tab_frame.winfo_children():
            widget.destroy()
            
        if fig is None:
            ttk.Label(tab_frame, text="Map unavailable.").pack(padx=20, pady=20)
            return
        
        try:
            # Download and add basemap HERE (in main thread)
            print("Adding map baselayer (this may take a moment)...")
            ax = fig.axes[0]
            cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery)
            cx.add_basemap(ax, source=cx.providers.CartoDB.PositronOnlyLabels, zoom=15)
            print("Baselayer added.")
            
            # Update self.map_fig so the export function uses the one with the background
            self.map_fig = fig 
            
            canvas = FigureCanvasTkAgg(fig, master=tab_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas, tab_frame)
            toolbar.update()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        except Exception as e:
            print(f"Failed to add basemap: {e}")
            ttk.Label(tab_frame, text=f"Map loaded without background (Error: {e})").pack(padx=20, pady=20)
            
            # Still show the red line path even if map tiles fail
            canvas = FigureCanvasTkAgg(fig, master=tab_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

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
            # Pass self.map_fig (which now has the basemap)
            gui_helpers.generate_pdf_export(
                output_pdf_path=save_path,
                log_file_name=self.log_file_name,
                summary_stats=self.summary_stats,
                timeline_data=self.timeline_data,
                map_fig=self.map_fig, 
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