"""
Handles the assembly of the final PDF report.
This file is UNCHANGED from your original.
"""

from fpdf import FPDF
from pathlib import Path

class PDFReport(FPDF):
    def header(self):
        logo_path = Path("logo.png")
        if logo_path.exists():
            self.image(str(logo_path), 10, 8, 15)
            self.set_font('Arial', 'B', 16)
            self.cell(20)
            self.cell(0, 10, 'BirdHunt Forensics', 0, 1, 'L')
            self.ln(5)
        else:
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'BirdHunt Forensics', 0, 1, 'C') 
            self.ln(5)
            
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'UAV Forensic Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'BirdHunt Forensics | Contact: support@birdhunt.com | Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_forensic_report(output_pdf_path, log_file_name, summary_stats, timeline_data,
                             map_image_path, alt_plot_path, rc_plot_path):
    
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 25, 190, 25, 'F')
    pdf.set_y(28)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(20, 8, 'File:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, log_file_name, 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(25, 8, 'Duration:', 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"{summary_stats.get('duration_sec', 0):.2f} seconds", 0, 1)
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Flight Timeline', 'B', 1, 'L')
    pdf.ln(2)
    
    if timeline_data:
        pdf.set_fill_color(50, 50, 100)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        
        pdf.cell(40, 8, "Time (UTC)", 1, 0, 'C', True)
        pdf.cell(30, 8, "Log Time", 1, 0, 'C', True)
        pdf.cell(0, 8, "Event Description", 1, 1, 'L', True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        
        fill = False
        for row in timeline_data:
            if fill:
                pdf.set_fill_color(235, 235, 235)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(40, 7, str(row['Real Time (UTC)']), 1, 0, 'C', fill)
            pdf.cell(30, 7, f"T+{float(row['Time (s)']):.1f}s", 1, 0, 'C', fill)
            pdf.cell(0, 7, f"  {row['Event']}", 1, 1, 'L', fill)
            
            fill = not fill
            
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, 'No critical events found.', 0, 1)
    
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Flight Path Map', 'B', 1, 'L')
    pdf.ln(2)
    if map_image_path and Path(map_image_path).is_file():
        pdf.image(str(map_image_path), h=110, x=35)
    else:
        pdf.cell(0, 10, 'Map unavailable.', 0, 1)
    
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Altitude Profile', 'B', 1, 'L')
    pdf.ln(2)
    if alt_plot_path and Path(alt_plot_path).is_file():
        pdf.image(str(alt_plot_path), w=180, x=15)
    else:
        pdf.cell(0, 10, 'Altitude plot unavailable.', 0, 1)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. Pilot Control Inputs', 'B', 1, 'L')
    pdf.ln(2)
    if rc_plot_path and Path(rc_plot_path).is_file():
        pdf.image(str(rc_plot_path), w=180, x=15)
    else:
        pdf.cell(0, 10, 'RC data unavailable.', 0, 1)

    try:
        pdf.output(output_pdf_path)
        print(f"\nSuccess: Report saved to {output_pdf_path}")
    except Exception as e:
        print(f"Report Error: {e}")