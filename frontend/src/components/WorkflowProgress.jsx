import React from 'react';
import './WorkflowProgress.css';

const WorkflowProgress = ({ currentStep }) => {
  const steps = [
    { id: 'upload', label: 'Upload Data', description: 'Upload import and export transaction data' },
    { id: 'analyze', label: 'Analyze', description: 'Identify duty drawback opportunities' },
    { id: 'document', label: 'Upload Documents', description: 'Provide supporting documentation' },
    { id: 'submit', label: 'Submit', description: 'Submit your drawback claim' }
  ];

  return (
    <div className="workflow-progress">
      <h3>Duty Drawback Process</h3>
      <div className="workflow-steps">
        {steps.map((step, index) => (
          <div 
            key={step.id} 
            className={`workflow-step ${currentStep >= index ? 'active' : ''} ${currentStep === index ? 'current' : ''}`}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-content">
              <div className="step-label">{step.label}</div>
              <div className="step-description">{step.description}</div>
            </div>
            {index < steps.length - 1 && <div className="step-connector"></div>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowProgress; 