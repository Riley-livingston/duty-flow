import React, { useState } from 'react';
import './CompanyForm.css';

const CompanyForm = ({ resultsFile, onFormGenerated, onError }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    claimant_name: '',
    claimant_address: '',
    claimant_id: '',
    port_code: '',
    signatory_name: '',
    signatory_title: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/generate-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_info: formData,
          results_file: resultsFile
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate form');
      }

      onFormGenerated(data.pdf_path);
    } catch (error) {
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="company-form-container">
      <h2>Enter Company Information</h2>
      <p>This information will be used to generate your CBP Form 7551.</p>
      
      <form onSubmit={handleSubmit} className="company-form">
        <div className="form-group">
          <label htmlFor="claimant_name">Company Name *</label>
          <input
            type="text"
            id="claimant_name"
            name="claimant_name"
            value={formData.claimant_name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="claimant_address">Company Address *</label>
          <input
            type="text"
            id="claimant_address"
            name="claimant_address"
            value={formData.claimant_address}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="claimant_id">EIN/Tax ID *</label>
          <input
            type="text"
            id="claimant_id"
            name="claimant_id"
            value={formData.claimant_id}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="port_code">Port Code</label>
          <input
            type="text"
            id="port_code"
            name="port_code"
            value={formData.port_code}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="signatory_name">Signatory Name *</label>
          <input
            type="text"
            id="signatory_name"
            name="signatory_name"
            value={formData.signatory_name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="signatory_title">Signatory Title *</label>
          <input
            type="text"
            id="signatory_title"
            name="signatory_title"
            value={formData.signatory_title}
            onChange={handleChange}
            required
          />
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Generating Form...' : 'Generate CBP Form 7551'}
        </button>
      </form>
    </div>
  );
};

export default CompanyForm; 