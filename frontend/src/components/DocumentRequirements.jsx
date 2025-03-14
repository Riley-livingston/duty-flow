import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './DocumentRequirements.css';

const DocumentRequirements = ({ importId, exportId, onComplete, readOnly = false, showDirectActionButtons = false }) => {
  const [requirements, setRequirements] = useState([]);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch document requirements from API
  useEffect(() => {
    const fetchRequirements = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/documents/requirements');
        
        // Convert the object to an array for easier mapping
        const requirementsArray = Object.entries(response.data).map(([key, value]) => ({
          key,
          ...value
        }));
        
        setRequirements(requirementsArray);
        
        // If we're in readOnly mode and don't have import/export IDs, we can finish loading now
        if (readOnly && !importId && !exportId) {
          setLoading(false);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching document requirements:', err);
        setError('Failed to load document requirements');
        setLoading(false);
      }
    };

    fetchRequirements();
  }, [readOnly, importId, exportId]);

  // Fetch document status when importId or exportId changes
  useEffect(() => {
    const fetchDocumentStatus = async () => {
      if (!importId && !exportId) {
        // In readOnly mode without IDs, we don't need to fetch status
        if (readOnly) {
          setLoading(false);
          return;
        }
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const params = new URLSearchParams();
        if (importId) params.append('import_id', importId);
        if (exportId) params.append('export_id', exportId);

        const response = await axios.get(
          `http://localhost:5000/api/documents/requirements/status?${params.toString()}`
        );
        
        setStatus(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching document status:', err);
        setError('Failed to load document status');
      } finally {
        setLoading(false);
      }
    };

    fetchDocumentStatus();
  }, [importId, exportId, readOnly]);

  // Check if all required documents are provided
  useEffect(() => {
    if (status.documents && status.missing_count === 0 && onComplete) {
      onComplete();
    }
  }, [status, onComplete]);

  const handleGenerateDocument = async (documentType) => {
    try {
      // Find the document requirement info
      const reqInfo = requirements.find(req => req.accepted_types.includes(documentType));
      if (!reqInfo || !reqInfo.can_generate) {
        alert(`Document type ${documentType} cannot be generated automatically`);
        return;
      }

      // Prepare data for document generation
      const data = {
        document_type: documentType,
        data: {
          import_transaction_id: importId,
          export_transaction_id: exportId,
          // Additional data needed for generation would go here
        }
      };

      // Call API to generate document
      const response = await axios.post('http://localhost:5000/api/documents/generate', data);
      
      if (response.data.success) {
        alert(`Document generated successfully: ${response.data.filename}`);
        // Refresh document status
        const params = new URLSearchParams();
        if (importId) params.append('import_id', importId);
        if (exportId) params.append('export_id', exportId);
        
        const statusResponse = await axios.get(
          `http://localhost:5000/api/documents/requirements/status?${params.toString()}`
        );
        setStatus(statusResponse.data);
      } else {
        alert(`Failed to generate document: ${response.data.error}`);
      }
    } catch (err) {
      console.error('Error generating document:', err);
      alert(`Error generating document: ${err.message}`);
    }
  };

  const handleDownloadGuide = async () => {
    try {
      window.open('http://localhost:5000/api/documentation-guide', '_blank');
    } catch (error) {
      console.error('Error downloading guide:', error);
      alert('Error downloading the documentation guide. Please try again later.');
    }
  };

  const getStatusBadge = (docKey) => {
    if (!status.documents || !status.documents[docKey]) {
      return <span className="status-badge missing">Missing</span>;
    }

    const docStatus = status.documents[docKey];
    if (docStatus.status === 'provided') {
      return <span className="status-badge provided">Provided</span>;
    } else {
      return <span className="status-badge missing">Missing</span>;
    }
  };

  // Build upload URL with query parameters for document type
  const getUploadUrl = (docType) => {
    const params = new URLSearchParams();
    params.append('type', docType);
    if (importId) params.append('import_id', importId);
    if (exportId) params.append('export_id', exportId);
    return `/documents/upload?${params.toString()}`;
  };

  return (
    <div className="document-requirements">
      <div className="requirements-header">
        <h2>Document Requirements</h2>
        <p className="info-text">
          Prepare these documents in advance to support your duty drawback claim.
        </p>
        <button 
          className="guide-download-button"
          onClick={handleDownloadGuide}
        >
          Download Detailed Guide (PDF)
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading document requirements...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <>
          {/* Only show status summary if we have status.documents (not in readOnly mode without IDs) */}
          {status.documents && (
            <div className="status-summary">
              <h3>Document Status</h3>
              <div className="status-progress">
                <div 
                  className="progress-bar" 
                  style={{ 
                    width: `${status.total_required ? ((status.total_required - status.missing_count) / status.total_required) * 100 : 0}%` 
                  }}
                />
              </div>
              <p>
                {status.missing_count === 0 ? (
                  <span className="complete">All required documents provided!</span>
                ) : (
                  <span className="incomplete">
                    {status.missing_count} of {status.total_required} required documents missing
                  </span>
                )}
              </p>
            </div>
          )}

          <div className="document-list">
            {requirements.map(doc => (
              <div key={doc.key} className={`document-card ${
                status.documents && status.documents[doc.key]?.status === 'provided' 
                  ? 'provided' 
                  : 'missing'
              }`}>
                <div className="document-header">
                  <h3>{doc.name}</h3>
                  {/* Only show status badge if we have status.documents */}
                  {status.documents && getStatusBadge(doc.key)}
                </div>
                
                <p className="document-description">{doc.description}</p>
                
                {/* Only show document info if we have this document and it's provided */}
                {status.documents && status.documents[doc.key]?.status === 'provided' && (
                  <div className="document-info">
                    <p>Filename: {status.documents[doc.key].filename}</p>
                    <p>Uploaded: {new Date(status.documents[doc.key].uploaded_at).toLocaleString()}</p>
                  </div>
                )}
                
                {/* Show upload buttons in two cases: 
                    1. When not in readOnly mode and we have status with missing documents
                    2. When showDirectActionButtons is true (for standalone document management) 
                */}
                {((!readOnly && status.documents && status.documents[doc.key]?.status === 'missing') || 
                  (showDirectActionButtons && (!status.documents || !status.documents[doc.key] || status.documents[doc.key]?.status === 'missing'))) && (
                  <div className="document-actions">
                    {doc.accepted_types.map((type) => (
                      <Link 
                        key={type}
                        to={`/upload?doctype=${type}&importId=${importId || ''}&exportId=${exportId || ''}`}
                        className="action-button upload"
                      >
                        Upload {type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </Link>
                    ))}
                    
                    {/* Only show generate button if we have status and can_generate is true */}
                    {status.documents && status.documents[doc.key]?.can_generate && (
                      <button 
                        className="action-button generate"
                        onClick={() => handleGenerateDocument(doc.accepted_types[0])}
                      >
                        Generate Automatically
                      </button>
                    )}
                  </div>
                )}
                
                <div className="document-tips">
                  <h4>Accepted Document Types</h4>
                  <ul>
                    {doc.accepted_types.map((type, i) => (
                      <li key={i}>{type.replace(/_/g, ' ').toUpperCase()}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentRequirements; 