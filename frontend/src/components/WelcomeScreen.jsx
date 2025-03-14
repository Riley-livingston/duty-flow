import React from 'react';
import './WelcomeScreen.css';

const WelcomeScreen = ({ onStartWizard }) => {
  return (
    <div className="welcome-screen">
      <div className="welcome-content">
        <h1>Welcome to DutyFlow</h1>
        <p className="tagline">Your customs duty drawback refund solution</p>
        
        <div className="welcome-cta">
          <button 
            className="start-wizard-button primary-cta" 
            onClick={onStartWizard}
          >
            Get My Refund
          </button>
        </div>
        
        <div className="welcome-card">
          <h2>Recover Your Import Duties</h2>
          <p>
            DutyFlow helps you identify and claim refunds for customs duties paid on imported goods 
            that were subsequently exported or destroyed under CBP supervision.
          </p>
          
          <div className="features">
            <div className="feature">
              <div className="feature-icon">📈</div>
              <div className="feature-text">
                <h3>Maximize Your Returns</h3>
                <p>Our analysis engine identifies all eligible duty drawback opportunities.</p>
              </div>
            </div>
            
            <div className="feature">
              <div className="feature-icon">📋</div>
              <div className="feature-text">
                <h3>Simplified Documentation</h3>
                <p>We handle all required forms and documentation for your drawback claims.</p>
              </div>
            </div>
            
            <div className="feature">
              <div className="feature-icon">⏱️</div>
              <div className="feature-text">
                <h3>Save Time and Effort</h3>
                <p>Automate the entire process from data analysis to form submission.</p>
              </div>
            </div>
          </div>
          
          <div className="get-started-section">
            <h3>Ready to get your refund?</h3>
            <p>Follow our simple 3-step process:</p>
            <ol>
              <li><strong>Upload Data</strong> - Provide your import and export transaction records</li>
              <li><strong>Submit Documents</strong> - Upload required supporting documentation</li>
              <li><strong>Generate Form</strong> - We'll prepare your CBP Form 7551 for submission</li>
            </ol>
          </div>
        </div>
        
        <div className="document-requirements-card">
          <h2>Document Requirements</h2>
          <p>To complete your drawback claim, you'll need the following documents:</p>
          
          <div className="requirements-list">
            <div className="requirement-item">
              <h3>📄 CBP Form 7552</h3>
              <p>Proof of duties paid on imported goods</p>
            </div>
            
            <div className="requirement-item">
              <h3>📄 CBP Form 7501</h3>
              <p>Entry Summary showing import details</p>
            </div>
            
            <div className="requirement-item">
              <h3>📄 Proof of Import</h3>
              <p>Documentation proving goods were imported</p>
            </div>
            
            <div className="requirement-item">
              <h3>📄 Proof of Export</h3>
              <p>Documentation proving goods were exported or destroyed</p>
            </div>
          </div>
          
          <p className="note">
            Don't have all these documents? Don't worry! You can still start the process 
            and upload additional documents later.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 