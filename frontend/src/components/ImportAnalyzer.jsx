import React, { useState, useEffect } from 'react';
import './ImportAnalyzer.css';

function ImportAnalyzer({ importId, exportId, onAnalysisComplete }) {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (importId) {
      analyzeData();
    }
  }, [importId, exportId]);

  const analyzeData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Construct the API endpoint URL
      let url = `/api/analyze?import_id=${importId}`;
      if (exportId) {
        url += `&export_id=${exportId}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Analysis failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      setAnalysisData(data);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(data);
      }
    } catch (err) {
      console.error('Error analyzing data:', err);
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="import-analyzer loading">
        <div className="loading-spinner"></div>
        <p>Analyzing your data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="import-analyzer error">
        <h3>Analysis Error</h3>
        <p>{error}</p>
        <button onClick={analyzeData} className="retry-button">Retry Analysis</button>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="import-analyzer empty">
        <p>No analysis data available.</p>
      </div>
    );
  }

  return (
    <div className="import-analyzer">
      <div className="analysis-summary">
        <div className="summary-card">
          <h3>Import Summary</h3>
          <div className="stat-row">
            <div className="stat">
              <span className="stat-value">{analysisData.import_count || 0}</span>
              <span className="stat-label">Imports</span>
            </div>
            <div className="stat">
              <span className="stat-value">${analysisData.total_duty_paid?.toFixed(2) || '0.00'}</span>
              <span className="stat-label">Total Duty Paid</span>
            </div>
          </div>
        </div>

        {exportId && (
          <div className="summary-card">
            <h3>Export Summary</h3>
            <div className="stat-row">
              <div className="stat">
                <span className="stat-value">{analysisData.export_count || 0}</span>
                <span className="stat-label">Exports</span>
              </div>
              <div className="stat">
                <span className="stat-value">{analysisData.matched_exports || 0}</span>
                <span className="stat-label">Matched Exports</span>
              </div>
            </div>
          </div>
        )}

        <div className="summary-card highlight">
          <h3>Drawback Summary</h3>
          <div className="stat-row">
            <div className="stat">
              <span className="stat-value">${analysisData.potential_refund?.toFixed(2) || '0.00'}</span>
              <span className="stat-label">Potential Refund</span>
            </div>
            <div className="stat">
              <span className="stat-value">{analysisData.eligible_transactions || 0}</span>
              <span className="stat-label">Eligible Transactions</span>
            </div>
          </div>
        </div>
      </div>

      {analysisData.matches && analysisData.matches.length > 0 && (
        <div className="matches-section">
          <h3>Import-Export Matches</h3>
          <div className="matches-table-container">
            <table className="matches-table">
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Import Date</th>
                  <th>Import Qty</th>
                  <th>Duty Paid</th>
                  <th>Export Date</th>
                  <th>Export Qty</th>
                  <th>Potential Refund</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.matches.map((match, index) => (
                  <tr key={index}>
                    <td>{match.product_id}</td>
                    <td>{new Date(match.import_date).toLocaleDateString()}</td>
                    <td>{match.import_qty}</td>
                    <td>${match.duty_paid?.toFixed(2) || '0.00'}</td>
                    <td>{match.export_date ? new Date(match.export_date).toLocaleDateString() : 'N/A'}</td>
                    <td>{match.export_qty || 'N/A'}</td>
                    <td>${match.refund_amount?.toFixed(2) || '0.00'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {analysisData.unmatched_imports && analysisData.unmatched_imports.length > 0 && (
        <div className="unmatched-section">
          <h3>Unmatched Imports</h3>
          <div className="matches-table-container">
            <table className="matches-table">
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Import Date</th>
                  <th>Quantity</th>
                  <th>Duty Paid</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {analysisData.unmatched_imports.map((item, index) => (
                  <tr key={index}>
                    <td>{item.product_id}</td>
                    <td>{new Date(item.import_date).toLocaleDateString()}</td>
                    <td>{item.quantity}</td>
                    <td>${item.duty_paid?.toFixed(2) || '0.00'}</td>
                    <td>
                      {item.eligible_for_future ? 
                        <span className="status eligible">Eligible for Future Export</span> : 
                        <span className="status ineligible">Ineligible</span>
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="actions">
        <button className="refresh-button" onClick={analyzeData}>
          Refresh Analysis
        </button>
      </div>
    </div>
  );
}

export default ImportAnalyzer;
