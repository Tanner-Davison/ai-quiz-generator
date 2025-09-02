export interface WikipediaContext {
  articles: Array<{
    title: string;
    extract: string;
    url: string;
    pageid: number;
  }>;
  keyFacts: string[];
  relatedTopics: string[];
  summary: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  wikipediaSources?: string[];
}

export interface QuizResponse {
  quiz_id?: string;
  topic: string;
  questions: QuizQuestion[];
  generated_at: string;
  wikipediaContext?: WikipediaContext;
}

export interface QuizResult {
  quiz_id: string;
  topic: string;
  user_answers: number[];
  correct_answers: number[];
  score: number;
  total_questions: number;
  percentage: number;
  submitted_at: string;
  feedback: string[];
  wikipediaEnhanced?: boolean;
  average_score?: number;
  total_attempts?: number;
}

export interface QuizHistory {
  id: string;
  topic: string;
  model?: string;
  temperature: number;
  created_at: string;
  question_count: number;
  submission_count: number;
  average_score?: number;
  wikipediaEnhanced?: boolean;
}
