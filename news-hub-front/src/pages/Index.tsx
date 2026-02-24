import { useQuery } from "@tanstack/react-query";
import { fetchArticles } from "@/data/articles";
import NewsCard from "@/components/NewsCard";
import { Zap, Loader2 } from "lucide-react";

const Index = () => {
  const { data: articles, isLoading, error } = useQuery({
    queryKey: ["articles"],
    queryFn: fetchArticles,
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center gap-2.5 px-4 py-4">
          <Zap className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold tracking-tight text-foreground">
            News<span className="text-primary">Hub</span>
          </h1>
        </div>
      </header>

      {/* News Grid */}
      <main className="mx-auto max-w-6xl px-4 py-8">
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center py-20">
            <p className="text-muted-foreground">Failed to load articles. Is the backend running?</p>
          </div>
        )}

        {articles && articles.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 gap-2">
            <p className="text-muted-foreground">No articles yet.</p>
            <p className="text-sm text-muted-foreground">
              Hit <code className="rounded bg-muted px-1.5 py-0.5">POST /api/sync</code> to fetch &amp; process articles.
            </p>
          </div>
        )}

        {articles && articles.length > 0 && (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
