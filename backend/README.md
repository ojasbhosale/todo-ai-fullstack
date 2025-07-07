# Smart Todo List - FastAPI Backend

A comprehensive FastAPI backend for an AI-powered smart todo list application with context-aware task management.

## 🚀 Features

- **AI-Powered Task Management**: Intelligent task prioritization, deadline suggestions, and enhanced descriptions
- **Context-Aware Processing**: Analyze daily context (emails, messages, notes) to provide relevant task suggestions
- **Smart Categorization**: Automatic category suggestions and usage tracking
- **RESTful API**: Complete CRUD operations for tasks, context entries, and categories
- **Async Support**: Built with FastAPI for high performance and async operations
- **Supabase Integration**: PostgreSQL database with modern async drivers
- **OpenAI Integration**: Advanced AI features using GPT models
- **Production Ready**: Comprehensive error handling, logging, and security measures

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.104+ with async/await support
- **Database**: PostgreSQL (via Supabase) with SQLAlchemy 2.0
- **AI**: OpenAI GPT-3.5/4 API
- **Validation**: Pydantic v2 for request/response validation
- **Environment**: Python 3.8+

## 📋 Prerequisites

Before running the application, ensure you have:

- Python 3.8 or higher
- PostgreSQL database (Supabase account)
- OpenAI API key
- Virtual environment (recommended)

## 🔧 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd smart-todo-fastapi
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the root directory:
```env
SUPABASE_PROJECT_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres
SECRET_KEY=your_secret_key
DEBUG=True
ENVIRONMENT=development
```

5. **Set up the database**:
```bash
# Run the Supabase setup script
python supabase_setup.py
```

6. **Start the development server**:
```bash
uvicorn main:app --reload
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

### Endpoints

#### Tasks API

**GET /api/v1/tasks/**
- Retrieve all tasks with optional filtering
- Query parameters:
  - `status`: Filter by status (pending, in_progress, completed, cancelled)
  - `category`: Filter by category name
  - `priority`: Filter by priority score (1-10)
  - `overdue`: Filter overdue tasks (true/false)
  - `skip`: Pagination offset
  - `limit`: Number of results to return

**POST /api/v1/tasks/**
- Create a new task
- Request body:
```json
{
  "title": "Complete project report",
  "description": "Finish the quarterly report",
  "category": "Work",
  "priority_score": 8,
  "deadline": "2024-01-15T15:00:00Z",
  "status": "pending"
}
```

**GET /api/v1/tasks/{task_id}**
- Retrieve specific task details

**PUT /api/v1/tasks/{task_id}**
- Update task information

**DELETE /api/v1/tasks/{task_id}**
- Delete a task

**POST /api/v1/tasks/ai-suggestions/**
- Get AI-powered task suggestions
- Request body:
```json
{
  "title": "Meeting with client",
  "description": "Discuss project requirements",
  "category": "Work",
  "context_data": [
    {
      "content": "Client meeting tomorrow at 3 PM",
      "source_type": "email"
    }
  ],
  "current_workload": 5
}
```

**GET /api/v1/tasks/statistics/**
- Get task statistics and analytics

#### Context API

**GET /api/v1/context/**
- Retrieve all context entries
- Query parameters:
  - `source_type`: Filter by source type (email, whatsapp, notes, etc.)
  - `is_processed`: Filter by processing status
  - `min_relevance`: Filter by minimum relevance score

**POST /api/v1/context/**
- Create new context entry
- Request body:
```json
{
  "content": "Meeting with client tomorrow at 3 PM to discuss project requirements",
  "source_type": "email",
  "meta_data": {
    "sender": "client@example.com",
    "subject": "Project Discussion"
  }
}
```

**POST /api/v1/context/analyze/**
- Analyze context content using AI
- Request body:
```json
{
  "content": "Important meeting tomorrow",
  "source_type": "email",
  "analyze_sentiment": true,
  "extract_keywords": true,
  "calculate_relevance": true
}
```

#### Categories API

**GET /api/v1/categories/**
- Retrieve all categories
- Query parameters:
  - `is_active`: Filter by active status
  - `min_usage`: Filter by minimum usage frequency
  - `search`: Search categories by name

**POST /api/v1/categories/**
- Create new category
- Request body:
```json
{
  "name": "Personal",
  "description": "Personal tasks and activities",
  "color": "#10B981",
  "is_active": true
}
```

**GET /api/v1/categories/statistics/**
- Get category statistics

**GET /api/v1/categories/popular/**
- Get most popular categories by usage

## 🤖 AI Features

### Task Prioritization
The AI analyzes task content and context to assign priority scores (1-10):
- **1-3**: Low priority, flexible timing
- **4-6**: Medium priority, complete within a week
- **7-8**: High priority, complete within 2-3 days
- **9-10**: Critical/urgent, needs immediate attention

### Deadline Suggestions
AI suggests realistic deadlines based on:
- Task complexity and priority
- Current workload
- Context clues about timing
- Historical completion patterns

### Context Analysis
The system processes daily context from various sources:
- **Email**: Meeting information, deadlines, project updates
- **WhatsApp/SMS**: Urgent notifications, personal reminders
- **Notes**: Task lists, ideas, planning information
- **Calendar**: Upcoming events, time constraints

### Enhanced Descriptions
AI enhances task descriptions by:
- Adding relevant context insights
- Suggesting specific steps or considerations
- Including timing and priority explanations
- Providing actionable recommendations

## 🔧 Configuration

### Database Models

The application uses SQLAlchemy 2.0 with async support:

- **Task**: Stores task information with AI enhancements
- **ContextEntry**: Stores daily context data with analysis
- **Category**: Manages task categories with usage tracking

### Environment Variables

All configuration is handled through environment variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_PROJECT_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...

# AI
OPENAI_API_KEY=sk-...

# Application
SECRET_KEY=...
DEBUG=True
ENVIRONMENT=development
```

