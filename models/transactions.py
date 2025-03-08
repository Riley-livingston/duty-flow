from models.db import db
from datetime import datetime

class ImportTransaction(db.Model):
    """Model for import transactions"""
    __tablename__ = 'import_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), nullable=False)
    import_date = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    product_description = db.Column(db.String(255), nullable=True)
    hs_code = db.Column(db.String(20), nullable=True)
    country_of_origin = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    value = db.Column(db.Float, nullable=True)
    duty_paid = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with documents
    documents = db.relationship(
        'Document', 
        primaryjoin="ImportTransaction.id==Document.import_transaction_id",
        backref='import_transaction', 
        lazy=True
    )

class ExportTransaction(db.Model):
    """Model for export transactions"""
    __tablename__ = 'export_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    export_reference = db.Column(db.String(50), nullable=False)
    export_date = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    value = db.Column(db.Float, nullable=True)
    matched_to_import = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with documents
    documents = db.relationship(
        'Document',
        primaryjoin="ExportTransaction.id==Document.export_transaction_id",
        backref='export_transaction',
        lazy=True
    ) 