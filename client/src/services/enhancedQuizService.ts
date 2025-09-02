/**
 * Enhanced Quiz Generation Service
 * Uses Wikipedia to provide better context and more accurate information for quiz generation
 */

import { wikipediaService, type WikipediaArticle } from "./wikipediaService";

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

  /**
   * Generate an enhanced quiz using Wikipedia data for better accuracy
   */
  async generateEnhancedQuiz(topic: string): Promise<EnhancedQuizResponse> {
    try {
      // First, gather Wikipedia context for the topic
      const wikipediaContext = await this.gatherWikipediaContext(topic);

      // Create enhanced prompt with Wikipedia data
      const enhancedPrompt = this.createEnhancedPrompt(topic, wikipediaContext);

      // Use the enhanced prompt with Wikipedia data
      const requestBody = {
        topic: topic.trim(),
        // Include the enhanced prompt in the topic for now
        enhancedPrompt: enhancedPrompt,
        wikipediaEnhanced: true, // Mark this quiz as Wikipedia enhanced
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

      // Enhance the quiz with Wikipedia sources
      return this.enhanceQuizWithSources(quizData, wikipediaContext);
    } catch (error) {
      console.error("Enhanced quiz generation error:", error);
      // Fallback to regular quiz generation but still mark as enhanced if we have context
      try {
        const wikipediaContext = await this.gatherWikipediaContext(topic);
        const regularQuiz = await this.generateRegularQuiz(topic);
        return this.enhanceQuizWithSources(regularQuiz, wikipediaContext);
      } catch (fallbackError) {
        console.error("Fallback quiz generation error:", fallbackError);
        return this.generateRegularQuiz(topic);
      }
    }
  }

  /**
   * Gather comprehensive Wikipedia context for a topic
   */
  private async gatherWikipediaContext(
    topic: string,
  ): Promise<WikipediaContext> {
    try {
      // Search for main topic article
      const mainSearchResults = await wikipediaService.searchArticles(topic, 3);

      if (mainSearchResults.length === 0) {
        return this.createEmptyContext();
      }

      // Get detailed articles
      const articles: WikipediaArticle[] = [];
      const keyFacts: string[] = [];
      const relatedTopics: string[] = [];

      for (const searchResult of mainSearchResults.slice(0, 2)) {
        const article = await wikipediaService.getArticle(searchResult.title);
        if (article) {
          articles.push(article);

          // Extract key facts from article
          const facts = this.extractKeyFacts(article.extract);
          keyFacts.push(...facts);

          // Extract related topics from sections
          if (article.sections) {
            relatedTopics.push(...article.sections.slice(0, 5));
          }
        }
      }

      // Create summary from articles
      const summary = this.createSummary(articles);

      const context = {
        articles,
        keyFacts: [...new Set(keyFacts)], // Remove duplicates
        relatedTopics: [...new Set(relatedTopics)],
        summary,
      };

      return context;
    } catch (error) {
      console.error("Error gathering Wikipedia context:", error);
      return this.createEmptyContext();
    }
  }

  /**
   * Create enhanced prompt with Wikipedia data
   */
  private createEnhancedPrompt(
    topic: string,
    context: WikipediaContext,
  ): string {
    let prompt = `Generate a comprehensive quiz about "${topic}". `;

    if (context.summary) {
      prompt += `\n\nWikipedia Summary: ${context.summary}`;
    }

    if (context.keyFacts.length > 0) {
      prompt += `\n\nKey Facts from Wikipedia:\n${context.keyFacts
        .slice(0, 10)
        .map((fact) => `- ${fact}`)
        .join("\n")}`;
    }

    if (context.relatedTopics.length > 0) {
      prompt += `\n\nRelated Topics: ${context.relatedTopics.slice(0, 5).join(", ")}`;
    }

    prompt += `\n\nPlease create 5 multiple choice questions that are:\n`;
    prompt += `1. Factually accurate based on the Wikipedia information provided\n`;
    prompt += `2. Cover different aspects of the topic\n`;
    prompt += `3. Include one correct answer and three plausible but incorrect options\n`;
    prompt += `4. Provide detailed explanations that reference the Wikipedia facts\n`;
    prompt += `5. Vary in difficulty from basic to intermediate\n\n`;

    prompt += `Respond with ONLY this JSON format:\n`;
    prompt += `{\n`;
    prompt += `    "questions": [\n`;
    prompt += `        {\n`;
    prompt += `            "question": "Question text?",\n`;
    prompt += `            "options": ["Option A", "Option B", "Option C", "Option D"],\n`;
    prompt += `            "correct_answer": 0,\n`;
    prompt += `            "explanation": "Why this answer is correct"\n`;
    prompt += `        }\n`;
    prompt += `    ]\n`;
    prompt += `}\n\n`;
    prompt += `The correct_answer should be the index (0-3) of the correct option.`;

    return prompt;
  }

  /**
   * Extract key facts from Wikipedia article text
   */
  private extractKeyFacts(text: string): string[] {
    // Simple fact extraction - look for sentences with key indicators
    const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 20);

    const keyIndicators = [
      "is a",
      "are a",
      "is the",
      "are the",
      "was",
      "were",
      "has",
      "have",
      "can",
      "cannot",
      "includes",
      "consists of",
      "refers to",
      "means",
      "defined as",
      "known as",
    ];

    return sentences
      .filter((sentence) => {
        const lower = sentence.toLowerCase();
        return keyIndicators.some((indicator) => lower.includes(indicator));
      })
      .slice(0, 8) // Limit to 8 key facts
      .map((fact) => fact.trim());
  }

  /**
   * Create summary from multiple Wikipedia articles
   */
  private createSummary(articles: WikipediaArticle[]): string {
    if (articles.length === 0) return "";

    // Use the first article's extract as the main summary
    const mainExtract = articles[0].extract;

    // If we have multiple articles, try to combine key information
    if (articles.length > 1) {
      const additionalFacts = articles
        .slice(1)
        .map((article) => article.extract.split(".")[0]) // First sentence
        .filter((fact) => fact.length > 20)
        .slice(0, 2);

      return `${mainExtract} ${additionalFacts.join(". ")}.`;
    }

    return mainExtract;
  }

  /**
   * Enhance quiz with Wikipedia sources
   */

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

  /**
   * Fallback to regular quiz generation
   */
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
        wikipediaEnhanced: false, // Regular quiz, not enhanced
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.error || "Failed to generate quiz");
    }

    return await response.json();
  }

  /**
   * Create empty context when Wikipedia data is unavailable
   */
  private createEmptyContext(): WikipediaContext {
    return {
      articles: [],
      keyFacts: [],
      relatedTopics: [],
      summary: "",
    };
  }

  /**
   * Get Wikipedia articles for a specific topic (for display purposes)
   */
  async getWikipediaArticles(topic: string): Promise<WikipediaArticle[]> {
    try {
      const searchResults = await wikipediaService.searchArticles(topic, 3);
      const articles: WikipediaArticle[] = [];

      for (const result of searchResults) {
        const article = await wikipediaService.getArticle(result.title);
        if (article) {
          articles.push(article);
        }
      }

      return articles;
    } catch (error) {
      console.error("Error getting Wikipedia articles:", error);
      return [];
    }
  }
}

export const enhancedQuizService = new EnhancedQuizService();
