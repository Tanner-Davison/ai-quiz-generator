
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

  async generateEnhancedQuiz(topic: string): Promise<EnhancedQuizResponse> {
    try {
      const wikipediaContext = await this.gatherWikipediaContext(topic);
      const enhancedPrompt = this.createEnhancedPrompt(topic, wikipediaContext);
      const requestBody = {
        topic: topic.trim(),
        enhancedPrompt: enhancedPrompt,
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
      return this.enhanceQuizWithSources(quizData, wikipediaContext);
    } catch (error) {
      console.error("Enhanced quiz generation error:", error);
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

  private async gatherWikipediaContext(
    topic: string,
  ): Promise<WikipediaContext> {
    try {
      const mainSearchResults = await wikipediaService.searchArticles(topic, 3);

      if (mainSearchResults.length === 0) {
        return this.createEmptyContext();
      }

      const articles: WikipediaArticle[] = [];
      const keyFacts: string[] = [];
      const relatedTopics: string[] = [];

      for (const searchResult of mainSearchResults.slice(0, 2)) {
        const article = await wikipediaService.getArticle(searchResult.title);
        if (article) {
          articles.push(article);

          const facts = this.extractKeyFacts(article.extract);
          keyFacts.push(...facts);

          if (article.sections) {
            relatedTopics.push(...article.sections.slice(0, 5));
          }
        }
      }

      const summary = this.createSummary(articles);

      const context = {
        articles,
        keyFacts: [...new Set(keyFacts)],
        relatedTopics: [...new Set(relatedTopics)],
        summary,
      };

      return context;
    } catch (error) {
      console.error("Error gathering Wikipedia context:", error);
      return this.createEmptyContext();
    }
  }

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

  private extractKeyFacts(text: string): string[] {
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
      .slice(0, 8)
      .map((fact) => fact.trim());
  }

  private createSummary(articles: WikipediaArticle[]): string {
    if (articles.length === 0) return "";

    const mainExtract = articles[0].extract;

    if (articles.length > 1) {
      const additionalFacts = articles
        .slice(1)
        .map((article) => article.extract.split(".")[0])
        .filter((fact) => fact.length > 20)
        .slice(0, 2);

      return `${mainExtract} ${additionalFacts.join(". ")}.`;
    }

    return mainExtract;
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

    return await response.json();
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
