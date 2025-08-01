# Smart Todo List - Full Stack Application

A comprehensive full-stack application featuring an AI-powered smart todo list with context-aware task management, built with React frontend and FastAPI backend.

## 🚀 Features

### Frontend (React + TypeScript)
- **Modern React App**: Built with Vite, TypeScript, and Tailwind CSS
- **Component Library**: Uses shadcn/ui for consistent, beautiful UI components
- **Responsive Design**: Mobile-first design that works on all devices
- **Real-time Updates**: Live preview and instant feedback
- **State Management**: Efficient state management with React Query

### Backend (FastAPI + PostgreSQL)
- **AI-Powered Task Management**: Intelligent task prioritization, deadline suggestions, and enhanced descriptions
- **Context-Aware Processing**: Analyze daily context (emails, messages, notes) to provide relevant task suggestions
- **Smart Categorization**: Automatic category suggestions and usage tracking
- **RESTful API**: Complete CRUD operations for tasks, context entries, and categories
- **Async Support**: Built with FastAPI for high performance and async operations
- **Supabase Integration**: PostgreSQL database with modern async drivers
- **OpenAI Integration**: Advanced AI features using GPT models

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Charts**: Recharts
- **State Management**: TanStack React Query
- **Routing**: React Router DOM
- **Forms**: React Hook Form with Zod validation

### Backend
- **Framework**: FastAPI 0.104+ with async/await support
- **Database**: PostgreSQL (via Supabase) with SQLAlchemy 2.0
- **AI**: OpenAI GPT-3.5/4 API
- **Validation**: Pydantic v2 for request/response validation
- **Environment**: Python 3.8+

## 📋 Prerequisites

### Frontend
- Node.js 16+ and npm
- Modern web browser

### Backend
- Python 3.8 or higher
- PostgreSQL database (Supabase account)
- OpenAI API key
- Virtual environment (recommended)

## 🔧 Installation & Setup

### Frontend Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd smart-todo-app
```

2. **Install frontend dependencies**:
```bash
npm install
```

3. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

### Backend Setup

1. **Navigate to backend directory** (if separate) or ensure you're in the root:
```bash
# If backend is in a separate directory
cd backend
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install backend dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the backend directory:
```env
SUPABASE_PROJECT_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your_project.supabase.co:5432/postgres
SECRET_KEY=your_secret_key
DEBUG=True
ENVIRONMENT=development
```

5. **Set up the database**:
```bash
python supabase_setup.py
```

6. **Start the backend server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Base URL
```
http://localhost:8000/api/v1
```

### Main Endpoints

#### Tasks API
- `GET /api/v1/tasks/` - Retrieve all tasks with filtering
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `POST /api/v1/tasks/ai-suggestions/` - Get AI-powered task suggestions
- `GET /api/v1/tasks/statistics/` - Get task analytics

#### Context API
- `GET /api/v1/context/` - Retrieve context entries
- `POST /api/v1/context/` - Create context entry
- `POST /api/v1/context/analyze/` - AI context analysis

