import React from "react";
import { HistorySectionStyles as styles } from "../cssmodules";
import type { QuizResult } from "../types/quiz";
import WikipediaEnhancementBadge from "./WikipediaEnhancementBadge";


interface HistorySectionProps {
  quizHistory: QuizResult[];
}

const HistorySection: React.FC<HistorySectionProps> = ({ quizHistory }) => {

  if (quizHistory.length === 0) {
    return (
      <div className={styles.historySection}>
        <div className={styles.emptyHistory}>
          <div className={styles.emptyHistoryIcon}>📚</div>
          <p className={styles.emptyHistoryText}>
            No quiz history yet. Take your first quiz to get started!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.historySection}>
      <div className={styles.historyHeader}>
        <h3 className={styles.historyTitle}>Recent Quiz History</h3>
        <p className={styles.historySubtitle}>Your latest quiz attempts</p>
      </div>
      <ul className={styles.historyList}>
        {quizHistory.slice(0, 5).map((result, index) => (
          <li key={index} className={styles.historyItem}>
            <div className={styles.historyItemHeader}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h4 className={styles.historyItemTitle}>{result.topic}</h4>
                {result.wikipediaEnhanced && (
                  <WikipediaEnhancementBadge compact />
                )}
              </div>
              <div className={styles.historyItemScore}>
                <span className={styles.scoreBadge}>
                  {result.score}/{result.total_questions}
                </span>
                <span className={styles.percentageBadge}>
                  {result.percentage ? result.percentage.toFixed(0) : 0}%
                </span>
              </div>
            </div>
            <div className={styles.historyItemDetails}>
              <span className={styles.historyItemDate}>
                {new Date(result.submitted_at).toLocaleDateString()}
              </span>
              {(result.average_score !== undefined || result.total_attempts !== undefined) && (
                <div style={{
                  display: 'flex',
                  gap: '12px',
                  marginTop: '4px',
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {result.average_score !== undefined && result.average_score !== null && (
                    <span>
                      📊 Avg: {result.average_score.toFixed(1)}%
                    </span>
                  )}
                  {result.total_attempts !== undefined && result.total_attempts !== null && (
                    <span>
                      🔄 Attempts: {result.total_attempts}
                    </span>
                  )}
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HistorySection;
