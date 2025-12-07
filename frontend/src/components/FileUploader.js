import React, { useRef, useState } from 'react';

const FileUploader = ({ onUpload, status }) => {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      setSelectedFile(file);
    } else {
      alert('Please select an Excel file (.xlsx or .xls)');
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleUpload = () => {
    if (selectedFile && onUpload) {
      onUpload(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 ${
          dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-white'
        } transition-colors`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".xlsx,.xls"
          onChange={handleChange}
        />

        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          {selectedFile ? (
            <div className="mt-4">
              <p className="text-sm text-gray-600">Selected file:</p>
              <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                Drag and drop your Excel file here, or
              </p>
              <button
                type="button"
                onClick={handleButtonClick}
                className="mt-2 text-sm font-medium text-primary-600 hover:text-primary-500"
              >
                browse files
              </button>
            </div>
          )}
        </div>
      </div>

      {selectedFile && (
        <div className="mt-4 flex gap-2">
          <button
            onClick={handleUpload}
            disabled={status === 'uploading'}
            className={`flex-1 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              status === 'uploading'
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
            }`}
          >
            {status === 'uploading' ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </span>
            ) : (
              'Upload File'
            )}
          </button>
          <button
            onClick={handleClear}
            disabled={status === 'uploading'}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Clear
          </button>
        </div>
      )}

      <p className="mt-2 text-xs text-gray-500">
        Supported formats: .xlsx, .xls (Max size: 10MB)
      </p>
    </div>
  );
};

export default FileUploader;