"""
Sanction Letter Generator - Worker Agent
Generates PDF sanction letter for approved loans
Uses reportlab for PDF generation
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

UPLOADS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def generate_sanction_letter(session: dict) -> dict:
    """
    Generate PDF sanction letter for approved loan
    Returns path to generated PDF
    """
    print("[SANCTION GENERATOR] Starting PDF generation...")
    
    customer = session.get("customer", {})
    loan_amount = session.get("approved_amount", session.get("loan_amount", 0))
    loan_tenure = session.get("loan_tenure", 12)
    interest_rate = session.get("interest_rate", 10.5)
    emi = session.get("calculated_emi", 0)
    
    customer_name = customer.get("name", "Customer")
    customer_city = customer.get("city", "")
    customer_phone = customer.get("phone", "")
    customer_id = customer.get("id", "")
    
    os.makedirs(UPLOADS_PATH, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sanction_letter_{customer_id}_{timestamp}.pdf"
    filepath = os.path.join(UPLOADS_PATH, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2d3748')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leading=16
    )
    
    story = []
    
    story.append(Paragraph("CAPITAL FINANCE LTD.", title_style))
    story.append(Paragraph("(A Non-Banking Financial Company)", ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.gray
    )))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("SANCTION LETTER", ParagraphStyle(
        'SanctionTitle', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER,
        textColor=colors.HexColor('#c53030'), spaceAfter=20
    )))
    
    ref_no = f"CFL/PL/{datetime.now().strftime('%Y%m%d')}/{customer_id}"
    story.append(Paragraph(f"<b>Reference No:</b> {ref_no}", body_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"<b>To,</b>", body_style))
    story.append(Paragraph(f"<b>{customer_name}</b>", body_style))
    story.append(Paragraph(f"{customer_city}", body_style))
    story.append(Paragraph(f"Phone: {customer_phone}", body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>Subject: Sanction of Personal Loan</b>", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        f"Dear {customer_name.split()[0]},",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "We are pleased to inform you that your Personal Loan application has been approved. "
        "Please find below the details of your sanctioned loan:",
        body_style
    ))
    story.append(Spacer(1, 15))
    
    total_interest = (emi * loan_tenure) - loan_amount
    total_payable = emi * loan_tenure
    
    loan_data = [
        ["Particulars", "Details"],
        ["Loan Amount", f"₹ {loan_amount:,.0f}"],
        ["Loan Tenure", f"{loan_tenure} months"],
        ["Interest Rate", f"{interest_rate}% per annum"],
        ["Monthly EMI", f"₹ {emi:,.0f}"],
        ["Total Interest Payable", f"₹ {total_interest:,.0f}"],
        ["Total Amount Payable", f"₹ {total_payable:,.0f}"],
        ["Processing Fee", "Nil (Waived)"],
        ["Prepayment Charges", "Nil after 6 EMIs"]
    ]
    
    table = Table(loan_data, colWidths=[3*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>Terms and Conditions:</b>", heading_style))
    terms = [
        "1. This sanction is valid for 30 days from the date of this letter.",
        "2. The loan amount will be disbursed to your registered bank account within 48 hours of document submission.",
        "3. EMI will be auto-debited from your bank account on the 5th of every month.",
        "4. Prepayment is allowed after completion of 6 EMIs without any charges.",
        "5. In case of default, penal interest of 2% per month will be charged on the overdue amount.",
        "6. This sanction is subject to the terms mentioned in the loan agreement."
    ]
    for term in terms:
        story.append(Paragraph(term, body_style))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Please sign and return the enclosed loan agreement along with the required documents to complete the disbursement process.",
        body_style
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Congratulations and thank you for choosing Capital Finance Ltd.!", body_style))
    story.append(Spacer(1, 40))
    
    story.append(Paragraph("<b>For Capital Finance Ltd.</b>", body_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("_______________________", body_style))
    story.append(Paragraph("<b>Authorized Signatory</b>", body_style))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        "<i>This is a system-generated letter and does not require a physical signature.</i>",
        ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))
    
    doc.build(story)
    
    print(f"[SANCTION GENERATOR] PDF generated successfully: {filename}")
    
    session["sanction_letter_path"] = filepath
    session["sanction_letter_filename"] = filename
    
    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "message": (
            f"📄 Your Sanction Letter has been generated!\n\n"
            f"Reference No: {ref_no}\n"
            f"Loan Amount: ₹{loan_amount:,.0f}\n"
            f"Monthly EMI: ₹{emi:,.0f}\n\n"
            f"Click the download button below to get your sanction letter.\n\n"
            f"Thank you for choosing Capital Finance Ltd. We look forward to serving you!"
        ),
        "show_download": True
    }
