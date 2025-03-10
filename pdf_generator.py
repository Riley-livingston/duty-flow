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
import pdfrw
from io import BytesIO
import random
import string
from pdfrw import PdfReader, PdfDict
from dateutil.relativedelta import relativedelta

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

class CBPFormGenerator:
    """Generator for CBP Form 7551 (Drawback Entry)"""
    
    def __init__(self):
        # Path to the blank CBP form template
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates/cbp form 7551.pdf')
        self.output_directory = os.path.join(os.path.dirname(__file__), 'generated_forms')
        
        # Ensure output directory exists
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            
        # Validate template exists
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"CBP Form 7551 template not found at: {self.template_path}")
    
    def generate_form(self, data):
        """
        Generate a filled CBP Form 7551 based on provided data
        
        Args:
            data (dict): Dictionary containing form field values
            
        Returns:
            str: Path to the generated PDF file
        """
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = data.get('claimant_name', '').replace(' ', '_')[:20]
        output_filename = f"drawback_form_7551_{company_name}_{timestamp}.pdf"
        output_path = os.path.join(self.output_directory, output_filename)
        
        try:
            # Try using PyPDF2 first (newer method)
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(self.template_path)
            writer = PdfWriter()
            
            # Copy pages from input to output
            for page in reader.pages:
                writer.add_page(page)
            
            # Update form fields
            if reader.get_fields():
                writer.update_page_form_field_values(
                    writer.pages[0], 
                    {k: v for k, v in data.items() if k in reader.get_fields()}
                )
                
                # Special handling for checkboxes
                for field_name, field_value in data.items():
                    if field_name in ['acclerated', 'abi', 'manual', 'yes14', 'no14'] and field_value:
                        # For checkboxes
                        if field_value.lower() == 'yes' or field_value == '/Yes':
                            writer.update_page_form_field_values(
                                writer.pages[0], 
                                {field_name: '/Yes'}
                            )
            
            # Write the result
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
        except Exception as e:
            print(f"Error using PyPDF2: {e}")
            print("Falling back to pdfrw method...")
            
            # Fallback to pdfrw method
            template = pdfrw.PdfReader(self.template_path)
            
            # Fill in form fields
            for page in template.pages:
                if page.Annots:
                    for annot in page.Annots:
                        if annot and annot.get('/T') and annot.get('/T') in data:
                            field_name = annot.get('/T')
                            field_value = data[field_name]
                            
                            # Handle checkboxes
                            if field_name in ['acclerated', 'abi', 'manual', 'yes14', 'no14']:
                                if field_value.lower() == 'yes' or field_value == '/Yes':
                                    annot.update(pdfrw.PdfDict(V=pdfrw.PdfName('Yes')))
                                else:
                                    annot.update(pdfrw.PdfDict(V=pdfrw.PdfName('Off')))
                            else:
                                # For text fields
                                annot.update(pdfrw.PdfDict(V=field_value))
                                
                            # Update appearance stream for immediate visibility
                            annot.update(pdfrw.PdfDict(AP=''))
            
            # Write the filled PDF to file
            pdfrw.PdfWriter().write(output_path, template)
        
        return output_path
    
    def generate_form_from_uploaded_data(self, import_df, export_df, company_info):
        """
        Generate a form from uploaded import and export data
        
        Args:
            import_df (DataFrame): Import data
            export_df (DataFrame): Export data
            company_info (dict): Company information
            
        Returns:
            str: Path to generated PDF
        """
        eligible_matches = self._find_eligible_matches(import_df, export_df)
        
        if not eligible_matches:
            raise ValueError("No eligible drawback matches found in the uploaded data")
        
        # Calculate totals
        total_duty_paid = sum(match['duty_amount'] for match in eligible_matches)
        refund_amount = total_duty_paid * 0.99  # 99% of duty paid
        
        # Generate a unique drawback entry number
        drawback_entry_no = f"DB{datetime.now().strftime('%Y%m%d')}-{self._generate_unique_id(5)}"
        
        # Create form data with exact field names from the PDF
        form_data = {
            # Basic identification fields
            'drawbacknumber': drawback_entry_no,
            'portcode': company_info.get('port_code', ''),
            'drawbacksection': '1313(j)(1)',
            
            # Claimant information
            'NameandAddressOfClaimant': (
                f"{company_info.get('name', '')}\n"
                f"{company_info.get('address', '')}\n"
                f"{company_info.get('city_state_zip', '')}"
            ),
            'claimantID': company_info.get('importer_number', ''),
            
            # Financial information
            'TotalDrawbackClaimed': f"${refund_amount:,.2f}",
            'MPFClaimed': f"${0:,.2f}",  # Typically 0 for simple cases
            
            # Set checkboxes - these need special handling
            'acclerated': '/Yes',  # Check accelerated payment
            'abi': '/Off',         # Electronic filing - Off if paper
            
            # Certificate info
            'printedname': company_info.get('contact_name', ''),
            'Date500': datetime.now().strftime('%m/%d/%Y')
        }
        
        # Add import entries (up to 4 on main form)
        for i, match in enumerate(eligible_matches[:4], 1):
            form_data[f'ImportEntry{i}'] = match['import_entry']
            form_data[f'PortCode{i}'] = company_info.get('port_code', '')
            form_data[f'ImportDate{i}'] = match['import_date'].strftime('%m/%d/%Y') if hasattr(match['import_date'], 'strftime') else match['import_date']
            form_data[f'Descrip{i}'] = match['product_description'][:30]  # Limit length
            form_data[f'Duty{i}'] = f"${match['duty_amount']:,.2f}"
            form_data[f'Duty99_{i}'] = f"${match['refund_amount']:,.2f}"
        
        # Add export information
        for i, match in enumerate(eligible_matches[:3], 1):
            form_data[f'Date39_{i}'] = match['export_date'].strftime('%m/%d/%Y') if hasattr(match['export_date'], 'strftime') else match['export_date']
            form_data[f'NameofExporter{i}'] = company_info.get('name', '')[:30]
            form_data[f'DescripofArticle{i}'] = match['product_description'][:30]
            form_data[f'Export{i}'] = match['export_reference']
        
        # Generate the form
        pdf_path = self.generate_form(form_data)
        
        # Generate attachment with detailed information
        attachment_path = self.generate_attachment(import_df, export_df, eligible_matches, form_data)
        
        return pdf_path
    
    def generate_attachment(self, import_df, export_df, eligible_matches, form_data, output_filename=None):
        """
        Generate a detailed attachment for CBP Form 7551
        
        Args:
            import_df (DataFrame): Import data
            export_df (DataFrame): Export data
            eligible_matches (list): List of eligible import-export matches
            form_data (dict): Form data used for the main form
            output_filename (str, optional): Output filename
            
        Returns:
            str: Path to the generated attachment
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_name = (form_data.get('claimant_name') or '').replace(' ', '_')[:20]
            output_filename = f"attachment_{company_name}_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_directory, output_filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Extract data safely (with fallbacks)
        drawback_entry = (
            form_data.get('drawbacknumber') or
            form_data.get('drawback_entry_no') or
            f"DB{datetime.now().strftime('%Y%m%d')}"
        )
        
        claimant_name = (
            form_data.get('claimant_name') or
            form_data.get('NameandAddressOfClaimant', '').split('\n')[0] if form_data.get('NameandAddressOfClaimant') else
            ''
        )
        
        claimant_address = (
            form_data.get('claimant_address') or
            ''
        )
        
        claimant_city_state_zip = (
            form_data.get('claimant_city_state_zip') or
            ''
        )
        
        claimant_contact = (
            form_data.get('claimant_contact') or
            form_data.get('printedname') or
            ''
        )
        
        total_duty_paid = (
            form_data.get('total_duty_paid') or
            form_data.get('total_p1') or
            f"${sum([match['duty_amount'] for match in eligible_matches]):.2f}"
        )
        
        total_refund_amount = (
            form_data.get('total_refund_amount') or
            form_data.get('TotalDrawbackClaimed') or
            f"${sum([match['refund_amount'] for match in eligible_matches]):.2f}"
        )
        
        # Create document elements
        elements = []
        
        # Title
        elements.append(Paragraph(f"Attachment to Drawback Entry {drawback_entry}", title_style))
        elements.append(Spacer(1, 12))
        
        # Claimant Info
        elements.append(Paragraph("Claimant Information", heading_style))
        elements.append(Paragraph(f"Claimant: {claimant_name}", normal_style))
        elements.append(Paragraph(f"Address: {claimant_address}, {claimant_city_state_zip}", normal_style))
        elements.append(Paragraph(f"Contact: {claimant_contact}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Eligible Matches
        elements.append(Paragraph("Eligible Drawback Items", heading_style))
        elements.append(Spacer(1, 6))
        
        # Create matches table
        if eligible_matches:
            # Create table headers
            match_data = [['Import Entry', 'Import Date', 'Export Reference', 'Export Date', 
                          'Product Code', 'Description', 'Duty Amount', 'Refund Amount']]
            
            # Add data rows
            for match in eligible_matches:
                match_data.append([
                    match['import_entry'],
                    match['import_date'].strftime('%Y-%m-%d') if hasattr(match['import_date'], 'strftime') else str(match['import_date']),
                    match['export_reference'],
                    match['export_date'].strftime('%Y-%m-%d') if hasattr(match['export_date'], 'strftime') else str(match['export_date']),
                    match['product_code'],
                    match['product_description'],
                    f"${match['duty_amount']:,.2f}",
                    f"${match['refund_amount']:,.2f}"
                ])
            
            match_table = Table(match_data)
            match_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(match_table)
            
            # Add summary
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Summary", heading_style))
            elements.append(Paragraph(f"Total eligible items: {len(eligible_matches)}", normal_style))
            
            # Use .get() method to avoid KeyError - replace with fallbacks
            elements.append(Paragraph(f"Total duty paid: {total_duty_paid}", normal_style))
            elements.append(Paragraph(f"Total refund amount: {total_refund_amount}", normal_style))
        else:
            elements.append(Paragraph("No eligible matches found", normal_style))
        
        # Build the document
        doc.build(elements)
        
        return output_path
    
    def generate_summary_csv(self, claims_data, output_filename=None):
        """
        Generate a CSV summary of all claims
        
        Args:
            claims_data (list): List of dictionaries containing claim data
            output_filename (str, optional): Filename for the CSV
            
        Returns:
            str: Path to the generated CSV file
        """
        import csv
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"drawback_claims_summary_{timestamp}.csv"
        
        output_path = os.path.join(self.output_directory, output_filename)
        
        # Determine fieldnames from the first claim's keys
        if not claims_data:
            raise ValueError("No claims data provided")
            
        fieldnames = list(claims_data[0].keys())
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(claims_data)
            
        return output_path

    def _find_eligible_matches(self, import_df, export_df):
        """
        Find eligible import-export matches for drawback
        
        Args:
            import_df (DataFrame): Import data
            export_df (DataFrame): Export data
            
        Returns:
            list: List of dictionaries with matching import-export pairs
        """
        eligible_matches = []
        
        # Convert dates to datetime
        if 'import_date' in import_df.columns:
            import_df['import_date'] = pd.to_datetime(import_df['import_date'])
        if 'export_date' in export_df.columns:
            export_df['export_date'] = pd.to_datetime(export_df['export_date'])
        
        # Match imports and exports based on product_code
        for _, export_row in export_df.iterrows():
            export_date = export_row['export_date']
            product_code = export_row['product_code']
            
            # Find matching imports (same product code, imported before export)
            matching_imports = import_df[
                (import_df['product_code'] == product_code) & 
                (import_df['import_date'] < export_date) & 
                (import_df['import_date'] > export_date - pd.Timedelta(days=3*365))  # 3-year window
            ]
            
            for _, import_row in matching_imports.iterrows():
                match = {
                    'import_entry': import_row.get('entry_number', 'Unknown'),
                    'import_date': import_row['import_date'],
                    'export_reference': export_row.get('reference_number', 'Unknown'),
                    'export_date': export_row['export_date'],
                    'product_code': product_code,
                    'product_description': import_row.get('product_description', 'Unknown'),
                    'duty_amount': float(import_row.get('duty_paid', 0)),
                    'refund_amount': float(import_row.get('duty_paid', 0)) * 0.99
                }
                eligible_matches.append(match)
        
        return eligible_matches

    def _get_date_range(self, dates):
        """
        Format a list of dates as a range string
        
        Args:
            dates (list): List of datetime objects
            
        Returns:
            str: Formatted date range string
        """
        if not dates:
            return "N/A"
        
        dates = [pd.to_datetime(date) for date in dates]
        earliest = min(dates).strftime('%Y-%m-%d')
        latest = max(dates).strftime('%Y-%m-%d')
        
        if earliest == latest:
            return earliest
        else:
            return f"{earliest} to {latest}"

    def _generate_unique_id(self, length=8):
        """Generate a unique ID string"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def process_and_generate_form(import_file_path, export_file_path, company_info):
    """
    Process import and export data files and generate a filled CBP Form 7551
    
    Args:
        import_file_path (str): Path to import data CSV
        export_file_path (str): Path to export data CSV
        company_info (dict): Dictionary with company information
        
    Returns:
        dict: Dictionary with paths to generated files
    """
    # Load data
    import_df = pd.read_csv(import_file_path)
    export_df = pd.read_csv(export_file_path)
    
    # Initialize form generator
    generator = CBPFormGenerator()
    
    # First, find eligible matches
    eligible_matches = generator._find_eligible_matches(import_df, export_df)
    
    if not eligible_matches:
        raise ValueError("No eligible drawback matches found in the uploaded data")
    
    # Generate form with data
    pdf_path = generator.generate_form_from_uploaded_data(import_df, export_df, company_info)
    
    # Calculate totals for the attachment
    total_duty_paid = sum(match['duty_amount'] for match in eligible_matches)
    refund_amount = total_duty_paid * 0.99  # 99% of duty paid
    
    # Prepare form data for attachment
    form_data = {
        'claimant_name': company_info.get('name', ''),
        'claimant_address': company_info.get('address', ''),
        'claimant_city_state_zip': company_info.get('city_state_zip', ''),
        'claimant_contact': company_info.get('contact_name', ''),
        'drawbacknumber': f"DB{datetime.now().strftime('%Y%m%d')}",
        'total_duty_paid': f"${total_duty_paid:,.2f}",
        'refund_percentage': '99%',
        'total_refund_amount': f"${refund_amount:,.2f}"
    }
    
    # Generate attachment with the eligible matches we found
    attachment_path = generator.generate_attachment(import_df, export_df, eligible_matches, form_data)
    
    return {
        'form': pdf_path,
        'attachment': attachment_path
    }

