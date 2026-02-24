import { Link } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import type { Article } from "@/data/articles";

const NewsCard = ({ article }: { article: Article }) => {
  const timeAgo = formatDistanceToNow(new Date(article.datePosted), { addSuffix: true });

  return (
    <Link to={`/article/${article.id}`} className="group block">
      <div className="overflow-hidden rounded-xl border border-border bg-card transition-all duration-300 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5">
        {/* Thumbnail */}
        <div className="relative h-48 overflow-hidden">
          <img
            src={article.coverImage}
            alt={article.title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <span className="absolute left-3 top-3 rounded-full bg-primary/90 px-3 py-1 text-xs font-medium text-primary-foreground backdrop-blur-sm">
            {article.category}
          </span>
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="mb-2 text-base font-semibold leading-snug text-card-foreground line-clamp-2 group-hover:text-primary transition-colors">
            {article.title}
          </h3>
          <p className="mb-3 text-sm text-muted-foreground line-clamp-2">
            {article.quickSummary}
          </p>

          {/* Meta */}
          <div className="flex items-center gap-2">
            <img src={article.publisherLogo} alt={article.publisherName} className="h-5 w-5 rounded-full" />
            <span className="text-xs text-muted-foreground">{article.publisherName}</span>
            <span className="text-xs text-muted-foreground">·</span>
            <span className="text-xs text-muted-foreground">{article.authorName}</span>
            <span className="ml-auto text-xs text-muted-foreground">{timeAgo}</span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default NewsCard;
