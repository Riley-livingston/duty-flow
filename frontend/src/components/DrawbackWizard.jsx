import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './DrawbackWizard.css';
import DocumentRequirements from './DocumentRequirements';
import DocumentUpload from './DocumentUpload';
import ImportAnalyzer from './ImportAnalyzer';
import StepIndicator from './StepIndicator';
import WelcomeScreen from './WelcomeScreen';

const WIZARD_STEPS = {
  WELCOME: 'welcome',
  INSTRUCTIONS: 'instructions',
  UPLOAD_IMPORTS: 'upload_imports',
  UPLOAD_EXPORTS: 'upload_exports',
  ANALYSIS: 'analysis',
  UPLOAD_DOCUMENTS: 'upload_documents',
  GENERATE_FORM: 'generate_form',
  COMPLETED: 'completed'
};

// Define wizard step data
const WIZARD_STEP_DATA = [
  { id: WIZARD_STEPS.WELCOME, label: 'Welcome' },
  { id: WIZARD_STEPS.INSTRUCTIONS, label: 'Instructions' },
  { id: WIZARD_STEPS.UPLOAD_IMPORTS, label: 'Import Data' },
  { id: WIZARD_STEPS.UPLOAD_EXPORTS, label: 'Export Data' },
  { id: WIZARD_STEPS.ANALYSIS, label: 'Analysis' },
  { id: WIZARD_STEPS.UPLOAD_DOCUMENTS, label: 'Documents' },
  { id: WIZARD_STEPS.GENERATE_FORM, label: 'Generate Form' },
  { id: WIZARD_STEPS.COMPLETED, label: 'Completed' }
];