def fill_drawback_form(import_entries, export_docs, company_info):
    """
    Fill the CBP Form 7551 (Drawback Entry) based on provided import and export data
    """
    import datetime
    import re
    import random
    
    # Path to the blank CBP Form 7551
    template_path = "templates/cbp form 7551.pdf"
    
    # Read the template
    template = PdfReader(template_path)
    
    # Format dates properly
    def format_date(date_value):
        """Format date to MM/DD/YYYY format"""
        if isinstance(date_value, datetime.datetime):
            return date_value.strftime('%m/%d/%Y')
        elif isinstance(date_value, str):
            try:
                # Try to parse as YYYY-MM-DD
                date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d')
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                try:
                    # Try to parse as MM/DD/YYYY
                    date_obj = datetime.datetime.strptime(date_value, '%m/%d/%Y')
                    return date_value  # Already in correct format
                except ValueError:
                    # Just return as is if we can't parse it
                    return date_value
        else:
            return ""
    
    # Calculate values
    total_import_value = 0
    total_duty_paid = 0
    
    for entry in import_entries:
        if isinstance(entry.get("total_value"), (int, float)):
            total_import_value += entry["total_value"]
        elif "line_items" in entry:
            # Calculate from line items if total not provided
            for item in entry["line_items"]:
                if "value" in item and isinstance(item["value"], (int, float)):
                    total_import_value += item["value"]
        
        if isinstance(entry.get("total_duty"), (int, float)):
            total_duty_paid += entry["total_duty"]
        elif "line_items" in entry:
            # Calculate from line items if total not provided
            for item in entry["line_items"]:
                if "duty_amount" in item and isinstance(item["duty_amount"], (int, float)):
                    total_duty_paid += item["duty_amount"]
    
    # Calculate export values
    total_export_value = 0
    for doc in export_docs:
        if isinstance(doc.get("total_value"), (int, float)):
            total_export_value += doc["total_value"]
        elif "items" in doc:
            for item in doc["items"]:
                if "value" in item and isinstance(item["value"], (int, float)):
                    total_export_value += item["value"]
    
    # Calculate drawback amount (typically 99% of duties paid on exported merchandise)
    export_ratio = min(1.0, total_export_value / max(1, total_import_value))
    drawback_amount = round(total_duty_paid * export_ratio * 0.99, 2)  # 99% of eligible duties
    
    # Create a unique drawback number
    drawback_number = f"DB-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Format the claimant address
    claimant_address = "\n".join([
        company_info['name'],
        company_info.get('address', ''),
        company_info.get('city_state_zip', '')
    ])
    
    # Format preparer address (same as claimant in this case)
    preparer_address = "\n".join([
        company_info.get('contact_name', 'John Trader') + ", Import Manager",
        company_info['name'],
        company_info.get('address', ''),
        company_info.get('city_state_zip', ''),
        company_info.get('phone', '(555) 123-4567')
    ])
    
    # Current date
    current_date = datetime.datetime.now().strftime('%m/%d/%Y')
    
    # Get formatted import dates
    import_dates = []
    for entry in import_entries:
        if entry.get("import_date"):
            import_dates.append(format_date(entry["import_date"]))
    
    # Get formatted export dates
    export_dates = []
    for doc in export_docs:
        if doc.get("export_date"):
            export_dates.append(format_date(doc["export_date"]))
    
    # Extract HTS codes and descriptions from import data
    hts_codes = []
    descriptions = []
    quantities = []
    
    for entry in import_entries:
        if "line_items" in entry:
            for item in entry["line_items"]:
                if "hts_code" in item:
                    hts_codes.append(item["hts_code"])
                if "description" in item:
                    descriptions.append(item["description"])
                if "quantity" in item:
                    quantities.append(str(item["quantity"]))
    
    # Create a comprehensive field mapping
    field_mapping = {
        # Header information
        'drawbacknumber': drawback_number,
        'portcode': '3901',  # Chicago
        'entrytypecode': '01',
        'claimantID': company_info.get('importer_number', '12-3456789'),
        'suretycode': '123',
        'bondtype': '9',
        'brokerID': 'BR123456',
        
        # Section 1: Basic claim info
        'NameandAddressOfClaimant': claimant_address,
        'NameandAddressofPreparer': preparer_address,
        'TotalDrawbackClaimed': f"${drawback_amount:,.2f}",
        'MPFClaimed': f"${round(total_duty_paid * 0.01, 2):,.2f}",
        'drawbacksection': '1313(j)(1)',
        'acclerated': '/Yes',  # Checkbox for accelerated payment
        'manual': '/Yes',      # Manual filing checkbox
        'yes14': '/Yes',       # Yes checkbox
        
        # Section 2: Import information - First entry
        'ImportEntry1': import_entries[0].get('entry_number', '') if len(import_entries) > 0 else '',
        'PortCode1': import_entries[0].get('port_code', '3901') if len(import_entries) > 0 else '',
        'ImportDate1': format_date(import_entries[0].get('import_date', '')) if len(import_entries) > 0 else '',
        'HTSUS1': hts_codes[0] if len(hts_codes) > 0 else '',
        'Descrip1': descriptions[0] if len(descriptions) > 0 else '',
        'Quantity1': quantities[0] if len(quantities) > 0 else '',
        'Value1': f"${import_entries[0].get('total_value', 0):,.2f}" if len(import_entries) > 0 else '',
        'Duty1': f"${import_entries[0].get('total_duty', 0):,.2f}" if len(import_entries) > 0 else '',
        'Duty99_1': f"${import_entries[0].get('total_duty', 0) * 0.99:,.2f}" if len(import_entries) > 0 else '',
        
        # Import entry data - Additional entries
        'ImportEntry2': import_entries[1].get('entry_number', '') if len(import_entries) > 1 else '',
        'PortCode2': import_entries[1].get('port_code', '3901') if len(import_entries) > 1 else '',
        'ImportDate2': format_date(import_entries[1].get('import_date', '')) if len(import_entries) > 1 else '',
        'HTSUS2_ds_1': hts_codes[1] if len(hts_codes) > 1 else '',
        'Descrip2': descriptions[1] if len(descriptions) > 1 else '',
        'Quantity2_p0': quantities[1] if len(quantities) > 1 else '',
        'Value2': f"${import_entries[1].get('total_value', 0):,.2f}" if len(import_entries) > 1 else '',
        'Duty2': f"${import_entries[1].get('total_duty', 0):,.2f}" if len(import_entries) > 1 else '',
        'Duty99_2': f"${import_entries[1].get('total_duty', 0) * 0.99:,.2f}" if len(import_entries) > 1 else '',
        
        'ImportEntry3': import_entries[2].get('entry_number', '') if len(import_entries) > 2 else '',
        'PortCode3': import_entries[2].get('port_code', '3901') if len(import_entries) > 2 else '',
        'ImportDate3': format_date(import_entries[2].get('import_date', '')) if len(import_entries) > 2 else '',
        'HTSUS3_ds_2': hts_codes[2] if len(hts_codes) > 2 else '',
        'Descrip3': descriptions[2] if len(descriptions) > 2 else '',
        'Quantity3_p0': quantities[2] if len(quantities) > 2 else '',
        'Value3': f"${import_entries[2].get('total_value', 0):,.2f}" if len(import_entries) > 2 else '',
        'Duty3': f"${import_entries[2].get('total_duty', 0):,.2f}" if len(import_entries) > 2 else '',
        'Duty99_3': f"${import_entries[2].get('total_duty', 0) * 0.99:,.2f}" if len(import_entries) > 2 else '',
        
        # Section 3: Delivery information
        'CD1': 'X',  # Consumed code
        'DateReceived1': import_dates[0] if import_dates else '',
        'DateUsed1': format_date((datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')),
        
        # Section 4: Export information
        'Date39_1': export_dates[0] if export_dates else '',
        'ActionCode1': '2',  # Export code
        'UniqueID1': export_docs[0].get('export_ref', 'EXP123456') if export_docs else '',
        'NameofExporter1': company_info['name'],
        'DescripofArticle1': export_docs[0]['items'][0]['description'] if export_docs and 'items' in export_docs[0] and export_docs[0]['items'] else '',
        'Quantity1_p1_n7': str(export_docs[0]['items'][0]['quantity']) if export_docs and 'items' in export_docs[0] and export_docs[0]['items'] else '',
        'Export1': export_docs[0].get('destination', 'Canada') if export_docs else '',
        
        # Additional export entries if available
        'Date39_2': export_dates[1] if len(export_dates) > 1 else '',
        'ActionCode2': '2' if len(export_docs) > 1 else '',
        'UniqueID2': export_docs[1].get('export_ref', '') if len(export_docs) > 1 else '',
        'NameofExporter2': company_info['name'] if len(export_docs) > 1 else '',
        'DescripofArticle2': export_docs[1]['items'][0]['description'] if len(export_docs) > 1 and 'items' in export_docs[1] and export_docs[1]['items'] else '',
        'Quantity2_p2': str(export_docs[1]['items'][0]['quantity']) if len(export_docs) > 1 and 'items' in export_docs[1] and export_docs[1]['items'] else '',
        'Export2': export_docs[1].get('destination', '') if len(export_docs) > 1 else '',
        
        # Certification
        'printedname': company_info.get('contact_name', 'John Trader'),
        'Date500': current_date,
        
        # Section 2: HTSUS/description related to import line items
        'description': 'Identical unused merchandise exported within 3 years of import',
        
        # Options and checkboxes 
        'option1': '/Yes',  # NAFTA/USMCA checkbox
        'corporation': '/Yes',  # Corporation type
        
        # Additional dates and totals
        'Date': current_date,
        'total_p0': f"${total_import_value:,.2f}",  # Total import value
        'total_p1': f"${drawback_amount:,.2f}"      # Total drawback amount
    }
    
    # Fill the form with our field mapping
    for page in template.pages:
        if page.Annots:
            for annotation in page.Annots:
                if annotation.Subtype == "/Widget" and hasattr(annotation, "/T") and annotation["/T"]:
                    key = annotation["/T"][1:-1]  # Remove parentheses
                    if key in field_mapping:
                        # For checkboxes
                        if annotation.get("/FT") == "/Btn" and field_mapping[key].startswith('/'):
                            if field_mapping[key] != '/Off':
                                annotation.update(pdfrw.PdfDict(AS=field_mapping[key], V=field_mapping[key]))
                        else:
                            # For text fields
                            annotation.update(pdfrw.PdfDict(V=field_mapping[key]))
    
    # Save the filled form
    output_path = f"filled_forms/cbp_form_7551_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdfrw.PdfWriter().write(output_path, template)
    
    print(f"Form filled with {len(field_mapping)} fields")
    return output_path
