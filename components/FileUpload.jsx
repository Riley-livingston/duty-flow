import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = ({ onStartProcessing, onProcessed, onError }) => {
  const [importFile, setImportFile] = useState(null);
  const [exportFile, setExportFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleImportFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImportFile(e.target.files[0]);
    }
  };

  const handleExportFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setExportFile(e.target.files[0]);
    }
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
      // Determine file type based on name or let user choose
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().includes('import')) {
        setImportFile(file);
      } else if (file.name.toLowerCase().includes('export')) {
        setExportFile(file);
      } else {
        // If can't determine, default to import file
        setImportFile(file);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!importFile) {
      onError("Import file is required");
      return;
    }
    
    onStartProcessing();
    
    const formData = new FormData();
    formData.append('import_file', importFile);
    
    if (exportFile) {
      formData.append('export_file', exportFile);
    }
    
    try {
      // Call the backend API
      const response = await fetch('http://localhost:5000/api/scan', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process files');
      }
      
      onProcessed(data);
    } catch (error) {
      onError(error.message || "Failed to process files");
    }
  };

  return (
    <div className="file-upload-container">
      <form onSubmit={handleSubmit} className="upload-form">
        <div 
          className={`drag-drop-area ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <div className="file-inputs">
            <div className="file-input-group">
              <label htmlFor="import-file">Import Transactions (CSV) *</label>
              <input
                type="file"
                id="import-file"
                accept=".csv"
                onChange={handleImportFileChange}
              />
              {importFile && <p className="file-name">{importFile.name}</p>}
            </div>
            
            <div className="file-input-group">
              <label htmlFor="export-file">Export Transactions (CSV)</label>
              <input
                type="file"
                id="export-file"
                accept=".csv"
                onChange={handleExportFileChange}
              />
              {exportFile && <p className="file-name">{exportFile.name}</p>}
            </div>
          </div>
          
          <p className="drag-drop-text">
            Drag and drop files here, or click to select files
          </p>
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={!importFile}
        >
          Scan for Eligible Refunds
        </button>
      </form>
    </div>
  );
};

export default FileUpload; 