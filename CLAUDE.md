# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI fortune-telling web application ("玄机阁" - AI算命大师) built as a single-page application with Supabase backend services. The application provides AI-powered fortune-telling consultations using Alibaba Cloud's Qwen model, enhanced with RAG (Retrieval-Augmented Generation) capabilities from a traditional Chinese fortune-telling knowledge base.

## Architecture

### Frontend
- **Single HTML file** (`index.html`): Contains all UI, styling, and JavaScript logic (75KB+)
- **Pure vanilla JavaScript**: No build tools or frameworks
- **Supabase Client**: Embedded via CDN for authentication and database operations
- **Marked.js**: For markdown rendering of AI responses
- **Responsive design**: Mobile-optimized with CSS media queries

### Backend Services
- **Supabase Auth**: User registration, login, email verification
- **Supabase Database**:
  - `user_quotas`: Tracks remaining conversation attempts per user
  - `chat_messages`: Stores conversation history with RLS policies
  - `payment_records`: Logs payment transactions via Stripe
  - `knowledge_base`: RAG knowledge base with 1024-dimensional vectors
- **Supabase Edge Functions** (Deno-based serverless functions):
  - `ai-chat`: Main AI chat proxy with streaming support
  - `ai-chat-with-rag`: Enhanced AI chat with knowledge base retrieval
  - `rag-search`: Vector similarity search for knowledge base
  - `generate-embeddings`: Text embedding generation
  - `stripe-checkout` & `stripe-webhook`: Payment processing
  - `alibaba-tts`: Text-to-speech synthesis

### API Integration
- **AI Model**: Alibaba Cloud Qwen-max via DashScope API
- **Embeddings**: Alibaba Cloud text-embedding-v4 model (1024 dimensions)
- **Streaming**: Real-time token streaming for better UX
- **RAG System**: Retrieves relevant knowledge from traditional fortune-telling texts

## Development Commands

### Local Testing
No build process required. Open directly in browser:
```bash
# Simple HTTP server (optional)
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Testing RAG Functionality
```bash
# Test RAG search API
python3 test_rag_api.py

# Test multiple queries
python3 test_multiple_queries.py

# Simple RAG test
python3 test_rag_simple.py

# HTML interface for testing
# Open test_rag.html in browser
```

### Deploying Supabase Edge Functions
Functions are deployed via Supabase Dashboard (web UI):
1. Go to Edge Functions → Create/Edit function
2. Paste code from corresponding `supabase/functions/[name]/index.ts`
3. Set environment variables in function secrets
4. Deploy via dashboard

**Critical Environment Variables:**
- `ALIBABA_API_KEY`: DashScope API key for AI model
- `STRIPE_SECRET_KEY`: Stripe payment processing
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook verification

### Deployment to GitHub Pages
```bash
git add .
git commit -m "your message"
git push
```
GitHub Pages auto-deploys from the repository root.

## Important Architecture Patterns

### RAG (Retrieval-Augmented Generation) Flow
1. User submits query via chat interface
2. `rag-search` function performs vector similarity search on `knowledge_base` table
3. Top 5 most relevant knowledge chunks retrieved (threshold ≥ 0.5)
4. Context injected into AI prompt via `ai-chat-with-rag` function
5. Enhanced response generated with traditional fortune-telling wisdom

### Vector Database Schema
```sql
-- knowledge_base table structure
CREATE TABLE knowledge_base (
  id SERIAL PRIMARY KEY,
  category TEXT,           -- 易经, 六十四卦, 梅花易数, 风水, etc.
  title TEXT,
  content TEXT,
  embedding VECTOR(1024)   -- 1024-dimensional vectors
);
```

### Streaming Implementation
The frontend handles both streaming and non-streaming responses:
1. Detects `text/event-stream` content type
2. Reads chunks via ReadableStream API
3. Parses SSE format (`data: {...}`)
4. Updates UI in real-time via `updateStreamingMessage()`
5. Falls back to simulated streaming for JSON responses

## Key Technical Details

### Quota System
- New users start with 2 free conversation attempts
- Conversations only deduct quota after successful AI response
- Payment integration via Stripe Checkout
- Mock payment adds 50 attempts for ¥4.99

### Chat History
- Messages auto-saved to `chat_messages` table after each exchange
- Loads last 50 messages on login
- System messages filtered from display
- "Clear History" function deletes all user messages with confirmation

### Security
- API keys stored in Supabase Edge Function environment variables
- Row Level Security (RLS) policies ensure users only access their own data
- CORS properly configured for cross-origin requests
- Sensitive config files (`config.js`) excluded via `.gitignore`

## Current Development Status

Based on `NEXT_TASKS.md`:
- ✅ RAG functionality implemented and working
- ✅ Vector generation issues resolved (dimension parameter fix)
- ✅ Knowledge base deduplicated (1,402 unique records)
- 🔄 Vector generation for all knowledge base entries in progress
- 📋 Ready for production deployment with Cloudflare CDN

## Knowledge Base Categories

The RAG system contains traditional Chinese fortune-telling texts:
- 易经 (I Ching) and 64 hexagrams
- 梅花易数 (Plum Blossom Numerology)
- 风水 (Feng Shui)
- 面相手相 (Physiognomy)
- 星座 (Astrology)
- 周公解梦 (Dream Interpretation)

## Common Troubleshooting

### Vector Generation Issues
- Use `dimension: 1024` (singular), not `dimensions`
- Control API call frequency (QPS limit: 20)
- Verify vector dimensions after generation

### RAG Search Not Working
- Check if embeddings are generated for all knowledge base entries
- Verify similarity threshold (current: 0.5)
- Ensure `rag-search` function uses dynamic query, not hardcoded

### Edge Function Deployment
- Functions deployed via Supabase Dashboard, not CLI
- Environment variables must be set in function secrets
- Check function logs in Supabase Dashboard for debugging