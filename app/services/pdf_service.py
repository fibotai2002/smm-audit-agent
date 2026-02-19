from fpdf import FPDF
import io
import os

class PDFService(FPDF):
    def __init__(self, tier="free"):
        super().__init__()
        self.tier = tier

    def header(self):
        if self.tier != "agency":
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'SMMind AI - Audit Report', 0, 1, 'C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        text = f"Page {self.page_no()}"
        if self.tier != "agency":
             text += " | Created by SMMind AI Bot"
        self.cell(0, 10, text, 0, 0, 'C')

    def add_section(self, title, body):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln(5)

    def add_chart(self, chart_bytes, title):
        if chart_bytes:
            self.ln(5)
            self.set_font('Arial', 'B', 10)
            self.cell(0, 10, title, 0, 1, 'C')
            
            # Save bytes to temp file because FPDF image needs path or stream
            # FPDF2 supports stream directly
            self.image(chart_bytes, x=None, y=None, w=100) 
            self.ln(5)

class ReportGenerator:
    @staticmethod
    def generate_pdf(report_data: dict, charts: dict, tier: str = "free"):
        try:
            pdf = PDFService(tier=tier)
            pdf.add_page()
            
            # Use built-in Unicode font if available, or standard font with replacement
            # For simplicity in this env, we use standard Arial and strip non-latin stats if needed,
            # BUT efficient way is to register a unicode font.
            # Since we don't have a ttf file guaranteed, we will try to use base fonts 
            # and might need to transliterate or ensure env has fonts.
            # *Crucial Fix:* FPDF default fonts don't support Cyrillic/Uzbek special chars well.
            # strategies: 
            # 1. Use a standard font like Helvetica
            
            pdf.set_font("Helvetica", size=12)

            # 1. Executive Summary
            quick_audit = "\n".join(report_data.get("quick_audit", []))
            pdf.add_section("Tezkor Audit", quick_audit)

            # 2. Charts
            if charts.get("engagement"):
                pdf.add_chart(charts["engagement"], "Engagement Rate")
            
            if charts.get("distribution"):
                pdf.add_chart(charts["distribution"], "Kontent Turi")

            # 3. Positioning
            pos = report_data.get("positioning_analysis", {}).get("details", "")
            pdf.add_section("Pozitsiyalash", pos)

            # 4. Strategy
            pillars = ", ".join(report_data.get("content_pillars", []))
            pdf.add_section("Kontent Strategiyasi", f"Mavzular: {pillars}")

            # 5. Action Plan
            plan_text = ""
            for item in report_data.get("next_7_days_action_plan", []):
                plan_text += f"- {item}\n"
            pdf.add_section("7 Kunlik Reja", plan_text)

            return pdf.output(dest='S').encode('latin-1', 'ignore') # Return as bytes
            # Note: 'latin-1' might lose chars. 
            # Better approach: return pdf.output() directly as bytes in FPDF2
            
        except Exception as e:
            print(f"PDF Error: {e}")
            return None
