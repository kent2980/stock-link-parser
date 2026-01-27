import axios from 'axios';
import {
  XBRLFileListResponse,
  XBRLFileInfo,
  XBRLDataResponse,
  CategoryDataResponse,
  XBRLHeadersResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const xbrlApi = {
  // XBRLヘッダー一覧を取得
  getHeaders: async (page: number = 1, limit: number = 20): Promise<XBRLHeadersResponse> => {
    const response = await api.get('/api/v1/xbrl/headers', {
      params: { page, limit },
    });
    return response.data;
  },

  // XBRLファイル一覧を取得
  getFiles: async (page: number = 1, limit: number = 20): Promise<XBRLFileListResponse> => {
    const response = await api.get('/api/v1/xbrl/files', {
      params: { page, limit },
    });
    return response.data;
  },

  // 特定のXBRLファイルの情報を取得
  getFileInfo: async (headItemKey: string): Promise<XBRLFileInfo> => {
    const response = await api.get(`/api/v1/xbrl/files/${headItemKey}`);
    return response.data;
  },

  // XBRLデータを取得
  getData: async (
    headItemKey: string,
    categories?: string,
    page: number = 1,
    limit: number = 100
  ): Promise<XBRLDataResponse> => {
    const response = await api.get(`/api/v1/xbrl/files/${headItemKey}/data`, {
      params: { categories, page, limit },
    });
    return response.data;
  },

  // 特定のカテゴリのデータを取得
  getCategoryData: async (
    headItemKey: string,
    category: string,
    page: number = 1,
    limit: number = 100
  ): Promise<CategoryDataResponse> => {
    const response = await api.get(
      `/api/v1/xbrl/files/${headItemKey}/data/${category}`,
      {
        params: { page, limit },
      }
    );
    return response.data;
  },
};

export default api;
