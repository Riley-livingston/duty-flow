import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DocumentUpload.css';

// Allow passing documentType as a prop for wizard flow
const DocumentUpload = ({ 
  onDocumentUploaded,
  importId: propImportId,
  exportId: propExportId,
  redirectAfterUpload = true,
  documentType: predefinedDocType = null,
  documentTypeLabel = null,
  acceptedFileTypes = null,
  useSmartDetection = false,
  onCancel = null
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract parameters from URL if present
  const queryParams = new URLSearchParams(location.search);
  const urlDocType = queryParams.get('doctype');
  const urlImportId = queryParams.get('importId');
  const urlExportId = queryParams.get('exportId');
  
  // Use URL params if available, otherwise use props
  const effectiveDocType = urlDocType || predefinedDocType;
  const effectiveImportId = urlImportId || propImportId;
  const effectiveExportId = urlExportId || propExportId;
  
  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState(effectiveDocType || '');
  const [tags, setTags] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [documentTypes, setDocumentTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [requirements, setRequirements] = useState({});
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [docTypeInfo, setDocTypeInfo] = useState(null);
  const [detectedType, setDetectedType] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);

  // Update document type whenever the prop or URL param changes
  useEffect(() => {
    if (effectiveDocType) {
      setDocumentType(effectiveDocType);
    }
  }, [effectiveDocType]);

  // Fetch document requirements on component mount
  useEffect(() => {
    const fetchRequirements = async () => {
      try {
        setLoading(true);
        
        // Get document requirements definition
        const requirementsResponse = await axios.get('http://localhost:5000/api/documents/requirements');
        setRequirements(requirementsResponse.data);
        
        // Build document types list from requirements
        const types = [];
        for (const [key, info] of Object.entries(requirementsResponse.data)) {
          for (const type of info.accepted_types) {
            types.push({
              value: type,
              label: `${info.name} (${type.replace(/_/g, ' ').toUpperCase()})`,
              category: key,
              description: info.description
            });
          }
        }
        
        setDocumentTypes(types);
        
        // If we have a predefined document type, find its info
        if (effectiveDocType) {
          const typeInfo = types.find(t => t.value === effectiveDocType);
          if (typeInfo) {
            setDocTypeInfo(typeInfo);
          }
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching document requirements:', err);
        setError('Failed to load document types');
        setLoading(false);
      }
    };
    
    fetchRequirements();
  }, [effectiveDocType]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      
      // If using smart detection, try to detect type when file is selected
      if (useSmartDetection && !effectiveDocType) {
        detectDocumentType(e.target.files[0]);
      }
    }
  };

  const handleDocumentTypeChange = (e) => {
    setDocumentType(e.target.value);
    
    // Update document type info
    const selectedType = documentTypes.find(t => t.value === e.target.value);
    if (selectedType) {
      setDocTypeInfo(selectedType);
    } else {
      setDocTypeInfo(null);
    }
  };

  const handleTagsChange = (e) => {
    setTags(e.target.value);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      
      // If using smart detection, try to detect type when file is dropped
      if (useSmartDetection && !effectiveDocType) {
        detectDocumentType(e.dataTransfer.files[0]);
      }
    }
  };

  // Function to detect document type from file content
  const detectDocumentType = async (file) => {
    if (!file) return;
    
    setIsDetecting(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        'http://localhost:5000/api/documents/detect-type',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (response.data.document_type) {
        setDocumentType(response.data.document_type);
        setDetectedType(response.data.document_type);
        
        // Update document type info for the detected type
        const typeInfo = documentTypes.find(t => t.value === response.data.document_type);
        if (typeInfo) {
          setDocTypeInfo(typeInfo);
        }
      }
    } catch (err) {
      console.error('Error detecting document type:', err);
      // Don't set error - just fail silently for detection
    } finally {
      setIsDetecting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    if (!documentType && !useSmartDetection) {
      setError('Please select a document type');
      return;
    }
    
    setUploading(true);
    setError(null);
    
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      
      // If document type is selected, include it - otherwise the API will detect it
      if (documentType || !useSmartDetection) {
        formData.append('document_type', documentType);
      }
      
      if (tags) {
        formData.append('tags', tags);
      }
      
      if (effectiveImportId) {
        formData.append('import_transaction_id', effectiveImportId);
      }
      
      if (effectiveExportId) {
        formData.append('export_transaction_id', effectiveExportId);
      }
      
      // Choose the right endpoint based on whether we're using smart detection
      const endpoint = useSmartDetection && !documentType
        ? 'http://localhost:5000/api/documents/smart-upload'
        : 'http://localhost:5000/api/documents/upload';
      
      // Upload document
      const response = await axios.post(
        endpoint,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Reset form
      setFile(null);
      // Only reset document type if it wasn't provided as a prop
      if (!effectiveDocType) {
        setDocumentType('');
      }
      setTags('');
      setUploading(false);
      setUploadSuccess(true);
      
      // Call the callback with document data
      if (onDocumentUploaded) {
        onDocumentUploaded(response.data);
      }
      
      // Handle redirect based on how the component was loaded
      if (redirectAfterUpload) {
        if (location.pathname === '/upload') {
          // Go back to previous page if loaded via URL
          navigate(-1);
        } else {
          // Redirect to document page if used directly
          window.location.href = `/documents/${response.data.id}`;
        }
      }
    } catch (err) {
      setUploading(false);
      setError(err.response?.data?.error || 'An error occurred while uploading the document');
      console.error('Upload error:', err);
    }
  };

  // Handle cancellation
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      navigate(-1);
    }
  };

  // Group document types by category
  const groupedDocumentTypes = {};
  documentTypes.forEach(type => {
    if (!groupedDocumentTypes[type.category]) {
      groupedDocumentTypes[type.category] = [];
    }
    groupedDocumentTypes[type.category].push(type);
  });

  // Get the document type display name
  const getDocumentTypeDisplayName = () => {
    if (documentTypeLabel) {
      return documentTypeLabel;
    }
    if (docTypeInfo) {
      return docTypeInfo.label;
    }
    return effectiveDocType ? effectiveDocType.replace(/_/g, ' ').toUpperCase() : null;
  };

  return (
    <div className="document-upload">
      <h2>
        {effectiveDocType 
          ? `Upload ${getDocumentTypeDisplayName() || 'Document'}`
          : useSmartDetection 
            ? 'Smart Document Upload' 
            : 'Upload Document'
        }
      </h2>
      
      {loading ? (
        <div className="loading">Loading document types...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div 
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDrag}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
          >
            <input
              type="file"
              id="file-upload"
              onChange={handleFileChange}
              className="file-input"
              accept={acceptedFileTypes || "*"}
            />
            <label htmlFor="file-upload" className="file-label">
              <div className="upload-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 14.9V4.99999H13V14.9H11Z" fill="#4CAF50"/>
                  <path d="M7.05026 10.0502L11 6.10051L14.9497 10.0502L13.5355 11.4644L12 9.92896L12 19H10L10 9.92896L8.46447 11.4644L7.05026 10.0502Z" fill="#4CAF50"/>
                  <path d="M4 14H6V19C6 19.5523 6.44772 20 7 20H17C17.5523 20 18 19.5523 18 19V14H20V19C20 20.6569 18.6569 22 17 22H7C5.34315 22 4 20.6569 4 19V14Z" fill="#4CAF50"/>
                </svg>
              </div>
              <div className="upload-text">
                <span className="primary-text">
                  {effectiveDocType 
                    ? `Upload ${getDocumentTypeDisplayName() || 'Document'}`
                    : 'Drag & drop file here or click to browse'
                  }
                </span>
                <span className="secondary-text">
                  {acceptedFileTypes 
                    ? `Accepted file types: ${acceptedFileTypes}` 
                    : 'Support for PDF, CSV, JPEG, PNG files'}
                </span>
                {docTypeInfo && (effectiveDocType || detectedType) && (
                  <span className="doc-type-info">
                    {docTypeInfo.description}
                    {detectedType && <strong> (Auto-detected)</strong>}
                  </span>
                )}
              </div>
            </label>
            {file && (
              <div className="selected-file">
                <span className="file-name">{file.name}</span>
                <button type="button" className="remove-file" onClick={() => setFile(null)}>✕</button>
              </div>
            )}
          </div>
          
          {/* Only show document type selection if not predefined and not using smart detection */}
          {!effectiveDocType && !useSmartDetection && (
            <div className="form-field">
              <label>Document Type:</label>
              <select 
                value={documentType} 
                onChange={handleDocumentTypeChange}
                required
              >
                <option value="">Select Document Type</option>
                
                {Object.entries(groupedDocumentTypes).map(([category, types]) => (
                  <optgroup 
                    key={category} 
                    label={requirements[category]?.name || category}
                  >
                    {types.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
              
              {/* Show selected document type description */}
              {documentType && !effectiveDocType && docTypeInfo && (
                <div className="document-type-description">
                  {docTypeInfo.description}
                </div>
              )}
            </div>
          )}
          
          {/* Show detected document type but allow override if using smart detection */}
          {useSmartDetection && detectedType && (
            <div className="form-field">
              <label>Detected Document Type:</label>
              <div className="detected-document-type">
                <span>{getDocumentTypeDisplayName() || detectedType.replace(/_/g, ' ').toUpperCase()}</span>
                <button 
                  type="button" 
                  className="change-type-button"
                  onClick={() => {
                    setDetectedType(null);
                    setDocumentType('');
                  }}
                >
                  Change
                </button>
              </div>
            </div>
          )}
          
          {/* Show document type selection if smart detection didn't work or user wants to change */}
          {useSmartDetection && !effectiveDocType && file && !detectedType && !isDetecting && (
            <div className="form-field">
              <label>Select Document Type:</label>
              <select 
                value={documentType} 
                onChange={handleDocumentTypeChange}
                required={!useSmartDetection}
              >
                <option value="">Select Document Type</option>
                
                {Object.entries(groupedDocumentTypes).map(([category, types]) => (
                  <optgroup 
                    key={category} 
                    label={requirements[category]?.name || category}
                  >
                    {types.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
          )}
          
          {/* Show detection status */}
          {useSmartDetection && isDetecting && (
            <div className="detecting-type">
              Detecting document type...
            </div>
          )}
          
          {/* Only show tags field when not in wizard mode */}
          {!effectiveDocType && (
            <div className="form-field">
              <label>Tags (optional):</label>
              <input 
                type="text" 
                value={tags} 
                onChange={handleTagsChange}
                placeholder="e.g., import-2023, entry-123456"
              />
              <small>Comma-separated tags to help organize documents</small>
            </div>
          )}
          
          <div className="form-actions">
            <button 
              type="button" 
              className="cancel-button"
              onClick={handleCancel}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="upload-button"
              disabled={uploading || !file || (!documentType && !useSmartDetection)}
            >
              {uploading ? 'Uploading...' : (
                useSmartDetection && !documentType
                  ? 'Smart Upload'
                  : `Upload ${effectiveDocType ? '' : 'Document'}`
              )}
            </button>
          </div>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {uploadSuccess && (
            <div className="success-message">
              Document uploaded successfully!
            </div>
          )}
        </form>
      )}
    </div>
  );
};

export default DocumentUpload; 