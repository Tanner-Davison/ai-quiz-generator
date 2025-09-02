import React, { useState, useEffect, useCallback } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useSearchParams,
} from "react-router-dom";
import { AppStyles as styles } from "./cssmodules";
import {
  TopicInputSection,
  QuizSection,
  ResultsSection,
  HistorySection,
  NavigationHeader,
  QuizHistoryPage,
} from "./components";

import type { QuizResponse, QuizResult, QuizHistory } from "./types/quiz";
import { enhancedQuizService } from "./services/enhancedQuizService";
import { scoreService } from "./services/scoreService";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const QuizGeneratorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [topic, setTopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [userAnswers, setUserAnswers] = useState<number[]>([]);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [results, setResults] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [quizHistory, setQuizHistory] = useState<QuizResult[]>([]);
  const [isLoadingQuiz, setIsLoadingQuiz] = useState(false);

  const quizId = searchParams.get("quiz");

  const resetToMainPage = useCallback(() => {
    setTopic("");
    setIsGenerating(false);
    setQuiz(null);
    setUserAnswers([]);
    setIsSubmitted(false);
    setResults(null);
    setError(null);
    setIsLoadingQuiz(false);
  }, []);

  useEffect(() => {
    if (quizId) {
      loadSpecificQuiz(quizId);
    } else {
      loadQuizHistory();
    }
  }, [quizId]);

  useEffect(() => {
    const handleResetQuiz = () => {
      resetToMainPage();
    };

    window.addEventListener('resetQuiz', handleResetQuiz);
    
    return () => {
      window.removeEventListener('resetQuiz', handleResetQuiz);
    };
  }, [resetToMainPage]);

  const loadQuizHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/quiz/history`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || 'Failed to load quiz history');
      }
      
      const historyData: QuizHistory[] = await response.json();
      
      const quizResults = historyData.map((quiz) => {
        const scoreStats = scoreService.getScoreStats(quiz.id);
        return {
          quiz_id: quiz.id,
          topic: quiz.topic,
          user_answers: [],
          correct_answers: [],
          score: 0,
          total_questions: quiz.question_count,
          percentage: 0,
          submitted_at: quiz.created_at,
          feedback: [],
          wikipediaEnhanced: quiz.wikipediaEnhanced || false,
          average_score: scoreStats?.averageScore || quiz.average_score,
          total_attempts: scoreStats?.totalAttempts || quiz.submission_count,
          personal_average_score: scoreStats?.averageScore || null,
          personal_attempts: scoreStats?.totalAttempts || 0,
          global_average_score: quiz.average_score,
          global_attempts: quiz.submission_count
        };
      });
      
      setQuizHistory(quizResults);
    } catch (error) {
      console.error('Error loading quiz history:', error);
    }
  };

  const loadSpecificQuiz = async (quizId: string) => {
    setIsLoadingQuiz(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/quiz/history/${quizId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to load quiz");
      }

      const quizData = await response.json();

      const quizResponse: QuizResponse = {
        quiz_id: quizData.id,
        topic: quizData.topic,
        questions: quizData.questions.map((q: any) => ({
          question: q.question,
          options: q.options,
          correct_answer: q.correct_answer,
          explanation: q.explanation,
        })),
        generated_at: quizData.created_at,
      };

      setQuiz(quizResponse);
      setUserAnswers(new Array(quizResponse.questions.length).fill(-1));
      setIsSubmitted(false);
      setResults(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quiz");
    } finally {
      setIsLoadingQuiz(false);
    }
  };

  const generateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setQuiz(null);
    setUserAnswers([]);
    setIsSubmitted(false);
    setResults(null);

    try {
      const response = await fetch(`${API_BASE_URL}/quiz/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          topic: topic.trim(),
          wikipediaEnhanced: false
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || 'Failed to generate quiz');
      }

      const quizData: QuizResponse = await response.json();
      setQuiz(quizData);
      setUserAnswers(new Array(quizData.questions.length).fill(-1));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateEnhancedQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setQuiz(null);
    setUserAnswers([]);
    setIsSubmitted(false);
    setResults(null);

    try {
      const quizData: QuizResponse = await enhancedQuizService.generateEnhancedQuiz(topic.trim());
      setQuiz(quizData);
      setUserAnswers(new Array(quizData.questions.length).fill(-1));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate enhanced quiz');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...userAnswers];
    newAnswers[questionIndex] = answerIndex;
    setUserAnswers(newAnswers);
  };

  const submitQuiz = async () => {

    if (!quiz) {
      setError('No quiz loaded. Please generate a quiz first.');
      return;
    }

    if (userAnswers.includes(-1)) {
      setError('Please answer all questions before submitting');
      return;
    }

    if (!quiz.quiz_id) {
      setError('Quiz ID is missing. Please generate a new quiz.');
      return;
    }

    try {
      const submissionData = {
        quiz_id: quiz.quiz_id,
        answers: userAnswers,
      };
      
      const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submissionData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || errorData.detail || 'Failed to submit quiz');
      }

      const resultData: QuizResult = await response.json();
      
      const scoreStats = scoreService.calculateAverageScore(resultData.quiz_id, resultData.percentage);
      
      const enhancedResult: QuizResult = {
        ...resultData,
        wikipediaEnhanced: quiz?.wikipediaContext ? true : false,
        average_score: scoreStats.averageScore,
        total_attempts: scoreStats.totalAttempts
      };
      
      setResults(enhancedResult);
      setIsSubmitted(true);
      setQuizHistory((prev) => [enhancedResult, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit quiz');
    }
  };

  const startNewQuiz = () => {
    resetToMainPage();
    window.history.replaceState({}, '', '/');
  };

  return (
    <div className={styles.app}>
      <main className={styles.appMain}>
        {!quiz && (
          <TopicInputSection
            topic={topic}
            setTopic={setTopic}
            isGenerating={isGenerating}
            onGenerateQuiz={generateQuiz}
            onGenerateEnhancedQuiz={generateEnhancedQuiz}
            error={error}
          />
        )}

        {isLoadingQuiz && (
          <div className={styles.loadingState}>
            <div className={styles.spinner}>⏳</div>
            <p>Loading quiz...</p>
          </div>
        )}

        {quiz && (
          <QuizSection
            quiz={quiz}
            userAnswers={userAnswers}
            onAnswerSelect={handleAnswerSelect}
            onSubmitQuiz={submitQuiz}
            onStartNewQuiz={startNewQuiz}
            showResults={isSubmitted && results !== null}
            isSubmitted={isSubmitted}
          />
        )}

        {results && isSubmitted && (
          <ResultsSection
            results={results}
            quiz={quiz}
            onStartNewQuiz={startNewQuiz}
          />
        )}

        <HistorySection quizHistory={quizHistory} />
        

      </main>

      <footer className={styles.appFooter}>
        <b>Github:</b>
        <a href="https://github.com/Tanner-Davison">tanner davison</a>{" "}
      </footer>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className={styles.app}>
        <NavigationHeader />

        <Routes>
          <Route path="/" element={<QuizGeneratorPage />} />
          <Route path="/history" element={<QuizHistoryPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
