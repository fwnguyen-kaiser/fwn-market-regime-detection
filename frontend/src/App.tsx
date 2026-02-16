import React, { useState, useEffect } from "react";
import { api } from "./services/api";
import { RegimeChart } from "./components/RegimeChart";
import { CurrentStatus, TripleStats, StabilityMetrics } from "./components/RegimeStats"; // Import lẻ
import { PredictionCard } from "./components/PredictionCard";
import type { AnalysisResult } from "./types/regime";
import "./App.css";

function App() {
  // ... (Giữ nguyên toàn bộ logic state và hàm handle, không thay đổi gì)
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2026-01-01");
  const [files, setFiles] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const fileList = await api.getFiles();
      setFiles(fileList);
      if (fileList.length > 0 && !selectedFile) setSelectedFile(fileList[0]);
    } catch (err) { console.error(err); }
  };

  const handleFetchData = async () => {
    setFetchLoading(true); setError(null);
    try {
      const response = await api.fetchData(ticker, startDate, endDate);
      await loadFiles(); setSelectedFile(response.filename);
    } catch (err: any) { setError(err.response?.data?.detail || "Error fetching data"); } 
    finally { setFetchLoading(false); }
  };

  const handleRunModel = async () => {
    if (!selectedFile) return;
    setLoading(true); setError(null); setAnalysisResult(null);
    try {
      const result = await api.analyze(selectedFile);
      setAnalysisResult(result);
    } catch (err: any) { setError(err.response?.data?.detail || "Analysis failed"); } 
    finally { setLoading(false); }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>
          <span className="brand-icon">Ξ</span> FinViewer
          <span className="brand-tagline">HMM Market Regime Intelligence</span>
        </h1>
      </header>

      <div className="super-grid">
        
        {/* COL 1: SIDEBAR (Rows 1-3) */}
        <div className="area-sidebar">
          <div className="control-panel">
            <h2 className="card-title">DATA CONTROL</h2>
            <div className="compact-form">
              <label>Ticker</label>
              <input type="text" className="input" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} />
            </div>
            <div className="date-row">
              <div className="compact-form">
                <label>Start</label>
                <input type="date" className="input" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
              <div className="compact-form">
                <label>End</label>
                <input type="date" className="input" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleFetchData} disabled={fetchLoading}>
              {fetchLoading ? "SYNCING..." : "SYNC DATA"}
            </button>
            <div className="separator"></div>
            <div className="compact-form">
              <label>Dataset</label>
              <select className="select" value={selectedFile} onChange={(e) => setSelectedFile(e.target.value)}>
                <option value="">-- Select File --</option>
                {files.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
            <button className="btn btn-accent" onClick={handleRunModel} disabled={loading || !selectedFile}>
              {loading ? "RUNNING..." : "RUN MODEL"}
            </button>
          </div>
        </div>

        {/* LOADING & ERROR */}
        {loading && <div className="area-overlay"><div className="spinner"></div></div>}
        {error && <div className="area-overlay error-msg">{error}</div>}

        {/* DATA DISPLAY AREAS */}
        {analysisResult ? (
          <>
            {/* COL 2: PREDICTION (Rows 1-2) */}
            <div className="area-prediction">
              <PredictionCard prediction={analysisResult.prediction} />
            </div>

            {/* COL 3: STATUS (Row 1) */}
            <div className="area-status">
              <CurrentStatus result={analysisResult} />
            </div>

            {/* COL 3: TRIPLE STATS (Row 2) */}
            <div className="area-triple">
              <TripleStats result={analysisResult} />
            </div>

            {/* COL 2 & 3: STABILITY (Row 3) */}
            <div className="area-stability">
              <StabilityMetrics result={analysisResult} />
            </div>

            {/* COL 1-3: CHART (Row 4) */}
            <div className="area-chart">
              <RegimeChart result={analysisResult} />
            </div>
          </>
        ) : !loading && (
          <div className="area-empty">
            <div className="empty-content">
              <h3>READY TO ANALYZE</h3>
              <p>Select dataset to initialize HMM Engine</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;