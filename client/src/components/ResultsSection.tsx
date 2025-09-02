import React from "react";
import { ResultsSectionStyles as styles } from "../cssmodules";
import type { QuizResponse, QuizResult } from "../types/quiz";

interface ResultsSectionProps {
  results: QuizResult;
  quiz: QuizResponse | null;
  onStartNewQuiz: () => void;
}

const ResultsSection: React.FC<ResultsSectionProps> = ({
  results,
  quiz,
  onStartNewQuiz,
}) => {
  const scoreThreshold = results.score;
  
  // dynamic score color
  const scoreClass =
    scoreThreshold <= 2
      ? styles.lowScore
      : scoreThreshold < 5
        ? styles.midScore
        : styles.highScore;

  return (
    <div className={`${styles.resultsSection} ${scoreClass}`}>
      <div className={styles.resultsHeader}>
        <h2 className={styles.resultsTitle}>Quiz Results</h2>
        <div className={styles.scoreDisplay}>
          <div className={styles.scoreValue}>{results.score}</div>
          <p className={styles.scoreLabel}>
            out of {results.total_questions} questions
          </p>
          <div className={styles.scoreDetails}>
            <div className={styles.scoreDetail}>
              <div className={styles.scoreDetailValue}>
                {results.percentage.toFixed(0)}%
              </div>
              <div className={styles.scoreDetailLabel}>Score</div>
            </div>
            <div className={styles.scoreDetail}>
              <div className={styles.scoreDetailValue}>{results.score}</div>
              <div className={styles.scoreDetailLabel}>Correct</div>
            </div>
            <div className={styles.scoreDetail}>
              <div className={styles.scoreDetailValue}>
                {results.total_questions - results.score}
              </div>
              <div className={styles.scoreDetailLabel}>Incorrect</div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.feedback}>
        <h3 className={styles.feedbackTitle}>Review</h3>
        {results.feedback.map((_feedback, index) => {
          const userAnswer = results.user_answers?.[index] ?? -1;
          const correctAnswer = quiz?.questions[index]?.correct_answer ?? -1;
          const isCorrect = userAnswer === correctAnswer;

          return (
            <div
              key={index}
              className={`${styles.feedbackItem} ${isCorrect ? styles.correctQuestion : styles.incorrectQuestion}`}
            >
              <h4 className={styles.questionTitle}>
                Question {index + 1}
                <span
                  className={
                    isCorrect ? styles.correctBadge : styles.incorrectBadge
                  }
                >
                  {isCorrect ? "✓ Correct" : "✗ Incorrect"}
                </span>
              </h4>
              {quiz && (
                <p className={styles.explanation}>
                  <strong>Explanation:</strong>{" "}
                  {quiz.questions[index].explanation}
                  {quiz.questions[index].wikipediaSources && quiz.questions[index].wikipediaSources.length > 0 && (
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      marginLeft: '8px',
                      fontSize: '12px',
                      color: '#6b7280'
                    }}>
                      <span>📚</span>
                      <span>Wikipedia enhanced</span>
                    </span>
                  )}
                </p>
              )}
              {!isCorrect && quiz && (
                <div className={styles.answerInfo}>
                  <p className={styles.userAnswer}>
                    <strong>Your answer:</strong>{" "}
                    {String.fromCharCode(65 + userAnswer)}.{" "}
                    {quiz.questions[index].options[userAnswer]}
                  </p>
                  <p className={styles.correctAnswer}>
                    <strong>Correct answer:</strong>{" "}
                    {String.fromCharCode(65 + correctAnswer)}.{" "}
                    {quiz.questions[index].options[correctAnswer]}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className={styles.actions}>
        <button onClick={onStartNewQuiz} className={styles.newQuizBtn}>
          Take Another Quiz
        </button>
      </div>
    </div>
  );
};
export default ResultsSection;