## 🛡️ Security

### Database Security
- Async PostgreSQL connections with connection pooling
- Parameterized queries to prevent SQL injection
- Environment-based configuration for sensitive data

### API Security
- Pydantic validation for all request/response data
- Comprehensive error handling with appropriate HTTP status codes
- CORS configuration for cross-origin requests

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

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at `/docs` to test all endpoints.

### Sample API Requests

#### Create a Task with AI Suggestions
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/ai-suggestions/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prepare presentation",
    "description": "Create slides for client meeting",
    "context_data": [
      {
        "content": "Client meeting scheduled for tomorrow at 3 PM",
        "source_type": "email"
      }
    ]
  }'
```

#### Get Task Statistics
```bash
curl "http://localhost:8000/api/v1/tasks/statistics/"
```

#### Filter Tasks by Priority
```bash
curl "http://localhost:8000/api/v1/tasks/?priority=8&status=pending"
```

## 🚀 Deployment

### Environment Setup
1. Set `DEBUG=False` in production
2. Configure proper CORS origins
3. Set up proper database credentials
4. Configure logging for production
5. Set up HTTPS

### Performance Optimization
- FastAPI's async support provides excellent performance
- Database connection pooling is configured automatically
- Use proper indexes on frequently queried fields

## 📋 TODO / Future Enhancements

- [ ] Add JWT authentication and user management
- [ ] Implement WebSocket support for real-time updates
- [ ] Add task scheduling and reminders
- [ ] Integrate with calendar APIs
- [ ] Add task templates and recurring tasks
- [ ] Implement team collaboration features
- [ ] Add comprehensive test suite
- [ ] Create task analytics dashboard
- [ ] Implement task dependencies
- [ ] Add time tracking features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the GitHub issues page
- Review the API documentation at `/docs`
- Contact the development team

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## Performance Benefits of FastAPI

- **High Performance**: FastAPI is one of the fastest Python frameworks
- **Async Support**: Native async/await support for better concurrency
- **Automatic Documentation**: Interactive API docs generated automatically
- **Type Safety**: Full type hints with runtime validation
- **Modern Python**: Built for Python 3.6+ with modern features