function DrawbackWizard() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [currentStep, setCurrentStep] = useState(WIZARD_STEPS.WELCOME);
  const [importData, setImportData] = useState(null);
  const [exportData, setExportData] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [importId, setImportId] = useState(null);
  const [exportId, setExportId] = useState(null);
  const [generatedFormPath, setGeneratedFormPath] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Calculate progress percentage based on current step
  const calculateProgress = () => {
    const steps = Object.values(WIZARD_STEPS);
    const currentIndex = steps.indexOf(currentStep);
    return Math.round((currentIndex / (steps.length - 1)) * 100);
  };

  // Get current step index
  const getCurrentStepIndex = () => {
    return WIZARD_STEP_DATA.findIndex(step => step.id === currentStep);
  };

  // Handle step navigation when clicking on step indicator
  const handleStepClick = (stepIndex) => {
    const targetStep = WIZARD_STEP_DATA[stepIndex].id;
    
    // Check if we can navigate to this step
    if (stepIndex <= getCurrentStepIndex()) {
      setCurrentStep(targetStep);
    } else if (stepIndex === getCurrentStepIndex() + 1) {
      // Allow going to next step if current step allows it
      if (currentStep === WIZARD_STEPS.WELCOME) {
        setCurrentStep(WIZARD_STEPS.INSTRUCTIONS);
      } else if (currentStep === WIZARD_STEPS.INSTRUCTIONS) {
        setCurrentStep(WIZARD_STEPS.UPLOAD_IMPORTS);
      } else if (currentStep === WIZARD_STEPS.UPLOAD_IMPORTS && importData) {
        setCurrentStep(WIZARD_STEPS.UPLOAD_EXPORTS);
      } else if (currentStep === WIZARD_STEPS.UPLOAD_EXPORTS) {
        handleAnalyzeData();
      } else if (currentStep === WIZARD_STEPS.ANALYSIS && analysisResults) {
        setCurrentStep(WIZARD_STEPS.UPLOAD_DOCUMENTS);
      } else if (currentStep === WIZARD_STEPS.UPLOAD_DOCUMENTS) {
        setCurrentStep(WIZARD_STEPS.GENERATE_FORM);
      }
    }
  };

  // Handle file uploads for import data
  const handleImportUploaded = (data) => {
    console.log("Import document uploaded:", data);
    
    if (!data || !data.id) {
      setError("Error: Uploaded file didn't return a valid document ID");
      return;
    }
    
    setImportData(data);
    setImportId(data.id);
    setCurrentStep(WIZARD_STEPS.UPLOAD_EXPORTS);
  };

  // Handle file uploads for export data
  const handleExportUploaded = (data) => {
    console.log("Export document uploaded:", data);
    
    if (!data || !data.id) {
      setError("Error: Uploaded file didn't return a valid document ID");
      return;
    }
    
    // Store the export data and ID in state for later use
    setExportData(data);
    setExportId(data.id);
    console.log("Setting exportId to:", data.id);
    
    // IMPORTANT: Pass the exportId directly rather than relying on state
    // This ensures the export ID is available immediately for analysis
    handleAnalyzeData(data.id);
  };

  // Handle analysis of import/export data
  // Modified to accept a direct exportId parameter
  const handleAnalyzeData = (directExportId = null) => {
    setCurrentStep(WIZARD_STEPS.ANALYSIS);
    setIsLoading(true);
    
    // Check if importId is valid
    if (!importId) {
      setError("No import data found. Please upload your import data first.");
      setIsLoading(false);
      return;
    }
    
    // Use the direct export ID if provided, otherwise fall back to state
    // This ensures that when called directly after upload, we use the correct ID
    const actualExportId = directExportId || exportId;
    
    // Build URL with proper parameter handling
    const analyzeUrl = `http://localhost:5000/api/analyze?import_id=${importId}${actualExportId ? `&export_id=${actualExportId}` : ''}`;
    
    // Log the analyze URL and exportId to debug
    console.log("Analyze URL:", analyzeUrl);
    console.log("Using exportId:", actualExportId);
    
    // Call API to analyze the data
    fetch(analyzeUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Analysis failed with status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Analysis results:", data);
        setAnalysisResults(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error analyzing data:', error);
        setError(error.message || 'An error occurred during analysis');
        setIsLoading(false);
      });
  };

  // Handle starting the wizard from welcome screen
  const handleStartWizard = () => {
    setCurrentStep(WIZARD_STEPS.INSTRUCTIONS);
  };

  // Handle generating the CBP Form 7551
  const handleGenerateForm = () => {
    setIsLoading(true);
    
    // Get form data from the form elements
    const formData = {
      company_name: document.getElementById('companyName').value,
      company_address: document.getElementById('companyAddress').value,
      company_city: document.getElementById('companyCity').value,
      company_state: document.getElementById('companyState').value,
      company_zip: document.getElementById('companyZip').value,
      company_ein: document.getElementById('companyEin').value,
      contact_name: document.getElementById('contactName').value,
      contact_phone: document.getElementById('contactPhone').value,
      contact_email: document.getElementById('contactEmail').value,
      results_file: analysisResults?.results_file || ''
    };
    
    // Call API to generate form
    fetch('http://localhost:5000/api/generate-form-wizard', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Form generation failed with status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      setGeneratedFormPath(data.form_path);
      setCurrentStep(WIZARD_STEPS.COMPLETED);
      setIsLoading(false);
    })
    .catch(error => {
      console.error('Error generating form:', error);
      setError(error.message || 'An error occurred during form generation');
      setIsLoading(false);
    });
  };

  // Render different content based on the current step
  const renderStepContent = () => {
    switch (currentStep) {
      case WIZARD_STEPS.WELCOME:
        return (
          <WelcomeScreen onStartWizard={handleStartWizard} />
        );

      case WIZARD_STEPS.INSTRUCTIONS:
        return (
          <div className="wizard-instructions">
            <h2>How to Get Your Drawback Refund</h2>
            <p>Follow these steps to analyze your import/export data and generate the required documentation for your duty drawback claim.</p>
            
            <div className="action-buttons top-action-buttons">
              <button className="primary-button" onClick={() => setCurrentStep(WIZARD_STEPS.UPLOAD_IMPORTS)}>
                Skip to Import Upload →
              </button>
            </div>
            
            <div className="instruction-steps">
              <div className="instruction-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Upload Import Data</h3>
                  <p>Provide your import transaction data in CSV format. This should include entry numbers, product IDs, import dates, quantities, and duty paid.</p>
                </div>
              </div>
              
              <div className="instruction-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Upload Export Data</h3>
                  <p>Provide your export transaction data in CSV format. This should include export references, product IDs, export dates, quantities, and destinations.</p>
                </div>
              </div>
              
              <div className="instruction-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Upload Supporting Documents</h3>
                  <p>Upload the required documentation such as CBP Form 7501, commercial invoices, and proof of export.</p>
                </div>
              </div>
              
              <div className="instruction-step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Review Analysis</h3>
                  <p>Review the analysis of eligible transactions and potential refund amounts.</p>
                </div>
              </div>
              
              <div className="instruction-step">
                <div className="step-number">5</div>
                <div className="step-content">
                  <h3>Generate CBP Form 7551</h3>
                  <p>Generate the completed CBP Form 7551 (Drawback Entry) for your claim submission.</p>
                </div>
              </div>
            </div>

            <div className="document-requirements-section">
              <h3>Required Documents</h3>
              <DocumentRequirements readOnly={true} showDirectActionButtons={false} />
            </div>
            
            <div className="action-buttons">
              <button className="primary-button" onClick={() => setCurrentStep(WIZARD_STEPS.UPLOAD_IMPORTS)}>
                Continue to Import Upload
              </button>
            </div>
          </div>
        );

      case WIZARD_STEPS.UPLOAD_IMPORTS:
        return (
          <div className="wizard-upload-imports">
            <h2>Step 1: Upload Import Data</h2>
            <p>Upload a CSV file containing your import transaction data.</p>
            <p className="help-text">Need a template? <a href="/templates/import_template.csv" download>Download Import CSV Template</a></p>
            
            <DocumentUpload 
              onDocumentUploaded={handleImportUploaded}
              documentType="import_data"
              documentTypeLabel="Import Transaction Data"
              acceptedFileTypes=".csv"
              redirectAfterUpload={false}
            />
            
            <div className="action-buttons">
              <button className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.INSTRUCTIONS)}>
                Back
              </button>
            </div>
          </div>
        );

      case WIZARD_STEPS.UPLOAD_EXPORTS:
        return (
          <div className="wizard-upload-exports">
            <h2>Step 2: Upload Export Data</h2>
            <p>Upload a CSV file containing your export transaction data.</p>
            <p className="help-text">Need a template? <a href="/templates/export_template.csv" download>Download Export CSV Template</a></p>
            
            <DocumentUpload 
              onDocumentUploaded={handleExportUploaded}
              documentType="export_data"
              documentTypeLabel="Export Transaction Data"
              acceptedFileTypes=".csv"
              redirectAfterUpload={false}
            />
            
            <div className="action-buttons">
              <button className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.UPLOAD_IMPORTS)}>
                Back
              </button>
              <button className="primary-button" onClick={() => handleAnalyzeData(null)}>
                Skip (Import Only Analysis)
              </button>
            </div>
          </div>
        );

      case WIZARD_STEPS.UPLOAD_DOCUMENTS:
        return (
          <div className="wizard-upload-documents">
            <h2>Step 4: Upload Supporting Documents</h2>
            <p>Upload the required documentation to support your drawback claim.</p>
            
            <DocumentRequirements 
              importId={importId}
              exportId={exportId}
              onComplete={() => setCurrentStep(WIZARD_STEPS.GENERATE_FORM)}
            />
            
            <div className="action-buttons">
              <button className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.ANALYSIS)}>
                Back
              </button>
              <button className="primary-button" onClick={() => setCurrentStep(WIZARD_STEPS.GENERATE_FORM)}>
                Continue to Form Generation
              </button>
            </div>
          </div>
        );

      case WIZARD_STEPS.ANALYSIS:
        return (
          <div className="wizard-analysis">
            <h2>Step 3: Drawback Analysis</h2>
            
            {isLoading ? (
              <div className="loading-indicator">
                <p>Analyzing your data...</p>
              </div>
            ) : analysisResults ? (
              <div className="analysis-results">
                <div className="summary-box">
                  <h3>Summary</h3>
                  <div className="summary-stats">
                    <div className="stat">
                      <span className="stat-label">Eligible Transactions</span>
                      <span className="stat-value">{analysisResults.eligible_transactions}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Potential Refund</span>
                      <span className="stat-value">${analysisResults.potential_refund.toFixed(2)}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Export Matches</span>
                      <span className="stat-value">{analysisResults.matched_exports}</span>
                    </div>
                  </div>
                </div>
                
                <div className="matches-table">
                  <h3>Import-Export Matches</h3>
                  <table>
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
                      {analysisResults.matches && analysisResults.matches.map((match, idx) => (
                        <tr key={idx}>
                          <td>{match.product_id}</td>
                          <td>{new Date(match.import_date).toLocaleDateString()}</td>
                          <td>{match.import_qty}</td>
                          <td>${match.duty_paid.toFixed(2)}</td>
                          <td>{match.export_date ? new Date(match.export_date).toLocaleDateString() : 'N/A'}</td>
                          <td>{match.export_qty || 'N/A'}</td>
                          <td>${match.refund_amount.toFixed(2)}</td>
                        </tr>
                      ))}
                      {(!analysisResults.matches || analysisResults.matches.length === 0) && (
                        <tr>
                          <td colSpan="7" className="no-data">No matches found</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                
                {analysisResults.unmatched_imports && analysisResults.unmatched_imports.length > 0 && (
                  <div className="unmatched-imports">
                    <h3>Unmatched Imports</h3>
                    <p>These imports have not been matched with exports. Some may be eligible for future exports.</p>
                    <table>
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
                        {analysisResults.unmatched_imports.map((item, idx) => (
                          <tr key={idx}>
                            <td>{item.product_id}</td>
                            <td>{new Date(item.import_date).toLocaleDateString()}</td>
                            <td>{item.quantity}</td>
                            <td>${item.duty_paid.toFixed(2)}</td>
                            <td>
                              <span className={`status ${item.eligible_for_future ? 'eligible' : 'ineligible'}`}>
                                {item.eligible_for_future ? 'Eligible for Future' : 'Ineligible'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                
                <div className="action-buttons">
                  <button className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.UPLOAD_EXPORTS)}>
                    Back
                  </button>
                  <button className="primary-button" onClick={() => setCurrentStep(WIZARD_STEPS.UPLOAD_DOCUMENTS)}>
                    Continue to Documents
                  </button>
                </div>
              </div>
            ) : (
              <p>No analysis results available.</p>
            )}
          </div>
        );

      case WIZARD_STEPS.GENERATE_FORM:
        return (
          <div className="wizard-generate-form">
            <h2>Step 5: Generate CBP Form 7551</h2>
            <p>Generate the CBP Form 7551 (Drawback Entry) for your claim submission.</p>
            
            <div className="company-info-form">
              <h3>Company Information</h3>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleGenerateForm();
              }}>
                <div className="form-group">
                  <label htmlFor="companyName">Company Name</label>
                  <input type="text" id="companyName" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="companyAddress">Address</label>
                  <input type="text" id="companyAddress" required />
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="companyCity">City</label>
                    <input type="text" id="companyCity" required />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="companyState">State</label>
                    <input type="text" id="companyState" required />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="companyZip">ZIP</label>
                    <input type="text" id="companyZip" required />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="companyEin">EIN/Tax ID</label>
                  <input type="text" id="companyEin" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="contactName">Contact Name</label>
                  <input type="text" id="contactName" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="contactPhone">Phone</label>
                  <input type="tel" id="contactPhone" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="contactEmail">Email</label>
                  <input type="email" id="contactEmail" required />
                </div>
                
                <div className="action-buttons">
                  <button type="button" className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.ANALYSIS)}>
                    Back
                  </button>
                  <button type="submit" className="primary-button" disabled={isLoading}>
                    {isLoading ? 'Generating...' : 'Generate Form'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        );

      case WIZARD_STEPS.COMPLETED:
        return (
          <div className="wizard-completed">
            <h2>Success! Your CBP Form 7551 is Ready</h2>
            <div className="completion-message">
              <div className="success-icon">✓</div>
              <p>Your drawback entry form has been successfully generated and is ready for download.</p>
            </div>
            
            <div className="form-preview">
              <h3>Form Preview</h3>
              <div className="pdf-preview">
                {generatedFormPath && (
                  <iframe 
                    src={`http://localhost:5000/api/preview/${generatedFormPath}`} 
                    title="CBP Form 7551 Preview"
                    width="100%"
                    height="500px"
                  ></iframe>
                )}
              </div>
            </div>
            
            <div className="next-steps">
              <h3>Next Steps</h3>
              <ol>
                <li>Download your completed CBP Form 7551</li>
                <li>Review the form for accuracy</li>
                <li>Print and sign the form</li>
                <li>Submit the form along with supporting documentation to CBP</li>
              </ol>
            </div>
            
            <div className="action-buttons">
              <button className="secondary-button" onClick={() => setCurrentStep(WIZARD_STEPS.GENERATE_FORM)}>
                Back
              </button>
              {generatedFormPath && (
                <a 
                  href={`http://localhost:5000/api/download/${generatedFormPath}`} 
                  download 
                  className="primary-button download-button"
                >
                  Download Form
                </a>
              )}
              <button className="secondary-button" onClick={() => {
                // Reset the wizard
                setCurrentStep(WIZARD_STEPS.WELCOME);
                setImportData(null);
                setExportData(null);
                setAnalysisResults(null);
                setImportId(null);
                setExportId(null);
                setGeneratedFormPath(null);
              }}>
                Start New Claim
              </button>
            </div>
          </div>
        );

      default:
        return <p>Unknown step</p>;
    }
  };

  return (
    <div className="drawback-wizard">
      {/* Step Indicator */}
      {currentStep !== WIZARD_STEPS.WELCOME && (
        <StepIndicator 
          steps={WIZARD_STEP_DATA.slice(1)} // Skip welcome screen in indicator
          currentStepIndex={getCurrentStepIndex() - 1} // Adjust for skip
          onStepClick={(idx) => handleStepClick(idx + 1)} // Adjust for skip
        />
      )}
      
      {/* Main content */}
      <div className="wizard-content">
        {renderStepContent()}
      </div>
      
      {/* Error message */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)} className="dismiss-button">Dismiss</button>
        </div>
      )}
    </div>
  );
}

export default DrawbackWizard;