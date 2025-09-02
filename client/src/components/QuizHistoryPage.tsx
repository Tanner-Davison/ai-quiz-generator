import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GlobalHistorySectionStyles as styles } from '../cssmodules';
import type { QuizHistory } from '../types/quiz';
import WikipediaEnhancementBadge from './WikipediaEnhancementBadge';
import { scoreService } from '../services/scoreService';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';



const QuizHistoryPage: React.FC = () => {
  const [quizHistory, setQuizHistory] = useState<QuizHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    fetchQuizHistory();
  }, []);

  const fetchQuizHistory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/quiz/history`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const historyData: QuizHistory[] = await response.json();
      

      
      // Enhance real quiz data with score statistics
      const enhancedHistoryData = historyData.map(quiz => {
        const scoreStats = scoreService.getScoreStats(quiz.id);
        return {
          ...quiz,
          average_score: scoreStats?.averageScore || quiz.average_score,
          submission_count: scoreStats?.totalAttempts || quiz.submission_count,
          wikipediaEnhanced: quiz.wikipediaEnhanced // Preserve the Wikipedia enhancement flag
        };
      });
      
      setQuizHistory(enhancedHistoryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch quiz history');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleBackToMain = () => {
    navigate('/');
  };

  const handleTakeQuiz = (quizId: string) => {
    navigate(`/?quiz=${quizId}`);
  };

  return (
    <div className={styles.quizHistoryPage}>
      <header className={styles.pageHeader}>
        <button 
          className={styles.backButton}
          onClick={handleBackToMain}
        >
          ← Back to Quiz Generator
        </button>
        <h1 className={styles.pageTitle}>All Quiz History</h1>
        <p className={styles.pageSubtitle}>Click on any quiz to take it again</p>

      </header>

      <main className={styles.pageContent}>
        {isLoading && (
          <div className={styles.loadingState}>
            <div className={styles.spinner}>⏳</div>
            <p>Loading quiz history...</p>
          </div>
        )}

        {error && (
          <div className={styles.errorState}>
            <p className={styles.errorText}>❌ {error}</p>
            <button 
              className={styles.retryButton}
              onClick={fetchQuizHistory}
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !error && quizHistory.length > 0 && (
          <div className={styles.historyGrid}>
            {quizHistory.map((quiz) => {

              
              return (
                <div 
                  key={quiz.id} 
                  className={styles.historyCard}
                  onClick={() => handleTakeQuiz(quiz.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleTakeQuiz(quiz.id);
                    }
                  }}
                >
                <div className={styles.historyCardHeader}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <h4 className={styles.historyCardTitle}>{quiz.topic}</h4>
                    {quiz.wikipediaEnhanced && (
                      <WikipediaEnhancementBadge />
                    )}

                  </div>
                  <div className={styles.historyCardMeta}>
                    <span className={styles.modelBadge}>{quiz.model || 'Default'}</span>
                    <span className={styles.tempBadge}>Temp: {quiz.temperature}</span>
                  </div>
                </div>
                
                <div className={styles.historyCardStats}>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Questions:</span>
                    <span className={styles.statValue}>{quiz.question_count}</span>
                  </div>
                  {quiz.average_score !== null && quiz.average_score !== undefined && (
                    <div className={styles.statItem}>
                      <span className={styles.statLabel}>Avg Score:</span>
                      <span className={styles.statValue}>{quiz.average_score.toFixed(1)}%</span>
                    </div>
                  )}
                  {quiz.submission_count > 0 && (
                    <div className={styles.statItem}>
                      <span className={styles.statLabel}>Attempts:</span>
                      <span className={styles.statValue}>{quiz.submission_count}</span>
                    </div>
                  )}
                  {quiz.submission_count > 2 && (() => {
                    const trend = scoreService.getPerformanceTrend(quiz.id);
                    return trend && trend.trend !== 0 && (
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Trend:</span>
                        <span 
                          className={styles.statValue}
                          style={{ 
                            color: trend.improving ? '#22c55e' : '#ef4444',
                            fontWeight: '600'
                          }}
                        >
                          {trend.improving ? '📈' : '📉'} {Math.abs(trend.trend).toFixed(1)}%
                        </span>
                      </div>
                    );
                  })()}
                </div>
                
                <div className={styles.historyCardFooter}>
                  <span className={styles.createdDate}>
                    Created: {formatDate(quiz.created_at)}
                  </span>
                  <div className={styles.takeQuizHint}>
                    🎯 Click to take this quiz
                  </div>
                </div>
              </div>
              );
            })}
          </div>
        )}

        {!isLoading && !error && quizHistory.length === 0 && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>📝</div>
            <h3>No quizzes found</h3>
            <p>No quizzes have been generated yet.</p>
            <p>Go back and create your first quiz to get started!</p>
            <button 
              className={styles.createQuizButton}
              onClick={handleBackToMain}
            >
              Create Your First Quiz
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default QuizHistoryPage;
