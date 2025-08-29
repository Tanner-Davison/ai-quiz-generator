export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

export interface QuizResponse {
  topic: string;
  questions: QuizQuestion[];
  generated_at: string;
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
}
