# Social Media Generator Backend

A FastAPI-based backend service for generating AI-powered social media content using OpenAI's GPT and DALL-E APIs. This system allows users to create campaigns, manage content generation in batches, and track progress through a comprehensive API.



## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL database (with existing schema)
- OpenAI API key
- Git (for cloning the repository)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
mkdir social-media-generator/backend
cd social-media-generator/backend
git clone <your-repository-url> .
```

### 2. Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the example environment file and configure your credentials:

```bash
# Copy the example environment file
cp .env.example .env
```

Then edit the `.env` file with your actual credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/social_media_db

# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Security Configuration
SECRET_KEY=your-secret-key-here

# Optional: Additional Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Database Setup

#### For Existing Database
The application expects an existing PostgreSQL database with the following schema. Ensure your database matches this structure:

#### Initialize New Database (Optional)
If starting from scratch:
```bash
# Create PostgreSQL database
createdb social_media_db

# Initialize tables and create default data
python init_db.py
```

**Default Admin Account Created:**
After running `init_db.py`, a default admin account will be created:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

You can use this account immediately for testing or create additional users via the registration API.

### 6. Start the Application
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 7. Quick Start with Admin Account
Once the application is running, you can immediately start using the API with the default admin account:

**Login Endpoint**: `POST http://localhost:8000/api/auth/login`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Or register additional users at: `POST http://localhost:8000/api/auth/register`
```json
  {
    "username": "adminnew",
    "email": "admin@example.com",
    "password": "adminnew123",
    "first_name": "adminnew",
    "last_name": "test"
  }
```

## 🚀 Features

### Core Functionality
- **AI Content Generation**: Automated caption and image generation using OpenAI's GPT-4o-mini and DALL-E 3
- **Campaign Management**: Create and manage social media campaigns with brand-specific settings
- **Batch Processing**: Generate multiple social media posts concurrently with rate limiting
- **User Authentication**: JWT-based authentication with secure user management
- **Progress Tracking**: Real-time monitoring of batch generation progress
- **Performance Testing**: Built-in performance testing capabilities

### API Endpoints
- **Authentication**: Register, login, logout, and user profile management
- **Campaigns**: Full CRUD operations for campaign management
- **Batch Processing**: Start batch jobs, monitor progress, and retrieve batch history
- **Health Monitoring**: API health check endpoints

## 🛠 Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application

### Database
- **PostgreSQL**: Primary database for data persistence
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management (ready for use)

### Authentication & Security
- **JWT (JSON Web Tokens)**: Stateless authentication with token blacklisting
- **bcrypt**: Password hashing
- **python-jose**: JWT token handling
- **HTTPBearer**: Token-based authentication scheme

### AI Integration
- **OpenAI API**: GPT-4o-mini for caption generation
- **DALL-E 3**: AI image generation

### Development Tools
- **Python 3.11+**: Programming language
- **python-dotenv**: Environment variable management
- **Pydantic**: Data validation and serialization
- **email-validator**: Email validation for user registration


## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout (with token blacklisting)
- `GET /api/auth/me` - Get current user info

#### Campaigns
- `POST /api/campaigns/` - Create new campaign
- `GET /api/campaigns/` - List user's campaigns (with pagination)
- `GET /api/campaigns/{id}` - Get specific campaign
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign (soft delete)

#### Batch Processing
- `POST /api/campaigns/{id}/generate-batch` - Start batch generation
- `GET /api/campaigns/{id}/batches` - Get all batch jobs for a campaign
- `GET /api/batch-jobs/{id}/status` - Check individual batch status

#### Health
- `GET /api/health` - API health check

## 🗄 Database Schema

### Users Table
```sql
users (
    id UUID PRIMARY KEY [uuid_generate_v4()],
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT now()
)
```

### Campaigns Table (Existing Schema)
```sql
campaigns (
    id UUID PRIMARY KEY [uuid_generate_v4()],
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    brand_name VARCHAR(255) NOT NULL,
    target_audience TEXT NULL,
    tone_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)
```

### Batch Jobs Table
```sql
batch_jobs (
    id VARCHAR PRIMARY KEY,
    campaign_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    total_posts INTEGER DEFAULT 0,
    completed_posts INTEGER DEFAULT 0,
    failed_posts INTEGER DEFAULT 0,
    created_by VARCHAR,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    error_log TEXT
)
```

### Campaign Posts Table
```sql
campaign_posts (
    id VARCHAR PRIMARY KEY,
    batch_job_id VARCHAR NOT NULL,
    campaign_id VARCHAR NOT NULL,
    brand_name VARCHAR NOT NULL,
    topic VARCHAR,
    tone VARCHAR NOT NULL,
    brief TEXT,
    target_audience VARCHAR,
    generated_caption TEXT,
    generated_image_url VARCHAR,
    status VARCHAR DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
)
```

## 🎯 Usage Examples

### 1. User Registration & Authentication

#### Option A: Use Default Admin Account
You can immediately use the pre-created admin account:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

#### Option B: Register a New User
```bash
# Register a new user (example)
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "first_name": "admin",
    "last_name": "test"
  }'

# Login and get token (using admin account)
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Logout (invalidate token)
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Campaign Management
```bash
# Create a campaign
curl -X POST "http://localhost:8000/api/campaigns/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Summer Collection 2025",
    "description": "Promotional campaign for summer line",
    "brand_name": "FashionBrand",
    "target_audience": "Young adults 18-30",
    "tone_id": "enthusiastic"
  }'

