import os
import sys

def list_form_fields(pdf_path):
    """List all form fields in a PDF with detailed information using PyPDF2"""
    try:
        # Try using PyPDF2 instead of pdfrw
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_path)
        print(f"Analyzing PDF: {pdf_path}")
        print(f"Total pages: {len(reader.pages)}")
        
        fields = reader.get_fields()
        
        if fields:
            print("\nForm Fields Found:")
            for field_name, field_obj in fields.items():
                print(f"  Field: {field_name}")
                if hasattr(field_obj, '/FT'):
                    print(f"    Type: {field_obj['/FT']}")
                print(f"    Value: {field_obj.get('/V', '')}")
                if hasattr(field_obj, '/Rect'):
                    print(f"    Rectangle: {field_obj['/Rect']}")
            
            print(f"\nTotal form fields found: {len(fields)}")
            return fields
        else:
            print("No form fields found in the document.")
            return {}
            
    except ImportError:
        print("PyPDF2 not found. Trying pdfrw approach...")
        try:
            import pdfrw
            pdf = pdfrw.PdfReader(pdf_path)
            fields = {}
            
            print(f"Analyzing PDF: {pdf_path}")
            print(f"Total pages: {len(pdf.pages)}")
            
            for page_idx, page in enumerate(pdf.pages):
                print(f"\nPage {page_idx + 1}:")
                
                if hasattr(page, 'Annots') and page.Annots:
                    annotations = page.Annots
                    print(f"  Found {len(annotations)} annotations")
                    
                    for idx, annot in enumerate(annotations):
                        if annot is None:
                            continue
                            
                        try:
                            field_name = str(annot.get('/T', ''))
                            if not field_name:
                                continue
                                
                            # Safer access to annotation properties
                            field_type = "Unknown"
                            if '/FT' in annot:
                                field_type = str(annot['/FT'])
                                
                            field_value = ""
                            if '/V' in annot:
                                field_value = str(annot['/V'])
                                
                            field_rect = []
                            if '/Rect' in annot:
                                field_rect = [float(x) for x in annot['/Rect']]
                            
                            fields[field_name] = {
                                'page': page_idx + 1,
                                'type': field_type,
                                'value': field_value,
                                'rect': field_rect,
                                'index': idx
                            }
                            
                            print(f"  Field: {field_name}")
                            print(f"    Type: {field_type}")
                            print(f"    Value: {field_value}")
                            print(f"    Rectangle: {field_rect}")
                            
                        except Exception as e:
                            print(f"  Error processing annotation {idx}: {e}")
                else:
                    print("  No form fields found on this page")
            
            print(f"\nTotal form fields found: {len(fields)}")
            return fields
            
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return {}
    
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return {}

if __name__ == "__main__":
    template_path = os.path.join(os.path.dirname(__file__), 'templates/cbp form 7551.pdf')
    if os.path.exists(template_path):
        try:
            fields = list_form_fields(template_path)
            if fields:
                print(f"\nTotal form fields found: {len(fields)}")
        except Exception as e:
            print(f"Failed to analyze PDF: {e}")
    else:
        print(f"Template not found at: {template_path}") 