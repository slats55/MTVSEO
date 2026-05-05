# SEO Agent OS — Web Dashboard

Next.js 14 dashboard for the Autonomous SEO Agent OS.

---

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS with custom dark theme
- **Icons:** Lucide React
- **Data fetching:** TanStack React Query (planned)
- **API:** FastAPI backend at `http://localhost:8000`

---

## Getting Started

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Pages

| Route | Description |
|-------|-------------|
| `/` | Main dashboard — score cards, recent crawls, top issues, quick actions |
| `/businesses` | Business list with search, SEO scores, and last crawl status |
| `/audits` | Full audit view — score breakdown, filterable issue list by severity |
| `/reports` | Saved report cards with download and view actions |

---

## Design System

Dark professional theme with slate/blue palette:

- Background: `hsl(222.2 84% 4.9%)` (near-black navy)
- Primary accent: `hsl(217.2 91.2% 59.8%)` (blue-500)
- Text: `hsl(210 40% 98%)` (slate-50)
- Borders: `hsl(217.2 32.6% 17.5%)` (slate-800)

Score grades use semantic color coding:
- **A** 🟢 `text-green-400` — score ≥ 80
- **B** 🟡 `text-yellow-400` — score 70-79
- **C** 🟠 `text-orange-400` — score 60-69
- **D** 🔴 `text-red-400` — score 50-59
- **F** 🚫 `text-red-600` — score < 50

---

## API Integration (Planned)

The dashboard will consume these API endpoints from `services/api`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/businesses` | List all businesses |
| POST | `/api/v1/businesses` | Create a business |
| GET | `/api/v1/websites?business_id=X` | List websites for a business |
| POST | `/api/v1/crawls` | Trigger a new crawl |
| GET | `/api/v1/crawls?website_id=X` | List crawl runs |
| GET | `/api/v1/crawls/{id}` | Get crawl status |
| GET | `/api/v1/pages?crawl_run_id=X` | List pages from a crawl |
| GET | `/api/v1/reports` | List saved reports |
| POST | `/api/v1/reports` | Generate a new report |

---

## Known Issues / TODO

- [ ] Replace mock data with real API calls via React Query
- [ ] Add business selector dropdown with real business list
- [ ] Add WebSocket / SSE for live crawl status updates
- [ ] Add report viewer with rendered markdown
- [ ] Add content calendar page
- [ ] Add opportunities / keyword map page
- [ ] Add settings / integrations page
- [ ] Add authentication (login/logout)
- [ ] Mobile responsive layout
