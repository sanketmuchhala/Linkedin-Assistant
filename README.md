# LinkedIn Connection Assistant

A black-mode-first application for managing LinkedIn connections with AI-powered personalized messages and pipeline tracking.

## Features

- 🎨 **Dark Mode First**: True black background (#000) with accessible contrast
- 🤖 **AI-Powered Messages**: Generate personalized connection notes (≤300 chars) and acceptance DMs (≤600 chars)
- 📋 **Kanban Pipeline**: Track connections through Draft → Requested → Accepted → In Conversation → Archived
- 🔍 **Search & Filter**: Find connections by name, company, tags, or context
- 🏷️ **Smart Tagging**: Organize connections with custom tags
- 📊 **Context Tracking**: Store why you connected, shared topics, evidence, and goals
- 🔗 **Multi-LLM Support**: Works with Gemini, DeepSeek, or local Ollama models
- 📱 **Responsive UI**: Clean interface built with shadcn/ui components

## Tech Stack

- **Framework**: Next.js 14 (App Router) + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui + lucide-react
- **Database**: SQLite via Prisma (file-based)
- **State Management**: Zustand for UI state
- **AI Providers**: Gemini, DeepSeek, or Ollama (local)
- **Validation**: Zod schemas
- **Dev Tools**: ESLint + Prettier

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Initialize database:**
   ```bash
   npx prisma migrate dev
   ```

4. **Seed with sample data:**
   ```bash
   npm run seed
   ```

5. **Start development server:**
   ```bash
   npm run dev
   ```

Visit `http://localhost:3000` to see your LinkedIn Connection Assistant.

## Environment Configuration

Edit `.env` to configure your LLM provider:

```env
# Choose provider: gemini, deepseek, or ollama
LLM_PROVIDER=gemini

# API Keys (based on provider)
GEMINI_API_KEY=your_api_key_here
DEEPSEEK_API_KEY=your_api_key_here

# Model settings (optional)
GEMINI_MODEL=gemini-1.5-pro
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

## Usage

### Adding a New Lead

1. Click "Add Lead" in the dashboard
2. Fill in contact details and context
3. Specify tone, goal, and any constraints
4. Click "Generate Messages" to create personalized content
5. Save as draft or with generated messages

### Managing the Pipeline

- **Dashboard**: View all connections organized by status
- **Drag or move**: Change connection status through the pipeline
- **Search**: Find connections by name, company, or context
- **Details**: Click any connection to view full details and edit

### Message Generation

The AI generates two types of messages:
- **Connection Note**: Personalized LinkedIn connection request (≤300 chars)
- **Acceptance DM**: Follow-up message after they accept (≤600 chars)

Messages consider your specified:
- Context and shared topics
- Professional tone preference
- Connection goal
- Things to avoid
- Call-to-action

## API Endpoints

- `GET /api/records` - List all connections with optional filters
- `POST /api/records` - Create new connection
- `GET /api/records/[id]` - Get specific connection
- `PATCH /api/records/[id]` - Update connection
- `DELETE /api/records/[id]` - Delete connection
- `POST /api/generate` - Generate AI messages for connection

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run seed` - Populate database with sample data
- `npx prisma migrate dev` - Run database migrations
- `npx prisma studio` - Open database browser

## Security & Privacy

- **No Auto-Actions**: Never automatically sends LinkedIn messages or scrapes data
- **Local Database**: All data stored locally in SQLite
- **API Keys**: Your LLM API keys never leave your environment
- **No Tracking**: No analytics or external data collection

## Next Steps

Three recommended upgrades to consider:

1. **CSV Import**: Bulk import connections from LinkedIn exports
2. **Gmail Integration**: Parse "You're now connected" notifications to auto-update status
3. **Reminder System**: Email/notification reminders for follow-up actions

## Contributing

This is a personal assistant tool. Feel free to fork and customize for your needs.

## License

MIT License - use it however you'd like!