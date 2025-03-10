#!/usr/bin/env python3
"""
Script to check PDF form fields using PyPDF2
"""

import os
import sys
from PyPDF2 import PdfReader

def extract_pdf_fields(pdf_path):
    """Extract PDF form fields using PyPDF2"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        return None
    
    try:
        reader = PdfReader(pdf_path)
        print(f"PDF has {len(reader.pages)} pages")
        
        fields = reader.get_fields()
        
        if fields:
            print(f"Found {len(fields)} form fields:")
            for i, (name, field) in enumerate(fields.items()):
                field_type = field.get('/FT', 'Unknown')
                value = field.get('/V', '')
                print(f"{i+1}. {name} (Type: {field_type}, Value: {value})")
        else:
            print("No form fields found. The PDF may be a flattened form or not a fillable form.")
            
            # Let's try an alternative approach checking for AcroForm
            root = reader.trailer.get('/Root')
            if root and '/AcroForm' in root:
                acroform = root['/AcroForm']
                if '/Fields' in acroform:
                    print(f"AcroForm detected with {len(acroform['/Fields'])} fields")
                    # But the fields may not be accessible through get_fields()
                    
        # Check annotations as an alternative way to detect form fields
        has_widget_annotations = False
        for page_num, page in enumerate(reader.pages):
            if page.get('/Annots'):
                annotations = page['/Annots']
                for i, annot in enumerate(annotations):
                    if annot.get('/Subtype') == '/Widget':
                        has_widget_annotations = True
                        print(f"Page {page_num+1} has Widget annotations (potential form fields)")
                        break
                if has_widget_annotations:
                    break
        
        return fields
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_pdf_fields.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_pdf_fields(pdf_path) 