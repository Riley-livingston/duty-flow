import os
import tempfile
import shutil
from datetime import datetime
from models.db import db
from werkzeug.utils import secure_filename
import atexit

# Use the uploads directory for temporary storage
UPLOADS_FOLDER = 'uploads'

# Clean up function to remove files from uploads directory on exit
@atexit.register
def cleanup_uploads():
    """Remove all files from uploads directory when application exits"""
    try:
        # Only cleanup if the folder exists
        if os.path.exists(UPLOADS_FOLDER):
            for filename in os.listdir(UPLOADS_FOLDER):
                file_path = os.path.join(UPLOADS_FOLDER, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file {file_path}: {str(e)}")
            print(f"Cleaned up files in {UPLOADS_FOLDER}")
    except Exception as e:
        print(f"Error in cleanup_uploads: {str(e)}")

class Document(db.Model):
    """Model for storing document information"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys to related entities
    import_transaction_id = db.Column(db.Integer, db.ForeignKey('import_transactions.id'), nullable=True)
    export_transaction_id = db.Column(db.Integer, db.ForeignKey('export_transactions.id'), nullable=True)
    
    # Tags for the document (comma-separated)
    tags = db.Column(db.String(500), nullable=True)
    
    # OCR extracted data (stored as JSON string)
    extracted_data = db.Column(db.Text, nullable=True)
    
    # Status of document processing
    processing_status = db.Column(db.String(50), default="pending")  # pending, processing, completed, failed
    
    # Notes about the document
    notes = db.Column(db.Text, nullable=True)
    
    @staticmethod
    def save_document(uploaded_file, document_type, import_id=None, export_id=None, tags=None):
        """
        Save an uploaded document file and create a document record
        
        Parameters:
        - uploaded_file: The uploaded file from request.files
        - document_type: Type of document (e.g., 'cbp_7501', 'commercial_invoice')
        - import_id: Optional ID of related import transaction
        - export_id: Optional ID of related export transaction
        - tags: Optional tags for the document
        
        Returns:
        - The created Document instance
        """
        # Create storage directory if it doesn't exist
        os.makedirs(UPLOADS_FOLDER, exist_ok=True)
        
        # Secure the filename and generate a unique name
        original_filename = uploaded_file.filename
        filename = secure_filename(original_filename)
        base, ext = os.path.splitext(filename)
        unique_filename = f"{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        
        # Store only the relative path in the database
        relative_path = os.path.join(UPLOADS_FOLDER, unique_filename)
        
        # Save the file
        uploaded_file.save(relative_path)
        
        # Create the document record
        document = Document(
            filename=unique_filename,
            original_filename=original_filename,
            document_type=document_type,
            file_path=relative_path,
            file_size=os.path.getsize(relative_path),
            mime_type=uploaded_file.content_type,
            import_transaction_id=import_id,
            export_transaction_id=export_id,
            tags=tags
        )
        
        db.session.add(document)
        db.session.commit()
        
        return document 