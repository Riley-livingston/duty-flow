import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import ResultsTable from './components/ResultsTable';
import CompanyForm from './components/CompanyForm';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCompanyForm, setShowCompanyForm] = useState(false);
  const [generatedPdfPath, setGeneratedPdfPath] = useState(null);

  const handleFilesProcessed = (data) => {
    setResults(data);
    setLoading(false);
  };

  const handleGenerateForm = () => {
    setShowCompanyForm(true);
  };

  const handleFormGenerated = (pdfPath) => {
    setGeneratedPdfPath(pdfPath);
    setShowCompanyForm(false);
  };

  const handleDownloadPdf = () => {
    if (generatedPdfPath) {
      window.open(`http://localhost:5000/api/download/${generatedPdfPath}`, '_blank');
    }
  };

  const handleDownloadCsv = () => {
    if (results && results.resultsFile) {
      window.open(`http://localhost:5000/api/download/${results.resultsFile}`, '_blank');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>DutyFlow</h1>
        <p>Duty Drawback Eligibility Scanner</p>
      </header>
      
      <main className="App-main">
        {!showCompanyForm && !generatedPdfPath && (
          <FileUpload 
            onStartProcessing={() => setLoading(true)}
            onProcessed={handleFilesProcessed}
            onError={(err) => {
              setError(err);
              setLoading(false);
            }}
          />
        )}
        
        {loading && (
          <div className="loading-indicator">
            <p>Processing your files...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}
        
        {results && !loading && !showCompanyForm && !generatedPdfPath && (
          <div className="results-container">
            <h2>Eligible Refunds</h2>
            <div className="summary-box">
              <h3>Summary</h3>
              <p>Total Eligible Transactions: {results.count}</p>
              <p>Total Potential Refund: ${results.totalRefund.toFixed(2)}</p>
              <div className="action-buttons">
                <button 
                  className="generate-form-button"
                  onClick={handleGenerateForm}
                >
                  Generate CBP Form 7551
                </button>
                <button 
                  className="download-csv-button"
                  onClick={handleDownloadCsv}
                >
                  Download CSV
                </button>
              </div>
            </div>
            <ResultsTable data={results.transactions} />
          </div>
        )}
        
        {showCompanyForm && (
          <CompanyForm 
            resultsFile={results.resultsFile}
            onFormGenerated={handleFormGenerated}
            onError={(err) => {
              setError(err);
              setShowCompanyForm(false);
            }}
          />
        )}
        
        {generatedPdfPath && (
          <div className="form-generated-container">
            <h2>CBP Form 7551 Generated Successfully</h2>
            <p>Your form has been generated and is ready for download.</p>
            <div className="action-buttons">
              <button 
                className="download-pdf-button"
                onClick={handleDownloadPdf}
              >
                Download PDF
              </button>
              <button 
                className="back-button"
                onClick={() => {
                  setGeneratedPdfPath(null);
                  setShowCompanyForm(false);
                }}
              >
                Back to Results
              </button>
            </div>
          </div>
        )}
      </main>
      
      <footer className="App-footer">
        <p>DutyFlow MVP &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App; 