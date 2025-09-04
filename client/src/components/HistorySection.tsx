import React from "react";
import { HistorySectionStyles as styles } from "../cssmodules";
import type { QuizResult } from "../types/quiz";
import { Link } from "react-router-dom";
import WikipediaEnhancementBadge from "./WikipediaEnhancementBadge";

interface HistorySectionProps {
  quizHistory: QuizResult[];
}

const HistorySection: React.FC<HistorySectionProps> = ({ quizHistory }) => {
  console.log(quizHistory);
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
        <h3 className={styles.historyTitle}>Recently Generated Quizzes</h3>
        <Link to="/history" className={styles.historySubtitle}>
          view all quizzes
        </Link>
      </div>
      <ul className={styles.historyList}>
        {quizHistory.slice(0, 5).map((result, index) => (
          <li key={index} className={styles.historyItem}>
            <div className={styles.historyItemHeader}>
              <div
                style={{ display: "flex", alignItems: "center", gap: "8px" }}
              >
                <h4 className={styles.historyItemTitle}>{result.topic}</h4>
                {result.wikipediaEnhanced && (
                  <WikipediaEnhancementBadge compact />
                )}
              </div>
              <div className={styles.historyItemScore}>
                {result.personal_average_score && (
                  <span className={styles.percentageBadge}>
                    {result.personal_average_score > 0
                      ? result.personal_average_score.toFixed(0)
                      : 0}
                    %
                  </span>
                )}
                {result.global_average_score && (
                  <span
                    className={`${styles.percentageBadge} ${styles.global}`}
                  >
                    {result.global_average_score > 0
                      ? result.global_average_score.toFixed(0)
                      : 0}
                    % 🌍
                  </span>
                )}
              </div>
            </div>
            <div className={styles.historyItemDetails}>
              <span className={styles.historyItemDate}>
                {new Date(result.submitted_at).toLocaleDateString()}
                :wa
              </span>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "4px",
                  marginTop: "4px",
                  fontSize: "12px",
                  color: "#6b7280",
                }}
              >
                {result.personal_average_score !== null &&
                  result.personal_average_score !== undefined && (
                    <span style={{ color: "#10b981", fontWeight: "500" }}>
                      📊 Your Avg: {result.personal_average_score.toFixed(1)}% (
                      {result.personal_attempts || 0} attempts)
                    </span>
                  )}
                <span style={{ color: "#1e40af" }}>
                  🌍 Global Avg:{" "}
                  {result.global_average_score !== null &&
                  result.global_average_score !== undefined
                    ? `${result.global_average_score.toFixed(1)}%`
                    : "No data"}{" "}
                  ({result.global_attempts || 0} total)
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HistorySection;
