# 🚀 Localhost Setup Guide

## Quick Start - One Command Setup

### Option 1: Use the Batch File (Windows)
```bash
cd C:\Users\RAO HAMZA\Desktop\kickstart
start.bat
```

### Option 2: Use Python Script
```bash
cd C:\Users\RAO HAMZA\Desktop\kickstart
python start.py
```

### Option 3: Manual Setup
```bash
# Step 1: Activate virtual environment
venv\Scripts\activate.bat

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access Points

Once the server is running, open these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **🎨 Frontend** | http://localhost:3000 | React application |
| **🔧 Backend API** | http://localhost:8000 | FastAPI server |
| **📚 API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **❤️ Health Check** | http://localhost:8000/health | System health status |
| **🗄️ Database Health** | http://localhost:8000/api/v1/database/health | Database status |
| **📊 System Info** | http://localhost:8000/api/v1/system/info | System information |

## 📋 Prerequisites

1. **PostgreSQL** running on localhost:5432
2. **Database** named `automated_book` created
3. **Python 3.9+** installed
4. **Node.js 16+** installed (for frontend)

## 🔧 Database Setup

Your database connection is configured in `.env`:
```
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/automated_book
```

The system will automatically:
- ✅ Create all necessary tables
- ✅ Set up indexes and triggers
- ✅ Insert sample data
- ✅ Verify everything is working

## 🎯 What Happens on Startup

1. **📡 Database Connection** - Tests PostgreSQL connection
2. **🔄 Database Migration** - Creates tables and setup
3. **✅ Health Check** - Verifies all systems ready
4. **🌐 Server Start** - Starts FastAPI on port 8000

## 🛠️ Troubleshooting

### Database Connection Issues
```bash
# Test database connection
psql -h localhost -p 5432 -U postgres -d automated_book

# If database doesn't exist, create it:
CREATE DATABASE automated_book;
```

### Port Already in Use
```bash
# Kill processes on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Virtual Environment Issues
```bash
# Create new virtual environment
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 🎨 Frontend Setup

In a separate terminal:
```bash
cd C:\Users\RAO HAMZA\Desktop\kickstart\frontend
npm install
npm start
```

## 📱 Using the System

1. Open http://localhost:3000
2. Click "Create New Book"
3. Enter book title and requirements
4. Watch AI generate outline
5. Review and approve outline
6. Generate chapters
7. Export final book

## 🔍 Database Management

You can manage the database via API endpoints:

### Check Database Health
```bash
GET http://localhost:8000/api/v1/database/health
```

### View Database Statistics
```bash
GET http://localhost:8000/api/v1/database/stats
```

### View All Tables
```bash
GET http://localhost:8000/api/v1/database/tables
```

### Run Migrations Manually
```bash
POST http://localhost:8000/api/v1/database/migrate
```

## 🎉 Success!

When you see this output, everything is working:

```
🚀 Starting Automated Book Generation System...
==================================================
📡 Step 1: Checking database connection...
✅ Database connection successful!

🔄 Step 2: Running database migrations...
✅ Database migrations completed!
   Tables created: ['books', 'chapters']

🌐 Step 3: Starting FastAPI server...
==================================================
🎉 System is ready!

📍 Localhost URLs:
   🎨 Frontend: http://localhost:3000
   🔧 Backend:  http://localhost:8000
   📚 API Docs: http://localhost:8000/docs
   ❤️ Health:   http://localhost:8000/health
   🗄️ Database: http://localhost:8000/api/v1/database/health

🚀 Starting server...
```

**Your Automated Book Generation System is now running!** 🎯
