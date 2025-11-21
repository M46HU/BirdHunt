# BirdHunt Forensic Analyzer

BirdHunt is a specialized forensic tool designed for analyzing UAV (Unmanned Aerial Vehicle) flight logs. It processes MAVLink `.tlog` files to reconstruct flight paths, analyze pilot inputs, and generate forensic reports.

## Features

- **Flight Path Reconstruction**: Visualizes the drone's path on a satellite map.
- **Timeline Analysis**: Automatically detects key events like takeoff, landing, and mode changes.
- **Pilot Input Analysis**: Plots RC channel inputs (Roll, Pitch, Throttle, Yaw) to determine pilot intent.
- **Forensic Reporting**: Exports a detailed PDF report with flight data, maps, and charts.
- **Standalone Application**: Can be packaged as a native macOS application.

## Installation

### Prerequisites
- Python 3.10 or higher
- **macOS**: Tested on macOS 15.x
- **Windows**: Windows 10/11
- **Linux**: Ubuntu 20.04+ (or similar)

### Setup

#### macOS / Linux
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BirdHunt
    ```
2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

#### Windows
1.  **Clone the repository:**
    ```cmd
    git clone <repository-url>
    cd BirdHunt
    ```
2.  **Create a virtual environment:**
    ```cmd
    python -m venv venv
    venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```cmd
    pip install -r requirements.txt
    ```

## Running from Source

To run the application directly from the Python source code:

**macOS / Linux:**
```bash
source venv/bin/activate
python Main.py
```

**Windows:**
```cmd
venv\Scripts\activate
python Main.py
```

## Building the Application

You can package the application as a standalone executable for your platform.

### macOS
To create a `.app` bundle:
1.  Ensure `venv` is active.
2.  Run:
    ```bash
    ./build_app.sh
    ```
3.  The application will be in `dist/BirdHunt.app`.

### Windows
To create a `.exe` executable:
1.  Ensure `venv` is active.
2.  Run:
    ```cmd
    build_app.bat
    ```
3.  The executable will be in `dist\BirdHunt\BirdHunt.exe`.

### Linux
To create a binary executable:
1.  Ensure `venv` is active.
2.  Run:
    ```bash
    ./build_app.sh
    ```
3.  The executable will be in `dist/BirdHunt/BirdHunt`.

## Usage

1.  Launch the application.
2.  Click **"Load .tlog File"** and select a MAVLink telemetry log.
3.  The application will process the log and display the **Summary & Timeline**.
4.  Switch tabs to view the **Flight Path**, **Altitude Profile**, and **RC Inputs**.
5.  Click **"Export to PDF"** to generate a forensic report.

## Troubleshooting

-   **Map not loading?** Ensure you have an active internet connection for tile downloading.
-   **SSL Errors?** The application includes a fix for macOS SSL certificate issues. If problems persist, ensure `certifi` is installed.
