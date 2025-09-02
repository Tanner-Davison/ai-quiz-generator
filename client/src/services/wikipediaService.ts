
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
  private readonly baseUrl = 'https://en.wikipedia.org/api/rest_v1';
  private readonly searchUrl = 'https://en.wikipedia.org/w/api.php';

  async searchArticles(query: string, limit: number = 5): Promise<WikipediaSearchResult[]> {
    try {
      const searchQuery = this.cleanQuery(query);
      const params = new URLSearchParams({
        action: 'query',
        format: 'json',
        list: 'search',
        srsearch: searchQuery,
        srlimit: limit.toString(),
        srprop: 'snippet|size',
        origin: '*'
      });

      const response = await fetch(`${this.searchUrl}?${params}`);
      
      if (!response.ok) {
        throw new Error(`Wikipedia search failed: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.query || !data.query.search) {
        return [];
      }

      return data.query.search.map((result: any) => ({
        title: result.title,
        snippet: this.cleanSnippet(result.snippet),
        pageid: result.pageid,
        url: `https://en.wikipedia.org/wiki/${encodeURIComponent(result.title.replace(/\s+/g, '_'))}`
      }));
    } catch (error) {
      console.error('Wikipedia search error:', error);
      return [];
    }
  }

  async getArticle(title: string): Promise<WikipediaArticle | null> {
    try {
      const cleanTitle = title.replace(/\s+/g, '_');
      const response = await fetch(`${this.baseUrl}/page/summary/${encodeURIComponent(cleanTitle)}`);
      
      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      
      return {
        title: data.title,
        extract: data.extract || '',
        url: data.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${cleanTitle}`,
        pageid: data.pageid,
        lastrevid: data.rev,
        sections: data.sections?.map((s: any) => s.title) || []
      };
    } catch (error) {
      console.error('Wikipedia article fetch error:', error);
      return null;
    }
  }

  async factCheck(content: string, topic?: string): Promise<FactCheckResult> {
    try {
      const keyTerms = this.extractKeyTerms(content, topic);
      
      if (keyTerms.length === 0) {
        return {
          query: content,
          found: false,
          confidence: 'low',
          relevanceScore: 0
        };
      }

      const primaryTerm = keyTerms[0];
      const searchResults = await this.searchArticles(primaryTerm, 3);
      
      if (searchResults.length === 0) {
        return {
          query: content,
          found: false,
          confidence: 'low',
          relevanceScore: 0
        };
      }

      const bestMatch = searchResults[0];
      const article = await this.getArticle(bestMatch.title);
      
      if (!article) {
        return {
          query: content,
          found: false,
          searchResults,
          confidence: 'low',
          relevanceScore: 0.3
        };
      }

      const relevanceScore = this.calculateRelevanceScore(content, article, keyTerms);
      
      let confidence: 'high' | 'medium' | 'low' = 'low';
      if (relevanceScore > 0.7) confidence = 'high';
      else if (relevanceScore > 0.4) confidence = 'medium';

      return {
        query: content,
        found: true,
        article,
        searchResults,
        confidence,
        relevanceScore
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

  private extractKeyTerms(content: string, topic?: string): string[] {
    const stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
      'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
      'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    ]);

    const fullText = topic ? `${topic} ${content}` : content;
    
    const words = fullText
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length >= 2 && !stopWords.has(word));

    const wordCount = new Map<string, number>();
    words.forEach(word => {
      wordCount.set(word, (wordCount.get(word) || 0) + 1);
    });

    return Array.from(wordCount.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([word]) => word);
  }

  private calculateRelevanceScore(content: string, article: WikipediaArticle, keyTerms: string[]): number {
    const contentLower = content.toLowerCase();
    const articleText = (article.title + ' ' + article.extract).toLowerCase();
    
    let score = 0;
    let matches = 0;

    keyTerms.forEach(term => {
      if (articleText.includes(term.toLowerCase())) {
        score += 0.3;
        matches++;
      }
    });

    if (keyTerms.some(term => article.title.toLowerCase().includes(term.toLowerCase()))) {
      score += 0.4;
    }

    const contentWords = contentLower.split(/\s+/).filter(word => word.length > 3);
    const articleWords = articleText.split(/\s+/).filter(word => word.length > 3);
    
    const commonWords = contentWords.filter(word => articleWords.includes(word));
    const overlapRatio = commonWords.length / Math.max(contentWords.length, 1);
    score += overlapRatio * 0.3;

    return Math.min(score, 1);
  }

  private cleanQuery(query: string): string {
    return query
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .substring(0, 100);
  }

  private cleanSnippet(snippet: string): string {
    return snippet
      .replace(/<[^>]*>/g, '')
      .replace(/&quot;/g, '"')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/\s+/g, ' ')
      .trim();
  }
}

export const wikipediaService = new WikipediaService();
