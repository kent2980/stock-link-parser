// APIレスポンスの型定義

export interface XBRLFile {
  head_item_key: string;
  zip_file_name: string;
  file_path?: string;
}

export interface XBRLFileListResponse {
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
  data: XBRLFile[];
}

export interface XBRLFileInfo {
  head_item_key: string;
  file_path: {
    head_item_key: string;
    path: string;
  };
  header: {
    company_name?: string;
    securities_code?: string;
    document_name?: string;
    reporting_date?: string;
    [key: string]: any;
  };
}

export interface QualitativeInfo {
  title: string;
  content: string[];
}

export interface XBRLDataResponse {
  head_item_key: string;
  data: {
    [category: string]: {
      total: number;
      page: number;
      limit: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
      data: any[];
    };
  };
}

export interface CategoryDataResponse {
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
  data: any[];
}

export interface XBRLHeader {
  head_item_key: string;
  company_name?: string;
  securities_code?: string;
  document_name?: string;
  reporting_date?: string;
  [key: string]: any;
}

export interface XBRLHeadersResponse {
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
  headers: XBRLHeader[];
}
