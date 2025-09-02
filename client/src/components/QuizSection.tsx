import React from "react";
import { QuestionCard, WikipediaSources } from "./index";
import { QuizSectionStyles as styles } from "../cssmodules";
import type { QuizResponse } from "../types/quiz";

interface QuizSectionProps {
  quiz: QuizResponse;
  userAnswers: number[];
  onAnswerSelect: (questionIndex: number, answerIndex: number) => void;
  onSubmitQuiz: () => void;
  onStartNewQuiz: () => void;
  showResults?: boolean;
  isSubmitted?: boolean;
}

const QuizSection: React.FC<QuizSectionProps> = ({
  quiz,
  userAnswers,
  onAnswerSelect,
  onSubmitQuiz,
  onStartNewQuiz,
  showResults = false,
  isSubmitted = false,
}) => {
  return (
    <div className={styles.quizSection}>
      <div className={styles.quizHeader}>
        <h3>
          Generated Quiz Topic:{" "}
          <b>{quiz.topic.charAt(0).toUpperCase() + quiz.topic.slice(1)}</b>
        </h3>
        {!showResults ? (
          <p>Answer all 5 questions to test your knowledge!</p>
        ) : (
          <div className={styles.quizResults}>
            <p className={styles.quizResultsText}>
              Quiz completed! Here are your results:
            </p>
            <div className={styles.quizScore}>
              <span className={styles.scoreValue}>
                {
                  userAnswers.filter(
                    (answer, index) =>
                      answer === quiz.questions[index].correct_answer,
                  ).length
                }
              </span>
              <span className={styles.scoreTotal}>
                / {quiz.questions.length}
              </span>
              <span className={styles.scorePercentage}>
                (
                {Math.round(
                  (userAnswers.filter(
                    (answer, index) =>
                      answer === quiz.questions[index].correct_answer,
                  ).length /
                    quiz.questions.length) *
                    100,
                )}
                %)
              </span>
            </div>
          </div>
        )}
      </div>

      {quiz.wikipediaContext && (
        <WikipediaSources wikipediaContext={quiz.wikipediaContext} />
      )}

      <div className={styles.questionsContainer}>
        {quiz.questions.map((question, questionIndex) => (
          <QuestionCard
            key={questionIndex}
            question={question}
            questionIndex={questionIndex}
            userAnswer={userAnswers[questionIndex]}
            onAnswerSelect={onAnswerSelect}
            showResults={showResults}
            isSubmitted={isSubmitted}
            topic={quiz.topic}
          />
        ))}
      </div>

      {!isSubmitted && (
        <div className={styles.quizActions}>
          <button
            onClick={onSubmitQuiz}
            disabled={userAnswers.includes(-1)}
            className={styles.submitBtn}
          >
            Submit Quiz
          </button>
          <button onClick={onStartNewQuiz} className={styles.newQuizBtn}>
            Start New Quiz
          </button>
        </div>
      )}
    </div>
  );
};

export default QuizSection;
