from pdfrw import PdfReader
import sys

def get_pdf_field_names(pdf_path):
    """Extract all field names from a PDF form"""
    # Read the PDF
    pdf = PdfReader(pdf_path)
    
    # Initialize a list to store field names
    field_names = []
    
    # Iterate through each page
    for page_idx, page in enumerate(pdf.pages):
        if page.Annots:
            for annotation in page.Annots:
                if annotation.Subtype == '/Widget' and hasattr(annotation, '/T'):
                    # Extract the field name (remove parentheses)
                    field_name = annotation['/T'][1:-1]
                    field_names.append((field_name, f"Page {page_idx+1}"))
    
    return field_names

if __name__ == "__main__":
    pdf_path = "templates/cbp form 7551.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    field_names = get_pdf_field_names(pdf_path)
    
    print(f"Found {len(field_names)} form fields in {pdf_path}:")
    for name, page in sorted(field_names):
        print(f"  - {name} ({page})") 