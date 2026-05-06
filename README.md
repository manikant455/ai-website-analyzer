# 🚀 AI Website Analyzer SaaS

> An intelligent website analysis platform that combines SEO auditing, security scanning, and AI-powered recommendations. Built with FastAPI and designed for real-world use.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI-412991.svg)](https://openai.com/)

---

## 📊 Live Demo Results

Here's a real analysis of **dabusco.com** performed by this tool:

### Overall Scores
- 🟡 **SEO Score**: 75/100 - Needs Improvement
- 🔴 **Security Score**: 25/100 - Critical Issues Found
- 🟢 **Performance**: 0.59s Load Time - Excellent
- 🟢 **Mobile**: Responsive Design - Good

### Key Findings
✅ Fast loading speed (0.59 seconds)
✅ Valid SSL certificate (Let's Encrypt)
✅ Mobile-friendly design
❌ Title too short (23 characters - needs 30-60)
❌ Missing meta description
❌ No H2 heading structure
🔴 All 6 security headers missing (CRITICAL)
🔴 No Content-Security-Policy implemented


### AI Recommendations Generated
1. **Implement Content-Security-Policy header immediately**
2. **Add Strict-Transport-Security header for HTTPS enforcement**
3. **Create compelling meta description (120-160 characters)**
4. **Expand title tag to 30-60 characters for better SEO**
5. **Add H2 headings for proper content hierarchy**

---

## ✨ What This Project Does

### 🔍 SEO Analysis Engine
- **Title Tag Audit**: Checks length, existence, and optimization
- **Meta Description Check**: Validates presence and length (120-160 chars)
- **Heading Structure**: Analyzes H1-H3 hierarchy
- **Image Optimization**: Detects missing alt text
- **Link Analysis**: Counts internal vs external links
- **Mobile Check**: Verifies viewport meta tag
- **Load Time**: Measures page speed
- **SSL Certificate**: Validates certificate chain
- **Scoring**: Automated 0-100 SEO score

### 🛡️ Security Scanner
- **SSL/TLS Verification**: Certificate validation
- **Security Headers**: Checks 6 critical headers
  - Strict-Transport-Security
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
  - X-XSS-Protection
  - Referrer-Policy
- **Port Scanning**: Detects open ports
- **Vulnerability Detection**: Identifies security gaps
- **Scoring**: 0-100 security rating

### 🤖 AI-Powered Intelligence
- **OpenAI GPT Integration**: Smart, contextual analysis
- **Smart Fallback**: Works without API key using rule-based analysis
- **Actionable Insights**: Prioritized fix recommendations
- **Clear Indicators**: Shows whether AI or fallback was used

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core programming language |
| **FastAPI** | High-performance web framework |
| **Uvicorn** | ASGI server |
| **BeautifulSoup4** | HTML parsing and analysis |
| **Pydantic** | Data validation |
| **OpenAI API** | AI-powered recommendations |
| **HTTPX** | Async HTTP client |
| **Docker** | Containerization |
| **REST API** | Clean API architecture |

---

## 📁 Project Structure
ai-website-analyzer/
│
├── app/
│ ├── main.py # Application entry point
│ ├── api/
│ │ └── routes.py # All API endpoints
│ ├── services/
│ │ ├── seo_analyzer.py # SEO analysis engine
│ │ ├── security_checker.py # Security scanning
│ │ └── ai_engine.py # AI analysis engine
│ ├── core/
│ │ └── config.py # Configuration
│ └── workers/
│ └── task_queue.py # Background tasks
│
├── tests/ # Test files
├── docker/ # Docker configs
├── requirements.txt # Dependencies
├── Dockerfile # Docker image
├── docker-compose.yml # Multi-container setup
├── .env.example # Environment template
├── .gitignore # Git ignore rules
└── README.md # Documentation


---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git

### Method 1: Local Installation (Easy)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-website-analyzer.git
cd ai-website-analyzer

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment (optional)
cp .env.example .env
# Edit .env if you want to add OpenAI API key

# 6. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Open in browser
# http://localhost:8000/docs


Method 2: Docker (Recommended)

# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-website-analyzer.git
cd ai-website-analyzer

# 2. Run with Docker Compose
docker-compose up --build

# 3. Access the application
# http://localhost:8000/docs

# 4. Stop when done
docker-compose down

Method 3: Docker Individual Container
# Build the image
docker build -t website-analyzer .

# Run the container
docker run -d -p 8000:8000 --name analyzer website-analyzer

# Check logs
docker logs -f analyzer

# Stop container
docker stop analyzer

📚 API Documentation
Interactive API Docs
Once running, visit http://localhost:8000/docs for Swagger UI

API Endpoints
Method	Endpoint	Description
GET	/	API information
GET	/api/v1/health	Health check & AI status
POST	/api/v1/scan	Start a website scan
GET	/api/v1/scan/{id}	Get scan results
GET	/api/v1/scans/recent	View recent scans

Usage Examples
1. Full Website Scan

curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "scan_type": "full"}'


2. SEO Only Scan

curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "scan_type": "seo"}'


