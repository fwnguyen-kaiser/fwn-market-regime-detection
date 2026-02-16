// frontend/src/pages/TestAPI.tsx
import React, { useState } from 'react';
import { useRegimeAnalysis } from '../hooks/useRegimeAnalysis';

export const TestAPI: React.FC = () => {
  const { loading, error, result, fetchData, analyze, getFiles } = useRegimeAnalysis();
  const [files, setFiles] = useState<string[]>([]);

  const handleFetch = async () => {
    try {
      const response = await fetchData('AAPL', '2024-01-01', '2024-12-31');
      console.log('Fetch response:', response);
      alert(`Success! File: ${response.filename}`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGetFiles = async () => {
    try {
      const fileList = await getFiles();
      setFiles(fileList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnalyze = async (filename: string) => {
    try {
      await analyze(filename);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>API Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>1. Fetch Data</h2>
        <button onClick={handleFetch} disabled={loading}>
          Fetch AAPL 2024 Data
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>2. List Files</h2>
        <button onClick={handleGetFiles} disabled={loading}>
          Get Available Files
        </button>
        {files.length > 0 && (
          <ul>
            {files.map(file => (
              <li key={file}>
                {file}
                <button onClick={() => handleAnalyze(file)}>Analyze</button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h2>Analysis Result</h2>
          <p><strong>Current Regime:</strong> {result.current_regime}</p>
          <p><strong>Total Days:</strong> {result.total_days}</p>
          <p><strong>N States:</strong> {result.n_states}</p>
          <p><strong>Persistence Quality:</strong> {result.persistence.quality}</p>
          <p><strong>Avg Duration:</strong> {result.persistence.avg_duration.toFixed(1)} days</p>
          
          <h3>Recent History:</h3>
          <ul>
            {result.regime_history.slice(-10).map((item, idx) => (
              <li key={idx}>{item.date}: {item.regime}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};