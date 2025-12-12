# Career Path Simulator 🚀

AI-driven multi-agent system for personalized career simulation using LangChain and LangGraph.

## Overview

This system helps students make informed career decisions by providing:
- **4-6 year personalized career roadmaps**
- **Success probability scoring and risk analysis**
- **Financial ROI predictions**
- **Skill gap analysis with learning paths**
- **Interactive dashboard data for visualization**

## Architecture

The system uses a LangGraph workflow with 7 specialized AI agents:

```
START
  │
  ▼
┌─────────────────┐
│ ProfileParser   │  Node A: Context Builder
│ (Semantic       │  - Normalizes profile data
│  Summary)       │  - Classifies user persona
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MarketScout     │  Node B: RAG Retriever
│ (Real-time      │  - Fetches market data
│  Market Data)   │  - Salary ranges, requirements
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GapAnalyst      │  Node C: Diagnostic Engine
│ (Skill Gap      │  - Compares profile vs market
│  Analysis)      │  - Identifies bottlenecks
└────────┬────────┘
         │
    ┌────┴────┐
    │ Gap>80%?│ ──Yes──► AlternativePathSuggester
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│TimelineSimulator│  Node D: Core Engine
│ (Year-by-Year   │  - 3 paths: Conservative,
│  Simulation)    │    Realistic, Ambitious
└────────┬────────┘
         │
    ┌────┴────┐  (Parallel Execution)
    │         │
    ▼         ▼
┌────────┐  ┌────────────┐
│Financial│  │RiskAssessor│
│Advisor  │  │(Probability│
│(ROI)    │  │ Engine)    │
└────┬───┘  └─────┬──────┘
     │            │
     └─────┬──────┘
           │
           ▼
┌─────────────────┐
│DashboardFormatter│  Node G: UI Mapper
│ (Frontend-ready │  - React Flow data
│  JSON)          │  - Recharts data
└────────┬────────┘
         │
         ▼
        END
```

## Installation

```bash
# Clone the repository
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
# or
uv sync

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Edit `.env` file with your API keys:

```env
# LLM Configuration
DEFAULT_LLM_TYPE=openai  # or "anthropic"
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here  # For market data search
```

## Running the Server

```bash
# Development
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## API Usage

### Run Career Simulation

```bash
curl -X POST "http://localhost:8000/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "current_education_level": "2nd Year B.Tech",
      "institution_name": "IIT Delhi",
      "current_major": "Computer Science",
      "current_gpa": 8.5,
      "grading_scale": "10.0",
      "expected_graduation_year": 2027,
      "target_career_fields": ["Technology", "AI/ML"],
      "specific_roles": ["Machine Learning Engineer"],
      "primary_career_goal": "Technical Excellence",
      "risk_tolerance": "Medium",
      "investment_capacity": "$5k-$20k",
      "current_country": "India"
    }
  }'
```

### Response Structure

```json
{
  "success": true,
  "simulation_id": "sim_1702400000",
  "processing_time_ms": 15000,
  "summary": {
    "persona": "High-Potential, Growth-Oriented Student",
    "success_probability": 75,
    "gap_score": 45,
    "total_investment": 15000,
    "timeline_years": 5
  },
  "dashboard_data": {
    "milestones": [...],
    "skill_nodes": [...],
    "salary_progression": [...],
    "risk_indicators": [...]
  },
  "timeline": {
    "recommended_path": "realistic",
    "paths": {
      "conservative": {...},
      "realistic": {...},
      "ambitious": {...}
    }
  },
  "financial_analysis": {...},
  "risk_assessment": {...},
  "gap_analysis": {...}
}
```

## Project Structure

```
agent/
├── main.py                 # FastAPI application entry point
├── pyproject.toml          # Project dependencies
├── .env.example            # Environment variables template
├── src/
│   ├── __init__.py
│   ├── graph.py            # LangGraph workflow definition
│   ├── models/
│   │   ├── __init__.py
│   │   ├── career_profile.py   # Input/output schemas
│   │   └── state.py            # Graph state schema
│   └── agents/
│       ├── __init__.py
│       ├── base.py             # Shared utilities
│       ├── profile_parser.py   # Node A
│       ├── market_scout.py     # Node B
│       ├── gap_analyst.py      # Node C
│       ├── timeline_simulator.py  # Node D
│       ├── financial_advisor.py   # Node E
│       ├── risk_assessor.py       # Node F
│       └── dashboard_formatter.py # Node G
└── frontend/               # React frontend (separate)
```

## Agent Details

### Node A: ProfileParser
- Normalizes GPA across different scales
- Infers skills from academic major
- Classifies user into persona types
- Generates semantic profile summary

### Node B: MarketScout
- Uses Tavily Search API for real-time data
- Fetches salary ranges by location
- Identifies hard vs soft requirements
- Tracks emerging skills in target fields

### Node C: GapAnalyst
- Calculates skill-to-requirement distance
- Identifies education/certification gaps
- Performs "vibe check" for psychometric mismatches
- Flags stress risks and personality frictions

### Node D: TimelineSimulator
- Generates 3 distinct career paths
- Year-by-year milestones with costs/hours
- Adjusts for risk tolerance and available time
- Includes potential setbacks and buffer time

### Node E: FinancialAdvisor
- Calculates total investment required
- Projects income over time
- Determines break-even point
- Suggests cost-saving opportunities

### Node F: RiskAssessor
- Assigns success probability (0-100%)
- Categorizes risks (market, personal, financial, technical)
- Compares to similar successful profiles
- Provides mitigation strategies

### Node G: DashboardFormatter
- Formats data for React Flow roadmap
- Creates skill tree structure
- Generates chart data for Recharts
- Compiles summary statistics

## "Vibe Check" Feature

The system includes psychometric alignment checks:

| User Trait | Target | Warning |
|------------|--------|---------|
| Low Risk Tolerance | Startup | ⚠️ High stress environment mismatch |
| Theoretical Style | Hands-on Role | Consider research-focused positions |
| Structured Preference | Dynamic Role | May struggle with ambiguity |
| Data-oriented | People-heavy Role | Look for hybrid positions |

## Evaluation Criteria Alignment

| Criteria | Implementation |
|----------|----------------|
| Innovation & Originality | Multi-agent orchestration with LangGraph |
| Technical Feasibility | Production-ready FastAPI backend |
| Real-world Impact | Actionable roadmaps with specific resources |
| AI Effectiveness | 7 specialized agents with RAG for market data |
| UI/UX | Dashboard-ready JSON with React Flow support |
| Scalability | Async processing, modular architecture |
| Accuracy | Real-time market data, psychometric analysis |

## License

MIT
