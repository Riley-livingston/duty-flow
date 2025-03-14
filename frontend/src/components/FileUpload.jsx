import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = ({ onStartProcessing, onProcessed, onError }) => {
  const [importFile, setImportFile] = useState(null);
  const [exportFile, setExportFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!importFile) {
      onError("Please select an import file");
      return;
    }
    
    setIsLoading(true);
    if (onStartProcessing) onStartProcessing();
    
    try {
      const formData = new FormData();
      formData.append('import_file', importFile);
      
      if (exportFile) {
        formData.append('export_file', exportFile);
        
        // Call API with both files
        const response = await axios.post('http://localhost:5000/api/scan-with-exports', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (onProcessed) onProcessed(response.data);
      } else {
        // Call API with just import file
        const response = await axios.post('http://localhost:5000/api/scan', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (onProcessed) onProcessed(response.data);
      }
    } catch (err) {
      console.error('Error processing files:', err);
      if (onError) onError(err.response?.data?.error || 'An error occurred while processing files');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>Upload Import/Export Data</h2>
      <p className="instructions">
        Upload your import data (and optionally export data) to analyze duty drawback eligibility.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="import-file">Import Data (CSV):</label>
          <div className="file-input-wrapper">
            <input
              type="file"
              id="import-file"
              accept=".csv"
              onChange={handleImportFileChange}
              className="file-input"
            />
            <label htmlFor="import-file" className="file-label">
              {importFile ? importFile.name : 'Choose file'}
            </label>
          </div>
          {importFile && (
            <div className="file-info">
              <span className="file-name">{importFile.name}</span>
              <span className="file-size">({(importFile.size / 1024).toFixed(1)} KB)</span>
              <button
                type="button"
                className="remove-file"
                onClick={() => setImportFile(null)}
              >
                Remove
              </button>
            </div>
          )}
          <p className="help-text">
            <a href="/templates/import_template.csv" download>Download Import Template</a>
          </p>
        </div>
        
        <div className="form-group">
          <label htmlFor="export-file">Export Data (CSV) - Optional:</label>
          <div className="file-input-wrapper">
            <input
              type="file"
              id="export-file"
              accept=".csv"
              onChange={handleExportFileChange}
              className="file-input"
            />
            <label htmlFor="export-file" className="file-label">
              {exportFile ? exportFile.name : 'Choose file'}
            </label>
          </div>
          {exportFile && (
            <div className="file-info">
              <span className="file-name">{exportFile.name}</span>
              <span className="file-size">({(exportFile.size / 1024).toFixed(1)} KB)</span>
              <button
                type="button"
                className="remove-file"
                onClick={() => setExportFile(null)}
              >
                Remove
              </button>
            </div>
          )}
          <p className="help-text">
            <a href="/templates/export_template.csv" download>Download Export Template</a>
          </p>
        </div>
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading || !importFile}
          >
            {isLoading ? 'Processing...' : 'Analyze Data'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FileUpload; 