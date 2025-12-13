<p align="center">
  <img src="https://img.shields.io/badge/AI-Career%20Planning-6366f1?style=for-the-badge&logo=brain&logoColor=white" alt="AI Career Planning"/>
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-22c55e?style=for-the-badge&logo=openai&logoColor=white" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/LiveKit-Voice%20AI-f59e0b?style=for-the-badge&logo=webrtc&logoColor=white" alt="Voice AI"/>
</p>

<h1 align="center">🚀 CareerPath</h1>

<p align="center">
  <strong>AI-Powered Career Simulation Platform</strong><br>
  Transform career uncertainty into a personalized roadmap with 7 AI agents working in harmony
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-demo">Demo</a>
</p>

---

## 🌟 Overview

**CareerPath** is an intelligent career simulation platform that helps students and professionals make informed career decisions through AI-driven analysis, real-time market data, and personalized roadmaps. The platform combines cutting-edge multi-agent AI orchestration with a beautiful, intuitive interface to deliver actionable career insights.

### What Makes CareerPath Different?

- **🤖 7 Specialized AI Agents** - Each agent handles a specific aspect of career planning
- **🗣️ Voice AI Counselor** - Real-time career counseling via LiveKit voice integration
- **📊 Data-Driven Insights** - Real-time market data from Tavily Search API
- **🎯 Personality Matching** - "Vibe Check" system for psychometric alignment
- **📈 Visual Roadmaps** - Interactive timelines with Recharts visualizations
- **📄 PDF Export** - Comprehensive career reports for offline review

---

## ✨ Features

### 🎯 Career Matching & Analysis

| Feature | Description |
|---------|-------------|
| **Smart Career Matching** | AI analyzes your profile to identify top 3 career fits with detailed reasoning |
| **Multi-Dimensional Scoring** | Skill fit, interest fit, market fit, and personality fit scores |
| **Market Intelligence** | Real-time salary data, job demand, and industry trends |
| **Gap Analysis** | Identifies skill gaps with personalized learning paths |

### 📅 Personalized Roadmaps

| Feature | Description |
|---------|-------------|
| **3 Career Paths** | Conservative, Realistic, and Ambitious timelines |
| **Year-by-Year Plans** | Detailed milestones with quarterly breakdowns |
| **Cost & Time Estimates** | Hours required and investment needed per milestone |
| **Success Indicators** | Track progress with measurable KPIs |

### 💰 Financial Projections

| Feature | Description |
|---------|-------------|
| **Total Investment Calculator** | Education, certifications, tools, and living costs |
| **ROI Analysis** | 5-year and 10-year return projections |
| **Break-Even Analysis** | When your investment pays off |
| **Salary Progression** | Year-over-year income projections |

### ⚠️ Risk Assessment

| Feature | Description |
|---------|-------------|
| **Success Probability** | AI-calculated success score (0-100%) |
| **Risk Categories** | Market, personal, financial, and technical risks |
| **Scenario Analysis** | Best case, worst case, and most likely outcomes |
| **Mitigation Strategies** | Actionable risk reduction recommendations |

### 🗣️ Voice AI Counselor

| Feature | Description |
|---------|-------------|
| **Real-Time Voice Chat** | Talk to an AI career counselor anytime |
| **Phone Integration** | SIP telephony support for phone calls |
| **Personalized Context** | Voice agent has access to your career roadmap |
| **Gemini Realtime** | Powered by Google's advanced AI |

### 🔐 Authentication & Security

| Feature | Description |
|---------|-------------|
| **Email/Password Auth** | Secure JWT-based authentication |
| **Social Login** | Google and GitHub OAuth integration |
| **Email Verification** | Secure email verification flow |
| **Password Recovery** | Secure password reset with token validation |

---

## 🏗️ Architecture

### Multi-Agent Workflow

CareerPath uses **LangGraph** to orchestrate 7 specialized AI agents in a sophisticated workflow:

```
                                    START
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │   Profile Parser    │
                           │  (Context Builder)  │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │   Career Matcher    │
                           │   (Fit Analyzer)    │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │    Market Scout     │
                           │   (Data Fetcher)    │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │    Gap Analyst      │
                           │   (Skill Mapper)    │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │ Timeline Simulator  │
                           │ (Roadmap Creator)   │
                           └──────────┬──────────┘
                                      │
                         ┌────────────┴────────────┐
                         │     (Parallel Run)      │
                         ▼                         ▼
               ┌─────────────────┐      ┌─────────────────┐
               │Financial Advisor│      │  Risk Assessor  │
               │(ROI Calculator) │      │(Success Predictor)
               └────────┬────────┘      └────────┬────────┘
                        │                        │
                        └───────────┬────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │Dashboard Formatter  │
                         │   (UI Mapper)       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                                   END
```

### AI Agents Deep Dive

