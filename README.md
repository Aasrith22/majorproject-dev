# EduSynapse - Multi-Agent Adaptive Learning Platform

An intelligent learning platform powered by a multi-agent AI system that provides personalized educational experiences through adaptive questioning, real-time feedback, and knowledge retrieval.

## Features

- **Multi-Agent System**: Four specialized AI agents work together:
  - Query Analysis Agent - Understands learner intent
  - Information Retrieval Agent - Fetches relevant educational content
  - Question Generation Agent - Creates adaptive assessments
  - Feedback Agent - Provides personalized learning guidance

- **Adaptive Learning**: Questions adapt to learner performance in real-time
- **Multiple Question Types**: MCQ, Fill-in-blank, Essay questions
- **Knowledge Base**: Vector-based semantic search for educational content
- **Multimodal Input**: Support for text, voice, and diagram inputs

## Tech Stack

### Frontend
- React + Vite
- Tailwind CSS + shadcn/ui
- React Query for state management

### Backend
- FastAPI (Python)
- MongoDB with Beanie ODM
- OpenAI GPT-4 / Google Gemini for LLM
- OpenAI Embeddings (or sentence-transformers as optional)
- NumPy-based vector similarity search

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB (local or Atlas)
- OpenAI API key or Google Gemini API key

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your-openai-api-key
   # OR
   GOOGLE_API_KEY=your-gemini-api-key
   
   MONGODB_URL=mongodb://localhost:27017
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open http://localhost:5173 in your browser

## Project Structure

```
majorproject-dev/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents (Query, Retrieval, Question, Feedback)
│   │   ├── models/          # MongoDB models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   └── utils/           # Embeddings & Vector store
│   └── data/
│       └── knowledge_base/  # Educational content JSON files
├── src/
│   ├── components/          # React components
│   ├── context/             # Learning context provider
│   ├── pages/               # Page components
│   ├── services/            # API services
│   └── types/               # TypeScript types
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | OpenAI API key | - |
| GOOGLE_API_KEY | Google Gemini API key | - |
| DEFAULT_LLM_PROVIDER | LLM provider to use | openai |
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017 |
| JWT_SECRET_KEY | Secret for JWT tokens | - |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | http://localhost:8000/api |

## Usage

1. Start both backend and frontend servers
2. Navigate to the Learn page
3. Select a topic or enter a custom topic
4. Choose question type and number of questions
5. Start learning session
6. Answer questions and receive real-time adaptive feedback

## License

MIT
