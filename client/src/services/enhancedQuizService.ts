const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

// ---- Types ----------------------------------------------------------------

export interface WikipediaArticle {
  title: string;
  extract: string;
  url: string;
  pageid: number;
  lastrevid: number;
  sections?: string[];
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

// ---- Helpers ---------------------------------------------------------------

function emptyContext(): WikipediaContext {
  return { articles: [], keyFacts: [], relatedTopics: [], summary: "" };
}

function attachSources(
  quizData: any,
  context: WikipediaContext,
): EnhancedQuizResponse {
  return {
    ...quizData,
    wikipediaContext: context,
    questions: quizData.questions.map((q: any) => ({
      ...q,
      wikipediaSources: context.articles.map((a) => a.title),
    })),
  };
}

async function fetchQuiz(
  topic: string,
  wikipediaEnhanced: boolean,
): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic: topic.trim(), wikipediaEnhanced }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.error || "Failed to generate quiz");
  }

  return res.json();
}

// ---- Public API ------------------------------------------------------------

export async function generateEnhancedQuiz(
  topic: string,
): Promise<EnhancedQuizResponse> {
  try {
    const data = await fetchQuiz(topic, true);

    const context: WikipediaContext = {
      articles: data.wikipedia_context?.articles ?? [],
      keyFacts: data.wikipedia_context?.key_facts ?? [],
      relatedTopics: data.wikipedia_context?.related_topics ?? [],
      summary: data.wikipedia_context?.summary ?? "",
    };

    return attachSources(data, context);
  } catch (error) {
    console.error("Enhanced quiz generation error:", error);

    try {
      const fallback = await fetchQuiz(topic, false);
      return attachSources(fallback, emptyContext());
    } catch (fallbackError) {
      console.error("Fallback quiz generation error:", fallbackError);
      const last = await fetchQuiz(topic, false);
      return { ...last, wikipediaContext: undefined };
    }
  }
}

export async function getWikipediaArticles(
  topic: string,
): Promise<WikipediaArticle[]> {
  try {
    const res = await fetch(
      `${API_BASE_URL}/wikipedia/articles?topic=${encodeURIComponent(topic)}&limit=3`,
    );

    if (!res.ok)
      throw new Error(`Failed to get Wikipedia articles: ${res.status}`);

    return (await res.json()) ?? [];
  } catch (error) {
    console.error("Error getting Wikipedia articles:", error);
    return [];
  }
}
