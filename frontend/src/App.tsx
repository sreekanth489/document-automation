import React, { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { ExtractedDataDisplay } from './components/ExtractedData';
import { FormFiller } from './components/FormFiller';
import {
  uploadDocuments,
  fillForm,
  PassportData,
  G28Data,
  ExtractedData,
} from './api/client';

type Status = 'idle' | 'uploading' | 'extracting' | 'filling' | 'success' | 'error';

function App() {
  const [passportFile, setPassportFile] = useState<File | null>(null);
  const [g28File, setG28File] = useState<File | null>(null);
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [passport, setPassport] = useState<PassportData | null>(null);
  const [g28, setG28] = useState<G28Data | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState<string>('');
  const [screenshotPath, setScreenshotPath] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!passportFile && !g28File) {
      setMessage('Please select at least one document');
      setStatus('error');
      return;
    }

    setStatus('uploading');
    setMessage('Uploading and extracting data...');

    try {
      const data = await uploadDocuments(passportFile, g28File);
      setExtractedData(data);
      setPassport(data.passport);
      setG28(data.g28);
      setStatus('success');
      setMessage('Data extracted successfully!');
    } catch (error: unknown) {
      setStatus('error');
      const err = error as { response?: { data?: { detail?: string } }; message?: string };
      setMessage(err.response?.data?.detail || err.message || 'Failed to extract data');
    }
  };

  const handleFillForm = async (headless: boolean) => {
    if (!extractedData) {
      setMessage('Please extract data first');
      setStatus('error');
      return;
    }

    setStatus('filling');
    setMessage('Filling the form...');
    setScreenshotPath(null);

    try {
      const response = await fillForm(
        extractedData.session_id,
        passport,
        g28,
        headless
      );

      if (response.success && response.screenshot_path) {
        const filename = response.screenshot_path.split('/').pop();
        setScreenshotPath(`/screenshots/${filename}`);
        setStatus('success');
        setMessage('Form filled successfully!');
      } else {
        setStatus('error');
        setMessage(response.message);
      }
    } catch (error: unknown) {
      setStatus('error');
      const err = error as { response?: { data?: { detail?: string } }; message?: string };
      setMessage(err.response?.data?.detail || err.message || 'Failed to fill form');
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case 'uploading':
      case 'extracting':
      case 'filling':
        return 'loading';
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      default:
        return '';
    }
  };

  return (
    <div className="container">
      <h1>Document Automation</h1>
      <p className="subtitle">
        Upload passport and G-28 documents to automatically fill the immigration form
      </p>

      {message && (
        <div className={`status ${getStatusClass()}`}>
          {message}
        </div>
      )}

      <div className="card">
        <h2>Upload Documents</h2>
        <div className="file-inputs">
          <FileUpload
            label="Passport"
            accept=".pdf,.jpg,.jpeg,.png"
            file={passportFile}
            onFileSelect={setPassportFile}
          />
          <FileUpload
            label="G-28 Form"
            accept=".pdf,.jpg,.jpeg,.png"
            file={g28File}
            onFileSelect={setG28File}
          />
        </div>
        <div className="btn-group">
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={status === 'uploading' || status === 'filling'}
          >
            {status === 'uploading' ? 'Extracting...' : 'Extract Data'}
          </button>
        </div>
      </div>

      {(passport || g28) && (
        <>
          <ExtractedDataDisplay
            passport={passport}
            g28={g28}
            onPassportChange={setPassport}
            onG28Change={setG28}
          />

          <FormFiller
            isLoading={status === 'filling'}
            screenshotPath={screenshotPath}
            onFillForm={handleFillForm}
          />
        </>
      )}
    </div>
  );
}

export default App;
