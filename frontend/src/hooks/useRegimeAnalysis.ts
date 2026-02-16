// frontend/src/hooks/useRegimeAnalysis.ts
import { useState } from 'react';
import { api } from '../services/api';
import type { AnalysisResult } from '../types/regime.ts';

export const useRegimeAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const fetchData = async (ticker: string, startDate: string, endDate: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.fetchData(ticker, startDate, endDate);
      return response;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const analyze = async (filename: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyze(filename);
      setResult(data);
      return data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getFiles = async () => {
    try {
      return await api.getFiles();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get files');
      throw err;
    }
  };

  return {
    loading,
    error,
    result,
    fetchData,
    analyze,
    getFiles,
  };
};