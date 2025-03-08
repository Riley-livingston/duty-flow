import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentList.css';

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

const DocumentList = ({ importId, exportId, onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('');

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      
      // Build query parameters
      let url = 'http://localhost:5000/api/documents';
      const params = new URLSearchParams();
      
      if (importId) params.append('import_transaction_id', importId);
      if (exportId) params.append('export_transaction_id', exportId);
      
      if (filterType) params.append('document_type', filterType);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      
      if (response.data.success) {
        setDocuments(response.data.documents);
      } else {
        setError(response.data.error || 'Failed to fetch documents');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Failed to load documents. Please try again.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [importId, exportId, filterType]);

  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    
    try {
      const response = await axios.delete(`http://localhost:5000/api/documents/${documentId}`);
      
      if (response.data.success) {
        // Update local state
        setDocuments(documents.filter(doc => doc.id !== documentId));
        
        // Notify parent component
        if (onDocumentDeleted) {
          onDocumentDeleted();
        }
      } else {
        setError(response.data.error || 'Failed to delete document');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document. Please try again.');
    }
  };

  const handleDownloadDocument = (documentId, filename) => {
    window.open(`http://localhost:5000/api/documents/${documentId}/download`, '_blank');
  };

  const getDocumentTypeLabel = (typeCode) => {
    const types = {
      'cbp_7501': 'CBP Form 7501',
      'commercial_invoice_import': 'Commercial Invoice (Import)',
      'bill_of_lading_import': 'Bill of Lading (Import)',
      'commercial_invoice_export': 'Commercial Invoice (Export)',
      'proof_of_export': 'Proof of Export',
      'certificate_of_delivery': 'Certificate of Delivery',
      'manufacturers_affidavit': 'Manufacturer\'s Affidavit',
      'other': 'Other Document'
    };
    
    return types[typeCode] || typeCode;
  };

  if (loading) {
    return <div className="loading-message">Loading documents...</div>;
  }
  
  if (error) {
    return <div className="error-message">{error}</div>;
  }
  
  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <p>No documents have been uploaded yet.</p>
      </div>
    );
  }
  
  return (
    <div className="document-list-container">
      <h3>Uploaded Documents</h3>
      
      <div className="document-cards">
        {documents.map(doc => (
          <div key={doc.id} className="document-card">
            <div className="document-card-header">
              <span className="document-type">{getDocumentTypeLabel(doc.document_type)}</span>
              <span className="document-date">{formatDate(doc.uploaded_at)}</span>
            </div>
            
            <div className="document-card-body">
              <p className="document-filename">{doc.filename}</p>
              {doc.description && (
                <p className="document-description">{doc.description}</p>
              )}
            </div>
            
            <div className="document-card-actions">
              <a 
                href={`http://localhost:5000/api/documents/${doc.id}/download`}
                className="download-button"
                target="_blank"
                rel="noopener noreferrer"
              >
                Download
              </a>
              <button 
                onClick={() => handleDelete(doc.id)}
                className="delete-button"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList; 