import fitz  # PyMuPDF
import os

def inspect_pdf_form(pdf_path):
    """Inspect PDF form fields using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        print(f"PDF: {pdf_path}")
        print(f"Pages: {len(doc)}")
        
        form_fields = []
        field_count = 0
        
        # Loop through pages
        for page_num, page in enumerate(doc):
            print(f"\nPage {page_num + 1}:")
            
            # Get form fields on this page
            fields = page.widgets()
            if fields:
                print(f"  Found {len(fields)} form fields")
                for i, field in enumerate(fields):
                    field_count += 1
                    
                    # Get properties
                    field_name = field.field_name
                    field_type = field.field_type
                    field_type_name = field.field_type_string
                    field_value = field.field_value
                    field_rect = field.rect
                    
                    form_fields.append({
                        'name': field_name,
                        'type': field_type_name,
                        'value': field_value,
                        'rect': [field_rect.x0, field_rect.y0, field_rect.x1, field_rect.y1],
                        'page': page_num + 1
                    })
                    
                    print(f"  Field #{field_count}: {field_name}")
                    print(f"    Type: {field_type_name} ({field_type})")
                    print(f"    Value: {field_value}")
                    print(f"    Rectangle: [{field_rect.x0}, {field_rect.y0}, {field_rect.x1}, {field_rect.y1}]")
            else:
                print("  No form fields found on this page")
        
        print(f"\nTotal form fields found: {field_count}")
        return form_fields
    
    except Exception as e:
        print(f"Error inspecting PDF: {e}")
        return []

if __name__ == "__main__":
    template_path = os.path.join(os.path.dirname(__file__), 'templates/cbp form 7551.pdf')
    if os.path.exists(template_path):
        fields = inspect_pdf_form(template_path)
    else:
        print(f"Template not found at: {template_path}") 