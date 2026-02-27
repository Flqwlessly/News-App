# NewsHub — Frontend

An AI-powered news aggregator frontend. NewsHub fetches and displays processed news articles with AI-generated summaries, and lets users chat with an AI assistant about any article — all in a clean, modern interface.

![React](https://img.shields.io/badge/React-18-blue?logo=react) ![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript) ![Vite](https://img.shields.io/badge/Vite-5-purple?logo=vite) ![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-teal?logo=tailwindcss)

---

## Features

- **News Feed** — Responsive grid of news cards with cover images, categories, publisher info, and relative timestamps
- **Article Detail** — Full article view with an AI-generated detailed summary and a "Why It Matters" section
- **AI Chatbot** — Floating chat assistant on every article page, context-aware and powered by the backend LLM
- **Live Data** — All content is fetched from a backend API; no hardcoded data in the frontend

---

## Tech Stack

| Tool | Purpose |
|---|---|
| React 18 + TypeScript | UI framework |
| Vite | Dev server & bundler |
| Tailwind CSS | Styling |
| shadcn/ui | Component library |
| React Router v6 | Client-side routing |
| TanStack React Query | Data fetching & caching |
| date-fns | Date formatting |
| lucide-react | Icons |

---

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- A running instance of the [NewsHub backend](https://github.com/majortom-39/news-hub-front) on `http://localhost:8000`

### Installation

```bash
# Clone the repo
git clone https://github.com/majortom-39/news-hub-front.git
cd news-hub-front

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at **http://localhost:8080**.

---

## Backend Dependency

This frontend is a pure UI shell — it requires a backend API running at `http://localhost:8000`. Without it, the app will display a "Failed to load articles" message.

### Required API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/articles` | Returns all processed articles |
| `GET` | `/api/articles/:id` | Returns a single article by ID |
| `POST` | `/api/chat` | Sends a chat message, returns an AI reply |
| `POST` | `/api/sync` | Triggers article scraping & AI processing |

### Article Schema

```ts
{
  id: string
  title: string
  quickSummary: string
  detailedSummary?: string
  whyItMatters?: string
  authorName: string
  publisherName: string
  publisherLogo: string   // image URL
  coverImage: string      // image URL
  datePosted: string      // ISO 8601
  category: string
  sourceUrl: string
  originalContent?: string
}
```

### Chat Request Body

```json
{
  "articleId": "abc123",
  "articleTitle": "...",
  "articleSummary": "...",
  "articleContent": "...",
  "history": [
    { "text": "What is this about?", "isUser": true },
    { "text": "It's about...", "isUser": false }
  ],
  "message": "Can you summarize the key points?"
}
```

---

## Project Structure

```
src/
├── components/
│   ├── ChatBot.tsx        # Floating AI chat widget
│   ├── NewsCard.tsx       # Article card for the home grid
│   └── ui/                # shadcn/ui component library
├── data/
│   └── articles.ts        # API functions & Article type definition
├── pages/
│   ├── Index.tsx          # Home feed page
│   ├── ArticlePage.tsx    # Single article detail page
│   └── NotFound.tsx       # 404 page
├── App.tsx                # Routing & global providers
└── main.tsx               # Entry point
```

---

## Scripts

```bash
npm run dev       # Start development server
npm run build     # Production build
npm run preview   # Preview production build locally
npm run lint      # Run ESLint
```
