import React from 'react';
import axios from 'axios';
import './DocumentPreview.css';

const DocumentPreview = () => {
  const requiredDocuments = [
    {
      type: 'cbp_7501',
      name: 'CBP Form 7501 (Entry Summary)',
      description: 'The official customs entry document showing duties paid on imported merchandise.',
      examples: ['Example: Form 7501 showing duty payment for eligible products.'],
      tips: ['Ensure the Entry Number is clearly visible', 'Must show the duty amount paid']
    },
    {
      type: 'commercial_invoice_import',
      name: 'Commercial Invoice (Import)',
      description: 'Invoice from supplier for imported goods.',
      examples: ['Example: Invoice from your overseas supplier for the imported merchandise.'],
      tips: ['Should include product details and value', 'Must match the products in your import data']
    },
    {
      type: 'bill_of_lading_import',
      name: 'Bill of Lading (Import)',
      description: 'Transport document for the imported goods.',
      examples: ['Example: Ocean or air bill of lading showing import shipment.'],
      tips: ['Should reference the entry number if possible', 'Must show shipper, consignee, and product info']
    },
    {
      type: 'proof_of_export',
      name: 'Proof of Export Documentation',
      description: 'Documentation showing the same or similar merchandise was later exported.',
      examples: ['Example: Export bill of lading, shipper\'s export declaration, etc.'],
      tips: ['Must clearly show the exported products', 'Should include export date and destination']
    }
  ];

  const handleDownloadGuide = async () => {
    try {
      // This will trigger a file download
      window.open('http://localhost:5000/api/documentation-guide', '_blank');
    } catch (error) {
      console.error('Error downloading guide:', error);
      alert('Error downloading the documentation guide. Please try again later.');
    }
  };

  return (
    <div className="document-preview">
      <div className="preview-header">
        <h2>Document Requirements</h2>
        <p className="info-text">
          Prepare these documents in advance to support your duty drawback claim. You'll be able to upload them after analyzing your transaction data.
        </p>
      </div>

      <div className="document-list-preview">
        {requiredDocuments.map(doc => (
          <div key={doc.type} className="document-card">
            <h3>{doc.name}</h3>
            <p className="document-description">{doc.description}</p>
            
            <div className="document-examples">
              <h4>Examples</h4>
              <ul>
                {doc.examples.map((example, i) => (
                  <li key={i}>{example}</li>
                ))}
              </ul>
            </div>
            
            <div className="document-tips">
              <h4>Tips</h4>
              <ul>
                {doc.tips.map((tip, i) => (
                  <li key={i}>{tip}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      <div className="document-message">
        <div className="message-box">
          <h3>Complete your analysis first</h3>
          <p>The document upload feature will be enabled after you upload and analyze your import and export data. This ensures we only request documents for eligible transactions.</p>
          <button 
            className="guide-download-button"
            onClick={handleDownloadGuide}
          >
            Download Documentation Guide
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentPreview; 