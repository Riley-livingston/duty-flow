import React, { useState, useEffect } from 'react';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';
import axios from 'axios';
import './DocumentManager.css';

const DocumentManager = ({ importId, exportId }) => {
  const [uploadMode, setUploadMode] = useState(false);
  const [documentStatus, setDocumentStatus] = useState({
    'cbp_7501': 'incomplete',
    'commercial_invoice_import': 'incomplete',
    'bill_of_lading_import': 'incomplete',
    'proof_of_export': 'incomplete'
  });
  const [loading, setLoading] = useState(true);
  
  // Function to update document status
  const updateDocumentStatus = async () => {
    try {
      setLoading(true);
      
      // Use the dedicated status endpoint
      let url = 'http://localhost:5000/api/documents/status';
      const params = new URLSearchParams();
      
      if (importId) params.append('import_id', importId);
      if (exportId) params.append('export_id', exportId);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      
      if (response.data.success) {
        setDocumentStatus(response.data.status);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error checking document status:', error);
      setLoading(false);
    }
  };
  
  // Call on initial load
  useEffect(() => {
    updateDocumentStatus();
  }, []);
  
  const handleDocumentUploaded = () => {
    // After successful upload, switch back to list view and update status
    setUploadMode(false);
    updateDocumentStatus();
  };
  
  return (
    <div className="document-manager">
      <div className="document-manager-header">
        <h2>Document Management</h2>
        {!uploadMode && (
          <button 
            className="upload-button" 
            onClick={() => setUploadMode(true)}
          >
            Upload New Document
          </button>
        )}
      </div>
      
      <div className="document-content">
        <div className="document-checklist">
          <h3>Document Checklist</h3>
          {loading ? (
            <div className="loading-spinner">Loading document status...</div>
          ) : (
            <ul className="checklist-items">
              <li className="checklist-item">
                <span className={`checklist-status ${documentStatus['cbp_7501']}`}>
                  {documentStatus['cbp_7501'] === 'complete' ? 'Complete' : 'Missing'}
                </span>
                <span className="checklist-label">CBP Form 7501</span>
              </li>
              <li className="checklist-item">
                <span className={`checklist-status ${documentStatus['commercial_invoice_import']}`}>
                  {documentStatus['commercial_invoice_import'] === 'complete' ? 'Complete' : 'Missing'}
                </span>
                <span className="checklist-label">Commercial Invoice</span>
              </li>
              <li className="checklist-item">
                <span className={`checklist-status ${documentStatus['bill_of_lading_import']}`}>
                  {documentStatus['bill_of_lading_import'] === 'complete' ? 'Complete' : 'Missing'}
                </span>
                <span className="checklist-label">Bill of Lading</span>
              </li>
              <li className="checklist-item">
                <span className={`checklist-status ${documentStatus['proof_of_export']}`}>
                  {documentStatus['proof_of_export'] === 'complete' ? 'Complete' : 'Missing'}
                </span>
                <span className="checklist-label">Proof of Export</span>
              </li>
            </ul>
          )}
        </div>
      
        <div className="document-workspace">
          {uploadMode ? (
            <DocumentUpload 
              onCancel={() => setUploadMode(false)} 
              onDocumentUploaded={handleDocumentUploaded}
              importId={importId}
              exportId={exportId}
            />
          ) : (
            <DocumentList 
              importId={importId}
              exportId={exportId}
              onDocumentDeleted={updateDocumentStatus}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentManager; 