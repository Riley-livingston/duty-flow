"""
Document Requirements Manager for Duty Drawback Applications

This module manages document requirements for CBP duty drawback applications.
It helps track which documents are required, which are provided, and validates 
document completeness for submission.
"""

from datetime import datetime
from models.document import Document
from flask import current_app
import os
import json
from sqlalchemy import and_, or_

# Define document requirement types
REQUIRED_DOCUMENT_TYPES = {
    'PROOF_OF_DUTY': {
        'name': 'Proof of Duties Paid',
        'description': 'Certificate of Delivery (CBP Form 7552) proving all duties and taxes were paid',
        'accepted_types': ['cbp_7552', 'certificate_of_delivery', 'duty_payment_receipt'],
        'required': True
    },
    'ENTRY_SUMMARY': {
        'name': 'Entry Summary',
        'description': 'CBP Form 7501 Entry Summary with import information',
        'accepted_types': ['cbp_7501', 'entry_summary'],
        'required': True
    },
    'IMPORT_PROOF': {
        'name': 'Proof of Import',
        'description': 'Customs clearance documentation with HS tariff classification and import value',
        'accepted_types': ['customs_clearance', 'import_invoice', 'commercial_invoice_import'],
        'required': True
    },
    'EXPORT_PROOF': {
        'name': 'Proof of Export',
        'description': 'Documents showing export of goods (bill of lading, commercial invoices, etc.)',
        'accepted_types': ['bill_of_lading', 'export_invoice', 'commercial_invoice_export', 'airway_bill'],
        'required': True
    },
    'DRAWBACK_ENTRY': {
        'name': 'Drawback Entry Form',
        'description': 'CBP Form 7551 (Drawback Entry) completed and signed',
        'accepted_types': ['cbp_7551', 'drawback_entry'],
        'required': True,
        'can_generate': True
    }
}

class DocumentRequirementsManager:
    """Manages document requirements for drawback applications"""
    
    def __init__(self, drawback_claim_id=None):
        """
        Initialize a document requirements manager
        
        Args:
            drawback_claim_id: Optional ID of a drawback claim to associate documents with
        """
        self.drawback_claim_id = drawback_claim_id
        
    def get_required_documents(self):
        """
        Get list of required documents for drawback application
        
        Returns:
            List of document requirement definitions
        """
        return REQUIRED_DOCUMENT_TYPES
    
    def check_document_status(self, import_id=None, export_id=None):
        """
        Check status of documents for a drawback application
        
        Args:
            import_id: Optional import transaction ID to filter by
            export_id: Optional export transaction ID to filter by
            
        Returns:
            Dictionary with document status information
        """
        result = {
            'complete': False,
            'documents': {},
            'missing_documents': [],
            'missing_count': 0,
            'total_required': len([doc for doc in REQUIRED_DOCUMENT_TYPES.values() if doc['required']])
        }
        
        # Query filters
        filters = []
        if import_id:
            filters.append(Document.import_transaction_id == import_id)
        if export_id:
            filters.append(Document.export_transaction_id == export_id)
            
        # Get all documents that match our criteria
        query = Document.query
        if filters:
            query = query.filter(or_(*filters))
        documents = query.all()
        
        # Check each required document type
        for req_type, req_info in REQUIRED_DOCUMENT_TYPES.items():
            matching_docs = [
                doc for doc in documents 
                if doc.document_type in req_info['accepted_types']
            ]
            
            if matching_docs:
                # Sort by upload date to get most recent
                matching_docs.sort(key=lambda x: x.uploaded_at, reverse=True)
                most_recent = matching_docs[0]
                
                result['documents'][req_type] = {
                    'status': 'provided',
                    'document_id': most_recent.id,
                    'filename': most_recent.original_filename,
                    'uploaded_at': most_recent.uploaded_at.isoformat(),
                    'document_type': most_recent.document_type,
                    'can_generate': req_info.get('can_generate', False)
                }
            else:
                # Document is missing
                result['missing_documents'].append(req_type)
                result['missing_count'] += 1
                
                result['documents'][req_type] = {
                    'status': 'missing',
                    'can_generate': req_info.get('can_generate', False)
                }
        
        # Check if all required documents are provided
        result['complete'] = result['missing_count'] == 0
        
        return result
    
    @staticmethod
    def extract_document_data(document_id):
        """
        Extract data from a document using OCR or other methods
        
        Args:
            document_id: ID of the document to extract data from
            
        Returns:
            Dictionary of extracted data or None if extraction failed
        """
        document = Document.query.get(document_id)
        if not document:
            return None
            
        # If document already has extracted data, return it
        if document.extracted_data:
            try:
                return json.loads(document.extracted_data)
            except:
                pass
        
        # Based on document type, use appropriate extraction logic
        if document.document_type == 'cbp_7501':
            # Implement entry summary extraction logic
            # This would call OCR or form field extraction
            extracted_data = {
                'entry_number': 'PLACEHOLDER',
                'entry_date': 'PLACEHOLDER',
                'import_value': 'PLACEHOLDER',
                'duty_paid': 'PLACEHOLDER'
            }
        elif document.document_type == 'cbp_7552':
            # Implement certificate of delivery extraction
            extracted_data = {
                'certificate_number': 'PLACEHOLDER',
                'duty_amount': 'PLACEHOLDER'
            }
        elif document.document_type in ['bill_of_lading', 'export_invoice']:
            # Implement export document extraction
            extracted_data = {
                'reference_number': 'PLACEHOLDER',
                'export_date': 'PLACEHOLDER',
                'destination': 'PLACEHOLDER'
            }
        else:
            # Generic extraction
            extracted_data = {
                'detected_text': 'PLACEHOLDER'
            }
        
        # Store extracted data with the document
        if extracted_data:
            document.extracted_data = json.dumps(extracted_data)
            document.processing_status = 'completed'
            from models.db import db
            db.session.commit()
            
        return extracted_data
    
    @staticmethod
    def generate_required_document(document_type, data, output_path=None):
        """
        Generate a required document based on provided data
        
        Args:
            document_type: Type of document to generate (e.g., 'cbp_7551')
            data: Data to use for document generation
            output_path: Optional path to save the generated document
            
        Returns:
            Path to the generated document or None if generation failed
        """
        if document_type == 'cbp_7551':
            # Generate CBP Form 7551 (Drawback Entry)
            from pdf_generator import fill_drawback_form
            
            # Prepare data for form generation
            import_entries = data.get('import_entries', [])
            export_docs = data.get('export_docs', [])
            company_info = data.get('company_info', {})
            
            # Generate the form
            try:
                return fill_drawback_form(import_entries, export_docs, company_info, output_path)
            except Exception as e:
                current_app.logger.error(f"Error generating CBP Form 7551: {str(e)}")
                return None
        
        return None 