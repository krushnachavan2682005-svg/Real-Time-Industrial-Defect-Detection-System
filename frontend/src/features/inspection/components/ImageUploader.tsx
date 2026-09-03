import React, { useRef, useState } from 'react';

interface Props {
  onFileSelect: (file: File) => void;
  isPending: boolean;
}

export const ImageUploader: React.FC<Props> = ({ onFileSelect, isPending }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files[0]);
    }
  };

  const handleFiles = (file: File) => {
    if (isPending) return;
    // Basic validation
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      alert('Unsupported file type. Please upload a JPEG or PNG.');
      return;
    }
    onFileSelect(file);
  };

  const onButtonClick = () => {
    if (isPending) return;
    inputRef.current?.click();
  };

  return (
    <div
      className={`image-uploader ${dragActive ? 'drag-active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={onButtonClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg, image/png, image/jpg"
        onChange={handleChange}
        disabled={isPending}
      />
      <div className="upload-icon">📁</div>
      <h3>Click or drag image to upload</h3>
      <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Supported formats: JPEG, PNG</p>
    </div>
  );
};
