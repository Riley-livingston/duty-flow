import React from 'react';
import './ResultsTable.css';

const ResultsTable = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="no-results">No results to display</div>;
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (value) => {
    if (value === undefined || value === null) return '-';
    return `$${parseFloat(value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  return (
    <div className="results-table">
      <h3>Transaction Details</h3>
      <div className="table-container">
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
            {data.map((transaction, index) => (
              <tr 
                key={index} 
                className={
                  transaction.is_eligible 
                    ? (transaction.has_export_match ? 'matched-row' : 'eligible-row') 
                    : ''
                }
              >
                <td>{transaction.entry_number || '-'}</td>
                <td>{transaction.product_id || '-'}</td>
                <td>{formatDate(transaction.import_date)}</td>
                <td>{transaction.quantity || '-'}</td>
                <td>{formatCurrency(transaction.duty_paid)}</td>
                <td>{formatCurrency(transaction.potential_refund)}</td>
                <td>
                  <span className={`status-badge ${transaction.is_eligible ? 'eligible' : 'ineligible'}`}>
                    {transaction.is_eligible ? 'Yes' : 'No'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${transaction.has_export_match ? 'matched' : 'unmatched'}`}>
                    {transaction.has_export_match ? 'Yes' : 'No'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="legend">
        <div className="legend-item">
          <div className="legend-color matched"></div>
          <span>Matched with Export</span>
        </div>
        <div className="legend-item">
          <div className="legend-color eligible"></div>
          <span>Eligible for Drawback</span>
        </div>
        <div className="legend-item">
          <div className="legend-color ineligible"></div>
          <span>Ineligible</span>
        </div>
      </div>
    </div>
  );
};

export default ResultsTable; 