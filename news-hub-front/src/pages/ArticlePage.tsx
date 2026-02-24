import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { ArrowLeft, ExternalLink, Loader2 } from "lucide-react";
import { fetchArticleById } from "@/data/articles";
import ChatBot from "@/components/ChatBot";

const ArticlePage = () => {
  const { id } = useParams();

  const { data: article, isLoading, error } = useQuery({
    queryKey: ["article", id],
    queryFn: () => fetchArticleById(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground">Article not found.</p>
      </div>
    );
  }

  const timeAgo = formatDistanceToNow(new Date(article.datePosted), { addSuffix: true });
  const summaryParagraphs = (article.detailedSummary || "").split("\n\n");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-4">
          <Link to="/" className="flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors">
            <ArrowLeft size={16} />
            Back to News
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        {/* Cover Image */}
        <div className="relative mb-6 overflow-hidden rounded-xl">
          <img src={article.coverImage} alt={article.title} className="h-72 w-full object-cover sm:h-96" />
          <span className="absolute left-4 top-4 rounded-full bg-primary/90 px-3 py-1 text-xs font-medium text-primary-foreground backdrop-blur-sm">
            {article.category}
          </span>
        </div>

        {/* Title */}
        <h1 className="mb-4 text-2xl font-bold leading-tight text-foreground sm:text-3xl">
          {article.title}
        </h1>

        {/* Meta */}
        <div className="mb-8 flex items-center gap-3 border-b border-border pb-6">
          <img src={article.publisherLogo} alt={article.publisherName} className="h-8 w-8 rounded-full" />
          <div>
            <p className="text-sm font-medium text-foreground">{article.publisherName}</p>
            <p className="text-xs text-muted-foreground">
              By {article.authorName} · {timeAgo}
            </p>
          </div>
        </div>

        {/* Detailed Summary */}
        <div className="mb-8 space-y-4">
          {summaryParagraphs.map((p, i) => (
            <p key={i} className="text-base leading-relaxed text-muted-foreground">
              {p}
            </p>
          ))}
        </div>

        {/* Why It Matters */}
        {article.whyItMatters && (
          <div className="mb-8 rounded-lg border border-primary/20 bg-primary/5 p-5">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-primary">
              Why It Matters
            </h3>
            <p className="text-sm leading-relaxed text-foreground">
              {article.whyItMatters}
            </p>
          </div>
        )}

        {/* Read Full Article */}
        <a
          href={article.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Read Full Article
          <ExternalLink size={16} />
        </a>
      </main>

      <ChatBot
        articleId={article.id}
        articleTitle={article.title}
        articleSummary={article.detailedSummary || article.quickSummary}
        articleContent={article.originalContent || ""}
      />
    </div>
  );
};

export default ArticlePage;
