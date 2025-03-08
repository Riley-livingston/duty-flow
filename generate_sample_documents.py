import os
import sys
from datetime import datetime, timedelta
import random
import string
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import pandas as pd

def ensure_directory(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_random_id(prefix, length=8):
    """Generate a random ID with a given prefix"""
    random_part = ''.join(random.choices(string.digits, k=length))
    return f"{prefix}{random_part}"

def get_safe_value(data, key, fallback=None):
    """Safely get a value from a DataFrame row or dict, with fallback value"""
    try:
        if hasattr(data, 'get') and callable(data.get):
            # It's a dict-like object
            return data.get(key, fallback)
        else:
            # It's likely a pandas Series or DataFrame row
            return data[key] if key in data else fallback
    except:
        return fallback

def load_sample_data():
    """Load or generate sample import/export transaction data"""
    # Check if we have sample transactions from the main app
    try:
        import_file = 'uploads/sample_imports.csv'
        if os.path.exists(import_file):
            import_data = pd.read_csv(import_file)
            print("Loaded existing import data with columns:", import_data.columns.tolist())
            
            # Check for required columns and add them if missing
            if 'country_of_origin' not in import_data.columns:
                if 'origin_country' in import_data.columns:
                    # Rename if similar column exists
                    import_data['country_of_origin'] = import_data['origin_country']
                else:
                    # Add with default values
                    countries = ['China', 'Vietnam', 'Mexico', 'Italy', 'Indonesia']
                    import_data['country_of_origin'] = [random.choice(countries) for _ in range(len(import_data))]
            
            # Add other required columns if missing
            required_columns = {
                'product_id': lambda: f"SKU{random.randint(1000, 9999)}",
                'product_description': lambda: random.choice([
                    "Men's Leather Shoes", "Women's Cotton Blouses", 
                    "Ceramic Coffee Mugs", "Stainless Steel Cookware Set", 
                    "Wooden Dining Table"
                ]),
                'hs_code': lambda: f"{random.randint(4000, 9000)}.{random.randint(10, 99)}.{random.randint(1000, 9999)}",
                'quantity': lambda: random.randint(50, 500),
                'value': lambda: round(random.uniform(1000, 20000), 2),
                'duty_paid': lambda: round(random.uniform(100, 2000), 2)
            }
            
            for col, default_func in required_columns.items():
                if col not in import_data.columns:
                    import_data[col] = [default_func() for _ in range(len(import_data))]
            
            return import_data
    except Exception as e:
        print(f"Error loading existing import data: {str(e)}")
        print("Generating sample data instead.")
    
    # If no file exists or loading failed, create some dummy data
    products = [
        {"id": "SKU001", "description": "Men's Leather Shoes", "hs_code": "6403.99.6000", "origin": "Italy"},
        {"id": "SKU002", "description": "Women's Cotton Blouses", "hs_code": "6206.30.3000", "origin": "Vietnam"},
        {"id": "SKU003", "description": "Ceramic Coffee Mugs", "hs_code": "6912.00.4800", "origin": "China"},
        {"id": "SKU004", "description": "Stainless Steel Cookware Set", "hs_code": "7323.93.0000", "origin": "China"},
        {"id": "SKU005", "description": "Wooden Dining Table", "hs_code": "9403.60.8000", "origin": "Malaysia"}
    ]
    
    import_data = []
    
    # Generate 5 random entries
    for i in range(5):
        product = random.choice(products)
        entry_date = random_date(datetime.now() - timedelta(days=180), datetime.now() - timedelta(days=30))
        entry_number = generate_random_id("EI", 9)
        
        import_data.append({
            "entry_number": entry_number,
            "import_date": entry_date.strftime("%Y-%m-%d"),
            "product_id": product["id"],
            "product_description": product["description"],
            "hs_code": product["hs_code"],
            "country_of_origin": product["origin"],
            "quantity": random.randint(50, 500),
            "value": round(random.uniform(1000, 20000), 2),
            "duty_paid": round(random.uniform(100, 2000), 2)
        })
    
    return pd.DataFrame(import_data)

def generate_cbp_7501(output_dir, entry_data):
    """Generate a sample CBP Form 7501 (Entry Summary)"""
    # Get safe values with fallbacks
    entry_number = get_safe_value(entry_data, 'entry_number', f"EI{random.randint(10000000, 99999999)}")
    import_date = get_safe_value(entry_data, 'import_date', datetime.now().strftime("%Y-%m-%d"))
    origin_country = get_safe_value(entry_data, 'country_of_origin', 'CHINA')
    product_desc = get_safe_value(entry_data, 'product_description', 'General Merchandise')
    hs_code = get_safe_value(entry_data, 'hs_code', '9999.99.9999')
    quantity = get_safe_value(entry_data, 'quantity', 100)
    value = get_safe_value(entry_data, 'value', 5000.00)
    duty_paid = get_safe_value(entry_data, 'duty_paid', 250.00)
    
    filename = os.path.join(output_dir, f"CBP_7501_{entry_number}.pdf")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=0.3*inch
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("U.S. CUSTOMS AND BORDER PROTECTION", title_style))
    elements.append(Paragraph("ENTRY SUMMARY", title_style))
    elements.append(Paragraph("CBP Form 7501", styles["Heading3"]))
    elements.append(Spacer(1, 0.2*inch))
    
    # Form data
    data = [
        ["1. Entry Number", entry_number, "2. Entry Type", "01 - Consumption"],
        ["3. Entry Date", import_date, "4. Importer of Record", "DUTYFLOW TEST INC"],
        ["5. Port Code", "2704 - SAVANNAH, GA", "6. Foreign Port", "VARIOUS"],
        ["7. Importer Number", "IMP123456789", "8. Consignee Number", "IMP123456789"],
        ["9. Mode of Transport", "11 - VESSEL", "10. Country of Origin", origin_country],
        ["11. Import Date", import_date, "12. B/L or AWB Number", f"BL{random.randint(10000, 99999)}"],
        ["13. Manufacturer ID", f"MFG{random.randint(10000, 99999)}", "14. Exporting Country", origin_country],
        ["15. Export Date", "", "16. I.T. Number", ""],
        ["17. I.T. Date", "", "18. Missing Docs", ""],
        ["19. Foreign Trade Zone", "", "20. U.S. Port of Unlading", "SAVANNAH, GA"],
        ["21. Location of Goods", "WAREHOUSE CODE 123", "22. Broker/Filer Information", "CUSTOMS BROKER INC\nFMC 12345"],
        ["23. Importer Address", "DUTYFLOW TEST INC\n123 IMPORT ST\nANYTOWN, GA 30301", "24. Reference Number", generate_random_id("REF", 6)],
        ["25. Ultimate Consignee", "DUTYFLOW TEST INC", "26. Declarant Signature", "ELECTRONICALLY SIGNED"],
    ]
    
    # Create the table
    form_table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    form_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(form_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Line Items header
    elements.append(Paragraph("Line Items", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    # Line item data
    line_headers = ["Line", "HTS Number", "Country\nof Origin", "Description of Merchandise", "Quantity", "Value", "Duty Rate", "Duty Amount"]
    line_data = [line_headers]
    
    # Add a single line item
    line_data.append([
        "1",
        hs_code,
        origin_country,
        product_desc,
        str(quantity),
        f"${value:.2f}",
        "3.7%",
        f"${duty_paid:.2f}"
    ])
    
    # Create the line items table
    line_table = Table(line_data, colWidths=[0.4*inch, 1*inch, 0.7*inch, 2.5*inch, 0.6*inch, 0.8*inch, 0.6*inch, 0.8*inch])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary data
    summary_data = [
        ["Total Entered Value", f"${value:.2f}", "Total Duty", f"${duty_paid:.2f}"],
        ["Total MPF", f"${value * 0.00346:.2f}", "Total Tax", "$0.00"],
        ["Other Fees", "$0.00", "Total Amount Due", f"${duty_paid + (value * 0.00346):.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(summary_table)
    
    # Build the document
    doc.build(elements)
    
    return filename

def generate_commercial_invoice(output_dir, entry_data):
    """Generate a sample Commercial Invoice"""
    # Get safe values with fallbacks
    entry_number = get_safe_value(entry_data, 'entry_number', f"EI{random.randint(10000000, 99999999)}")
    import_date = get_safe_value(entry_data, 'import_date', datetime.now().strftime("%Y-%m-%d"))
    origin_country = get_safe_value(entry_data, 'country_of_origin', 'CHINA')
    product_desc = get_safe_value(entry_data, 'product_description', 'General Merchandise')
    product_id = get_safe_value(entry_data, 'product_id', 'SKU12345')
    hs_code = get_safe_value(entry_data, 'hs_code', '9999.99.9999')
    quantity = get_safe_value(entry_data, 'quantity', 100)
    value = get_safe_value(entry_data, 'value', 5000.00)
    
    filename = os.path.join(output_dir, f"Commercial_Invoice_{entry_number}.pdf")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=0.3*inch
    )
    
    elements = []
    
    # Company header
    elements.append(Paragraph(f"EXPORTCO {origin_country} LTD", title_style))
    elements.append(Paragraph("COMMERCIAL INVOICE", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice details
    invoice_number = generate_random_id("INV", 6)
    import_datetime = parse_date(import_date)
    invoice_date = import_datetime - timedelta(days=random.randint(5, 15))
    invoice_date_str = invoice_date.strftime("%Y-%m-%d")
    
    invoice_data = [
        ["Invoice Number", invoice_number, "Seller", f"EXPORTCO {origin_country} LTD\n123 EXPORT ROAD\n{origin_country}"],
        ["Invoice Date", invoice_date_str, "Buyer", "DUTYFLOW TEST INC\n123 IMPORT ST\nANYTOWN, GA 30301\nUSA"],
        ["Terms", "FOB ORIGIN", "Ship To", "DUTYFLOW TEST INC\nWAREHOUSE #456\n456 WAREHOUSE BLVD\nSAVANNAH, GA 31408\nUSA"],
        ["Currency", "USD", "Incoterms", "FOB"],
        ["Payment Terms", "NET 30", "Shipment Ref", entry_number]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 3.4*inch])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Line items
    elements.append(Paragraph("Items", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    item_headers = ["Item", "Description", "HTS Code", "Country of Origin", "Quantity", "Unit Price", "Total"]
    item_data = [item_headers]
    
    unit_price = value / quantity
    
    item_data.append([
        product_id,
        product_desc,
        hs_code,
        origin_country,
        str(quantity),
        f"${unit_price:.2f}",
        f"${value:.2f}"
    ])
    
    item_table = Table(item_data, colWidths=[0.7*inch, 2*inch, 1*inch, 1*inch, 0.7*inch, 0.8*inch, 0.8*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(item_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary
    summary_data = [
        ["", "", "Subtotal", f"${value:.2f}"],
        ["", "", "Shipping", "$0.00"],
        ["", "", "Insurance", "$0.00"],
        ["", "", "Total", f"${value:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('GRID', (2, 0), (3, -1), 0.5, colors.black),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Declaration
    declaration_text = "We hereby certify that the information on this invoice is true and correct and the contents and value of this shipment is as stated above."
    elements.append(Paragraph(declaration_text, styles["Normal"]))
    elements.append(Spacer(1, 0.2*inch))
    
    # Signature
    elements.append(Paragraph("Authorized Signature: _______________________", styles["Normal"]))
    elements.append(Paragraph(f"Date: {invoice_date_str}", styles["Normal"]))
    
    # Build the document
    doc.build(elements)
    
    return filename

def generate_bill_of_lading(output_dir, entry_data):
    """Generate a sample Bill of Lading"""
    # Get safe values with fallbacks
    entry_number = get_safe_value(entry_data, 'entry_number', f"EI{random.randint(10000000, 99999999)}")
    import_date = get_safe_value(entry_data, 'import_date', datetime.now().strftime("%Y-%m-%d"))
    origin_country = get_safe_value(entry_data, 'country_of_origin', 'CHINA')
    product_desc = get_safe_value(entry_data, 'product_description', 'General Merchandise')
    product_id = get_safe_value(entry_data, 'product_id', 'SKU12345')
    hs_code = get_safe_value(entry_data, 'hs_code', '9999.99.9999')
    quantity = get_safe_value(entry_data, 'quantity', 100)
    value = get_safe_value(entry_data, 'value', 5000.00)
    
    filename = os.path.join(output_dir, f"Bill_of_Lading_{entry_number}.pdf")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=0.3*inch
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("SHIPPING LINE CORPORATION", title_style))
    elements.append(Paragraph("BILL OF LADING", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # B/L details
    bl_number = f"BL{random.randint(10000, 99999)}"
    
    # Calculate dates
    import_date = datetime.strptime(import_date, "%Y-%m-%d")
    sailing_date = import_date - timedelta(days=random.randint(10, 20))
    sailing_date_str = sailing_date.strftime("%Y-%m-%d")
    
    shipping_data = [
        ["Bill of Lading No.", bl_number, "Booking No.", generate_random_id("BKG", 6)],
        ["Export References", entry_number, "Shipper", f"EXPORTCO {origin_country} LTD\n123 EXPORT ROAD\n{origin_country}"],
        ["Vessel", f"MV {random.choice(['PACIFIC', 'ATLANTIC', 'SOUTHERN', 'NORTHERN'])} {random.choice(['STAR', 'EXPLORER', 'TRADER', 'MARINER'])}", "Consignee", "DUTYFLOW TEST INC\n123 IMPORT ST\nANYTOWN, GA 30301\nUSA"],
        ["Voyage No.", f"V{random.randint(100, 999)}", "Notify Party", "DUTYFLOW TEST INC\n123 IMPORT ST\nANYTOWN, GA 30301\nUSA"],
        ["Port of Loading", random.choice([f"PORT OF {origin_country}", "SHANGHAI, CHINA", "BUSAN, KOREA", "SINGAPORE"]), "Port of Discharge", "SAVANNAH, GA, USA"],
        ["Sailing Date", sailing_date_str, "Delivery Agent", "SHIPPING AGENT USA INC."]
    ]
    
    shipping_table = Table(shipping_data, colWidths=[1.5*inch, 1.8*inch, 1.1*inch, 2.6*inch])
    shipping_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(shipping_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Container details
    elements.append(Paragraph("Container Information", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    container_headers = ["Container No.", "Seal No.", "Type", "Packages", "Package Type", "Weight (kg)", "Volume (m³)"]
    container_data = [container_headers]
    
    # Weight calculation (rough estimate based on value)
    weight = quantity * random.uniform(0.3, 2.0)
    volume = weight / random.uniform(200, 300)
    
    container_data.append([
        f"CNTR{random.randint(1000000, 9999999)}",
        f"SEAL{random.randint(10000, 99999)}",
        "40' HC",
        str(int(quantity / random.randint(50, 200))),
        "CARTONS",
        f"{weight:.2f}",
        f"{volume:.2f}"
    ])
    
    container_table = Table(container_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 0.7*inch, 1*inch, 1*inch, 1*inch])
    container_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(container_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Cargo description
    elements.append(Paragraph("Cargo Description", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    cargo_data = [
        ["Marks & Numbers", "Description of Goods", "H.S. Code", "Quantity"],
        [f"DUTYFLOW\nORDER #{entry_number}\nMFG: {origin_country}", product_desc, hs_code, f"{quantity} PCS"]
    ]
    
    cargo_table = Table(cargo_data, colWidths=[1.5*inch, 3.5*inch, 1*inch, 1*inch])
    cargo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(cargo_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer and signatures
    elements.append(Paragraph("SHIPPED on board the Vessel in apparent good order and condition.", styles["Normal"]))
    elements.append(Spacer(1, 0.3*inch))
    
    signature_data = [
        ["For SHIPPING LINE CORPORATION", "", "Place and date of issue", ""],
        ["", "", f"{random.choice(['HONG KONG', 'SINGAPORE', 'SHANGHAI', 'TOKYO'])}, {sailing_date_str}", ""],
        ["_____________________________", "", "Number of Original B/L", ""],
        ["Authorized Signature", "", "THREE (3)", ""]
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 1*inch, 2*inch, 1*inch])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
        ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),
    ]))
    
    elements.append(signature_table)
    
    # Build the document
    doc.build(elements)
    
    return filename

def generate_export_proof(output_dir, entry_data):
    """Generate a sample Export Proof Document"""
    # Get safe values with fallbacks
    entry_number = get_safe_value(entry_data, 'entry_number', f"EI{random.randint(10000000, 99999999)}")
    import_date = get_safe_value(entry_data, 'import_date', datetime.now().strftime("%Y-%m-%d"))
    origin_country = get_safe_value(entry_data, 'country_of_origin', 'CHINA')
    product_desc = get_safe_value(entry_data, 'product_description', 'General Merchandise')
    product_id = get_safe_value(entry_data, 'product_id', 'SKU12345')
    hs_code = get_safe_value(entry_data, 'hs_code', '9999.99.9999')
    quantity = get_safe_value(entry_data, 'quantity', 100)
    value = get_safe_value(entry_data, 'value', 5000.00)
    
    filename = os.path.join(output_dir, f"Export_Proof_{entry_number}.pdf")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=0.3*inch
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("CERTIFICATE OF EXPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Generate export date (slightly after import)
    import_date = datetime.strptime(import_date, "%Y-%m-%d")
    export_date = import_date + timedelta(days=random.randint(20, 120))
    export_date_str = export_date.strftime("%Y-%m-%d")
    
    # Export details
    export_ref = generate_random_id("EXP", 8)
    
    # Pick a random destination
    destinations = {
        "Canada": "TORONTO, ON",
        "Mexico": "MEXICO CITY",
        "Germany": "HAMBURG",
        "Japan": "TOKYO",
        "Australia": "SYDNEY",
        "Brazil": "SAO PAULO",
        "United Kingdom": "LONDON",
        "France": "PARIS"
    }
    
    export_country = random.choice(list(destinations.keys()))
    export_city = destinations[export_country]
    
    export_data = [
        ["Certificate Number", export_ref, "Exporter", "DUTYFLOW TEST INC\n123 IMPORT ST\nANYTOWN, GA 30301\nUSA"],
        ["Date of Export", export_date_str, "Consignee", f"REEXPORTCO {export_country} INC\n456 IMPORT AVENUE\n{export_city}\n{export_country}"],
        ["Transport Method", random.choice(["Vessel", "Air Freight", "Road", "Rail"]), "Port of Export", "SAVANNAH, GA, USA"],
        ["Related Entry Number", entry_number, "Port of Destination", export_city],
        ["Export Value", f"${value * random.uniform(1.1, 1.5):.2f}", "Master Bill Reference", generate_random_id("MBL", 8)]
    ]
    
    export_table = Table(export_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 2.8*inch])
    export_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(export_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Goods description
    elements.append(Paragraph("Description of Goods", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    goods_headers = ["Item", "Description", "HTS Code", "Origin", "Quantity", "Value"]
    goods_data = [goods_headers]
    
    goods_data.append([
        product_id,
        product_desc,
        hs_code,
        origin_country,
        str(quantity),
        f"${value:.2f}"
    ])
    
    goods_table = Table(goods_data, colWidths=[0.7*inch, 2.5*inch, 1*inch, 1*inch, 0.8*inch, 1*inch])
    goods_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(goods_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Certification
    elements.append(Paragraph("Certification", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    certification_text = """I hereby certify that the goods described above were exported from the United States in the quantity, value, and on the date shown above. These goods were imported into the United States as per the related entry number. No drawback claim has been or will be made by our company other than through the current claim process."""
    
    elements.append(Paragraph(certification_text, styles["Normal"]))
    elements.append(Spacer(1, 0.3*inch))
    
    # Signatures
    signature_data = [
        ["Authorized Signature", "", "Customs Authentication", ""],
        ["_____________________________", "", "_____________________________", ""],
        ["Name: JOHN SMITH", "", "Name:", ""],
        ["Title: EXPORT COMPLIANCE OFFICER", "", "Title:", ""],
        ["Date: " + export_date_str, "", "Date:", ""]
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 1*inch, 2*inch, 1*inch])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(signature_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Seal or stamp
    elements.append(Paragraph("OFFICIAL STAMP / SEAL", styles["Heading3"]))
    elements.append(Spacer(1, 0.1*inch))
    
    # Create a box for the stamp
    seal_data = [
        ["PLACE OFFICIAL EXPORT"],
        ["CERTIFICATION STAMP HERE"],
        [""],
        ["SAMPLE - NOT VALID"]
    ]
    
    seal_table = Table(seal_data, colWidths=[3*inch])
    seal_table.setStyle(TableStyle([
        ('BOX', (0, 0), (0, -1), 2, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 3), (0, 3), colors.red),
    ]))
    
    elements.append(seal_table)
    
    # Build the document
    doc.build(elements)
    
    return filename

def debug_print(df, title="DataFrame Contents"):
    """Print DataFrame information for debugging"""
    print(f"\n{title}:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print("\nSample data (first row):")
    if not df.empty:
        for col, val in df.iloc[0].items():
            print(f"  {col} = {val}")
    print("\n")

def parse_date(date_str, default=None):
    """Parse a date string in various formats"""
    if not date_str:
        return default or datetime.now()
        
    try:
        # Try various formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y%m%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, try pandas
        return pd.to_datetime(date_str).to_pydatetime()
    except:
        # If all parsing fails, return default
        return default or datetime.now()

def main():
    """Main function to generate all sample documents"""
    print("Generating sample customs documents...")
    
    # Create sample documents directory
    output_dir = 'sample_documents'
    ensure_directory(output_dir)
    
    # Load or generate sample transaction data
    import_data = load_sample_data()
    
    # Debug output
    debug_print(import_data, "Sample Import Data")
    
    # Process each transaction
    generated_files = []
    
    for _, entry in import_data.iterrows():
        # Generate a CBP Form 7501
        cbp_file = generate_cbp_7501(output_dir, entry)
        generated_files.append(cbp_file)
        
        # Generate Commercial Invoice
        invoice_file = generate_commercial_invoice(output_dir, entry)
        generated_files.append(invoice_file)
        
        # Generate Bill of Lading
        bl_file = generate_bill_of_lading(output_dir, entry)
        generated_files.append(bl_file)
        
        # Generate Export Proof
        export_file = generate_export_proof(output_dir, entry)
        generated_files.append(export_file)
    
    # Print the results
    print(f"Generated {len(generated_files)} sample documents in '{output_dir}' folder:")
    for f in generated_files:
        print(f"- {os.path.basename(f)}")
    
    print("\nYou can now upload these documents to test the document management system.")
    print("Each document corresponds to entries in the sample import/export data.")

if __name__ == "__main__":
    main() 