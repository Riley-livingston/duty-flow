from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import pandas as pd
import os
import datetime
import random
import string
from fpdf import FPDF
from faker import Faker
# Add new imports for screenshots and PDF visualization
import time
from PIL import Image
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import io
import tempfile
import platform
import subprocess
import re

fake = Faker()

# Constants for more realistic data
CUSTOMS_PORTS = {
    "0101": "PORTLAND, MAINE",
    "0401": "BOSTON, MASSACHUSETTS",
    "1001": "NEW YORK, NEW YORK",
    "2809": "LOS ANGELES, CALIFORNIA",
    "3901": "CHICAGO, ILLINOIS",
    "5301": "HOUSTON, TEXAS"
}

HTS_CODES = {
    "8471.30.0100": "Portable digital automatic data processing machines",
    "8517.12.0000": "Telephones for cellular networks",
    "8528.52.0000": "Monitors capable of connecting to automatic data processing machines",
    "8504.40.8500": "Power adapters for computers and electronics",
    "8544.42.9090": "Electrical conductors for a voltage not exceeding 1,000 V",
    "3926.90.9985": "Plastic components for electronics"
}

SHIPPING_CARRIERS = ["Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd", "ONE", "Evergreen"]
VESSEL_NAMES = ["MAERSK DENVER", "MSC OSCAR", "CMA CGM ANTOINE", "COSCO SHIPPING UNIVERSE", 
                "EVER GIVEN", "ONE APUS", "OOCL HONG KONG"]

# Create directories if they don't exist
for dir_name in ["test_documents", "test_data"]:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def random_entry_number():
    """Generate a realistic CBP entry number"""
    # Format is typically: 3 letters followed by 8 digits
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}-{suffix}"

def random_hts_code():
    """Generate a realistic HTS code"""
    # Format is typically 10 digits with dots (e.g., 8471.30.0100)
    first = random.randint(1000, 9999)
    second = random.randint(10, 99)
    third = random.randint(1000, 9999)
    return f"{first}.{second}.{third}"

def create_realistic_import_data(num_records=10):
    """Create realistic import data for CBP Form 7551"""
    # Create common entry information
    entry_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(180, 300))
    entry_number = random_entry_number()
    
    # Common product categories
    categories = [
        ("Electronic Components", 0.025),
        ("Machinery Parts", 0.03),
        ("Textiles", 0.055),
        ("Plastics", 0.04),
        ("Automotive Parts", 0.025),
        ("Chemical Products", 0.035),
        ("Consumer Goods", 0.045)
    ]
    
    data = {
        'entry_number': [],
        'import_date': [],
        'product_code': [],
        'hts_number': [],
        'product_description': [],
        'quantity': [],
        'unit_price': [],
        'total_value': [],
        'duty_rate': [],
        'duty_paid': [],
        'country_of_origin': []
    }
    
    origin_countries = ["CN", "MX", "VN", "IN", "TH", "JP", "DE", "IT", "BR"]
    
    for i in range(num_records):
        # Pick a product category
        category, duty_rate = random.choice(categories)
        
        # Create realistic product codes: 2 letters + 4 digits + optional letter
        product_code = f"{category[:2].upper()}{random.randint(1000, 9999)}"
        if random.random() > 0.5:
            product_code += random.choice(string.ascii_uppercase)
            
        # Create product description
        adjectives = ["Premium", "Standard", "Industrial", "Commercial", "High-Grade"]
        description = f"{random.choice(adjectives)} {category[:-1]}"
        
        # Calculate financial values
        quantity = random.randint(10, 500)
        unit_price = round(random.uniform(5.0, 150.0), 2)
        total_value = round(quantity * unit_price, 2)
        duty_paid = round(total_value * duty_rate, 2)
        
        # Add small variation to import dates
        record_date = entry_date + datetime.timedelta(days=random.randint(-5, 5))
        
        # Add to data dictionary
        data['entry_number'].append(entry_number)
        data['import_date'].append(record_date.strftime('%Y-%m-%d'))
        data['product_code'].append(product_code)
        data['hts_number'].append(random_hts_code())
        data['product_description'].append(description)
        data['quantity'].append(quantity)
        data['unit_price'].append(unit_price)
        data['total_value'].append(total_value)
        data['duty_rate'].append(duty_rate)
        data['duty_paid'].append(duty_paid)
        data['country_of_origin'].append(random.choice(origin_countries))
    
    # Create DataFrame and save as CSV
    df = pd.DataFrame(data)
    csv_path = "test_data/realistic_imports.csv"
    df.to_csv(csv_path, index=False)
    print(f"Created realistic import data: {csv_path}")
    
    # Also create a commercial invoice PDF
    create_import_invoice_pdf(df)
    
    return df

