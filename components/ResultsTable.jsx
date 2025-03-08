import React, { useState } from 'react';
import './ResultsTable.css';

const ResultsTable = ({ data }) => {
  const [sortField, setSortField] = useState('refund_amount');
  const [sortDirection, setSortDirection] = useState('desc');
  const [searchTerm, setSearchTerm] = useState('');
  
  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  const sortedData = [...data].sort((a, b) => {
    if (a[sortField] < b[sortField]) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (a[sortField] > b[sortField]) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });
  
  const filteredData = sortedData.filter(item => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      item.entry_number.toLowerCase().includes(searchLower) ||
      item.product_id.toLowerCase().includes(searchLower)
    );
  });
  
  return (
    <div className="results-table-container">
      <div className="table-controls">
        <input
          type="text"
          placeholder="Search by entry number or product ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        
        <div className="export-options">
          <button className="export-button">
            Export to CSV
          </button>
        </div>
      </div>
      
      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('entry_number')}>
                Entry Number
                {sortField === 'entry_number' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('product_id')}>
                Product ID
                {sortField === 'product_id' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('import_date')}>
                Import Date
                {sortField === 'import_date' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('export_date')}>
                Export Date
                {sortField === 'export_date' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('days_difference')}>
                Days
                {sortField === 'days_difference' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('refundable_quantity')}>
                Quantity
                {sortField === 'refundable_quantity' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th onClick={() => handleSort('refund_amount')}>
                Refund Amount
                {sortField === 'refund_amount' && (
                  <span className="sort-indicator">
                    {sortDirection === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item, index) => (
              <tr key={index}>
                <td>{item.entry_number}</td>
                <td>{item.product_id}</td>
                <td>{item.import_date}</td>
                <td>{item.export_date}</td>
                <td>{item.days_difference}</td>
                <td>{item.refundable_quantity}</td>
                <td>${item.refund_amount.toFixed(2)}</td>
                <td>
                  <button className="action-button">
                    Generate Form
                  </button>
                </td>
              </tr>
            ))}
            
            {filteredData.length === 0 && (
              <tr>
                <td colSpan="8" className="no-results">
                  No matching transactions found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable; 