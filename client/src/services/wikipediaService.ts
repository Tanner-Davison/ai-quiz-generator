export interface WikipediaSearchResult {
  title: string;
  snippet: string;
  pageid: number;
  url: string;
}

export interface WikipediaArticle {
  title: string;
  extract: string;
  url: string;
  pageid: number;
  lastrevid: number;
  sections?: string[];
}

export interface FactCheckResult {
  query: string;
  found: boolean;
  article?: WikipediaArticle;
  searchResults?: WikipediaSearchResult[];
  confidence: 'high' | 'medium' | 'low';
  relevanceScore: number;
}

class WikipediaService {
  private readonly API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

  async searchArticles(query: string, limit: number = 5): Promise<WikipediaSearchResult[]> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/wikipedia/search?query=${encodeURIComponent(query)}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`Wikipedia search failed: ${response.status}`);
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Wikipedia search error:', error);
      return [];
    }
  }

  async getArticle(title: string): Promise<WikipediaArticle | null> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/wikipedia/article/${encodeURIComponent(title)}`);
      
      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      
      return {
        title: data.title,
        extract: data.extract || '',
        url: data.url,
        pageid: data.pageid,
        lastrevid: data.lastrevid,
        sections: data.sections || []
      };
    } catch (error) {
      console.error('Wikipedia article fetch error:', error);
      return null;
    }
  }

  async factCheck(content: string, topic?: string): Promise<FactCheckResult> {
    try {
      const params = new URLSearchParams({
        content: content,
        ...(topic && { topic })
      });

      const response = await fetch(`${this.API_BASE_URL}/wikipedia/fact-check?${params}`);
      
      if (!response.ok) {
        throw new Error(`Fact-check failed: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        query: data.query,
        found: data.found,
        article: data.article,
        searchResults: data.search_results || [],
        confidence: data.confidence,
        relevanceScore: data.relevance_score
      };
    } catch (error) {
      console.error('Fact-checking error:', error);
      return {
        query: content,
        found: false,
        confidence: 'low',
        relevanceScore: 0
      };
    }
  }
}

export const wikipediaService = new WikipediaService();