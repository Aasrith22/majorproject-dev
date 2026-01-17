# EduSynapse Backend

## Multi-Agent Adaptive Learning Platform Backend

This backend powers EduSynapse's intelligent adaptive learning system using CrewAI for agent orchestration.

## Architecture Overview

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic & Beanie models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── agents/              # CrewAI agent definitions
│   └── utils/               # Utility functions
├── data/                    # Knowledge base & vector indices
├── requirements.txt         # Python dependencies
└── .env.example            # Environment template
```

## Quick Start

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Start MongoDB
Make sure MongoDB is running locally or update `MONGODB_URL` in `.env`

### 5. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Learning Sessions
- `POST /api/sessions/start` - Start new learning session
- `GET /api/sessions/{session_id}` - Get session details
- `POST /api/sessions/{session_id}/input` - Submit learner input
- `POST /api/sessions/{session_id}/end` - End session

### Assessments
- `GET /api/assessments/question` - Get next adaptive question
- `POST /api/assessments/submit` - Submit answer for evaluation
- `GET /api/assessments/feedback/{response_id}` - Get detailed feedback

### Dashboard
- `GET /api/dashboard/progress` - Get learning progress
- `GET /api/dashboard/analytics` - Get detailed analytics
- `GET /api/dashboard/recommendations` - Get learning recommendations

## Agent Pipeline

The CrewAI orchestration follows this sequence:

1. **Query Analysis Agent** → Understands learner intent
2. **Information Retrieval Agent** → Fetches relevant content
3. **Question Generation Agent** → Creates adaptive assessments
4. **Feedback Agent** → Generates personalized feedback

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes* |
| `MONGODB_URL` | MongoDB connection string | Yes |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Yes |

*At least one LLM provider key is required

## Development

### Run Tests
```bash
pytest tests/ -v
```

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License
MIT License - EduSynapse Team
