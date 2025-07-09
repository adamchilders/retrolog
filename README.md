# RetroLog - AI-Powered Reflective Journaling Application

RetroLog is a modern web application designed to help users build better habits, maintain discipline, and track personal growth through structured journaling with AI-powered insights. The application uses Google's Gemini AI to provide personalized insights and adaptive questioning based on user entries.

## 🌟 Features

### Core Functionality
- **Time-Block Journaling**: Structured entries for Morning, Lunch, and Evening sessions
- **AI-Powered Insights**: Get personalized analysis and actionable suggestions for individual entries
- **Adaptive Questioning**: AI generates relevant questions based on your past entries and patterns
- **Summary Analytics**: Weekly, daily, and monthly trend analysis with AI-generated insights
- **User Authentication**: Secure login and registration system with JWT tokens
- **Responsive Design**: Clean, terminal-inspired interface that works across devices

### AI Features
- **Individual Entry Analysis**: Gemini AI analyzes each journal entry to identify patterns, sentiments, and themes
- **Actionable Suggestions**: Receive 1-2 specific, actionable steps to improve well-being and productivity
- **Smart Question Generation**: AI creates personalized questions based on your journaling history
- **Trend Analysis**: Comprehensive summaries of your progress over different time periods

## 🏗️ Architecture

RetroLog follows a modern microservices architecture with the following components:

### Backend (FastAPI + Python)
- **API Framework**: FastAPI for high-performance REST API
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication with OAuth2
- **AI Integration**: Google Gemini API for insights and question generation
- **Containerization**: Docker for consistent deployment

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript for type safety
- **HTTP Client**: Axios for API communication
- **Styling**: Terminal-inspired CSS design
- **Build Tool**: Create React App with TypeScript template
- **Deployment**: Nginx for production serving

### Database Schema
- **Users**: User accounts with secure password hashing
- **Journal Entries**: Time-blocked entries with timestamps
- **Answers**: Question-answer pairs for each journal entry

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API key
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd retrolog
   ```

2. **Set up environment variables**
   Create a `.env` file in the `backend` directory:
   ```env
   GOOGLE_API_KEY="your_gemini_api_key_here"
   ```

3. **Build and run the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### First Time Setup
1. Register a new account through the web interface
2. Log in with your credentials
3. Start your first journal entry for the current time block
4. Explore AI insights and adaptive questioning features

## 📁 Project Structure

```
retrolog/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI application and routes
│   │   ├── models.py       # SQLAlchemy database models
│   │   ├── schemas.py      # Pydantic data schemas
│   │   ├── crud.py         # Database operations
│   │   ├── services.py     # AI services and business logic
│   │   └── database.py     # Database configuration
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   └── App.css         # Styling
│   ├── public/             # Static assets
│   ├── Dockerfile          # Frontend container configuration
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Multi-container orchestration
├── REQUIREMENTS.md         # System requirements
└── README.md              # This file
```

## 🔧 Development

### Running in Development Mode

**Backend Development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**
```bash
cd frontend
npm install
npm start
```

### Environment Variables
- `GOOGLE_API_KEY`: Required for AI features
- `DATABASE_URL`: MySQL connection string (auto-configured in Docker)
- `SECRET_KEY`: JWT signing key (auto-generated)

## 🔒 Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **JWT Authentication**: Stateless authentication with configurable expiration
- **CORS Protection**: Configured for frontend-backend communication
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🤖 AI Integration

RetroLog leverages Google's Gemini AI for several key features:

### Insight Generation
- Analyzes journal entries for patterns and themes
- Provides actionable suggestions for improvement
- Identifies sentiment and emotional trends

### Adaptive Questioning
- Generates personalized questions based on past entries
- Builds upon previous themes and challenges
- Fallback to default questions if AI is unavailable

### Summary Analytics
- Creates comprehensive trend analysis
- Identifies successes and areas for improvement
- Provides habit-building recommendations

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Internet connection for AI features

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **Network**: Stable broadband connection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

## 🔮 Future Enhancements

- Mobile application development
- Advanced analytics dashboard
- Integration with fitness and productivity apps
- Multi-language support
- Offline mode capabilities
- Data export functionality
