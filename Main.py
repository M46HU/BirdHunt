"""
Main entry point for the BirdHunt Forensic Analyzer GUI.
This file starts the application.
"""

# --- START OF SSL FIX ---
# This is the "gold standard" fix for macOS SSL certificate errors.
# It forces Python's SSL module to use the certificate bundle
# provided by the `certifi` package. This must run *before*
# any network requests are made (e.g., by contextily).
import ssl
import certifi

try:
    # Set the default SSL context to use certifi's CA bundle
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except Exception as e:
    print(f"Warning: Could not apply SSL fix: {e}")
# --- END OF SSL FIX ---


# --- THREADING FIX ---
# We must set the Matplotlib backend *before* any other
# module (like plotting or mapping) imports pyplot.
# 'Agg' is a non-interactive backend that is thread-safe
# and renders to a buffer, which is perfect for our GUI.
import matplotlib
matplotlib.use('Agg')
# --- END THREADING FIX ---

import sys
import os

# This adds the root directory to the Python path,
# which allows us to use the 'Analysis' and 'GUI' packages.
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
        # On macOS, Tkinter might have issues if not run correctly.
        # This helps catch any final errors.
        try:
            # Try to show an error popup as a last resort
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")
        except Exception:
            pass # If even this fails, just exit