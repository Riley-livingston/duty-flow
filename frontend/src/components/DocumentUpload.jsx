import React, { useState } from 'react';
import axios from 'axios';
import './DocumentUpload.css';

const DOCUMENT_TYPES = [
  { value: 'cbp_7501', label: 'CBP Form 7501 (Entry Summary)' },
  { value: 'commercial_invoice_import', label: 'Commercial Invoice (Import)' },
  { value: 'bill_of_lading_import', label: 'Bill of Lading (Import)' },
  { value: 'commercial_invoice_export', label: 'Commercial Invoice (Export)' },
  { value: 'proof_of_export', label: 'Proof of Export' },
  { value: 'certificate_of_delivery', label: 'Certificate of Delivery' },
  { value: 'manufacturers_affidavit', label: 'Manufacturer\'s Affidavit' },
  { value: 'other', label: 'Other Document' }
];

const DocumentUpload = ({ onDocumentUploaded, importId, exportId }) => {
  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState('');
  const [tags, setTags] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDocumentTypeChange = (e) => {
    setDocumentType(e.target.value);
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
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }
    
    if (!documentType) {
      setError('Please select a document type');
      return;
    }
    
    setUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    
    if (tags) {
      formData.append('tags', tags);
    }
    
    if (importId) {
      formData.append('import_transaction_id', importId);
    }
    
    if (exportId) {
      formData.append('export_transaction_id', exportId);
    }
    
    try {
      const response = await axios.post('http://localhost:5000/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Reset form
      setFile(null);
      setDocumentType('');
      setTags('');
      
      // Notify parent component
      if (onDocumentUploaded) {
        onDocumentUploaded(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <h3>Upload Supporting Document</h3>
      <form onSubmit={handleSubmit}>
        <div 
          className={`drag-drop-area ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <div className="file-input">
            <input
              type="file"
              id="document-file"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
              className={file ? 'has-file' : ''}
            />
            <label htmlFor="document-file">
              {file ? file.name : 'Click or drag file to upload'}
            </label>
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="document-type">Document Type:</label>
          <select
            id="document-type"
            value={documentType}
            onChange={handleDocumentTypeChange}
            required
          >
            <option value="">Select Document Type</option>
            {DOCUMENT_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="document-tags">Tags (comma separated):</label>
          <input
            type="text"
            id="document-tags"
            value={tags}
            onChange={handleTagsChange}
            placeholder="e.g., important, verified, needs-review"
          />
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          type="submit" 
          className="upload-button" 
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Upload Document"}
        </button>
      </form>
    </div>
  );
};

export default DocumentUpload; 