// src/services/api.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const api = {
  fetchData: async (ticker: string, startDate: string, endDate: string) => {
    const response = await axios.post(`${API_URL}/market/fetch`, {
      ticker,
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },
  
  getFiles: async (): Promise<string[]> => {
    const response = await axios.get(`${API_URL}/market/files`);
    return response.data.files;
  },

  analyze: async (filename: string) => {
    const response = await axios.post(`${API_URL}/market/analyze`, {
      filename,
    });
    return response.data;
  },
};