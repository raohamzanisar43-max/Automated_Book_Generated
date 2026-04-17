# Automated Book Generation System

A professional full-stack AI-powered system for automated book generation with human-in-the-loop review capabilities.

## 🚀 Features

### Core Functionality
- **AI-Powered Outline Generation**: Generate comprehensive book outlines using advanced LLMs
- **Chapter-by-Chapter Generation**: Create chapters with context chaining for consistency
- **Human-in-the-Loop Review**: Review and provide feedback at every stage
- **Multi-Format Export**: Export books as DOCX, PDF, or TXT files
- **Real-Time Notifications**: Email and MS Teams webhook notifications
- **Research Integration**: Web search integration for fact-based content

### Workflow Stages
1. **Input & Outline Stage**: Create book with AI-generated outline
2. **Chapter Generation Stage**: Generate chapters with previous chapter context
3. **Final Compilation Stage**: Compile and export the final book

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with async SQLAlchemy
- **AI Integration**: OpenAI GPT-4 for content generation
- **Research**: SerpAPI for web search integration
- **Notifications**: SMTP email + MS Teams webhooks
- **Export**: python-docx, reportlab for PDF generation

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React Query for server state
- **Routing**: React Router for navigation
- **UI Components**: Custom components with Lucide icons

### Database Schema
- **Books**: Main book records with status tracking
- **Chapters**: Individual chapters with content and summaries
- **Notes**: Human feedback at each stage
- **Status Tracking**: Comprehensive workflow status management

## 📋 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.9+ |
| **Database** | PostgreSQL, SQLAlchemy |
| **AI/ML** | OpenAI GPT-4, SerpAPI |
| **Frontend** | React 18, Tailwind CSS |
| **State Management** | React Query |
| **Notifications** | SMTP, MS Teams Webhooks |
| **Export** | python-docx, reportlab |
| **Authentication** | JWT (configurable) |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL database
- OpenAI API key
- (Optional) SerpAPI key for web search

### Backend Setup

1. **Clone and navigate to backend**:
```bash
cd kickstart
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database**:
```bash
# Ensure PostgreSQL is running
# Create database and update .env with database URL
```

6. **Run the backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env if needed
```

4. **Run the frontend**:
```bash
npm start
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Create a New Book
1. Click "Create New Book" on the dashboard
2. Enter book title and detailed requirements
3. System automatically generates outline using AI

### 2. Review and Approve Outline
1. Review the AI-generated outline
2. Add feedback notes if needed
3. Approve to proceed to chapter generation
4. Request regeneration if changes needed

### 3. Generate Chapters
1. Chapters are generated sequentially
2. Each chapter uses previous chapters as context
3. Review and provide feedback on each chapter
4. Regenerate chapters if needed

### 4. Final Review and Export
1. Once all chapters are complete, proceed to final review
2. Add any final notes or approve for compilation
3. Export book in desired format (DOCX, PDF, TXT)

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# AI Services
OPENAI_API_KEY=your_openai_key_here
SERPAPI_KEY=your_serpapi_key_here

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# MS Teams (Optional)
TEAMS_WEBHOOK_URL=your_teams_webhook_url

# Security
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## 📊 API Endpoints

### Books
- `GET /api/v1/books` - List all books
- `POST /api/v1/books` - Create new book
- `GET /api/v1/books/{id}` - Get book details
- `PUT /api/v1/books/{id}/outline` - Update outline
- `POST /api/v1/books/{id}/regenerate-outline` - Regenerate outline

### Chapters
- `GET /api/v1/books/{id}/chapters` - List book chapters
- `POST /api/v1/books/{id}/chapters/{number}` - Generate chapter

### Export
- `POST /api/v1/books/{id}/export` - Export book

## 🔔 Notifications

The system sends notifications for key events:
- Outline ready for review
- Chapter generation complete
- Waiting for human feedback
- Book compilation complete
- Errors or workflow pauses

### Email Configuration
Configure SMTP settings in `.env` for email notifications.

### MS Teams Integration
Add Teams webhook URL to receive notifications in Microsoft Teams.

## 🧠 AI Integration

### OpenAI Configuration
- Uses GPT-4 for high-quality content generation
- Configurable model selection in settings
- Temperature and token limits optimized for book generation

### Web Search Integration
- SerpAPI integration for research-backed content
- Automatic fact-checking and source incorporation
- Configurable search depth and sources

## 📈 Workflow States

```
draft_outline → review_outline → generating_chapters → reviewing_chapters → compiling → completed
      ↓              ↓                    ↓                    ↓           ↓
   paused        paused               paused               paused      paused
```

## 🧪 Testing

### Backend Tests
```bash
# Run tests (when implemented)
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend Deployment
1. Set up production database
2. Configure environment variables
3. Build and deploy using Docker or preferred method
4. Run migrations if using Alembic

### Frontend Deployment
1. Build for production: `npm run build`
2. Deploy to static hosting (Vercel, Netlify, etc.)
3. Configure API URL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the troubleshooting guide
3. Create an issue with detailed information

## 🎯 Performance Considerations

- **Async Operations**: All database operations are async
- **Caching**: React Query provides intelligent caching
- **Background Tasks**: Heavy operations run in background
- **Rate Limiting**: Configurable API rate limiting
- **Database Optimization**: Indexed queries for performance

## 🔒 Security Features

- **JWT Authentication**: Secure API access
- **Input Validation**: Comprehensive input validation
- **SQL Injection Prevention**: ORM-based queries
- **CORS Configuration**: Proper cross-origin setup
- **Environment Variables**: Sensitive data in environment

## 📱 Mobile Compatibility

The frontend is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablet devices
- Mobile devices (iOS and Android)

## 🔄 Continuous Integration

The system supports CI/CD pipelines for:
- Automated testing
- Code quality checks
- Automated deployment
- Security scanning

---

**Built with ❤️ using modern web technologies**
"# Automated_Book_Generated" 
