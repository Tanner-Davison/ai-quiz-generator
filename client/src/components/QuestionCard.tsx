import React from 'react';
import { QuestionCardStyles as styles } from '../cssmodules';
import type { QuizQuestion } from '../types/quiz';

interface QuestionCardProps {
  question: QuizQuestion;
  questionIndex: number;
  userAnswer: number;
  onAnswerSelect: (questionIndex: number, answerIndex: number) => void;
  showResults?: boolean;
  isSubmitted?: boolean;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  questionIndex,
  userAnswer,
  onAnswerSelect,
  showResults = false,
  isSubmitted = false
}) => {
  const correctAnswer = question.correct_answer;

  return (
    <div className={styles.questionCard}>
      <div className={styles.questionHeader}>
        <div className={styles.questionNumber}>Question {questionIndex + 1}</div>
        <p className={styles.questionText}>{question.question}</p>
      </div>
      
      <ul className={styles.answersList}>
        {question.options.map((option, optionIndex) => {
          const isCorrect = optionIndex === correctAnswer;
          const isSelected = userAnswer === optionIndex;
          const isWrong = isSelected && !isCorrect;
          
          return (
            <li key={optionIndex} className={styles.answerItem}>
              <button
                type="button"
                className={`${styles.answerButton} ${
                  isSelected ? styles.selected : ''
                } ${
                  showResults && isCorrect ? styles.correct : ''
                } ${
                  showResults && isWrong ? styles.incorrect : ''
                }`}
                onClick={() => onAnswerSelect(questionIndex, optionIndex)}
                disabled={isSubmitted}
              >
                                  <span className={styles.answerText}>
                    {String.fromCharCode(65 + optionIndex)}. {option}
                    {showResults && isCorrect && (
                      <span className={styles.correctAnswerLabel}> (Correct)</span>
                    )}
                  </span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default QuestionCard;
