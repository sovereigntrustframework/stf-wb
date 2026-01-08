# STF-Workbench Web UI

Quick start guide for the web interface.

## Setup

### Backend

```bash
# Install web dependencies
pip install -e ".[web]"

# Run the backend server
python -m stfwb_web.app
# or
uvicorn stfwb_web.app:app --reload
```

Backend runs on http://localhost:8000

Endpoints:
- `GET /health` - Health check
- `GET /events` - Server-Sent Events stream
- `POST /test/emit` - Emit test event (dev only)

### Frontend

```bash
cd stfwb_web_ui

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs on http://localhost:5173

## Testing the SSE Connection

1. Start the backend: `uvicorn stfwb_web.app:app --reload`
2. Start the frontend: `cd stfwb_web_ui && npm run dev`
3. Open http://localhost:5173 in your browser
4. You should see:
   - Backend status: healthy
   - SSE: 🟢 Connected
   - Periodic heartbeat events
5. Click "Emit Test Event" to send a test event through the SSE stream

## Development

The frontend proxies API requests to the backend through Vite:
- `/api/*` → `http://localhost:8000/*`

This avoids CORS issues during development.

## Architecture

```
stfwb_web/          # FastAPI backend
├── app.py          # Main FastAPI app with SSE
├── models.py       # Pydantic models
├── auth/           # GitHub OAuth (future)
├── api/            # API routes (future)
└── git/            # Git workspace management (future)

stfwb_web_ui/       # React frontend
├── src/
│   ├── App.tsx     # Main component with SSE client
│   └── main.tsx    # Entry point
├── package.json
└── vite.config.ts  # Vite config with proxy
```

## Next Steps

See docs/ideas/web_ui/stf-wb-mvp-plan.md for the full implementation roadmap.

Phase 1 (Foundation) - CURRENT:
- ✅ Backend scaffold with FastAPI
- ✅ SSE endpoint (/events)
- ✅ Frontend with SSE client
- 🔄 Test connection end-to-end

Phase 2 (Authentication):
- GitHub App setup
- OAuth flow
- User session management

Phase 3 (Core Features):
- Project management
- Run execution
- Real-time progress

Phase 4 (Publication):
- PR creation
- Review workflow
- Publication tracking
