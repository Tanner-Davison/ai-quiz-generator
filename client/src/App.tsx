import React, { useState, useEffect } from "react";
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
import type { QuizResponse, QuizResult } from "./types/quiz";

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

  useEffect(() => {
    if (quizId) {
      loadSpecificQuiz(quizId);
    } else {
      // Reset to main page state when no quiz ID is present
      resetToMainPage();
    }
  }, [quizId]);

  const resetToMainPage = () => {
    setTopic("");
    setIsGenerating(false);
    setQuiz(null);
    setUserAnswers([]);
    setIsSubmitted(false);
    setResults(null);
    setError(null);
    setIsLoadingQuiz(false);
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
        body: JSON.stringify({ topic: topic.trim() }),
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

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...userAnswers];
    newAnswers[questionIndex] = answerIndex;
    setUserAnswers(newAnswers);
  };

  const submitQuiz = async () => {
    if (userAnswers.includes(-1)) {
      setError('Please answer all questions before submitting');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quiz_id: quiz?.topic || 'quiz',
          answers: userAnswers,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || 'Failed to submit quiz');
      }

      const resultData: QuizResult = await response.json();
      setResults(resultData);
      setIsSubmitted(true);
      setQuizHistory((prev) => [resultData, ...prev]);
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
