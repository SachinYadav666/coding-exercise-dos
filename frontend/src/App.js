import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProductionDashboard from './components/ProductionDashboard';
import FileUploader from './components/FileUploader';
import ProductionCard from './components/ProductionCard';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [productionItems, setProductionItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);

  // Fetch production items on component mount
  useEffect(() => {
    fetchProductionItems();
  }, []);

  const fetchProductionItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/api/production-items`);
      setProductionItems(response.data.items || []);
    } catch (err) {
      setError('Failed to fetch production items');
      console.error('Error fetching production items:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setUploadStatus('uploading');
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus('success');
      console.log('Upload successful:', response.data);

      // Refresh production items after successful upload
      setTimeout(() => {
        fetchProductionItems();
        setUploadStatus(null);
      }, 2000);
    } catch (err) {
      setUploadStatus('error');
      setError('Failed to upload file. Please try again.');
      console.error('Upload error:', err);

      setTimeout(() => {
        setUploadStatus(null);
      }, 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">
              Production Planning Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {productionItems.length} items
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Upload Production Sheet</h2>
            <FileUploader
              onUpload={handleFileUpload}
              status={uploadStatus}
            />
            {uploadStatus === 'success' && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800">
                  File uploaded successfully! Processing data...
                </p>
              </div>
            )}
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Dashboard Section */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-4">Production Overview</h2>
          <ProductionDashboard items={productionItems} />
        </div>

        {/* Production Items Grid */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Production Line Items</h2>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : productionItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {productionItems.map((item) => (
                <ProductionCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No production items yet
              </h3>
              <p className="text-gray-500">
                Upload a production planning sheet to get started
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;