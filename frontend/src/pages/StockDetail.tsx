import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { xbrlApi } from '../services/api';
import { XBRLFileInfo, QualitativeInfo } from '../types';
import './StockDetail.css';

const StockDetail: React.FC = () => {
  const { headItemKey } = useParams<{ headItemKey: string }>();
  const [fileInfo, setFileInfo] = useState<XBRLFileInfo | null>(null);
  const [qualitativeInfo, setQualitativeInfo] = useState<QualitativeInfo[]>([]);
  const [financialData, setFinancialData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'financial' | 'qualitative'>('info');

  useEffect(() => {
    if (headItemKey) {
      loadData();
    }
  }, [headItemKey]);

  const loadData = async () => {
    if (!headItemKey) return;

    try {
      setLoading(true);
      setError(null);

      // ファイル情報を取得
      const info = await xbrlApi.getFileInfo(headItemKey);
      setFileInfo(info);

      // 定性情報を取得
      try {
        const qualitativeResponse = await xbrlApi.getCategoryData(
          headItemKey,
          'qualitative_info',
          1,
          100
        );
        if (qualitativeResponse.data && Array.isArray(qualitativeResponse.data)) {
          setQualitativeInfo(qualitativeResponse.data);
        }
      } catch (err) {
        console.warn('定性情報の取得に失敗:', err);
      }

      // 財務データを取得
      try {
        const financialResponse = await xbrlApi.getCategoryData(
          headItemKey,
          'ix_non_fraction_enriched',
          1,
          100
        );
        if (financialResponse.data && Array.isArray(financialResponse.data)) {
          setFinancialData(financialResponse.data);
        }
      } catch (err) {
        console.warn('財務データの取得に失敗:', err);
      }
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
    return (
      <div className="error">
        エラー: {error}
        <br />
        <Link to="/" className="btn btn-primary" style={{ marginTop: '20px', display: 'inline-block' }}>
          銘柄一覧に戻る
        </Link>
      </div>
    );
  }

  if (!fileInfo) {
    return <div className="error">データが見つかりません</div>;
  }

  return (
    <div className="stock-detail">
      <Link to="/" className="back-link">← 銘柄一覧に戻る</Link>

      <div className="detail-header">
        <h2 className="page-title">
          {fileInfo.header.company_name || fileInfo.header.document_name || '財務諸表'}
        </h2>
        {fileInfo.header.securities_code && (
          <p className="securities-code">証券コード: {fileInfo.header.securities_code}</p>
        )}
        {fileInfo.header.reporting_date && (
          <p className="reporting-date">報告日: {fileInfo.header.reporting_date}</p>
        )}
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          基本情報
        </button>
        <button
          className={`tab ${activeTab === 'financial' ? 'active' : ''}`}
          onClick={() => setActiveTab('financial')}
        >
          財務諸表
        </button>
        <button
          className={`tab ${activeTab === 'qualitative' ? 'active' : ''}`}
          onClick={() => setActiveTab('qualitative')}
        >
          定性情報
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'info' && (
          <div className="card">
            <h3 className="card-title">基本情報</h3>
            <table className="table">
              <tbody>
                <tr>
                  <th>ヘッドアイテムキー</th>
                  <td>{fileInfo.head_item_key}</td>
                </tr>
                {fileInfo.header.company_name && (
                  <tr>
                    <th>会社名</th>
                    <td>{fileInfo.header.company_name}</td>
                  </tr>
                )}
                {fileInfo.header.securities_code && (
                  <tr>
                    <th>証券コード</th>
                    <td>{fileInfo.header.securities_code}</td>
                  </tr>
                )}
                {fileInfo.header.document_name && (
                  <tr>
                    <th>書類名</th>
                    <td>{fileInfo.header.document_name}</td>
                  </tr>
                )}
                {fileInfo.header.reporting_date && (
                  <tr>
                    <th>報告日</th>
                    <td>{fileInfo.header.reporting_date}</td>
                  </tr>
                )}
                {fileInfo.file_path?.path && (
                  <tr>
                    <th>ファイルパス</th>
                    <td>{fileInfo.file_path.path}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'financial' && (
          <div className="card">
            <h3 className="card-title">財務諸表データ</h3>
            {financialData.length === 0 ? (
              <p>財務データがありません</p>
            ) : (
              <div className="data-table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>項目</th>
                      <th>値</th>
                      <th>単位</th>
                      <th>期間</th>
                    </tr>
                  </thead>
                  <tbody>
                    {financialData.slice(0, 50).map((item: any, index: number) => (
                      <tr key={index}>
                        <td>{item.label || item.name || '-'}</td>
                        <td>{item.value !== undefined ? item.value : '-'}</td>
                        <td>{item.unit || '-'}</td>
                        <td>{item.context || item.period || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {financialData.length > 50 && (
                  <p className="data-note">表示件数: 50件 / 全{financialData.length}件</p>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'qualitative' && (
          <div className="card">
            <h3 className="card-title">定性情報</h3>
            {qualitativeInfo.length === 0 ? (
              <p>定性情報がありません</p>
            ) : (
              <div className="qualitative-content">
                {qualitativeInfo.map((item, index) => (
                  <div key={index} className="qualitative-item">
                    <h4 className="qualitative-title">{item.title}</h4>
                    <div className="qualitative-text">
                      {item.content && item.content.length > 0 ? (
                        <ul>
                          {item.content.map((text, textIndex) => (
                            <li key={textIndex}>{text}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>内容がありません</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StockDetail;
