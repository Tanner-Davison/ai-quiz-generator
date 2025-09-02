/**
 * Score Management Service
 * Handles calculation and storage of quiz scores and averages
 */

import type { QuizResult } from '../types/quiz';

export interface ScoreStats {
  averageScore: number;
  totalAttempts: number;
  bestScore: number;
  worstScore: number;
  recentScores: number[];
}

class ScoreService {
  private readonly STORAGE_KEY = 'quiz_scores';

  /**
   * Calculate average score for a quiz based on all attempts
   */
  calculateAverageScore(quizId: string, newScore: number): ScoreStats {
    const allScores = this.getAllScores();
    const quizScores = allScores[quizId] || [];
    
    // Add the new score
    const updatedScores = [...quizScores, newScore];
    
    // Calculate statistics
    const averageScore = updatedScores.reduce((sum, score) => sum + score, 0) / updatedScores.length;
    const bestScore = Math.max(...updatedScores);
    const worstScore = Math.min(...updatedScores);
    const recentScores = updatedScores.slice(-5); // Last 5 attempts
    
    // Save updated scores
    allScores[quizId] = updatedScores;
    this.saveAllScores(allScores);
    
    return {
      averageScore: Math.round(averageScore * 10) / 10, // Round to 1 decimal
      totalAttempts: updatedScores.length,
      bestScore,
      worstScore,
      recentScores
    };
  }

  /**
   * Get score statistics for a specific quiz
   */
  getScoreStats(quizId: string): ScoreStats | null {
    const allScores = this.getAllScores();
    const quizScores = allScores[quizId];
    
    if (!quizScores || quizScores.length === 0) {
      return null;
    }
    
    const averageScore = quizScores.reduce((sum, score) => sum + score, 0) / quizScores.length;
    const bestScore = Math.max(...quizScores);
    const worstScore = Math.min(...quizScores);
    const recentScores = quizScores.slice(-5);
    
    return {
      averageScore: Math.round(averageScore * 10) / 10,
      totalAttempts: quizScores.length,
      bestScore,
      worstScore,
      recentScores
    };
  }

  /**
   * Get all scores for all quizzes
   */
  private getAllScores(): Record<string, number[]> {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error loading scores from localStorage:', error);
      return {};
    }
  }

  /**
   * Save all scores to localStorage
   */
  private saveAllScores(scores: Record<string, number[]>): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(scores));
    } catch (error) {
      console.error('Error saving scores to localStorage:', error);
    }
  }

  /**
   * Clear all scores (for testing/debugging)
   */
  clearAllScores(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  /**
   * Get leaderboard of best average scores
   */
  getLeaderboard(limit: number = 10): Array<{ quizId: string; averageScore: number; totalAttempts: number }> {
    const allScores = this.getAllScores();
    const leaderboard: Array<{ quizId: string; averageScore: number; totalAttempts: number }> = [];
    
    for (const [quizId, scores] of Object.entries(allScores)) {
      if (scores.length > 0) {
        const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        leaderboard.push({
          quizId,
          averageScore: Math.round(averageScore * 10) / 10,
          totalAttempts: scores.length
        });
      }
    }
    
    return leaderboard
      .sort((a, b) => b.averageScore - a.averageScore)
      .slice(0, limit);
  }

  /**
   * Get performance trends for a quiz
   */
  getPerformanceTrend(quizId: string): { improving: boolean; trend: number } {
    const allScores = this.getAllScores();
    const quizScores = allScores[quizId];
    
    if (!quizScores || quizScores.length < 3) {
      return { improving: false, trend: 0 };
    }
    
    // Compare first half vs second half of attempts
    const midPoint = Math.floor(quizScores.length / 2);
    const firstHalf = quizScores.slice(0, midPoint);
    const secondHalf = quizScores.slice(midPoint);
    
    const firstHalfAvg = firstHalf.reduce((sum, score) => sum + score, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, score) => sum + score, 0) / secondHalf.length;
    
    const trend = secondHalfAvg - firstHalfAvg;
    const improving = trend > 0;
    
    return { improving, trend: Math.round(trend * 10) / 10 };
  }
}

export const scoreService = new ScoreService();
