import React from 'react';
import { GlobalHistorySectionStyles as styles } from '../cssmodules';

interface GlobalHistorySectionProps {
  onViewAllQuizzes: () => void;
}

const GlobalHistorySection: React.FC<GlobalHistorySectionProps> = ({ onViewAllQuizzes }) => {
  return (
    <div className={styles.globalHistorySection}>
      <div className={styles.globalHistoryHeader}>
        <button 
          className={styles.showAllButton}
          onClick={onViewAllQuizzes}
        >
          📚 Show All Previous Quizzes
        </button>
      </div>
    </div>
  );
};

export default GlobalHistorySection;
