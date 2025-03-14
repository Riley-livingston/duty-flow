from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models.document import Document, db
from document_requirements import DocumentRequirementsManager, REQUIRED_DOCUMENT_TYPES
import re
import pandas as pd
from PyPDF2 import PdfReader

document_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """API endpoint to upload a document"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get document metadata
        document_type = request.form.get('document_type')
        if not document_type:
            return jsonify({'error': 'Document type is required'}), 400
        
        import_id = request.form.get('import_transaction_id')
        export_id = request.form.get('export_transaction_id')
        tags = request.form.get('tags')
        
        # Save document
        document = Document.save_document(
            file, 
            document_type, 
            import_id=import_id, 
            export_id=export_id, 
            tags=tags
        )
        
        # Return document info
        return jsonify({
            'success': True,
            'id': document.id,
            'filename': document.original_filename,
            'document_type': document.document_type,
            'uploaded_at': document.uploaded_at.isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/detect-type', methods=['POST'])
def detect_document_type():
    """API endpoint to detect document type from file contents"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Detect document type based on file content
        detected_type = detect_type_from_content(file)
        
        if detected_type:
            return jsonify({
                'success': True,
                'document_type': detected_type,
                'confidence': 'high' if detected_type else 'low'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not detect document type with confidence'
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/smart-upload', methods=['POST'])
def smart_upload_document():
    """API endpoint to upload a document with automatic type detection"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Try to detect document type if not provided
        document_type = request.form.get('document_type')
        if not document_type:
            # Create a copy of the file since we need to read it twice
            file_copy = file
            document_type = detect_type_from_content(file_copy)
            
            if not document_type:
                return jsonify({'error': 'Could not detect document type automatically. Please specify the document type.'}), 400
            
            # Rewind the file for saving
            file.seek(0)
        
        import_id = request.form.get('import_transaction_id')
        export_id = request.form.get('export_transaction_id')
        tags = request.form.get('tags')
        
        # Save document
        document = Document.save_document(
            file, 
            document_type, 
            import_id=import_id, 
            export_id=export_id, 
            tags=tags
        )
        
        # Return document info
        return jsonify({
            'success': True,
            'id': document.id,
            'filename': document.original_filename,
            'document_type': document.document_type,
            'detected': document_type is not None,
            'uploaded_at': document.uploaded_at.isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def detect_type_from_content(file):
    """
    Detect document type based on file content
    Returns the document type or None if detection fails
    """
    filename = file.filename.lower()
    
    # Check file extension first
    if filename.endswith('.csv'):
        # Read the CSV file and check the headers
        try:
            df = pd.read_csv(file)
            file.seek(0)  # Reset file pointer after reading
            
            # Check for import entries
            if any(col.lower() in ['entry_number', 'entry no', 'entry'] for col in df.columns):
                if any(col.lower() in ['duty', 'duty_paid', 'payment'] for col in df.columns):
                    return 'import_entry'
            
            # Check for export declarations
            if any(col.lower() in ['export', 'export_id', 'declaration'] for col in df.columns):
                return 'export_declaration'
                
            # Check for duty payment proofs
            if any(col.lower() in ['payment', 'receipt', 'duty_paid'] for col in df.columns):
                return 'proof_of_duty'
        except:
            pass
    
    elif filename.endswith('.pdf'):
        # Extract text from PDF and check for patterns
        try:
            reader = PdfReader(file)
            file.seek(0)  # Reset file pointer after reading
            
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # Convert to lowercase for easier pattern matching
            text_lower = text.lower()
            
            # Check for import entry patterns
            if re.search(r'(entry\s*summary|entry\s*number|customs\s*entry)', text_lower):
                return 'entry_summary'
            
            # Check for export declaration patterns
            if re.search(r'(export\s*declaration|shipper\'s\s*export\s*declaration|sed)', text_lower):
                return 'export_declaration'
            
            # Check for proof of duty payment
            if re.search(r'(duty\s*payment|receipt|customs\s*duty\s*paid)', text_lower):
                return 'proof_of_duty'
            
            # Check for proof of export
            if re.search(r'(bill\s*of\s*lading|airway\s*bill|proof\s*of\s*export)', text_lower):
                return 'proof_of_export'
        except:
            pass
    
    # If no type could be detected, return None
    return None

@document_bp.route('/api/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """API endpoint to get document metadata"""
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'id': document.id,
            'filename': document.original_filename,
            'document_type': document.document_type,
            'file_size': document.file_size,
            'uploaded_at': document.uploaded_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'import_transaction_id': document.import_transaction_id,
            'export_transaction_id': document.export_transaction_id,
            'tags': document.tags,
            'processing_status': document.processing_status,
            'notes': document.notes
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/<int:document_id>/download', methods=['GET'])
def download_document(document_id):
    """API endpoint to download a document"""
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return send_file(
            document.file_path,
            mimetype=document.mime_type,
            as_attachment=True,
            download_name=document.original_filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    """API endpoint to update document metadata"""
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Update document metadata
        data = request.json
        if 'document_type' in data:
            document.document_type = data['document_type']
        if 'tags' in data:
            document.tags = data['tags']
        if 'notes' in data:
            document.notes = data['notes']
        if 'import_transaction_id' in data:
            document.import_transaction_id = data['import_transaction_id']
        if 'export_transaction_id' in data:
            document.export_transaction_id = data['export_transaction_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document updated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """API endpoint to delete a document"""
    try:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete the file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete the database record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents', methods=['GET'])
def list_documents():
    """API endpoint to list documents with filtering"""
    try:
        # Parse query parameters
        import_id = request.args.get('import_transaction_id')
        export_id = request.args.get('export_transaction_id')
        doc_type = request.args.get('document_type')
        
        # Build query
        query = Document.query
        
        if import_id:
            query = query.filter_by(import_transaction_id=import_id)
        if export_id:
            query = query.filter_by(export_transaction_id=export_id)
        if doc_type:
            query = query.filter_by(document_type=doc_type)
        
        # Order by upload date (newest first)
        query = query.order_by(Document.uploaded_at.desc())
        
        # Execute query
        documents = query.all()
        
        # Format results
        results = []
        for doc in documents:
            results.append({
                'id': doc.id,
                'filename': doc.original_filename,
                'document_type': doc.document_type,
                'uploaded_at': doc.uploaded_at.isoformat(),
                'import_transaction_id': doc.import_transaction_id,
                'export_transaction_id': doc.export_transaction_id,
                'tags': doc.tags,
                'processing_status': doc.processing_status,
                'file_size': doc.file_size
            })
        
        return jsonify({
            'success': True,
            'documents': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/status', methods=['GET'])
def check_document_status():
    """API endpoint to check document status for required document types"""
    try:
        # Required document types to check
        required_types = ['cbp_7501', 'commercial_invoice_import', 'bill_of_lading_import', 'proof_of_export']
        
        # Get import/export IDs from query params if provided
        import_id = request.args.get('import_id')
        export_id = request.args.get('export_id')
        
        # Build base query
        status = {}
        
        # Check status for each document type
        for doc_type in required_types:
            query = Document.query.filter_by(document_type=doc_type)
            
            if import_id:
                query = query.filter_by(import_transaction_id=import_id)
            
            if export_id:
                query = query.filter_by(export_transaction_id=export_id)
            
            # Document exists if query returns results
            status[doc_type] = 'complete' if query.first() else 'incomplete'
        
        return jsonify({
            'success': True,
            'status': status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/documents/requirements', methods=['GET'])
def get_document_requirements():
    """Get list of required documents for drawback application"""
    manager = DocumentRequirementsManager()
    return jsonify(manager.get_required_documents())

@document_bp.route('/api/documents/requirements/status', methods=['GET'])
def check_requirements_status():
    """Check status of required documents for a drawback application"""
    import_id = request.args.get('import_id')
    export_id = request.args.get('export_id')
    
    # Convert string IDs to integers if provided
    if import_id and import_id.isdigit():
        import_id = int(import_id)
    else:
        import_id = None
        
    if export_id and export_id.isdigit():
        export_id = int(export_id)
    else:
        export_id = None
    
    manager = DocumentRequirementsManager()
    status = manager.check_document_status(import_id, export_id)
    
    return jsonify(status)

@document_bp.route('/api/documents/extract/<int:document_id>', methods=['GET'])
def extract_document_data(document_id):
    """Extract data from a document using OCR or form field extraction"""
    manager = DocumentRequirementsManager()
    extracted_data = manager.extract_document_data(document_id)
    
    if extracted_data:
        return jsonify({
            'success': True,
            'document_id': document_id,
            'data': extracted_data
        })
    else:
        return jsonify({
            'success': False,
            'document_id': document_id,
            'error': 'Failed to extract data from document'
        }), 400

@document_bp.route('/api/documents/generate', methods=['POST'])
def generate_required_document():
    """Generate a required document based on provided data"""
    # Get document type from request
    document_type = request.json.get('document_type')
    if not document_type:
        return jsonify({'error': 'Document type is required'}), 400
    
    # Check if document type can be generated
    req_info = None
    for key, info in REQUIRED_DOCUMENT_TYPES.items():
        if document_type in info['accepted_types'] and info.get('can_generate'):
            req_info = info
            break
    
    if not req_info:
        return jsonify({'error': f'Document type {document_type} cannot be generated'}), 400
    
    # Get generation data from request
    data = request.json.get('data', {})
    
    # Generate the document
    manager = DocumentRequirementsManager()
    document_path = manager.generate_required_document(document_type, data)
    
    if document_path and os.path.exists(document_path):
        # Create a document record
        with open(document_path, 'rb') as f:
            from werkzeug.datastructures import FileStorage
            file = FileStorage(
                stream=f,
                filename=os.path.basename(document_path),
                content_type='application/pdf'
            )
            
            # Get IDs for relationships
            import_id = data.get('import_transaction_id')
            export_id = data.get('export_transaction_id')
            
            # Save the document
            document = Document.save_document(
                file,
                document_type,
                import_id=import_id,
                export_id=export_id,
                tags='generated'
            )
            
            return jsonify({
                'success': True,
                'document_id': document.id,
                'filename': document.original_filename,
                'file_path': document_path
            })
    else:
        return jsonify({
            'success': False,
            'error': f'Failed to generate {document_type} document'
        }), 400

@document_bp.route('/api/document-groups', methods=['GET'])
def list_document_groups():
    """API endpoint to list document groups"""
    try:
        # Implement document groups management
        # For MVP, we'll return a simple response
        # TODO: Implement proper document groups with a database model
        return jsonify({
            'groups': [
                {
                    'id': 1,
                    'name': 'Import/Export Set 1',
                    'created_at': datetime.now().isoformat(),
                    'documents': [
                        {
                            'id': 1,
                            'filename': 'import_entry_123.csv',
                            'document_type': 'import_entry',
                            'uploaded_at': datetime.now().isoformat()
                        },
                        {
                            'id': 2,
                            'filename': 'export_declaration_456.pdf',
                            'document_type': 'export_declaration',
                            'uploaded_at': datetime.now().isoformat()
                        }
                    ]
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/document-groups', methods=['POST'])
def create_document_group():
    """API endpoint to create a document group"""
    try:
        data = request.json
        name = data.get('name')
        document_ids = data.get('document_ids', [])
        
        if not name:
            return jsonify({'error': 'Group name is required'}), 400
        
        if not document_ids:
            return jsonify({'error': 'At least one document is required'}), 400
        
        # TODO: Implement proper document groups with a database model
        # For MVP, we just return a success response
        
        return jsonify({
            'success': True,
            'message': 'Document group created',
            'group': {
                'id': 1,  # This would be a real ID in a full implementation
                'name': name,
                'created_at': datetime.now().isoformat(),
                'document_ids': document_ids
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/api/document-groups/<int:group_id>', methods=['GET'])
def get_document_group(group_id):
    """API endpoint to get a document group"""
    try:
        # TODO: Implement proper document group retrieval
        # For MVP, we just return a sample response
        
        return jsonify({
            'id': group_id,
            'name': 'Sample Document Group',
            'created_at': datetime.now().isoformat(),
            'documents': [
                {
                    'id': 1,
                    'filename': 'import_entry_123.csv',
                    'document_type': 'import_entry',
                    'uploaded_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'filename': 'export_declaration_456.pdf',
                    'document_type': 'export_declaration',
                    'uploaded_at': datetime.now().isoformat()
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 