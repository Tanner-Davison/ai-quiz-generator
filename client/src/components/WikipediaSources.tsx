import React, { useState } from 'react';
import type { WikipediaContext } from '../types/quiz';

interface WikipediaSourcesProps {
  wikipediaContext?: WikipediaContext;
  compact?: boolean;
}

const WikipediaSources: React.FC<WikipediaSourcesProps> = ({ wikipediaContext, compact = false }) => {
  const [showDetails, setShowDetails] = useState(false);

  if (!wikipediaContext || wikipediaContext.articles.length === 0) {
    return null;
  }

  if (compact) {
    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        borderRadius: '4px',
        backgroundColor: '#f0f9ff',
        border: '1px solid #0ea5e9',
        fontSize: '12px',
        color: '#0369a1'
      }}>
        <span>📚</span>
        <span>Enhanced with Wikipedia</span>
      </div>
    );
  }

  return (
    <div style={{
      padding: '12px',
      borderRadius: '8px',
      backgroundColor: '#f8fafc',
      border: '1px solid #e2e8f0',
      marginTop: '12px'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '8px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#1e40af',
          fontWeight: '600'
        }}>
          <span style={{ fontSize: '16px' }}>📚</span>
          <span>Enhanced with Wikipedia Data</span>
        </div>
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          style={{
            background: 'none',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            padding: '4px 8px',
            fontSize: '12px',
            color: '#6b7280',
            cursor: 'pointer'
          }}
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {wikipediaContext.summary && (
        <div style={{
          padding: '8px',
          backgroundColor: '#ffffff',
          borderRadius: '6px',
          border: '1px solid #e5e7eb',
          marginBottom: '8px'
        }}>
          <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', color: '#374151' }}>
            Wikipedia Summary:
          </h4>
          <p style={{
            margin: '0',
            fontSize: '12px',
            color: '#4b5563',
            lineHeight: '1.4'
          }}>
            {wikipediaContext.summary.substring(0, 200)}
            {wikipediaContext.summary.length > 200 ? '...' : ''}
          </p>
        </div>
      )}

      {showDetails && (
        <div>
          {wikipediaContext.articles.map((article, index) => (
            <div
              key={index}
              style={{
                padding: '8px',
                backgroundColor: '#ffffff',
                borderRadius: '6px',
                border: '1px solid #e5e7eb',
                marginBottom: '8px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '4px'
              }}>
                <span style={{ fontSize: '14px' }}>📖</span>
                <a
                  href={`https://en.wikipedia.org/wiki/${encodeURIComponent(article.title.replace(/\s+/g, '_'))}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#2563eb',
                    textDecoration: 'none',
                    fontWeight: '600',
                    fontSize: '14px'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
                  onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
                >
                  {article.title}
                </a>
              </div>
              <p style={{
                fontSize: '12px',
                color: '#4b5563',
                margin: '0',
                lineHeight: '1.4'
              }}>
                {article.extract.substring(0, 150)}
                {article.extract.length > 150 ? '...' : ''}
              </p>
            </div>
          ))}

          {wikipediaContext.keyFacts.length > 0 && (
            <div style={{
              padding: '8px',
              backgroundColor: '#ffffff',
              borderRadius: '6px',
              border: '1px solid #e5e7eb'
            }}>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', color: '#374151' }}>
                Key Facts Used:
              </h4>
              <ul style={{
                margin: '0',
                paddingLeft: '16px',
                fontSize: '12px',
                color: '#4b5563'
              }}>
                {wikipediaContext.keyFacts.slice(0, 3).map((fact, index) => (
                  <li key={index} style={{ marginBottom: '2px' }}>
                    {fact.substring(0, 100)}
                    {fact.length > 100 ? '...' : ''}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WikipediaSources;
