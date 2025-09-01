import React from "react";
import { HistorySectionStyles as styles } from "../cssmodules";
import type { QuizResult } from "../types/quiz";

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
        <h3 className={styles.historyTitle}>Latest Quiz</h3>
        <p className={styles.historySubtitle}>Your recent quiz attempts</p>
      </div>
      <ul className={styles.historyList}>
        {quizHistory.slice(0, 5).map((result, index) => (
          <li key={index} className={styles.historyItem}>
            <div className={styles.historyItemHeader}>
              <h4 className={styles.historyItemTitle}>{result.topic}</h4>
              <div className={styles.historyItemScore}>
                <span className={styles.scoreBadge}>
                  {result.score}/{result.total_questions}
                </span>
                <span className={styles.percentageBadge}>
                  {result.percentage.toFixed(0)}%
                </span>
              </div>
            </div>
            <div className={styles.historyItemDetails}>
              <span className={styles.historyItemDate}>
                {new Date(result.submitted_at).toLocaleDateString()}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HistorySection;
