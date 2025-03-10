from PyPDF2 import PdfReader, PdfWriter
import os
import datetime
from io import BytesIO

def fill_form_with_pypdf2(template_path, output_path, field_data):
    """Fill PDF form using PyPDF2"""
    # Read the PDF
    reader = PdfReader(template_path)
    writer = PdfWriter()
    
    # Copy all pages from the template
    for page in reader.pages:
        writer.add_page(page)
    
    # Update form fields
    writer.update_page_form_field_values(
        writer.pages[0], field_data
    )
    
    # Write the filled PDF to a file
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    
    return output_path

# Example usage
if __name__ == "__main__":
    template_path = "templates/cbp form 7551.pdf"
    output_path = f"filled_forms/filled_form_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Example data to fill in the form
    field_data = {
        "drawbacknumber": "TEST-12345",
        "NameandAddressOfClaimant": "Test Company Inc.\n123 Main St\nAnytown, CA 12345",
        # Add more fields as needed
    }
    
    fill_form_with_pypdf2(template_path, output_path, field_data)
    print(f"Form filled and saved to: {output_path}") 