import React from 'react';

interface WikipediaEnhancementBadgeProps {
  compact?: boolean;
  className?: string;
}

const WikipediaEnhancementBadge: React.FC<WikipediaEnhancementBadgeProps> = ({ 
  compact = false, 
  className = '' 
}) => {
  if (compact) {
    return (
      <div 
        className={className}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: '2px 6px',
          borderRadius: '4px',
          backgroundColor: '#f0f9ff',
          border: '1px solid #0ea5e9',
          fontSize: '10px',
          color: '#0369a1',
          fontWeight: '500'
        }}
        title="This quiz was enhanced with Wikipedia data for better accuracy"
      >
        <span>📚</span>
        <span>Enhanced</span>
      </div>
    );
  }

  return (
    <div 
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        borderRadius: '6px',
        backgroundColor: '#f0f9ff',
        border: '1px solid #0ea5e9',
        fontSize: '12px',
        color: '#0369a1',
        fontWeight: '600'
      }}
      title="This quiz was enhanced with Wikipedia data for better accuracy"
    >
      <span>📚</span>
      <span>Wikipedia Enhanced</span>
    </div>
  );
};

export default WikipediaEnhancementBadge;