| Agent | Role | Key Functions |
|-------|------|---------------|
| **Profile Parser** | Context Builder | Normalizes GPA, classifies persona, generates semantic summary |
| **Career Matcher** | Fit Analyzer | Matches profile to careers, scores on 4 dimensions, provides reasoning |
| **Market Scout** | Data Fetcher | Real-time market data, salary ranges, skill requirements |
| **Gap Analyst** | Skill Mapper | Skill gaps, education gaps, "vibe check" for personality fit |
| **Timeline Simulator** | Roadmap Creator | 3 career paths, year-by-year milestones, buffer time |
| **Financial Advisor** | ROI Calculator | Investment analysis, break-even, funding options |
| **Risk Assessor** | Success Predictor | Probability scoring, risk factors, mitigation strategies |

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React/Vite)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   Landing   │ │  Simulation │ │  Dashboard  │ │   Voice AI  │   │
│  │    Page     │ │   Wizard    │ │    View     │ │   Client    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
┌─────────────────┐ ┌───────────────┐ ┌────────────────┐
│  Node.js API    │ │  Python API   │ │   LiveKit      │
│  (Express)      │ │  (FastAPI)    │ │   Server       │
│                 │ │               │ │                │
│ • Auth/JWT      │ │ • LangGraph   │ │ • Voice Agent  │
│ • OAuth         │ │ • AI Agents   │ │ • WebRTC       │
│ • Email         │ │ • Simulation  │ │ • SIP/Phone    │
└────────┬────────┘ └───────┬───────┘ └────────────────┘
         │                  │
         └────────┬─────────┘
                  ▼
         ┌───────────────┐
         │   MongoDB     │
         │   Database    │
         │               │
         │ • Users       │
         │ • Accounts    │
         │ • Roadmaps    │
         └───────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI Framework |
| **TypeScript** | Type Safety |
| **Vite** | Build Tool |
| **TailwindCSS 4** | Styling |
| **Framer Motion** | Animations |
| **Recharts** | Data Visualization |
| **Redux Toolkit** | Global State |
| **Zustand** | Simulation State |
| **React Hook Form** | Form Management |
| **LiveKit Components** | Voice AI Integration |
| **jsPDF** | PDF Export |

### Backend (Node.js)
| Technology | Purpose |
|------------|---------|
| **Express 5** | Web Framework |
| **TypeScript** | Type Safety |
| **Prisma** | ORM |
| **MongoDB** | Database |
| **Passport.js** | Authentication |
| **JWT** | Token Management |
| **Nodemailer** | Email Service |
| **AWS S3** | File Storage |

### Backend (Python)
| Technology | Purpose |
|------------|---------|
| **FastAPI** | API Framework |
| **LangChain** | LLM Framework |
| **LangGraph** | Agent Orchestration |
| **Tavily** | Market Data Search |
| **LiveKit Agents** | Voice AI |
| **Pydantic** | Data Validation |
| **Motor** | Async MongoDB |

### AI & ML
| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4** | Primary LLM |
| **Anthropic Claude** | Alternative LLM |
| **Groq** | Fast Inference |
| **Google Gemini** | Voice AI |
| **Tavily Search** | Real-time Data |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| **LiveKit Cloud** | Voice/Video Platform |
| **MongoDB Atlas** | Database Hosting |
| **AWS S3** | File Storage |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.12
- **MongoDB** (local or Atlas)
- **pnpm** or **npm**
- **uv** (Python package manager) or **pip**

### Environment Variables

#### Python Server (`.env`)
```env
# LLM Configuration
DEFAULT_LLM_TYPE=groq  # "groq", "openai", or "anthropic"
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Search API
TAVILY_API_KEY=your_tavily_api_key

# Database
DATABASE_URL=mongodb+srv://...
ACCESS_JWT_SECRET=your_jwt_secret
REFRESH_JWT_SECRET=your_refresh_secret

# LiveKit (Voice AI)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
GOOGLE_API_KEY=your_google_api_key
```

#### Node.js Server (`.env`)
```env
PORT=8080
DATABASE_URL=mongodb+srv://...
FRONTEND_URL=http://localhost:5173

ACCESS_JWT_SECRET=your_jwt_secret
REFRESH_JWT_SECRET=your_refresh_secret

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Email
EMAIL_USER=your_email
EMAIL_PASS=your_app_password

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET_NAME=your_bucket_name
```

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/your-org/careerpath.git
cd careerpath
```

#### 2. Setup Frontend (Client)
```bash
cd client
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`

#### 3. Setup Node.js Server
```bash
cd server
npm install
npx prisma generate
npm run dev
```
Auth API will be available at `http://localhost:8080`

#### 4. Setup Python Server
```bash
cd python-server
uv sync  # or pip install -e .
uv run python main.py
```
AI API will be available at `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 5. Start Voice Agent (Optional)
```bash
cd python-server
uv run python voice_agent.py dev
```

---

## 📖 API Reference

### Career Simulation Endpoints

#### Start Career Matching (Stage 1)
```http
POST /match-careers
Content-Type: application/json