def create_import_invoice_pdf(import_df):
    """Create a realistic commercial invoice PDF from import data"""
    
    # Group by entry number
    entry_groups = import_df.groupby('entry_number')
    
    for entry_number, group in entry_groups:
        # Get first row for date and other details
        first_row = group.iloc[0]
        import_date = first_row['import_date']
        
        # Create invoice number
        invoice_num = f"INV-{entry_number[4:]}"
        
        # Calculate totals
        total_value = group['total_value'].sum()
        total_duty = group['duty_paid'].sum()
        
        # Create the PDF
        c = canvas.Canvas(f"test_documents/commercial_invoice_{entry_number}.pdf", pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 1*inch, "COMMERCIAL INVOICE")
        
        # Invoice details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, height - 1.5*inch, "Invoice Details:")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.75*inch, f"Invoice Number: {invoice_num}")
        c.drawString(1*inch, height - 2*inch, f"Entry Number: {entry_number}")
        c.drawString(1*inch, height - 2.25*inch, f"Date: {import_date}")
        c.drawString(1*inch, height - 2.5*inch, f"Importer: Test Company Inc.")
        c.drawString(1*inch, height - 2.75*inch, f"Importer ID: TEST12345")
        c.drawString(1*inch, height - 3*inch, f"Port Code: 2704")
        
        # Table header
        y = height - 3.5*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.5*inch, y, "Product Code")
        c.drawString(1.5*inch, y, "HTS Number")
        c.drawString(3*inch, y, "Description")
        c.drawString(4.5*inch, y, "Qty")
        c.drawString(5*inch, y, "Unit Price")
        c.drawString(6*inch, y, "Total")
        c.drawString(7*inch, y, "Duty Paid")
        
        # Draw line under header
        y -= 0.2*inch
        c.line(0.5*inch, y, 7.5*inch, y)
        
        # Table rows
        c.setFont("Helvetica", 10)
        for _, row in group.iterrows():
            y -= 0.3*inch
            if y < 1*inch:  # Start a new page if needed
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, height - 1*inch, "COMMERCIAL INVOICE (continued)")
                c.setFont("Helvetica", 10)
                y = height - 1.5*inch
                
            c.drawString(0.5*inch, y, str(row['product_code']))
            c.drawString(1.5*inch, y, str(row['hts_number']))
            c.drawString(3*inch, y, str(row['product_description'])[:20])
            c.drawString(4.5*inch, y, str(row['quantity']))
            c.drawString(5*inch, y, f"${row['unit_price']:.2f}")
            c.drawString(6*inch, y, f"${row['total_value']:.2f}")
            c.drawString(7*inch, y, f"${row['duty_paid']:.2f}")
        
        # Total
        y -= 0.5*inch
        c.line(0.5*inch, y + 0.2*inch, 7.5*inch, y + 0.2*inch)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(5.5*inch, y, f"Total Value: ${total_value:.2f}")
        y -= 0.25*inch
        c.drawString(5.5*inch, y, f"Total Duty Paid: ${total_duty:.2f}")
        
        # Footer with CBP-specific information
        y -= 0.75*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.5*inch, y, "U.S. Customs Information")
        c.setFont("Helvetica", 10)
        y -= 0.25*inch
        c.drawString(0.5*inch, y, "This merchandise qualifies for drawback under 19 U.S.C § 1313(j)(1)")
        y -= 0.25*inch
        c.drawString(0.5*inch, y, "All duties, taxes and fees were paid on the date of importation.")
        
        # Signature block
        y -= 0.5*inch
        c.drawString(0.5*inch, y, "Authorized Signature: _________________________")
        y -= 0.25*inch
        c.drawString(0.5*inch, y, "Name: Jane Tester")
        y -= 0.25*inch
        c.drawString(0.5*inch, y, "Title: Import Manager")
        y -= 0.25*inch
        c.drawString(0.5*inch, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        
        # Page footer
        c.setFont("Helvetica", 8)
        c.drawString(0.5*inch, 0.5*inch, f"Document generated for testing on {datetime.datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(0.5*inch, 0.4*inch, "This document contains information for CBP Form 7551 testing purposes.")
        
        c.save()
        
        print(f"Created commercial invoice: test_documents/commercial_invoice_{entry_number}.pdf")

def create_realistic_export_data(import_df, num_records=None):
    """Create realistic export data that matches import data"""
    
    if num_records is None:
        num_records = len(import_df)
    
    # Use product codes from imports
    product_codes = import_df['product_code'].unique()
    
    # Create export dates that are after import dates
    min_import_date = pd.to_datetime(import_df['import_date']).min()
    max_export_lag = (datetime.datetime.now() - min_import_date).days - 30  # Allow 30 days buffer
    
    data = {
        'reference_number': [],
        'export_date': [],
        'product_code': [],
        'quantity': [],
        'destination': [],
        'export_value': []
    }
    
    # Generate up to 3 different export shipments
    export_shipments = []
    for i in range(min(3, num_records // 3 + 1)):
        ref_num = f"EXP-{random.randint(10000000, 99999999)}"
        export_date = min_import_date + datetime.timedelta(days=random.randint(30, max(31, max_export_lag)))
        export_shipments.append((ref_num, export_date))
    
    destinations = ["Canada", "Mexico", "EU", "UK", "Japan", "Australia", "Brazil", "South Korea"]
    
    # For each product in import, create an export record
    for code in product_codes:
        # Get import info
        import_rows = import_df[import_df['product_code'] == code]
        if len(import_rows) == 0:
            continue
            
        total_imported = import_rows['quantity'].sum()
        avg_price = import_rows['unit_price'].mean()
        
        # Randomize how much was exported (50-100% of imported)
        export_pct = random.uniform(0.5, 1.0)
        total_to_export = int(total_imported * export_pct)
        
        # Distribute across shipments
        remaining = total_to_export
        for ref_num, export_date in export_shipments:
            if remaining <= 0:
                break
                
            # Decide how much goes in this shipment
            if len(export_shipments) == 1:
                qty = remaining
            else:
                qty = random.randint(1, remaining)
                
            # Add slight premium for export value
            export_value = round(qty * avg_price * random.uniform(1.05, 1.15), 2)
            
            # Add to data
            data['reference_number'].append(ref_num)
            data['export_date'].append(export_date.strftime('%Y-%m-%d'))
            data['product_code'].append(code)
            data['quantity'].append(qty)
            data['destination'].append(random.choice(destinations))
            data['export_value'].append(export_value)
            
            remaining -= qty
    
    # Create DataFrame and save as CSV
    df = pd.DataFrame(data)
    csv_path = "test_data/realistic_exports.csv"
    df.to_csv(csv_path, index=False)
    print(f"Created realistic export data: {csv_path}")
    
    # Create export proof document
    create_export_proof_pdf(df)
    
    return df

def create_export_proof_pdf(export_df):
    """Create a realistic export proof PDF from export data"""
    
    # Group by reference number
    ref_groups = export_df.groupby('reference_number')
    
    for ref_number, group in ref_groups:
        # Get first row for date and other details
        first_row = group.iloc[0]
        export_date = first_row['export_date']
        
        # Calculate totals
        total_value = group['export_value'].sum()
        
        # Create the PDF
        c = canvas.Canvas(f"test_documents/export_proof_{ref_number}.pdf", pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 1*inch, "EXPORT PROOF DOCUMENT")
        
        # Export details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, height - 1.5*inch, "Export Details:")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.75*inch, f"Reference Number: {ref_number}")
        c.drawString(1*inch, height - 2*inch, f"Export Date: {export_date}")
        c.drawString(1*inch, height - 2.25*inch, f"Exporter: Test Company Inc.")
        c.drawString(1*inch, height - 2.5*inch, f"CBP Export ID: EXP12345")
        
        # Add a destination if all items have the same destination
        destinations = group['destination'].unique()
        if len(destinations) == 1:
            c.drawString(1*inch, height - 2.75*inch, f"Destination: {destinations[0]}")
        
        # Table header
        y = height - 3.25*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Product Code")
        c.drawString(2.5*inch, y, "Quantity")
        c.drawString(3.5*inch, y, "Destination")
        c.drawString(5*inch, y, "Value")
        
        # Draw line under header
        y -= 0.2*inch
        c.line(1*inch, y, 7*inch, y)
        
        # Table rows
        c.setFont("Helvetica", 10)
        for _, row in group.iterrows():
            y -= 0.3*inch
            if y < 1*inch:  # Start a new page if needed
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, height - 1*inch, "EXPORT PROOF DOCUMENT (continued)")
                c.setFont("Helvetica", 10)
                y = height - 1.5*inch
                
            c.drawString(1*inch, y, str(row['product_code']))
            c.drawString(2.5*inch, y, str(row['quantity']))
            c.drawString(3.5*inch, y, str(row['destination']))
            c.drawString(5*inch, y, f"${row['export_value']:.2f}")
        
        # Total
        y -= 0.5*inch
        c.line(1*inch, y + 0.2*inch, 7*inch, y + 0.2*inch)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(4*inch, y, f"Total Export Value: ${total_value:.2f}")
        
        # Certificate of Export
        y -= 0.75*inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(width/2 - 1*inch, y, "CERTIFICATE OF EXPORT")
        
        y -= 0.5*inch
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, y, "This is to certify that the merchandise described above was exported from the United States")
        y -= 0.25*inch
        c.drawString(1*inch, y, f"on {export_date} and has not been returned to the United States.")
        
        # Drawback statement
        y -= 0.5*inch
        c.drawString(1*inch, y, "This merchandise qualifies for drawback under 19 U.S.C § 1313(j)(1).")
        
        # Signature block
        y -= 0.5*inch
        c.drawString(1*inch, y, "Authorized Signature: _________________________")
        y -= 0.25*inch
        c.drawString(1*inch, y, "Name: Jane Tester")
        y -= 0.25*inch
        c.drawString(1*inch, y, "Title: Export Manager")
        y -= 0.25*inch
        c.drawString(1*inch, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        
        # Official stamp placeholder
        y -= 0.75*inch
        c.circle(2*inch, y, 0.5*inch)
        c.drawString(1.5*inch, y, "STAMP")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 0.5*inch, f"Document generated for testing on {datetime.datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(1*inch, 0.4*inch, "This document contains information for CBP Form 7551 testing purposes.")
        
        c.save()
        
        print(f"Created export proof document: test_documents/export_proof_{ref_number}.pdf")

def create_billoflading_pdf(export_df):
    """Create a bill of lading PDF for the export shipments"""
    
    # Group by reference number
    ref_groups = export_df.groupby('reference_number')
    
    for ref_number, group in ref_groups:
        # Get first row for date and destination
        first_row = group.iloc[0]
        export_date = first_row['export_date']
        
        destinations = group['destination'].unique()
        destination = destinations[0] if len(destinations) == 1 else "Multiple Destinations"
        
        # Calculate totals
        total_qty = group['quantity'].sum()
        
        # Get a list of the product codes
        products = group['product_code'].unique()
        
        # Generate a BL number
        bl_number = f"BL-{random.randint(10000000, 99999999)}"
        
        # Create the PDF
        c = canvas.Canvas(f"test_documents/bill_of_lading_{ref_number}.pdf", pagesize=letter)
        width, height = letter
        
        # Header
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 1*inch, "BILL OF LADING")
        
        # BL details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, height - 1.5*inch, "Bill of Lading Details:")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.75*inch, f"B/L Number: {bl_number}")
        c.drawString(1*inch, height - 2*inch, f"Export Reference: {ref_number}")
        c.drawString(1*inch, height - 2.25*inch, f"Ship Date: {export_date}")
        
        # Shipper and Consignee
        y = height - 3*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Shipper:")
        c.setFont("Helvetica", 10)
        y -= 0.2*inch
        c.drawString(1*inch, y, "Test Company Inc.")
        y -= 0.2*inch
        c.drawString(1*inch, y, "123 Test Street")
        y -= 0.2*inch
        c.drawString(1*inch, y, "Testville, TS 12345")
        y -= 0.2*inch
        c.drawString(1*inch, y, "United States")
        
        y = height - 3*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(4.5*inch, y, "Consignee:")
        c.setFont("Helvetica", 10)
        y -= 0.2*inch
        c.drawString(4.5*inch, y, f"International Buyer - {destination}")
        y -= 0.2*inch
        c.drawString(4.5*inch, y, "Foreign Address Line 1")
        y -= 0.2*inch
        c.drawString(4.5*inch, y, "Foreign Address Line 2")
        y -= 0.2*inch
        c.drawString(4.5*inch, y, f"{destination}")
        
        # Cargo information
        y -= 0.5*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Cargo Information:")
        
        # Draw a box around cargo details
        box_top = y - 0.25*inch
        box_height = 2*inch
        c.rect(1*inch, box_top - box_height, 6*inch, box_height)
        
        y = box_top - 0.3*inch
        c.setFont("Helvetica", 10)
        c.drawString(1.2*inch, y, f"Total Packages: {len(products)}")
        y -= 0.25*inch
        c.drawString(1.2*inch, y, f"Total Quantity: {total_qty} units")
        y -= 0.25*inch
        c.drawString(1.2*inch, y, f"Description: Export merchandise for {destination}")
        y -= 0.25*inch
        
        # List some products
        c.drawString(1.2*inch, y, "Products: " + ", ".join(products[:3]))
        if len(products) > 3:
            y -= 0.25*inch
            c.drawString(1.2*inch, y, "and others...")
        
        # Terms and declarations
        y = box_top - box_height - 0.5*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Terms and Declarations:")
        
        y -= 0.3*inch
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, y, "This is to certify that the above-named materials are properly classified,")
        y -= 0.2*inch
        c.drawString(1*inch, y, "described, packaged, marked and labeled, and are in proper condition for")
        y -= 0.2*inch
        c.drawString(1*inch, y, "transportation according to applicable regulations.")
        
        # Signature blocks
        y -= 0.5*inch
        c.line(1*inch, y, 3.5*inch, y)
        c.line(4.5*inch, y, 7*inch, y)
        
        y -= 0.2*inch
        c.drawString(1*inch, y, "Shipper Signature")
        c.drawString(4.5*inch, y, "Carrier Signature")
        
        y -= 0.3*inch
        c.drawString(1*inch, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(4.5*inch, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 0.5*inch, f"Document generated for testing on {datetime.datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(1*inch, 0.4*inch, "This document contains information for CBP Form 7551 testing purposes.")
        
        c.save()
        
        print(f"Created bill of lading: test_documents/bill_of_lading_{ref_number}.pdf")

class TestDocumentGenerator:
    def __init__(self, company_name=None):
        self.company_name = company_name or fake.company()
        self.company_address = fake.address()
        self.company_ein = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
        
    def generate_import_entry_summary(self, entry_number=None):
        """Generate a realistic CBP Form 7501 (Entry Summary) for imports"""
        if not entry_number:
            entry_number = f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}-{random.randint(0, 9)}"
            
        port_code, port_name = random.choice(list(CUSTOMS_PORTS.items()))
        
        # Create consistent dates (import date should be before export date)
        import_date = fake.date_between(start_date='-1y', end_date='-30d')
        
        # Generate between 1-5 line items
        line_items = []
        total_value = 0
        total_duty = 0
        
        for i in range(random.randint(1, 5)):
            hts_code, description = random.choice(list(HTS_CODES.items()))
            quantity = random.randint(100, 1000)
            unit_price = round(random.uniform(5, 500), 2)
            value = round(quantity * unit_price, 2)
            duty_rate = round(random.uniform(0.025, 0.1), 3)
            duty_amount = round(value * duty_rate, 2)
            
            line_items.append({
                "line_number": i+1,
                "hts_code": hts_code,
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "value": value,
                "duty_rate": duty_rate,
                "duty_amount": duty_amount
            })
            
            total_value += value
            total_duty += duty_amount
        
        # Create a dictionary with all the entry summary data
        entry_data = {
            "entry_number": entry_number,
            "entry_type": "01 - Consumption",
            "port_code": port_code,
            "port_name": port_name,
            "import_date": import_date.strftime("%m/%d/%Y"),
            "importer": self.company_name,
            "importer_address": self.company_address,
            "importer_ein": self.company_ein,
            "manufacturer": fake.company(),
            "manufacturer_address": fake.address(),
            "vessel_name": random.choice(VESSEL_NAMES),
            "bill_of_lading": f"BL{random.randint(10000000, 99999999)}",
            "line_items": line_items,
            "total_value": total_value,
            "total_duty": total_duty
        }
        
        # Generate the PDF
        self._generate_entry_summary_pdf(entry_data)
        
        return entry_data
    
    def generate_export_documentation(self, related_import_entry=None):
        """Generate export documentation related to a previous import"""
        if related_import_entry:
            # Use the same products as the import, but with potentially different quantities
            import_items = related_import_entry["line_items"]
            
            # Export date should be after import date
            import_date = datetime.datetime.strptime(related_import_entry["import_date"], "%m/%d/%Y")
            export_date = fake.date_between(start_date=import_date, end_date='+180d')
            
            # Create export documentation with the same products
            export_items = []
            for item in import_items:
                # Use 70-100% of the imported quantity
                export_quantity = int(item["quantity"] * random.uniform(0.7, 1.0))
                
                export_items.append({
                    "description": item["description"],
                    "hts_code": item["hts_code"],
                    "quantity": export_quantity,
                    "unit_price": item["unit_price"], 
                    "value": round(export_quantity * item["unit_price"], 2)
                })
            
            export_doc = {
                "exporter": self.company_name,
                "exporter_address": self.company_address,
                "export_date": export_date.strftime("%m/%d/%Y"),
                "port_of_export": random.choice(list(CUSTOMS_PORTS.values())),
                "destination": fake.country(),
                "transport_method": random.choice(["Vessel", "Air", "Truck"]),
                "carrier": random.choice(SHIPPING_CARRIERS),
                "items": export_items,
                "related_import_entry": related_import_entry["entry_number"]
            }
            
            # Generate the export PDF
            self._generate_export_documentation_pdf(export_doc)
            
            return export_doc
        else:
            # Generate standalone export documentation
            return self._generate_standalone_export_doc()
    
    def _generate_entry_summary_pdf(self, entry_data):
        """Generate a PDF of the Entry Summary (7501)"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "U.S. Customs and Border Protection", 0, 1, "C")
        pdf.cell(0, 10, "ENTRY SUMMARY (CBP Form 7501)", 0, 1, "C")
        
        # Entry details section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Entry Details", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Entry Number: {entry_data['entry_number']}", 0, 1)
        pdf.cell(0, 8, f"Entry Type: {entry_data['entry_type']}", 0, 1)
        pdf.cell(0, 8, f"Port of Entry: {entry_data['port_code']} - {entry_data['port_name']}", 0, 1)
        pdf.cell(0, 8, f"Import Date: {entry_data['import_date']}", 0, 1)
        pdf.cell(0, 8, f"Vessel/Carrier: {entry_data['vessel_name']}", 0, 1)
        pdf.cell(0, 8, f"Bill of Lading: {entry_data['bill_of_lading']}", 0, 1)
        
        # Importer section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Importer Information", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Importer: {entry_data['importer']}", 0, 1)
        pdf.cell(0, 8, f"Importer EIN: {entry_data['importer_ein']}", 0, 1)
        pdf.multi_cell(0, 8, f"Address: {entry_data['importer_address']}")
        
        # Manufacturer section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Manufacturer Information", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Manufacturer: {entry_data['manufacturer']}", 0, 1)
        pdf.multi_cell(0, 8, f"Address: {entry_data['manufacturer_address']}")
        
        # Line items section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Merchandise Details", 0, 1)
        
        # Table header
        pdf.set_font("Arial", "B", 8)
        pdf.cell(10, 8, "Line", 1)
        pdf.cell(25, 8, "HTS Code", 1)
        pdf.cell(55, 8, "Description", 1)
        pdf.cell(20, 8, "Quantity", 1)
        pdf.cell(20, 8, "Unit Price", 1)
        pdf.cell(25, 8, "Value", 1)
        pdf.cell(20, 8, "Duty Rate", 1)
        pdf.cell(25, 8, "Duty Amount", 1, 1)
        
        # Table content
        pdf.set_font("Arial", "", 8)
        for item in entry_data['line_items']:
            pdf.cell(10, 8, str(item['line_number']), 1)
            pdf.cell(25, 8, item['hts_code'], 1)
            pdf.cell(55, 8, item['description'][:30], 1)
            pdf.cell(20, 8, str(item['quantity']), 1)
            pdf.cell(20, 8, f"${item['unit_price']:.2f}", 1)
            pdf.cell(25, 8, f"${item['value']:.2f}", 1)
            pdf.cell(20, 8, f"{item['duty_rate']:.1%}", 1)
            pdf.cell(25, 8, f"${item['duty_amount']:.2f}", 1, 1)
        
        # Totals
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 8, "", 0)
        pdf.cell(25, 8, "Total Value:", 0)
        pdf.cell(45, 8, f"${entry_data['total_value']:.2f}", 0, 1)
        pdf.cell(130, 8, "", 0)
        pdf.cell(25, 8, "Total Duty:", 0)
        pdf.cell(45, 8, f"${entry_data['total_duty']:.2f}", 0, 1)
        
        # Save the PDF
        filename = f"test_documents/import_entry_{entry_data['entry_number'].replace('-', '_')}.pdf"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf.output(filename)
        print(f"Generated import entry summary: {filename}")
    
    def _generate_export_documentation_pdf(self, export_data):
        """Generate a PDF of export documentation"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "EXPORT DOCUMENTATION", 0, 1, "C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SHIPPER'S EXPORT DECLARATION", 0, 1, "C")
        
        # Export details
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, "Export Details", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Exporter: {export_data['exporter']}", 0, 1)
        pdf.multi_cell(0, 8, f"Address: {export_data['exporter_address']}")
        pdf.cell(0, 8, f"Date of Export: {export_data['export_date']}", 0, 1)
        pdf.cell(0, 8, f"Port of Export: {export_data['port_of_export']}", 0, 1)
        pdf.cell(0, 8, f"Destination: {export_data['destination']}", 0, 1)
        pdf.cell(0, 8, f"Transport Method: {export_data['transport_method']}", 0, 1)
        pdf.cell(0, 8, f"Carrier: {export_data['carrier']}", 0, 1)
        
        if 'related_import_entry' in export_data:
            pdf.cell(0, 8, f"Related Import Entry: {export_data['related_import_entry']}", 0, 1)
        
        # Items table
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, "Merchandise Details", 0, 1)
        
        # Table header
        pdf.set_font("Arial", "B", 8)
        pdf.cell(60, 8, "Description", 1)
        pdf.cell(30, 8, "HTS Code", 1)
        pdf.cell(30, 8, "Quantity", 1)
        pdf.cell(30, 8, "Unit Price", 1)
        pdf.cell(40, 8, "Value", 1, 1)
        
        # Table content
        pdf.set_font("Arial", "", 8)
        total_value = 0
        for item in export_data['items']:
            pdf.cell(60, 8, item['description'][:35], 1)
            pdf.cell(30, 8, item['hts_code'], 1)
            pdf.cell(30, 8, str(item['quantity']), 1)
            pdf.cell(30, 8, f"${item['unit_price']:.2f}", 1)
            pdf.cell(40, 8, f"${item['value']:.2f}", 1, 1)
            total_value += item['value']
        
        # Total
        pdf.set_font("Arial", "B", 10)
        pdf.cell(150, 8, "Total Value:", 0)
        pdf.cell(40, 8, f"${total_value:.2f}", 0, 1)
        
        # Save the PDF
        export_date_formatted = export_data['export_date'].replace('/', '_')
        filename = f"test_documents/export_doc_{export_date_formatted}.pdf"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf.output(filename)
        print(f"Generated export documentation: {filename}")

    def generate_complete_drawback_package(self, num_entries=3):
        """Generate a complete set of documents needed for a drawback claim"""
        import_entries = []
        export_docs = []
        
        # Generate import entries
        for _ in range(num_entries):
            import_entry = self.generate_import_entry_summary()
            import_entries.append(import_entry)
            
            # Generate matching export documentation
            export_doc = self.generate_export_documentation(import_entry)
            export_docs.append(export_doc)
        
        # Generate a summary spreadsheet of all entries for easy reference
        self._generate_drawback_summary(import_entries, export_docs)
        
        return {
            "import_entries": import_entries,
            "export_docs": export_docs
        }
    
    def _generate_drawback_summary(self, import_entries, export_docs):
        """Generate an Excel summary of all documents for the drawback claim"""
        summary_data = []
        
        for i, entry in enumerate(import_entries):
            export = export_docs[i]
            
            for imp_item in entry["line_items"]:
                # Find the matching export item
                exp_item = next((item for item in export["items"] if item["hts_code"] == imp_item["hts_code"]), None)
                
                if exp_item:
                    summary_data.append({
                        "Import Entry": entry["entry_number"],
                        "Import Date": entry["import_date"],
                        "Export Date": export["export_date"],
                        "HTS Code": imp_item["hts_code"],
                        "Description": imp_item["description"],
                        "Imported Qty": imp_item["quantity"],
                        "Exported Qty": exp_item["quantity"],
                        "Unit Price": imp_item["unit_price"],
                        "Import Value": imp_item["value"],
                        "Export Value": exp_item["value"],
                        "Duty Rate": imp_item["duty_rate"],
                        "Duty Paid": imp_item["duty_amount"],
                        "Potential Refund": round(imp_item["duty_amount"] * (exp_item["quantity"] / imp_item["quantity"]), 2)
                    })
        
        # Create a pandas DataFrame and export to Excel
        df = pd.DataFrame(summary_data)
        filename = f"test_documents/drawback_summary_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Generated drawback summary: {filename}")

