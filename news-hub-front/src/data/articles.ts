export interface Article {
  id: string;
  title: string;
  quickSummary: string;
  detailedSummary?: string;
  whyItMatters?: string;
  authorName: string;
  publisherName: string;
  publisherLogo: string;
  coverImage: string;
  datePosted: string;
  category: string;
  sourceUrl: string;
  originalContent?: string;
}

const API_BASE = "http://localhost:8000";

export async function fetchArticles(): Promise<Article[]> {
  const res = await fetch(`${API_BASE}/api/articles`);
  if (!res.ok) throw new Error("Failed to fetch articles");
  const data = await res.json();
  return data.articles;
}

export async function fetchArticleById(id: string): Promise<Article> {
  const res = await fetch(`${API_BASE}/api/articles/${id}`);
  if (!res.ok) throw new Error("Article not found");
  return res.json();
}

export async function sendChatMessage(
  articleId: string,
  articleTitle: string,
  articleSummary: string,
  articleContent: string,
  history: { text: string; isUser: boolean }[],
  message: string
): Promise<string> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      articleId,
      articleTitle,
      articleSummary,
      articleContent,
      history,
      message,
    }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  const data = await res.json();
  return data.reply;
}
