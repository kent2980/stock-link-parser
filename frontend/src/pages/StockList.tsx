import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { xbrlApi } from '../services/api';
import { XBRLHeader } from '../types';
import './StockList.css';

const StockList: React.FC = () => {
  const [headers, setHeaders] = useState<XBRLHeader[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);

  useEffect(() => {
    loadHeaders();
  }, [page]);

  const loadHeaders = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await xbrlApi.getHeaders(page, 20);
      setHeaders(response.headers);
      setTotalPages(response.pages);
      setHasNext(response.has_next);
      setHasPrev(response.has_prev);
    } catch (err: any) {
      setError(err.message || 'データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (error) {
    return <div className="error">エラー: {error}</div>;
  }

  return (
    <div className="stock-list">
      <h2 className="page-title">銘柄一覧</h2>
      
      {headers.length === 0 ? (
        <div className="no-data">データがありません</div>
      ) : (
        <>
          <div className="header-list">
            {headers.map((header) => (
              <Link
                key={header.head_item_key}
                to={`/stock/${header.head_item_key}`}
                className="header-item"
              >
                <div className="header-item-content">
                  <div className="header-main">
                    <h3 className="header-company-name">
                      {header.company_name || '会社名不明'}
                    </h3>
                    {header.securities_code && (
                      <span className="header-securities-code">
                        {header.securities_code}
                      </span>
                    )}
                  </div>
                  <div className="header-details">
                    {header.document_name && (
                      <span className="header-document-name">
                        {header.document_name}
                      </span>
                    )}
                    {header.reporting_date && (
                      <span className="header-reporting-date">
                        報告日: {header.reporting_date}
                      </span>
                    )}
                  </div>
                </div>
                <div className="header-arrow">→</div>
              </Link>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => setPage(page - 1)}
              disabled={!hasPrev}
            >
              前へ
            </button>
            <span className="current-page">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={!hasNext}
            >
              次へ
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default StockList;