#### Categories API
- `GET /api/v1/categories/` - Retrieve categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/statistics/` - Category stats

## 🤖 AI Features

### Task Prioritization
The AI analyzes task content and context to assign priority scores (1-10):
- **1-3**: Low priority, flexible timing
- **4-6**: Medium priority, complete within a week
- **7-8**: High priority, complete within 2-3 days
- **9-10**: Critical/urgent, needs immediate attention

### Context Analysis
The system processes daily context from various sources:
- **Email**: Meeting information, deadlines, project updates
- **WhatsApp/SMS**: Urgent notifications, personal reminders
- **Notes**: Task lists, ideas, planning information
- **Calendar**: Upcoming events, time constraints

## 📊 Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    category VARCHAR(100) DEFAULT '',
    priority_score INTEGER DEFAULT 5 CHECK (priority_score >= 1 AND priority_score <= 10),
    deadline TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    ai_enhanced_description TEXT DEFAULT '',
    ai_suggested_tags JSONB DEFAULT '[]',
    context_references JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Context Entries Table
```sql
CREATE TABLE context_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    processed_insights JSONB DEFAULT '{}',
    meta_data JSONB DEFAULT '{}',
    is_processed BOOLEAN DEFAULT false,
    relevance_score DECIMAL(3,2) DEFAULT 0.0,
    extracted_keywords JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    usage_frequency INTEGER DEFAULT 0,
    color VARCHAR(7) DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🐳 Docker Deployment

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 8080
CMD ["npm", "run", "preview"]
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "3000:8080"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env
```

## 🧪 Testing

### Frontend Testing
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Backend Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📱 Frontend Components

### Key Components
- **Task Management**: Create, edit, delete, and organize tasks
- **AI Suggestions**: Get intelligent task recommendations
- **Context Analysis**: Process and analyze daily context
- **Category Management**: Organize tasks with smart categories
- **Analytics Dashboard**: View task statistics and insights
- **Responsive Design**: Works seamlessly on desktop and mobile

### UI Library
Built with shadcn/ui components:
- Cards, Buttons, Forms, Dialogs
- Data Tables, Charts, Alerts
- Navigation, Tabs, Accordions
- Toast notifications, Tooltips

## 🔧 Development Commands

### Frontend
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

### Backend
```bash
uvicorn main:app --reload                    # Development server
python -m pytest                            # Run tests
alembic upgrade head                         # Run database migrations
python -c "from app.core.database import create_tables; import asyncio; asyncio.run(create_tables())"  # Create tables
```

## 🛡️ Security

### Frontend Security
- Type-safe API calls with TypeScript
- Input validation with Zod schemas
- XSS protection through React's built-in sanitization
- HTTPS enforcement in production

### Backend Security
- Async PostgreSQL connections with connection pooling
- Parameterized queries to prevent SQL injection
- Pydantic validation for all request/response data
- Environment-based configuration for sensitive data
- CORS configuration for cross-origin requests

## 🚀 Production Deployment

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to platforms like Vercel, Netlify, or serve from CDN
3. Configure environment variables for API endpoints

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure proper CORS origins
3. Set up proper database credentials
4. Configure logging for production
5. Deploy to platforms like Render, Railway, or AWS

### Environment Variables

#### Frontend (.env)
```env
VITE_API_URL=https://your-api-domain.com
VITE_APP_NAME=Smart Todo List
```

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_PROJECT_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...
OPENAI_API_KEY=sk-...
SECRET_KEY=...
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

## 📋 Future Enhancements

### Frontend
- [ ] Offline support with service workers
- [ ] Progressive Web App (PWA) features
- [ ] Dark/light theme toggle
- [ ] Drag and drop task organization
- [ ] Keyboard shortcuts
- [ ] Export/import functionality

### Backend
- [ ] JWT authentication and user management
- [ ] WebSocket support for real-time updates
- [ ] Task scheduling and reminders
- [ ] Calendar API integration
- [ ] Task templates and recurring tasks
- [ ] Team collaboration features
- [ ] Comprehensive test suite
- [ ] Task dependencies
- [ ] Time tracking features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices for frontend
- Use Pydantic models for backend validation
- Write tests for new features
- Update documentation as needed
- Follow the existing code style

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Check the GitHub issues page
- Review the API documentation at `/docs`
- Frontend documentation in component comments
- Contact the development team

## 📚 Additional Resources

### Frontend
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 🏗️ Architecture Overview

```
Frontend (React + TypeScript)
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Route components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utilities and configurations
│   └── types/         # TypeScript type definitions

Backend (FastAPI + Python)
├── app/
│   ├── api/           # API route handlers
│   ├── core/          # Core functionality (config, database)
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   └── services/      # Business logic services
```

This full-stack application provides a modern, scalable solution for intelligent task management with AI-powered features and a beautiful, responsive user interface.
