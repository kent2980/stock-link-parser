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
  const [financialStatements, setFinancialStatements] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'financial' | 'qualitative'>('info');

  useEffect(() => {
    if (headItemKey) {
      loadData();
    }
  }, [headItemKey]);

  // 財務諸表データを期間ごとにグループ化してテーブル形式に変換
  const formatFinancialStatements = (data: any) => {
    if (!data) {
      console.warn('formatFinancialStatements: data is null or undefined');
      return null;
    }

    // APIレスポンスの構造を確認
    const enrichedData = data.ix_non_fraction_enriched;
    const contextData = data.ix_context;

    if (!enrichedData || !contextData) {
      console.warn('formatFinancialStatements: missing required data', {
        hasEnriched: !!enrichedData,
        hasContext: !!contextData,
        keys: Object.keys(data || {})
      });
      return null;
    }

    const financialItems = (enrichedData.data || enrichedData) || [];
    const contexts = (contextData.data || contextData) || [];

    // コンテキスト情報をマップに変換
    const contextMap: { [key: string]: any } = {};
    contexts.forEach((ctx: any) => {
      const contextId = Array.isArray(ctx.context_id) ? ctx.context_id[0] : ctx.context_id;
      if (contextId) {
        contextMap[contextId] = ctx;
      }
    });

    // ixbrl_roleごとにグループ化
    const roleGroups: { [role: string]: { periods: { [key: string]: any }, items: { [key: string]: any } } } = {};

    financialItems.forEach((item: any) => {
      const role = item.ixbrl_role || item.role || 'その他';
      
      // ロールグループが存在しない場合は作成
      if (!roleGroups[role]) {
        roleGroups[role] = {
          periods: {},
          items: {},
        };
      }

      const periods = roleGroups[role].periods;
      const items = roleGroups[role].items;

      const contextId = Array.isArray(item.context) ? item.context[0] : item.context;
      const context = contextMap[contextId];
      
      // ラベルを取得（優先順位: verboseLabel > standardLabel > 最初のラベル）
      let label = item.name || '-';
      if (item.labels && Array.isArray(item.labels) && item.labels.length > 0) {
        const verboseLabel = item.labels.find((l: any) => 
          l.role && l.role.includes('verboseLabel') && l.lang === 'ja'
        );
        const standardLabel = item.labels.find((l: any) => 
          l.role && l.role.includes('standardLabel') && l.lang === 'ja'
        );
        const jaLabel = item.labels.find((l: any) => l.lang === 'ja');
        
        label = verboseLabel?.label || standardLabel?.label || jaLabel?.label || item.labels[0]?.label || label;
      }

      // 期間情報を取得
      let periodLabel = contextId || '-';
      if (context) {
        const periodStart = context.period_start || context.start_date;
        const periodEnd = context.period_end || context.end_date;
        if (periodStart && periodEnd) {
          periodLabel = `${periodStart} ～ ${periodEnd}`;
        } else if (periodEnd) {
          periodLabel = periodEnd;
        }
      }

      // 数値を取得
      const numeric = item.display_numeric || item.numeric || '-';
      const unit = item.display_scale || (item.scale ? `${Math.pow(10, parseInt(item.scale))}円` : '円') || '-';

      // 期間をキーとしてグループ化
      if (!periods[periodLabel]) {
        periods[periodLabel] = {
          label: periodLabel,
          contextId: contextId,
          context: context,
        };
      }

      // 項目をキーとしてグループ化
      const itemKey = item.name || item.item_key || label;
      if (!items[itemKey]) {
        items[itemKey] = {
          label: label,
          name: item.name,
          values: {},
        };
      }

      items[itemKey].values[periodLabel] = {
        numeric: numeric,
        unit: unit,
        raw: item.numeric,
        scale: item.scale,
      };
    });

    // 各ロールごとに期間と項目をソートして返す
    const result: { [role: string]: { periods: any[], items: any[] } } = {};
    
    Object.keys(roleGroups).forEach((role) => {
      const group = roleGroups[role];
      result[role] = {
        periods: Object.values(group.periods).sort((a: any, b: any) => 
          (a.label || '').localeCompare(b.label || '')
        ),
        items: Object.values(group.items).sort((a: any, b: any) => 
          (a.label || '').localeCompare(b.label || '')
        ),
      };
    });

    return result;
  };

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
          500
        );
        if (qualitativeResponse.data && Array.isArray(qualitativeResponse.data)) {
          setQualitativeInfo(qualitativeResponse.data);
        }
      } catch (err) {
        console.warn('定性情報の取得に失敗:', err);
      }

      // 財務データを取得（旧形式 - 後方互換性のため保持）
      try {
        const financialResponse = await xbrlApi.getCategoryData(
          headItemKey,
          'ix_non_fraction_enriched',
          1,
          500
        );
        if (financialResponse.data && Array.isArray(financialResponse.data)) {
          setFinancialData(financialResponse.data);
        }
      } catch (err) {
        console.warn('財務データの取得に失敗:', err);
      }

      // 正式な財務諸表データを取得（categories=1,3）
      try {
        const statementsResponse = await xbrlApi.getData(headItemKey, '1,3', 1, 500);
        if (statementsResponse.data) {
          const formatted = formatFinancialStatements(statementsResponse.data);
          setFinancialStatements(formatted);
        }
      } catch (err) {
        console.warn('財務諸表データの取得に失敗:', err);
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
            <h3 className="card-title">財務諸表</h3>
            {financialStatements && typeof financialStatements === 'object' && Object.keys(financialStatements).length > 0 ? (
              <div className="financial-statements-container">
                {Object.keys(financialStatements).map((role: string) => {
                  const roleData = financialStatements[role];
                  if (!roleData || !roleData.periods || !roleData.items || roleData.periods.length === 0 || roleData.items.length === 0) {
                    return null;
                  }

                  // ロール名を表示用に整形（URLから最後の部分を取得）
                  const roleDisplayName = role.split('/').pop() || role;

                  return (
                    <div key={role} className="statement-group">
                      <h4 className="statement-group-title">{roleDisplayName}</h4>
                      <table className="financial-statements-table">
                        <thead>
                          <tr>
                            <th className="statement-item-header">項目</th>
                            {roleData.periods.map((period: any, index: number) => (
                              <th key={index} className="statement-period-header">
                                {period.label}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {roleData.items.map((item: any, itemIndex: number) => (
                            <tr key={itemIndex} className="statement-row">
                              <td className="statement-item-label">{item.label}</td>
                              {roleData.periods.map((period: any, periodIndex: number) => {
                                const value = item.values[period.label];
                                return (
                                  <td key={periodIndex} className="statement-value">
                                    {value ? (
                                      <React.Fragment>
                                        <span className="statement-numeric">
                                          {value.numeric !== '-' ? value.numeric : '-'}
                                        </span>
                                        {value.unit && value.numeric !== '-' && (
                                          <span className="statement-unit">{value.unit}</span>
                                        )}
                                      </React.Fragment>
                                    ) : (
                                      <span className="statement-empty">-</span>
                                    )}
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  );
                })}
              </div>
            ) : financialData.length > 0 ? (
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
            ) : (
              <p>財務データがありません</p>
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
