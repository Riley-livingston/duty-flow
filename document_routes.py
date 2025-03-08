from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models.document import Document, db

document_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif'}

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
            'document_id': document.id,
            'filename': document.original_filename,
            'document_type': document.document_type,
            'uploaded_at': document.uploaded_at.isoformat()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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