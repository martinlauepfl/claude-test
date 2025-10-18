# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI fortune-telling web application ("玄机阁" - AI算命大师) built as a single-page application with Supabase backend services. The application provides AI-powered fortune-telling consultations using Alibaba Cloud's Qwen model, with user authentication, quota management, and chat history persistence.

## Architecture

### Frontend
- **Single HTML file** (`index.html`): Contains all UI, styling, and JavaScript logic
- **Pure vanilla JavaScript**: No build tools or frameworks
- **Supabase Client**: Embedded via CDN for authentication and database operations
- **Marked.js**: For markdown rendering of AI responses

### Backend Services
- **Supabase Auth**: User registration, login, email verification
- **Supabase Database**:
  - `user_quotas`: Tracks remaining conversation attempts per user
  - `chat_messages`: Stores conversation history with RLS policies
  - `payment_records`: Logs payment transactions (currently mock)
- **Supabase Edge Function** (`supabase/functions/ai-chat/index.ts`):
  - Deno-based serverless function
  - Proxies requests to Alibaba Cloud Qwen API
  - Protects API keys from frontend exposure
  - Supports streaming responses

### API Integration
- **AI Model**: Alibaba Cloud Qwen-max via DashScope API
- **Streaming**: Real-time token streaming for better UX
- **System Prompt**: Dynamic fortune-teller persona with contextual time awareness

## Key Technical Details

### Authentication Flow
1. Users register with email/password via Supabase Auth
2. Email verification required (enforced via banner in UI)
3. Session management handled automatically by Supabase client
4. Auth state changes trigger UI updates via `onAuthStateChange`

### Quota System
- New users start with 2 free conversation attempts
- Conversations only deduct quota after successful AI response
- Payment modal shows when quota depleted
- Mock payment adds 50 attempts for ¥4.99

### Chat History
- Messages auto-saved to `chat_messages` table after each exchange
- Loads last 50 messages on login
- System messages filtered from display
- "Clear History" function deletes all user messages with confirmation

### Security
- API keys stored in Supabase Edge Function environment variables (never in frontend)
- Row Level Security (RLS) policies ensure users only access their own data
- CORS properly configured for cross-origin requests
- Sensitive config files (`config.js`) excluded via `.gitignore`

## Development Commands

### Testing Locally
Open `index.html` directly in a browser or use a simple HTTP server:
```bash
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Deploying Supabase Edge Function
The function is deployed via Supabase Dashboard (web UI):
1. Go to Edge Functions → Create/Edit `ai-chat`
2. Paste code from `supabase/functions/ai-chat/index.ts`
3. Set environment variable `ALIBABA_API_KEY` in function secrets
4. Deploy via dashboard

### Deployment to GitHub Pages
```bash
git add .
git commit -m "your message"
git push
```
GitHub Pages auto-deploys from the repository root.

## Important File Locations

- **Main application**: `index.html` (lines 1-1477)
- **Edge function**: `supabase/functions/ai-chat/index.ts`
- **Deployment guides**: `SUPABASE_DEPLOYMENT.md`, `DEPLOYMENT.md`, `CHAT_HISTORY_SETUP.md`
- **Ignored sensitive data**: `config.js` (contains API keys, must not be committed)

## System Prompt Architecture

The fortune-teller persona is defined in `getSystemPrompt()` (index.html:791-816):
- Dynamic time-of-day detection (morning/afternoon/evening)
- Casual, direct tone with occasional philosophical depth
- Remembers user information across conversations via history
- Chinese colloquial expressions ("这事儿吧", "真的", etc.)

## Database Schema

### user_quotas
- `user_id`: UUID (foreign key to auth.users)
- `quota`: Integer (remaining attempts)
- `total_purchased`: Integer (lifetime purchase count)

### chat_messages
- `user_id`: UUID (foreign key to auth.users)
- `role`: TEXT ('user', 'assistant', 'system')
- `content`: TEXT (message content)
- `created_at`: Timestamp
- Index on `(user_id, created_at DESC)` for efficient history queries

### payment_records
- `user_id`: UUID
- `amount`: Numeric (payment amount)
- `quota_added`: Integer
- `payment_method`: TEXT
- `status`: TEXT ('completed', etc.)

## Configuration Notes

### Supabase Project
- URL: `https://mulrkyqqhaustbojzzes.supabase.co`
- Anon key embedded in `index.html:782` (safe for public exposure)
- Edge Function endpoint: `/functions/v1/ai-chat`

### AI Model
- Current model: `qwen-max` (highest quality, specified in edge function)
- API endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- Streaming enabled for real-time response display

## Streaming Implementation

The frontend handles both streaming and non-streaming responses (index.html:1282-1358):
1. Detects `text/event-stream` content type
2. Reads chunks via ReadableStream API
3. Parses SSE format (`data: {...}`)
4. Updates UI in real-time via `updateStreamingMessage()`
5. Falls back to simulated streaming for JSON responses

## Common Workflows

### Adding New Features to Chat
1. Modify `index.html` JavaScript section (after line 772)
2. Update conversation history management if needed
3. Consider database schema changes if persistence required
4. Test locally before committing

### Changing AI Model Behavior
1. Edit `getSystemPrompt()` function for persona changes
2. Modify Edge Function (`index.ts`) to change model parameters
3. Redeploy Edge Function via Supabase Dashboard

### Updating Quota/Payment Logic
1. Payment amounts: Search for `4.99` in `index.html`
2. Quota increments: Modify `handlePayment()` function
3. Database updates handled via Supabase client in frontend