3. Security Only Scan

curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "scan_type": "security"}'


4. Get Scan Results
curl http://localhost:8000/api/v1/scan/YOUR_SCAN_ID

5. Health Check

curl http://localhost:8000/api/v1/health

Scan Types
full - Complete SEO + Security analysis

seo - SEO analysis only

security - Security analysis only

⚙️ Configuration
Environment Variables (.env file)
env
# Application Settings
APP_NAME=AI Website Analyzer
DEBUG=True

# AI Configuration (Optional)
# Get API key: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-key-here

# Database (Optional)
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
AI Modes
Mode	Configuration	Analysis Type
AI-Powered	Set OPENAI_API_KEY	GPT-3.5 Turbo analysis
Fallback	Leave empty	Rule-based analysis
Without API Key: The app works perfectly using intelligent rule-based analysis
With API Key: Get advanced AI-powered insights and recommendations

🧪 Testing
Using Swagger UI (Easiest)
Open http://localhost:8000/docs

Click any endpoint

Click "Try it out"

Enter parameters

Click "Execute"

Using Command Line
bash
# Test scan
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "scan_type": "full"}' | python3 -m json.tool

# Check health
curl http://localhost:8000/api/v1/health | python3 -m json.tool

# View recent scans
curl http://localhost:8000/api/v1/scans/recent | python3 -m json.tool
🎯 Real-World Use Cases
Web Developers: Pre-launch website audits

SEO Specialists: Client website analysis

Security Teams: Quick vulnerability scans

Digital Marketers: Competitor analysis

Freelancers: Add value to client services

Students: Learn web technologies

📈 Sample Response
json
{
  "id": "abc-123-def-456",
  "url": "https://example.com",
  "status": "completed",
  "seo_score": {
    "score": 75,
    "title_tag": {
      "exists": true,
      "content": "Example Website",
      "length": 16,
      "issues": ["Title is too short (less than 30 characters)"]
    },
    "meta_description": {
      "exists": false,
      "issues": ["Missing meta description"]
    },
    "load_time": 0.59,
    "mobile_friendly": true
  },
  "security_score": {
    "score": 25,
    "ssl_valid": true,
    "vulnerabilities": [
      "Missing security headers: Content-Security-Policy"
    ]
  },
  "ai_summary": "Analysis revealed issues with meta tags and security headers...",
  "ai_suggestions": [
    "Add Content-Security-Policy header",
    "Create meta description (120-160 characters)"
  ],
  "ai_analysis_metadata": {
    "is_ai_generated": false,
    "note": "⚠️ Fallback rule-based analysis"
  }
}
🐳 Docker Commands
bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build --force-recreate

# Remove everything
docker-compose down -v
