import React, { useState } from 'react';
import axios from 'axios';
import './CompanyForm.css';

const CompanyForm = ({ resultsFile, onFormGenerated, onError }) => {
  const [formData, setFormData] = useState({
    company_name: '',
    company_address: '',
    company_city: '',
    company_state: '',
    company_zip: '',
    company_ein: '',
    contact_name: '',
    contact_phone: '',
    contact_email: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [id]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resultsFile) {
      if (onError) onError("No results file available. Please analyze your data first.");
      return;
    }
    
    try {
      setIsLoading(true);
      
      const requestData = {
        ...formData,
        results_file: resultsFile
      };
      
      const response = await axios.post('http://localhost:5000/api/generate-form', requestData);
      
      if (response.data.success && response.data.form_path) {
        if (onFormGenerated) onFormGenerated(response.data.form_path);
      } else {
        throw new Error(response.data.error || 'Failed to generate form');
      }
    } catch (err) {
      console.error('Error generating form:', err);
      if (onError) onError(err.response?.data?.error || 'An error occurred while generating the form');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="company-form">
      <h2>Company Information for CBP Form 7551</h2>
      <p className="form-instructions">
        Please provide your company information to complete the CBP Form 7551 (Drawback Entry).
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="company_name">Company Name</label>
          <input
            type="text"
            id="company_name"
            value={formData.company_name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="company_address">Address</label>
          <input
            type="text"
            id="company_address"
            value={formData.company_address}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="company_city">City</label>
            <input
              type="text"
              id="company_city"
              value={formData.company_city}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="company_state">State</label>
            <input
              type="text"
              id="company_state"
              value={formData.company_state}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="company_zip">ZIP Code</label>
            <input
              type="text"
              id="company_zip"
              value={formData.company_zip}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="company_ein">EIN/Tax ID</label>
          <input
            type="text"
            id="company_ein"
            value={formData.company_ein}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-section-divider">
          <h3>Contact Information</h3>
        </div>
        
        <div className="form-group">
          <label htmlFor="contact_name">Contact Name</label>
          <input
            type="text"
            id="contact_name"
            value={formData.contact_name}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="contact_phone">Phone Number</label>
            <input
              type="tel"
              id="contact_phone"
              value={formData.contact_phone}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="contact_email">Email</label>
            <input
              type="email"
              id="contact_email"
              value={formData.contact_email}
              onChange={handleChange}
              required
            />
          </div>
        </div>
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Generating Form...' : 'Generate CBP Form 7551'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CompanyForm; 