# Get all campaigns
curl -X GET "http://localhost:8000/api/campaigns/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Batch Content Generation
```bash
# Start batch generation
curl -X POST "http://localhost:8000/api/campaigns/CAMPAIGN_ID/generate-batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Summer Posts Batch",
    "posts": [
      {
        "brand_name": "FashionBrand",
        "topic": "New Summer Collection",
        "tone": "enthusiastic",
        "brief": "Showcase our vibrant summer clothing line",
        "target_audience": "Fashion-forward millennials"
      }
    ]
  }'

# Get batch history for campaign
curl -X GET "http://localhost:8000/api/campaigns/CAMPAIGN_ID/batches" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for content generation | Yes | - |
| `SECRET_KEY` | JWT signing secret | Yes | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | 30 |

### Performance Settings

- **Concurrent Processing**: Maximum 5 simultaneous OpenAI API calls
- **Rate Limiting**: Built-in semaphore-based concurrency control
- **Token Expiration**: 30 minutes by default
- **Pagination**: Default limit of 100 records per request

## 🏗 Architecture & Design Decisions

### Authentication Strategy
- **JWT Tokens**: Stateless authentication for scalability
- **Token Blacklisting**: In-memory blacklist for secure logout functionality
- **User Isolation**: All resources are user-scoped for security
- **Password Security**: bcrypt hashing with salt

### Content Generation
- **Concurrent Processing**: Batch jobs process multiple posts simultaneously
- **Error Handling**: Individual post failures don't stop the entire batch
- **Progress Tracking**: Real-time status updates for user experience
- **Status Management**: Detailed status tracking for each post and batch

### Database Design
- **UUID Primary Keys**: For better security and distribution (campaigns, users)
- **Soft Deletes**: Campaign deletion preserves data integrity
- **Audit Trails**: Created/updated timestamps for all entities
- **Foreign Key Relationships**: Proper data relationships and constraints

### API Design
- **RESTful Principles**: Clear resource-based URL structure
- **Consistent Responses**: Standardized response formats with proper HTTP status codes
- **Pagination Support**: Efficient data retrieval for large datasets
- **Authentication Required**: All endpoints (except auth) require valid tokens

## 🧪 Testing

### Performance Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Run performance tests (requires OpenAI API key)
python test_performance.py
```

### OpenAI Service Testing
```bash
# Test OpenAI integration
python -c "import asyncio; from test import test_openai; asyncio.run(test_openai())"
```

### API Testing
- Use the interactive Swagger UI at `/docs`
- Import Postman collections for comprehensive testing
- Health check endpoint for monitoring: `GET /api/health`

## 🚦 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check DATABASE_URL format (should be `postgresql://` not `psql://`)
   - Ensure database exists and user has permissions

2. **OpenAI API Errors**
   - Verify API key is valid and properly set in `.env`
   - Check account credits and usage limits
   - Monitor rate limits (5 concurrent requests max)

3. **Authentication Issues**
   - Ensure SECRET_KEY is set in `.env`
   - Check token expiration (30 minutes default)
   - Verify user exists and password is correct
   - For logout issues, check token blacklisting

4. **Environment Variable Issues**
   - Ensure `python-dotenv` is installed
   - Check `.env` file is in the backend directory
   - Verify environment variables are loaded correctly

5. **Virtual Environment Issues**
   - Activate virtual environment: `source venv/bin/activate`
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.11+)

### Performance Optimization

1. **Database**: Use connection pooling for high-traffic scenarios
2. **Caching**: Implement Redis for token blacklisting in production
3. **Background Jobs**: Use Celery for asynchronous batch processing
4. **Rate Limiting**: Adjust `max_concurrent` in BatchGenerationService for OpenAI limits

## 🔮 Future Enhancements

- **Real-time Updates**: WebSocket support for live progress updates
- **Content Templates**: Predefined templates for different content types
- **Analytics**: Content performance tracking and analytics
- **Multi-platform Support**: Integration with various social media platforms
- **Workflow Management**: Advanced campaign scheduling and automation
- **File Upload**: Support for uploading images and brand assets
- **Content Moderation**: Automated content moderation and filtering

## 📁 Project Structure

```
backend/
├── api/                    # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── batch.py           # Batch processing endpoints
│   └── campaigns.py       # Campaign management endpoints
├── models/                # Database models
│   ├── user.py           # User model
│   ├── campaign.py       # Campaign model
│   ├── batch_job.py      # Batch job model
│   └── campaign_post.py  # Campaign post model
├── services/              # Business logic services
│   ├── batch_service.py  # Batch processing logic
│   └── openai_service.py # OpenAI API integration
├── .gitignore           # Git ignore rules (excludes venv/ and .env/)
├── auth.py              # Authentication utilities
├── database.py          # Database configuration
├── init_db.py          # Database initialization
├── main.py             # FastAPI application
├── requirements.txt    # Python dependencies
├── test.py            # OpenAI service tests
└── test_performance.py # Performance testing
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review troubleshooting section above
- Test endpoints using the Swagger UI

---

**Built with ❤️ using FastAPI and OpenAI**  