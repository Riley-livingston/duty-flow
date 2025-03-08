from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import json
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_cbp_form_7551(data, output_path="cbp_form_7551.pdf"):
    """
    Generate a filled CBP Form 7551 (Drawback Entry)
    
    Parameters:
    - data: Dictionary containing form data
    - output_path: Path to save the generated PDF
    
    Returns:
    - Path to the generated PDF
    """
    # Create a canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Add form title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 1*inch, "U.S. Customs and Border Protection")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 1.3*inch, "DRAWBACK ENTRY - Form 7551")
    
    # Add form fields
    c.setFont("Helvetica", 10)
    
    # Section 1: Claimant Information
    y_pos = height - 2*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_pos, "1. CLAIMANT INFORMATION")
    c.setFont("Helvetica", 10)
    
    y_pos -= 0.3*inch
    c.drawString(1*inch, y_pos, "Claimant Name:")
    c.drawString(2.5*inch, y_pos, data.get("claimant_name", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Claimant Address:")
    c.drawString(2.5*inch, y_pos, data.get("claimant_address", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Claimant ID Number:")
    c.drawString(2.5*inch, y_pos, data.get("claimant_id", ""))
    
    # Section 2: Entry Information
    y_pos -= 0.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_pos, "2. ENTRY INFORMATION")
    c.setFont("Helvetica", 10)
    
    y_pos -= 0.3*inch
    c.drawString(1*inch, y_pos, "Port Code:")
    c.drawString(2.5*inch, y_pos, data.get("port_code", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Entry Number:")
    c.drawString(2.5*inch, y_pos, data.get("entry_number", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Entry Date:")
    c.drawString(2.5*inch, y_pos, data.get("entry_date", ""))
    
    # Section 3: Drawback Information
    y_pos -= 0.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_pos, "3. DRAWBACK INFORMATION")
    c.setFont("Helvetica", 10)
    
    y_pos -= 0.3*inch
    c.drawString(1*inch, y_pos, "Drawback Provision:")
    c.drawString(2.5*inch, y_pos, data.get("drawback_provision", "1313(j)(1)"))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Total Drawback Claim:")
    c.drawString(2.5*inch, y_pos, f"${data.get('total_claim', '0.00')}")
    
    # Section 4: Merchandise Information
    y_pos -= 0.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_pos, "4. MERCHANDISE INFORMATION")
    c.setFont("Helvetica", 10)
    
    # Table headers
    y_pos -= 0.3*inch
    col1 = 1*inch
    col2 = 2.5*inch
    col3 = 4*inch
    col4 = 5.5*inch
    col5 = 7*inch
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(col1, y_pos, "Product ID")
    c.drawString(col2, y_pos, "Description")
    c.drawString(col3, y_pos, "Import Date")
    c.drawString(col4, y_pos, "Export Date")
    c.drawString(col5, y_pos, "Refund Amount")
    
    # Table data
    c.setFont("Helvetica", 8)
    
    merchandise = data.get("merchandise", [])
    for item in merchandise:
        y_pos -= 0.2*inch
        c.drawString(col1, y_pos, item.get("product_id", ""))
        c.drawString(col2, y_pos, item.get("description", ""))
        c.drawString(col3, y_pos, item.get("import_date", ""))
        c.drawString(col4, y_pos, item.get("export_date", ""))
        c.drawString(col5, y_pos, f"${item.get('refund_amount', '0.00')}")
    
    # Section 5: Certification
    y_pos -= 0.5*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_pos, "5. CERTIFICATION")
    c.setFont("Helvetica", 10)
    
    y_pos -= 0.3*inch
    certification_text = "I declare that the information contained in this document is true and correct to the best of my knowledge and belief."
    c.drawString(1*inch, y_pos, certification_text)
    
    y_pos -= 0.5*inch
    c.drawString(1*inch, y_pos, "Signature: _______________________________")
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Name: " + data.get("signatory_name", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Title: " + data.get("signatory_title", ""))
    
    y_pos -= 0.25*inch
    c.drawString(1*inch, y_pos, "Date: " + data.get("signature_date", datetime.now().strftime("%Y-%m-%d")))
    
    # Add form number and date at bottom
    c.setFont("Helvetica", 8)
    c.drawString(1*inch, 0.5*inch, "CBP Form 7551 (Simulated for DutyFlow MVP)")
    c.drawString(width - 2*inch, 0.5*inch, "Page 1 of 1")
    
    # Save the PDF
    c.save()
    return output_path

def generate_form_from_eligible_transactions(results_file, company_info=None):
    """
    Generate a CBP Form 7551-like PDF report for eligible duty drawback transactions.
    Simplified for small and medium-sized businesses.
    
    Parameters:
    - results_file: Path to the CSV file with analyzed transactions
    - company_info: Dictionary with company information
    
    Returns:
    - Path to the generated PDF file
    """
    # Default company info if not provided
    if company_info is None:
        company_info = {
            'name': 'Your Company Name',
            'address': '123 Business St, Suite 100',
            'city_state_zip': 'Anytown, ST 12345',
            'contact_name': 'Contact Person',
            'phone': '(555) 555-5555',
            'email': 'contact@yourcompany.com',
            'importer_number': 'IMPxxxxxxxx'
        }
    
    # Load the transactions data
    transactions_df = pd.read_csv(results_file)
    
    # Filter for eligible transactions only
    eligible_df = transactions_df[transactions_df['is_eligible'] == True]
    
    if len(eligible_df) == 0:
        raise ValueError("No eligible transactions found for drawback claim")
    
    # Create output directory if it doesn't exist
    output_dir = 'reports'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'drawback_claim_{timestamp}.pdf')
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Create a custom style for the company header
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        alignment=1  # Center alignment
    )
    
    # Create a custom style for section headers
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading3'],
        fontSize=12,
        leading=14,
        spaceBefore=10,
        spaceAfter=6
    )
    
    # Create content elements
    elements = []
    
    # Add title
    elements.append(Paragraph("Duty Drawback Claim Report", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add company information
    elements.append(Paragraph(f"<b>{company_info['name']}</b>", company_style))
    elements.append(Paragraph(company_info['address'], company_style))
    elements.append(Paragraph(company_info['city_state_zip'], company_style))
    elements.append(Paragraph(f"Contact: {company_info['contact_name']}", company_style))
    elements.append(Paragraph(f"Phone: {company_info['phone']} | Email: {company_info['email']}", company_style))
    elements.append(Paragraph(f"Importer of Record #: {company_info['importer_number']}", company_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add report summary
    elements.append(Paragraph("Claim Summary", subtitle_style))
    
    # Summary data
    total_entries = eligible_df['entry_number'].nunique()
    total_duty_paid = eligible_df['duty_paid'].sum()
    total_potential_refund = eligible_df['potential_refund'].sum()

    # Convert string dates to datetime objects if they aren't already
    if isinstance(eligible_df['import_date'].iloc[0], str):
        min_date = pd.to_datetime(eligible_df['import_date'].min()).strftime('%m/%d/%Y')
        max_date = pd.to_datetime(eligible_df['import_date'].max()).strftime('%m/%d/%Y')
    else:
        min_date = eligible_df['import_date'].min().strftime('%m/%d/%Y')
        max_date = eligible_df['import_date'].max().strftime('%m/%d/%Y')

    date_range = f"{min_date} to {max_date}"
    
    summary_data = [
        ["Total Eligible Entries:", f"{total_entries}"],
        ["Date Range:", date_range],
        ["Total Duty Paid:", f"${total_duty_paid:,.2f}"],
        ["Potential Refund (99%):", f"${total_potential_refund:,.2f}"]
    ]
    
    # Create summary table
    summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add SMB-friendly guidance
    elements.append(Paragraph("Small Business Filing Guide", section_style))
    
    guidance_text = """
    <b>Next Steps for Your Drawback Claim:</b>
    
    1. <b>Verify your documentation:</b> Ensure you have all import documentation (CBP Form 7501, commercial invoices) for the entries listed in this report.
    
    2. <b>Prepare export evidence:</b> If you've exported these goods, gather proof of exportation (bills of lading, export invoices).
    
    3. <b>Consider a drawback specialist:</b> For first-time filers, consulting with a drawback specialist can help maximize your refund.
    
    4. <b>File electronically:</b> Submit your claim through ACE (Automated Commercial Environment) or work with a customs broker.
    
    5. <b>Maintain records:</b> Keep all documentation for at least 3 years after the date of payment.
    
    <i>Note: This report is a preliminary analysis. Actual refund amounts may vary based on CBP review.</i>
    """
    
    elements.append(Paragraph(guidance_text, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add eligible transactions
    elements.append(Paragraph("Eligible Transactions", subtitle_style))
    
    # Prepare transaction data for table
    transaction_data = [["Entry Number", "Import Date", "Product ID", "Duty Paid", "Potential Refund"]]
    
    # Group by entry number to consolidate entries
    entry_groups = eligible_df.groupby('entry_number').agg({
        'import_date': 'min',
        'product_id': lambda x: ', '.join(x.unique()[:3]) + ('...' if len(x.unique()) > 3 else ''),
        'duty_paid': 'sum',
        'potential_refund': 'sum'
    }).reset_index()
    
    for _, row in entry_groups.iterrows():
        # Convert import_date to datetime if it's a string
        if isinstance(row['import_date'], str):
            formatted_date = pd.to_datetime(row['import_date']).strftime('%m/%d/%Y')
        else:
            formatted_date = row['import_date'].strftime('%m/%d/%Y')
        
        transaction_data.append([
            row['entry_number'],
            formatted_date,
            row['product_id'],
            f"${row['duty_paid']:,.2f}",
            f"${row['potential_refund']:,.2f}"
        ])
    
    # Create transactions table
    transaction_table = Table(transaction_data, colWidths=[1*inch, 1*inch, 2.5*inch, 1*inch, 1*inch])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(transaction_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add disclaimer for SMBs
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.darkgrey
    )
    
    disclaimer_text = """
    This report is generated by DutyFlow and is intended as a preliminary analysis tool for small and medium-sized businesses. 
    It does not constitute legal or financial advice. Duty drawback regulations are complex and subject to change. 
    We recommend consulting with a licensed customs broker or trade attorney before filing a drawback claim.
    """
    
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build the PDF
    doc.build(elements)
    
    return output_file

def generate_sample_form():
    """Generate a sample form with mock data for demonstration"""
    
    # Sample data
    sample_data = {
        "claimant_name": "DutyFlow Demo Company",
        "claimant_address": "100 Trade Avenue, Suite 200, Seattle, WA 98101",
        "claimant_id": "EIN-98-7654321",
        "port_code": "3001",
        "entry_number": "E54321",
        "entry_date": "2023-05-15",
        "drawback_provision": "1313(j)(1)",
        "total_claim": "2500.75",
        "signatory_name": "Jane Doe",
        "signatory_title": "Import Manager",
        "signature_date": datetime.now().strftime("%Y-%m-%d"),
        "merchandise": [
            {
                "product_id": "PROD-1234",
                "description": "Industrial Machinery Parts",
                "import_date": "2022-03-15",
                "export_date": "2023-01-20",
                "refund_amount": "1250.50"
            },
            {
                "product_id": "PROD-5678",
                "description": "Electronic Components",
                "import_date": "2022-05-10",
                "export_date": "2023-02-15",
                "refund_amount": "875.25"
            },
            {
                "product_id": "PROD-9012",
                "description": "Chemical Compounds",
                "import_date": "2022-06-22",
                "export_date": "2022-12-05",
                "refund_amount": "375.00"
            }
        ]
    }
    
    output_path = "sample_cbp_form_7551.pdf"
    return generate_cbp_form_7551(sample_data, output_path)

def generate_document_guide(output_path="documentation_guide.pdf"):
    """
    Generate a PDF guide explaining required documentation for duty drawback claims
    
    Returns:
    - Path to the generated PDF
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Custom styles
    document_title_style = ParagraphStyle(
        'DocumentTitle',
        parent=subtitle_style,
        fontSize=14,
        textColor=colors.blue,
        spaceAfter=6
    )
    
    document_desc_style = ParagraphStyle(
        'DocumentDescription',
        parent=normal_style,
        fontSize=10,
        leftIndent=20,
        spaceBefore=0
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=normal_style,
        fontSize=10,
        leftIndent=40,
        firstLineIndent=-20,
        spaceBefore=0
    )
    
    # Document content
    elements = []
    
    # Title
    elements.append(Paragraph("Documentation Guide for Duty Drawback Claims", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Introduction
    intro_text = """
    This guide explains the documentation required to support your duty drawback claim. 
    Having these documents properly prepared before submitting your claim will speed up 
    processing and increase your chances of approval.
    """
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Required Documents Section
    elements.append(Paragraph("Required Documentation", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Document 1: CBP Form 7501
    elements.append(Paragraph("1. CBP Form 7501 (Entry Summary)", document_title_style))
    elements.append(Paragraph(
        "The official customs entry document that shows duties paid on imported merchandise.", 
        document_desc_style
    ))
    elements.append(Paragraph("• Must clearly show the Entry Number and date", bullet_style))
    elements.append(Paragraph("• Must show the duty amount paid", bullet_style))
    elements.append(Paragraph("• Should include HTS codes for the imported merchandise", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Document 2: Commercial Invoice
    elements.append(Paragraph("2. Commercial Invoice (Import)", document_title_style))
    elements.append(Paragraph(
        "The invoice from your supplier for the imported goods.", 
        document_desc_style
    ))
    elements.append(Paragraph("• Should include detailed product descriptions", bullet_style))
    elements.append(Paragraph("• Must show product values and quantities", bullet_style))
    elements.append(Paragraph("• Should reference the import shipment if possible", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Document 3: Bill of Lading
    elements.append(Paragraph("3. Bill of Lading (Import)", document_title_style))
    elements.append(Paragraph(
        "The transport document for the imported goods.", 
        document_desc_style
    ))
    elements.append(Paragraph("• Shows proof that the goods were transported to the US", bullet_style))
    elements.append(Paragraph("• Should identify shipper, consignee, and carrier", bullet_style))
    elements.append(Paragraph("• May reference the entry number", bullet_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Document 4: Proof of Export
    elements.append(Paragraph("4. Proof of Export Documentation", document_title_style))
    elements.append(Paragraph(
        "Documentation showing that the same or similar merchandise was later exported.", 
        document_desc_style
    ))
    elements.append(Paragraph("• Can include export bills of lading", bullet_style))
    elements.append(Paragraph("• Shipper's Export Declarations (SEDs)", bullet_style))
    elements.append(Paragraph("• Certificates of Origin for exported goods", bullet_style))
    elements.append(Paragraph("• Must clearly show the exported products and quantities", bullet_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Tips Section
    elements.append(Paragraph("Best Practices for Document Preparation", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    tips_data = [
        ["1", "Ensure Legibility", "All documents should be clearly legible. Scan at 300 DPI or higher."],
        ["2", "Use PDF Format", "Convert all documents to PDF format for consistency."],
        ["3", "Highlight Key Information", "Consider highlighting key information like duty amounts and entry numbers."],
        ["4", "Organize by Entry", "Keep documents organized by entry number for easier reference."],
        ["5", "Verify Completeness", "Check that all pages of multi-page documents are included."]
    ]
    
    # Create tips table
    tips_table = Table(tips_data, colWidths=[0.3*inch, 1.5*inch, 4*inch])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(tips_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Final notes
    elements.append(Paragraph("Document Submission Process", subtitle_style))
    final_text = """
    After analyzing your transaction data in DutyFlow, you'll be prompted to upload 
    these supporting documents for each eligible transaction. The system will guide you 
    through matching documents to the appropriate entries and verify that all required 
    documentation is provided before submission.
    """
    elements.append(Paragraph(final_text, normal_style))
    
    # Build the document
    doc.build(elements)
    
    return output_path

def main():
    """Main function to generate all sample documents"""
    print("Generating sample customs documents...")
    
    # Create sample documents directory
    output_dir = 'sample_documents'
    ensure_directory(output_dir)
    
    # Load or generate sample transaction data
    import_data = load_sample_data()
    
    # Debug - print first row to see structure
    if not import_data.empty:
        print("\nSample data first row:")
        first_row = import_data.iloc[0]
        for col, val in first_row.items():
            print(f"  {col} = {val}")
    
    # Rest of function continues...

if __name__ == "__main__":
    # Example usage
    sample_company = {
        'name': 'ABC Imports, LLC',
        'address': '123 Main Street',
        'city_state_zip': 'Portland, OR 97201',
        'contact_name': 'Jane Smith',
        'phone': '(503) 555-1234',
        'email': 'jane@abcimports.com',
        'importer_number': 'IMP12345678'
    }
    
    try:
        # Assuming there's a results file to use
        results_file = "results/import_analysis_20230301_120000.csv"
        if os.path.exists(results_file):
            pdf_path = generate_form_from_eligible_transactions(results_file, sample_company)
            print(f"PDF report generated: {pdf_path}")
        else:
            print(f"Results file not found: {results_file}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
