"""
Main entry point for the BirdHunt Forensic Analyzer GUI.
This file starts the application.
"""

import ssl
import certifi

try:
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except Exception as e:
    print(f"Warning: Could not apply SSL fix: {e}")

import matplotlib
matplotlib.use('Agg')

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from GUI.gui_app import BirdHuntApp
except ImportError as e:
    print("Error: Could not import application modules.")
    print("Please ensure all files are in the correct directories")
    print(f"and all requirements from 'requirements.txt' are installed.")
    print(f"\nImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)


if __name__ == "__main__":
    try:
        app = BirdHuntApp()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start app: {e}")
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")
        except Exception:
            pass