{
  "profile": {
    "current_education_level": "3rd Year B.Tech",
    "current_major": "Computer Science",
    "current_gpa": 8.5,
    "target_career_fields": ["Technology", "AI/ML"],
    "risk_tolerance": "Medium"
  }
}
```

#### Run Full Simulation (Stage 2)
```http
POST /simulate
Content-Type: application/json

{
  "profile": { ... },
  "selected_career": "Machine Learning Engineer",
  "session_id": "session_123"
}
```

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/signin` | User login |
| GET | `/api/auth/verify-email/:token` | Verify email |
| POST | `/api/auth/reset-password` | Request password reset |
| POST | `/api/auth/reset-password/:token` | Reset password |
| POST | `/api/auth/refresh` | Refresh JWT token |
| GET | `/api/auth/google` | Google OAuth |
| GET | `/api/auth/github` | GitHub OAuth |

---

## 📊 Dashboard Features

### Visualizations Included

- **📈 Salary Progression Chart** - Line chart comparing 3 career paths
- **🎯 Skills Radar** - Current vs required skill levels
- **📊 Risk Breakdown** - Pie chart of risk categories
- **💰 Investment Breakdown** - Where your money goes
- **📅 Timeline Progress** - Year-by-year milestone tracking
- **🔄 Path Comparison Table** - Side-by-side path metrics

### PDF Export

Export a comprehensive career report including:
- Executive summary with key metrics
- Selected career fit analysis
- Year-by-year roadmap
- Skills gap analysis with learning paths
- Financial projections and ROI
- Risk assessment and mitigation
- Personalized recommendations

---

## 🎙️ Voice AI Counselor

### Features

- **Real-time Conversation** - Natural voice interaction with AI counselor
- **Personalized Context** - Agent knows your career roadmap
- **Multi-Platform** - Web browser and phone (SIP) support
- **Function Calling** - Can run simulations during conversation

### Starting a Voice Session

```javascript
// Connect to voice agent
const connectionDetails = await fetch('/api/voice/token');
const room = new Room();
await room.connect(connectionDetails.serverUrl, connectionDetails.token);
```

---

## 🧪 "Vibe Check" System

CareerPath includes psychometric alignment checks to ensure career fit:

| User Trait | Target Environment | Warning |
|------------|-------------------|---------|
| Low Risk Tolerance | Startup | ⚠️ High stress mismatch |
| Theoretical Style | Hands-on Role | Consider research positions |
| Structured Preference | Dynamic Startup | May struggle with ambiguity |
| Introvert | Sales-heavy Role | Look for technical tracks |

---

## 📁 Project Structure

```
careerpath/
├── client/                    # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages
│   │   │   ├── Home/          # Landing page
│   │   │   ├── SimulatePage/  # Career simulation wizard
│   │   │   ├── CareerFitsPage/# Career selection
│   │   │   ├── DashboardPage/ # Results dashboard
│   │   │   ├── Login/         # Authentication
│   │   │   └── SignUp/        # Registration
│   │   ├── lib/               # Utilities & API
│   │   ├── store/             # Redux store
│   │   └── hooks/             # Custom hooks
│   └── package.json
│
├── server/                    # Node.js Backend
│   ├── src/
│   │   ├── auth/              # Authentication logic
│   │   ├── config/            # Passport, mailer config
│   │   ├── middleware/        # Express middleware
│   │   └── utils/             # Helper functions
│   ├── prisma/                # Database schema
│   └── package.json
│
├── python-server/             # Python AI Backend
│   ├── src/
│   │   ├── agents/            # 7 AI agents
│   │   │   ├── profile_parser.py
│   │   │   ├── career_matcher.py
│   │   │   ├── market_scout.py
│   │   │   ├── gap_analyst.py
│   │   │   ├── timeline_simulator.py
│   │   │   ├── financial_advisor.py
│   │   │   ├── risk_assessor.py
│   │   │   └── dashboard_formatter.py
│   │   ├── models/            # Data schemas
│   │   ├── graph.py           # LangGraph workflow
│   │   └── database.py        # MongoDB connection
│   ├── voice_agent.py         # LiveKit voice AI
│   ├── main.py                # FastAPI entry point
│   └── pyproject.toml
│
└── README.md
```

---

## 🤝 Team

**Team Forbidden Phishers** - Unisys U3 Hackathon

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain & LangGraph** - Multi-agent orchestration framework
- **LiveKit** - Real-time voice infrastructure
- **Tavily** - AI search for market data
- **Shadcn/ui** - Beautiful React components
- **Vercel** - Design inspiration

---

<p align="center">
  <strong>Built with ❤️ by Team Forbidden Phishers</strong>
</p>

<p align="center">
  <a href="#-careerpath">Back to Top ↑</a>
</p>