def run_enhanced_test():
    """Main function to create all test documents"""
    print("Creating enhanced test documents for CBP Form 7551...")
    
    # Create import data
    import_df = create_realistic_import_data(num_records=15)
    
    # Create matching export data
    export_df = create_realistic_export_data(import_df)
    
    # Create bill of lading
    create_billoflading_pdf(export_df)
    
    print("\nAll test documents created successfully!")
    print("The following files are available for testing:")
    print("1. CSV Data:")
    print("   - test_data/realistic_imports.csv")
    print("   - test_data/realistic_exports.csv")
    print("2. Sample Documents:")
    for file in os.listdir("test_documents"):
        if file.endswith(".pdf"):
            print(f"   - test_documents/{file}")
    
    print("\nTo test form filling with this data, run:")
    print("python test_direct_form_filling.py")

def run_comprehensive_test(num_entries=3, fill_form=True, take_screenshot=True):
    """
    Comprehensive test function that combines functionality from other test scripts.
    This replaces the need for separate test_pdf_filling.py, test_pdf.py, and create_sample_documents.py
    
    Parameters:
    - num_entries: Number of import entries to generate
    - fill_form: Whether to fill a CBP Form 7551 with the generated test data
    - take_screenshot: Whether to take screenshots of the filled form
    
    Returns:
    - Dictionary with paths to generated files
    """
    print("=== Running Comprehensive PDF Generation Test ===")
    results = {}
    
    # Add current date to results
    results['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Make sure output directories exist
    for directory in ['test_documents', 'test_data', 'filled_forms', 'screenshots']:
        os.makedirs(directory, exist_ok=True)
    
    # Step 1: Generate test documents using the TestDocumentGenerator
    print("\nGenerating test documents...")
    company_name = "Acme Test Trading, Inc."
    generator = TestDocumentGenerator(company_name)
    
    # Create a test package with import entries and matching exports
    print("Creating drawback package...")
    package = generator.generate_complete_drawback_package(num_entries=num_entries)
    results['package'] = package
    
    # Step 2: Create realistic import/export data (CSV)
    print("\nGenerating realistic import/export CSV data...")
    import_df = create_realistic_import_data(num_records=15)
    export_df = create_realistic_export_data(import_df)
    
    # Save dataframes to CSV
    import_csv = "test_data/comprehensive_imports.csv"
    export_csv = "test_data/comprehensive_exports.csv"
    import_df.to_csv(import_csv, index=False)
    export_df.to_csv(export_csv, index=False)
    results['import_csv'] = import_csv
    results['export_csv'] = export_csv
    
    print(f"Generated import data: {import_csv}")
    print(f"Generated export data: {export_csv}")
    
    # Step 3: Fill form if requested
    if fill_form:
        try:
            from pdf_generator import fill_drawback_form
            
            print("\nFilling CBP Form 7551...")
            # Create company info for form filling
            company_info = {
                "name": company_name,
                "address": "123 Trade Avenue, Suite 100",
                "city_state_zip": "Import City, CA 90001",
                "contact_name": "John Trader",
                "phone": "(555) 123-4567",
                "email": "john@acmetest.com",
                "importer_number": generator.company_ein
            }
            
            # Use the direct form filling method
            try:
                filled_form_path = fill_drawback_form(
                    package['import_entries'],
                    package['export_docs'],
                    company_info
                )
                results['filled_form'] = filled_form_path
                print(f"Form successfully filled: {filled_form_path}")
                
                # Take screenshot of filled form if requested
                if take_screenshot:
                    screenshot_path = capture_pdf_screenshot(filled_form_path, "screenshots/filled_form.png")
                    results['screenshot'] = screenshot_path
                    
                    # Analyze form fields to identify missing or incorrect fields
                    analysis_path = analyze_filled_form(filled_form_path, "screenshots/analysis_form.png")
                    results['analysis'] = analysis_path
                    
                    # Try to open the filled PDF with the default viewer
                    try:
                        import webbrowser
                        webbrowser.open(filled_form_path)
                        print(f"Opened filled form: {filled_form_path}")
                    except Exception as e:
                        print(f"Could not open filled form: {str(e)}")
            except Exception as e:
                print(f"Error filling form: {str(e)}")
                import traceback
                traceback.print_exc()
            
        except ImportError as e:
            print(f"Could not import form filling modules: {str(e)}")
    
    print("\nComprehensive test completed successfully!")
    return results

def create_realistic_form_data(package):
    """
    Create realistic form data based on the generated package
    
    Args:
        package: A dictionary containing import_entries and export_docs
        
    Returns:
        dict: Realistic form data for CBP Form 7551
    """
    # Extract data from the first import entry and export doc
    import_entry = package['import_entries'][0] if package['import_entries'] else None
    export_doc = package['export_docs'][0] if package['export_docs'] else None
    
    # Calculate total values
    total_duty_paid = 0
    total_value = 0
    for entry in package['import_entries']:
        for item in entry['line_items']:
            total_duty_paid += item['duty_amount']
            total_value += item['value']
    
    # Calculate drawback amount (99% of total duty paid)
    drawback_amount = round(total_duty_paid * 0.99, 2)
    
    # Create a realistic drawback entry number
    drawback_number = f"DB{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    # Format the claimant address
    claimant_address = "\n".join([
        "Acme Test Trading, Inc.",
        "123 Trade Avenue, Suite 100",
        "Import City, CA 90001"
    ])
    
    # Format preparer address
    preparer_address = "\n".join([
        "John Trader, Import Manager",
        "Acme Test Trading, Inc.",
        "123 Trade Avenue, Suite 100",
        "Import City, CA 90001",
        "(555) 123-4567"
    ])
    
    # Current date formatted for the form
    current_date = datetime.datetime.now().strftime('%m/%d/%Y')
    
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
                # If already in MM/DD/YYYY format, return as is
                if re.match(r'\d{2}/\d{2}/\d{4}', date_value):
                    return date_value
                # Just return as is if we can't parse it
                return date_value
        else:
            return ""
    
    # Create the form data with many more fields filled
    form_data = {
        # Header information
        'drawbacknumber': drawback_number,
        'portcode': '3901',
        'entrytypecode': '01',
        'claimantID': '12-3456789',
        'suretycode': '123',
        'bondtype': '9',
        'brokerID': 'BR123456',
        
        # Section 1: Basic claim info
        'NameandAddressOfClaimant': claimant_address,
        'TotalDrawbackClaimed': f"${drawback_amount:,.2f}",
        'MPFClaimed': f"${round(total_duty_paid * 0.01, 2):,.2f}",
        'drawbacksection': '1313(j)(1)',
        'acclerated': '/Yes',  # Checkbox for accelerated payment
        'manual': '/Yes',  # Manual filing checkbox
        
        # Section 2: Import information
        'ImportEntry1': import_entry['entry_number'] if import_entry else '',
        'PortCode1': import_entry.get('port_code', '3901') if import_entry else '',
        'ImportDate1': format_date(import_entry['import_date']) if import_entry else '',
        'HTSUS1': import_entry['line_items'][0]['hts_code'] if import_entry and import_entry['line_items'] else '',
        'Descrip1': import_entry['line_items'][0]['description'] if import_entry and import_entry['line_items'] else '',
        'Quantity1': str(import_entry['line_items'][0]['quantity']) if import_entry and import_entry['line_items'] else '',
        'Value1': f"${import_entry['line_items'][0]['value']:,.2f}" if import_entry and import_entry['line_items'] else '',
        'Duty1': f"${import_entry['line_items'][0]['duty_amount']:,.2f}" if import_entry and import_entry['line_items'] else '',
        'Duty99_1': f"${import_entry['line_items'][0]['duty_amount'] * 0.99:,.2f}" if import_entry and import_entry['line_items'] else '',
        
        # Add more import entries if available
        'ImportEntry2': package['import_entries'][1]['entry_number'] if len(package['import_entries']) > 1 else '',
        'PortCode2': package['import_entries'][1].get('port_code', '3901') if len(package['import_entries']) > 1 else '',
        'ImportDate2': format_date(package['import_entries'][1]['import_date']) if len(package['import_entries']) > 1 else '',
        'HTSUS2_ds_1': package['import_entries'][1]['line_items'][0]['hts_code'] if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        'Descrip2': package['import_entries'][1]['line_items'][0]['description'] if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        'Quantity2_p0': str(package['import_entries'][1]['line_items'][0]['quantity']) if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        'Value2': f"${package['import_entries'][1]['line_items'][0]['value']:,.2f}" if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        'Duty2': f"${package['import_entries'][1]['line_items'][0]['duty_amount']:,.2f}" if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        'Duty99_2': f"${package['import_entries'][1]['line_items'][0]['duty_amount'] * 0.99:,.2f}" if len(package['import_entries']) > 1 and package['import_entries'][1]['line_items'] else '',
        
        'ImportEntry3': package['import_entries'][2]['entry_number'] if len(package['import_entries']) > 2 else '',
        'PortCode3': package['import_entries'][2].get('port_code', '3901') if len(package['import_entries']) > 2 else '',
        'ImportDate3': format_date(package['import_entries'][2]['import_date']) if len(package['import_entries']) > 2 else '',
        'HTSUS3_ds_2': package['import_entries'][2]['line_items'][0]['hts_code'] if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        'Descrip3': package['import_entries'][2]['line_items'][0]['description'] if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        'Quantity3_p0': str(package['import_entries'][2]['line_items'][0]['quantity']) if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        'Value3': f"${package['import_entries'][2]['line_items'][0]['value']:,.2f}" if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        'Duty3': f"${package['import_entries'][2]['line_items'][0]['duty_amount']:,.2f}" if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        'Duty99_3': f"${package['import_entries'][2]['line_items'][0]['duty_amount'] * 0.99:,.2f}" if len(package['import_entries']) > 2 and package['import_entries'][2]['line_items'] else '',
        
        # Section 3: Delivery information
        'CD1': 'X',  # Consumed code
        'DateReceived1': format_date(import_entry['import_date']) if import_entry else '',
        'DateUsed1': format_date((datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')) if import_entry else '',
        
        # Section 4: Export information (if available)
        'Date39_1': format_date(export_doc['export_date']) if export_doc else '',
        'ActionCode1': '2',  # Export code
        'UniqueID1': export_doc.get('export_ref', 'EXP123456') if export_doc else '',
        'NameofExporter1': 'Acme Test Trading, Inc.',
        'DescripofArticle1': export_doc['items'][0]['description'] if export_doc and export_doc['items'] else '',
        'Quantity1_p1_n7': str(export_doc['items'][0]['quantity']) if export_doc and export_doc['items'] else '',
        'Export1': export_doc.get('destination', 'Canada') if export_doc else '',
        
        # Certification
        'printedname': 'John Trader',
        'Date500': current_date,
        
        # Preparer information
        'NameandAddressofPreparer': preparer_address,
        
        # Section 2: HTSUS/description related to import line items
        'description': 'Identical unused merchandise exported within 3 years of import',
        
        # Options and checkboxes 
        'option1': '/Yes',
        'corporation': '/Yes',
        
        # Additional dates and totals
        'Date': current_date,
        'total_p0': f"${total_value:,.2f}",
        'total_p1': f"${drawback_amount:,.2f}"
    }
    
    return form_data

def capture_pdf_screenshot(pdf_path, output_path):
    """
    Capture a screenshot of a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the screenshot
        
    Returns:
        str: Path to the screenshot
    """
    try:
        # Use a more robust approach to capture PDF screenshots
        print(f"Creating screenshot of {pdf_path}...")
        
        # For PyMuPDF errors, try a direct approach with reportlab
        try:
            # First try PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Determine the number of pages
            num_pages = len(doc)
            
            # Create a figure to hold all pages
            fig, axes = plt.subplots(num_pages, 1, figsize=(8.5, 11 * num_pages))
            
            # Handle the case of a single page
            if num_pages == 1:
                axes = [axes]
            
            # Add each page to the figure
            for i, page in enumerate(doc):
                # Render page to an image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # higher resolution
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                # Add to the figure
                axes[i].imshow(img)
                axes[i].axis('off')
                axes[i].set_title(f"Page {i+1}")
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            # If PyMuPDF fails, try a different approach
            print(f"PyMuPDF error: {str(e)}")
            
            # Use ImageMagick if available
            try:
                import subprocess
                result = subprocess.run(['convert', '-density', '150', pdf_path, output_path], 
                                      check=True, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    print(f"Used ImageMagick to create screenshot")
                else:
                    print(f"ImageMagick error: {result.stderr.decode('utf-8')}")
                    # Create a placeholder image with error message
                    create_error_image(output_path, f"Error capturing PDF: {str(e)}")
            except Exception as img_error:
                print(f"ImageMagick not available: {str(img_error)}")
                # Create a placeholder image with error message
                create_error_image(output_path, f"Error capturing PDF: {str(e)}")
        
        print(f"Screenshot saved to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        # Create a placeholder image
        create_error_image(output_path, f"Error capturing PDF: {str(e)}")
        return output_path

def create_error_image(output_path, error_message):
    """Create a placeholder image with error message"""
    # Create a simple error image
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.text(0.5, 0.5, error_message, ha='center', va='center', wrap=True)
    ax.axis('off')
    plt.savefig(output_path)
    plt.close(fig)
    print(f"Created error placeholder image: {output_path}")

def analyze_filled_form(pdf_path, output_path):
    """
    Analyze filled form fields and create an annotated version
    
    Args:
        pdf_path: Path to the filled PDF form
        output_path: Path to save the annotated form
        
    Returns:
        str: Path to the annotated form
    """
    try:
        print(f"Analyzing form fields in {pdf_path}...")
        
        # Get field names using PyPDF2 instead of pdfrw
        from PyPDF2 import PdfReader
        pdf = PdfReader(pdf_path)
        
        # Dictionary to store filled and empty fields
        fields_status = {'filled': [], 'empty': []}
        
        # Check each page for fields
        form_fields = pdf.get_fields()
        if form_fields:
            for field_name, field in form_fields.items():
                # Get the field value
                field_value = field.get('/V', '')
                
                # Determine if field has a value (handle different types of values)
                has_value = False
                if field_value:
                    if isinstance(field_value, str):
                        has_value = len(field_value.strip()) > 0
                    else:
                        has_value = True
                
                # Assume field is on first page for simplicity
                page_num = 1
                
                if has_value:
                    fields_status['filled'].append((field_name, f"Page {page_num}"))
                else:
                    fields_status['empty'].append((field_name, f"Page {page_num}"))
        
        # Create a screenshot of the PDF
        screenshot_path = capture_pdf_screenshot(pdf_path, output_path)
        
        # Create a text summary
        with open(output_path.replace(".png", ".txt"), "w") as f:
            f.write(f"Analysis of {pdf_path}\n")
            f.write(f"Total fields detected: {len(fields_status['filled']) + len(fields_status['empty'])}\n")
            f.write(f"Filled fields: {len(fields_status['filled'])}\n")
            f.write(f"Empty fields: {len(fields_status['empty'])}\n\n")
            
            f.write("Filled fields:\n")
            for field_name, page_info in fields_status['filled']:
                f.write(f"  - {field_name} ({page_info})\n")
            
            f.write("\nEmpty fields:\n")
            for field_name, page_info in fields_status['empty']:
                f.write(f"  - {field_name} ({page_info})\n")
        
        print(f"Analysis saved to {output_path}")
        print(f"Text summary saved to {output_path.replace('.png', '.txt')}")
        
        return output_path
    
    except Exception as e:
        print(f"Error analyzing form: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Still create a screenshot even if analysis fails
        screenshot_path = capture_pdf_screenshot(pdf_path, output_path)
        
        # Create a basic error report
        with open(output_path.replace(".png", ".txt"), "w") as f:
            f.write(f"Error analyzing {pdf_path}: {str(e)}\n")
            f.write("Please check if the PDF has proper form fields.\n")
        
        return output_path

if __name__ == "__main__":
    generator = TestDocumentGenerator("Acme Global Traders, Inc.")
    package = generator.generate_complete_drawback_package(5)
    run_enhanced_test()
    
    # Uncomment to run the comprehensive test
    # results = run_comprehensive_test() 