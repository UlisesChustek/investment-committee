# src/pdf_generator.py
from fpdf import FPDF
import re
import os

class InvestmentReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set bottom margin to 35mm to reserve space for the footer
        self.set_auto_page_break(auto=True, margin=35)

    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Investment Committee', 0, 1, 'L')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Automated Equity Research Report', 0, 1, 'L')
        self.line(10, 28, 200, 28)
        self.ln(12)

    def footer(self):
        # Position footer at 30mm from bottom
        self.set_y(-30) 
        self.set_font('Arial', 'I', 7)
        self.set_text_color(100, 100, 100) # Subtle gray color
        disclaimer = "LEGAL DISCLAIMER: This report is an AI-generated informative tool. It does not constitute financial advice, " \
                     "investment recommendations, or legal solicitation. The user assumes all responsibility for investment decisions."
        self.multi_cell(0, 4, disclaimer, 0, 'C')
        self.ln(2)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240) 
        self.cell(0, 10, title.upper(), 0, 1, 'L', 1)
        self.ln(3)

    def add_section_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        clean_text = body.replace('**', '').replace('* ', '- ').strip()
        self.multi_cell(0, 7, clean_text)
        self.ln(5)

# src/pdf_generator.py

def create_pdf(ticker, report_text, save_path, chart_path=None):
    pdf = InvestmentReportPDF()
    pdf.add_page()
    
    # Title Header
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, f'EQUITY RESEARCH: {ticker}', 0, 1, 'C')
    pdf.ln(5)

    segments = re.split(r'###\s+', report_text)
    
    for segment in segments:
        if not segment.strip(): continue
        lines = segment.split('\n', 1)
        if len(lines) > 1:
            title = lines[0].strip()
            body = lines[1].strip()
            
            pdf.add_section_title(title)
            pdf.add_section_body(body)
            
            # --- INSERT CHART HERE ---
            # If we just finished the Quantitative Data section, add the image
            if "Quantitative Data" in title and chart_path and os.path.exists(chart_path):
                # pdf.image(name, x, y, width)
                pdf.image(chart_path, x=15, w=180) 
                pdf.ln(5)
        else:
            pdf.add_section_body(segment)

    pdf.output(save_path)
    return save_path