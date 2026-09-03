import React, { useState } from 'react';
import '../styles.css';
import { ImageUploader } from '../components/ImageUploader';
import { BoundingBoxOverlay } from '../components/BoundingBoxOverlay';
import { InspectionResultPanel } from '../components/InspectionResultPanel';
import { useInspection } from '../hooks/useInspection';

export const InspectionPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const { mutate: runInspection, data: result, isPending, error, reset } = useInspection();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(URL.createObjectURL(file));
    reset(); // Clear previous results
  };

  const handleRunInspection = () => {
    if (selectedFile) {
      runInspection(selectedFile);
    }
  };

  const handleReplace = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    reset();
  };

  return (
    <div className="inspection-container">
      <div className="inspection-header">
        <h1>Live Inspection</h1>
        <p>Upload an industrial surface image for AI inspection</p>
      </div>

      {!selectedFile && (
        <ImageUploader onFileSelect={handleFileSelect} isPending={isPending} />
      )}

      {selectedFile && !result && !isPending && !error && (
        <div className="image-preview-container">
          <div className="image-preview-header">
            <div className="file-info">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">{(selectedFile.size / 1024).toFixed(1)} KB</span>
            </div>
            <div className="preview-actions">
              <button className="btn btn-danger" onClick={handleReplace}>Remove</button>
              <button className="btn btn-primary" onClick={handleRunInspection}>Run Inspection</button>
            </div>
          </div>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
             <img src={previewUrl!} alt="Preview" style={{ width: '100%', height: 'auto', borderRadius: '8px' }} />
          </div>
        </div>
      )}

      {isPending && (
        <div className="loading-state">
          <div className="spinner"></div>
          <h3>Inspecting Surface...</h3>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Running AI Model and Analyzing Defects</p>
        </div>
      )}

      {error && (
        <div className="error-state">
          <h3>Inspection Failed</h3>
          <p>{error.message || 'Unable to process the image. Please try again.'}</p>
          <button className="btn btn-primary" onClick={handleReplace} style={{ marginTop: '1rem' }}>Try Again</button>
        </div>
      )}

      {result && previewUrl && (
        <div className="result-layout">
          <div>
             <div className="image-preview-header" style={{ marginBottom: '1rem', background: 'var(--bg-surface, #1e293b)', padding: '1rem', borderRadius: '8px' }}>
                <span className="file-name">{selectedFile?.name}</span>
                <button className="btn btn-primary" onClick={handleReplace}>Upload New Image</button>
             </div>
             <BoundingBoxOverlay imageUrl={previewUrl} defects={result.defects} />
          </div>
          <div>
            <InspectionResultPanel data={result} />
          </div>
        </div>
      )}
    </div>
  );
};
