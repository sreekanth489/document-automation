import React from 'react';

interface FormFillerProps {
  isLoading: boolean;
  screenshotPath: string | null;
  onFillForm: (headless: boolean) => void;
}

export function FormFiller({ isLoading, screenshotPath, onFillForm }: FormFillerProps) {
  return (
    <div className="card">
      <h2>Form Automation</h2>
      <p style={{ marginBottom: '1rem', color: '#666' }}>
        Click to auto-fill the form with the extracted data.
      </p>

      <div className="btn-group">
        <button
          className="btn btn-secondary"
          onClick={() => onFillForm(false)}
          disabled={isLoading}
        >
          {isLoading ? 'Filling Form...' : 'Fill Form (Visible Browser)'}
        </button>
        <button
          className="btn btn-primary"
          onClick={() => onFillForm(true)}
          disabled={isLoading}
        >
          {isLoading ? 'Filling Form...' : 'Fill Form (Background)'}
        </button>
      </div>

      {screenshotPath && (
        <div className="screenshot-container">
          <h3 style={{ marginTop: '1.5rem', marginBottom: '0.5rem' }}>
            Filled Form Screenshot
          </h3>
          <img
            src={screenshotPath}
            alt="Filled form screenshot"
          />
        </div>
      )}
    </div>
  );
}
