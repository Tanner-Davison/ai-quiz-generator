
import type { WikipediaArticle } from "./wikipediaService";

export interface EnhancedQuizRequest {
  topic: string;
  useWikipediaEnhancement?: boolean;
}

export interface WikipediaContext {
  articles: WikipediaArticle[];
  keyFacts: string[];
  relatedTopics: string[];
  summary: string;
}

export interface EnhancedQuizResponse {
  quiz_id?: string;
  topic: string;
  questions: Array<{
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
    wikipediaSources?: string[];
  }>;
  generated_at: string;
  wikipediaContext?: WikipediaContext;
}

class EnhancedQuizService {
  private readonly API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:3000";

  async generateEnhancedQuiz(topic: string): Promise<EnhancedQuizResponse> {
    try {
      const requestBody = {
        topic: topic.trim(),
        wikipediaEnhanced: true,
      };

      const response = await fetch(`${this.API_BASE_URL}/quiz/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail?.error || "Failed to generate enhanced quiz",
        );
      }

      const quizData = await response.json();
      
      // Convert backend Wikipedia context to frontend format
      const wikipediaContext: WikipediaContext = {
        articles: quizData.wikipedia_context?.articles || [],
        keyFacts: quizData.wikipedia_context?.key_facts || [],
        relatedTopics: quizData.wikipedia_context?.related_topics || [],
        summary: quizData.wikipedia_context?.summary || ""
      };

      // Add Wikipedia context to quiz data for frontend
      const enhancedQuizData = {
        ...quizData,
        wikipediaContext: wikipediaContext
      };

      return this.enhanceQuizWithSources(enhancedQuizData, wikipediaContext);
    } catch (error) {
      console.error("Enhanced quiz generation error:", error);
      try {
        const regularQuiz = await this.generateRegularQuiz(topic);
        return this.enhanceQuizWithSources(regularQuiz, this.createEmptyContext());
      } catch (fallbackError) {
        console.error("Fallback quiz generation error:", fallbackError);
        return this.generateRegularQuiz(topic);
      }
    }
  }


  private enhanceQuizWithSources(
    quizData: any,
    context: WikipediaContext,
  ): EnhancedQuizResponse {
    const enhancedQuiz = {
      ...quizData,
      wikipediaContext: context,
      wikipediaEnhanced: true,
      questions: quizData.questions.map((question: any) => ({
        ...question,
        wikipediaSources: context.articles.map((article) => article.title),
      })),
    };

    return enhancedQuiz;
  }

  private async generateRegularQuiz(
    topic: string,
  ): Promise<EnhancedQuizResponse> {
    const response = await fetch(`${this.API_BASE_URL}/quiz/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        topic: topic.trim(),
        wikipediaEnhanced: false,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || "Failed to generate quiz");
    }

    const quizData = await response.json();
    
    // Ensure the response has the expected structure
    return {
      ...quizData,
      wikipediaContext: undefined,
      wikipediaEnhanced: false
    };
  }

  private createEmptyContext(): WikipediaContext {
    return {
      articles: [],
      keyFacts: [],
      relatedTopics: [],
      summary: "",
    };
  }

  async getWikipediaArticles(topic: string): Promise<WikipediaArticle[]> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/wikipedia/articles?topic=${encodeURIComponent(topic)}&limit=3`);
      
      if (!response.ok) {
        throw new Error(`Failed to get Wikipedia articles: ${response.status}`);
      }

      const articles = await response.json();
      return articles || [];
    } catch (error) {
      console.error("Error getting Wikipedia articles:", error);
      return [];
    }
  }
}

export const enhancedQuizService = new EnhancedQuizService();
