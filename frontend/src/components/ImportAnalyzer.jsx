import React, { useState } from "react";
import axios from "axios";
import "./ImportAnalyzer.css";
import DocumentManager from './DocumentManager';
import WorkflowProgress from './WorkflowProgress';
import DocumentRequirements from './DocumentRequirements';

const ImportAnalyzer = () => {
  const [importFile, setImportFile] = useState(null);
  const [exportFile, setExportFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("upload");
  const [workflowStep, setWorkflowStep] = useState(0);

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

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

  const handleAnalyze = async () => {
    console.log("Starting analysis...");
    
    if (!importFile) {
      setError("Import file is required");
      return;
    }
    
    if (!exportFile) {
      setError("Export file is required");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("import_file", importFile);
    formData.append("export_file", exportFile);
    
    try {
      console.log("Sending API request...");
      const response = await axios.post("http://localhost:5000/api/scan-with-exports", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      
      console.log("Response received:", response.data);
      setResults(response.data);
      setLoading(false);
      setWorkflowStep(2);
      setActiveTab("documents");
      
    } catch (err) {
      console.error("API Error:", err);
      setLoading(false);
      setError(err.response?.data?.error || "An error occurred during analysis");
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAnalyze();
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (value) => {
    if (value === undefined || value === null) return "-";
    return `$${parseFloat(value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  return (
    <div className="import-analyzer">
      <WorkflowProgress currentStep={workflowStep} />
      
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => handleTabChange('upload')}
        >
          Upload Data
        </button>
        <button 
          className={`tab-button ${activeTab === 'requirements' ? 'active' : ''}`}
          onClick={() => handleTabChange('requirements')}
        >
          Requirements
        </button>
        <button 
          className={`tab-button ${activeTab === 'documents' ? 'active' : ''} ${!results ? 'disabled' : ''}`}
          onClick={() => results && handleTabChange('documents')}
          title={!results ? "Complete analysis first" : ""}
        >
          Documents
        </button>
      </div>
      
      {activeTab === 'upload' && (
        <div className="upload-section">
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-group">
              <label htmlFor="import-file">Import Transactions CSV:</label>
              <input
                type="file"
                id="import-file"
                accept=".csv"
                onChange={handleImportFileChange}
                required
              />
              {importFile && (
                <div className="file-name">Selected: {importFile.name}</div>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="export-file">Export Transactions CSV:</label>
              <input
                type="file"
                id="export-file"
                accept=".csv"
                onChange={handleExportFileChange}
                required
              />
              {exportFile && (
                <div className="file-name">Selected: {exportFile.name}</div>
              )}
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-actions">
              <button 
                type="submit" 
                className="submit-button" 
                disabled={loading}
              >
                {loading ? "Processing..." : "Analyze Data"}
              </button>
            </div>
          </form>
          
          {loading && (
            <div className="loading-indicator">
              Analyzing your data... This may take a moment.
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'requirements' && (
        <div className="requirements-section">
          <DocumentRequirements />
        </div>
      )}
      
      {activeTab === 'documents' && (
        <div className="documents-section">
          {results ? (
            <DocumentManager 
              importId={null}
              exportId={null}
            />
          ) : (
            <div className="no-analysis-message">
              <p>Please upload and analyze your data before accessing document management.</p>
              <button 
                className="primary-button"
                onClick={() => handleTabChange('upload')}
              >
                Go to Upload
              </button>
            </div>
          )}
        </div>
      )}
      
      {results && (
        <div className="results-container">
          <h3>Analysis Results</h3>
          
          <div className="refund-estimate-banner">
            <h2>Estimated Potential Refund</h2>
            <div className="refund-amount">{formatCurrency(results.totalRefund)}</div>
            <p>Based on {results.eligibleCount} eligible transactions with {results.matchedCount} export matches</p>
          </div>
          
          <div className="summary-box">
            <p><strong>Total Import Transactions:</strong> {results.count}</p>
            <p><strong>Eligible Transactions:</strong> {results.eligibleCount}</p>
            <p><strong>Matched with Exports:</strong> {results.matchedCount}</p>
            <p><strong>Total Duty Paid:</strong> {formatCurrency(results.totalDuty)}</p>
          </div>
          
          <div className="summary-report">
            <h4>Summary Report</h4>
            <pre>{results.summary}</pre>
          </div>
          
          <div className="button-group">
            <a 
              href={`http://localhost:5000/api/download/${results.resultsFile}`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="download-button"
            >
              Download Full Analysis CSV
            </a>
            
            <button
              type="button"
              className="pdf-button"
              onClick={() => window.open("http://localhost:5000/api/generate-pdf-report", "_blank")}
            >
              Generate PDF Report
            </button>
          </div>
          
          <div className="smb-guidance">
            <h4>Small Business Guidance</h4>
            <p>
              Based on your import and export data, 
              you may be eligible for duty drawback refunds. 
              Small businesses typically recover between 5-15% of their total duty payments through drawback.
            </p>
            <p>
              <strong>Next Steps:</strong> Download the PDF report for detailed guidance on filing your claim.
            </p>
          </div>
          
          <div className="transactions-table">
            <h4>Import Transactions</h4>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Entry Number</th>
                    <th>Product ID</th>
                    <th>Import Date</th>
                    <th>Quantity</th>
                    <th>Duty Paid</th>
                    <th>Potential Refund</th>
                    <th>Eligible</th>
                    <th>Export Match</th>
                  </tr>
                </thead>
                <tbody>
                  {results.transactions.map((transaction, index) => (
                    <tr key={index} className={transaction.is_eligible ? (transaction.has_export_match ? "matched-row" : "eligible-row") : ""}>
                      <td>{transaction.entry_number || "-"}</td>
                      <td>{transaction.product_id || "-"}</td>
                      <td>{formatDate(transaction.import_date)}</td>
                      <td>{transaction.quantity || "-"}</td>
                      <td>{formatCurrency(transaction.duty_paid)}</td>
                      <td>{formatCurrency(transaction.potential_refund)}</td>
                      <td>{transaction.is_eligible ? "Yes" : "No"}</td>
                      <td>{transaction.has_export_match ? "Yes" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="transactions-table">
            <h4>Export Transactions</h4>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Export Reference</th>
                    <th>Product ID</th>
                    <th>Export Date</th>
                    <th>Quantity</th>
                    <th>Destination</th>
                    <th>Matched to Import</th>
                  </tr>
                </thead>
                <tbody>
                  {results.exportTransactions.map((transaction, index) => (
                    <tr key={index} className={transaction.matched_to_import ? "matched-row" : ""}>
                      <td>{transaction.export_reference || "-"}</td>
                      <td>{transaction.product_id || "-"}</td>
                      <td>{formatDate(transaction.export_date)}</td>
                      <td>{transaction.quantity || "-"}</td>
                      <td>{transaction.destination || "-"}</td>
                      <td>{transaction.matched_to_import ? "Yes" : "No"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImportAnalyzer;
