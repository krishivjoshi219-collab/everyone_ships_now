import io
import html
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReportEngine:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Premium Corporate Typography (No Emojis to prevent font crashes)
        self.title_style = ParagraphStyle(
            'DocTitle', parent=self.styles['Heading1'], fontName='Helvetica-Bold', 
            fontSize=22, textColor=colors.HexColor('#1e1b4b'), spaceAfter=14
        )
        self.section_style = ParagraphStyle(
            'SectionHeading', parent=self.styles['Heading2'], fontName='Helvetica-Bold', 
            fontSize=14, textColor=colors.HexColor('#1e3a8a'), spaceBefore=16, spaceAfter=8
        )
        self.body_style = ParagraphStyle(
            'BodyTextCustom', parent=self.styles['Normal'], fontName='Helvetica', 
            fontSize=11, textColor=colors.HexColor('#334155'), leading=16, spaceAfter=10
        )
        self.code_style = ParagraphStyle(
            'CodeTextCustom', parent=self.styles['Normal'], fontName='Courier', 
            fontSize=10, textColor=colors.HexColor('#0f172a'), backColor=colors.HexColor('#f8fafc'), 
            borderColor=colors.HexColor('#e2e8f0'), borderWidth=1, borderPadding=10, 
            spaceBefore=8, spaceAfter=12
        )

    def _sanitize(self, raw_text: str) -> str:
        """
        Critical Safeguard: Converts dangerous < and > characters into HTML-safe entities 
        so ReportLab's Paragraph parser doesn't crash on code snippets like <module>.
        """
        if not raw_text:
            return ""
        return html.escape(str(raw_text)).replace('\n', '<br/>')

    def generate_executive_report(self, payload: dict) -> bytes:
        """
        Transforms the unified analysis payload into a premium 3-page PDF buffer.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        # ==========================================
        # 📄 PAGE 1: EXECUTIVE SUMMARY & AI INSIGHT
        # ==========================================
        story.append(Paragraph("[DIAGNOSTIC] DEPENDENCE DOC", self.title_style))
        story.append(Paragraph("<b>AUTOMATED SYSTEM DIAGNOSTIC REPORT</b>", self.section_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(f"<b>Analysis Core ID:</b> {self._sanitize(payload.get('analysis_id', 'UNKNOWN'))}", self.body_style))
        story.append(Paragraph(f"<b>Verification Integrity Match:</b> {payload.get('metrics', {}).get('confidence_percentage', 0)}%", self.body_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph("1. Primary Incident Analysis", self.section_style))
        
        # Truncate BEFORE sanitizing to prevent splitting HTML entities
        raw_explanation = payload.get('ai_insights', {}).get('explanation', 'No explanation available.')
        if len(raw_explanation) > 3500:
            raw_explanation = raw_explanation[:3500] + "... [Content truncated for Executive Summary length limits]."
        safe_explanation = self._sanitize(raw_explanation)
        story.append(Paragraph(safe_explanation, self.body_style))
        
        # High-End Metric Table
        story.append(Spacer(1, 20))
        metric_data = [
            ["Detected Domains", "Engineered Fixes", "Analysis Protocol"],
            [str(len(payload.get('detected_domains', []))), str(len(payload.get('recovery_order_stack', []))), "Heuristics Matrix"]
        ]
        t = Table(metric_data, colWidths=[150, 150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#f8fafc')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ]))
        story.append(t)
        
        story.append(PageBreak())

        # ==========================================
        # 📄 PAGE 2: PREDICTIVE PRE-THINKING MATRIX
        # ==========================================
        story.append(Paragraph("2. Predictive Pre-Thinking & Risk Matrix", self.section_style))
        story.append(Paragraph("<i>Automated evaluation of secondary execution vectors, downstream package compatibility, and runtime hazard simulations.</i>", self.body_style))
        story.append(Spacer(1, 15))
        
        # Truncate BEFORE sanitizing
        raw_pre_thinking = payload.get('ai_insights', {}).get('pre_thinking', 'Simulation logs unavailable.')
        if len(raw_pre_thinking) > 3500:
            raw_pre_thinking = raw_pre_thinking[:3500] + "... [Content truncated for Executive Summary length limits]."
        safe_pre_thinking = self._sanitize(raw_pre_thinking)
        story.append(Paragraph(safe_pre_thinking, self.body_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("<b>Verified System Guardrails:</b>", self.section_style))
        for check in payload.get("metrics", {}).get("verification_checklist", []):
            story.append(Paragraph(f"• {self._sanitize(check)}", self.body_style))

        story.append(PageBreak())

        # ==========================================
        # 📄 PAGE 3: ORDERED RECOVERY EXECUTION STACK
        # ==========================================
        story.append(Paragraph("3. Target Remediation Command Stack", self.section_style))
        story.append(Paragraph("Execute the following deterministic terminal patches sequentially to restore the local execution environment.", self.body_style))
        story.append(Spacer(1, 15))

        recovery_stack = payload.get("recovery_order_stack", [])
        if not recovery_stack:
            story.append(Paragraph("System Analysis Status Clean: No environmental path gaps isolated.", self.body_style))
        else:
            for step in recovery_stack:
                story.append(Paragraph(f"<b>Vector Step {step.get('step')}: {self._sanitize(step.get('target'))}</b>", self.body_style))
                story.append(Paragraph(f"<i>Reason: {self._sanitize(step.get('explanation'))}</i>", self.body_style))
                story.append(Paragraph(self._sanitize(step.get('command', '')), self.code_style))
                story.append(Spacer(1, 10))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
