import React from 'react';
import './StepIndicator.css';

const StepIndicator = ({ steps, currentStepIndex, onStepClick }) => {
  return (
    <div className="step-indicator">
      <div className="step-indicator-container">
        {steps.map((step, index) => {
          const isActive = index === currentStepIndex;
          const isCompleted = index < currentStepIndex;
          const isClickable = index < currentStepIndex || index === currentStepIndex;
          
          const stepClassName = `step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`;
          
          return (
            <div 
              key={step.id}
              className={stepClassName}
              onClick={() => isClickable && onStepClick && onStepClick(index)}
              role={isClickable ? 'button' : undefined}
              tabIndex={isClickable ? 0 : undefined}
            >
              <div className="step-number">
                {isCompleted ? (
                  <span className="step-check">✓</span>
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              <div className="step-label">{step.label}</div>
              
              {index < steps.length - 1 && (
                <div className={`step-connector ${isCompleted ? 'completed' : ''}`}></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicator; 