"""
Career Path Simulator - Main Entry Point
FastAPI application for the multi-agent career simulation system
"""

import os
import json
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

from src.models.career_profile import CareerProfile
from src.models.state import CareerSimulationState, CareerMatcherResult, CareerFit
from src.graph import (
    run_career_simulation, 
    run_career_simulation_async, 
    run_career_matching_async,
    run_career_simulation_for_selected_async,
    career_simulator,
)


# In-memory session storage for two-stage process
# In production, use Redis or database
_session_store: dict[str, dict] = {}


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Career Path Simulator starting up...")
    print("📊 Multi-agent system initialized")
    yield
    print("👋 Career Path Simulator shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Career Path Simulator",
    description="""
    AI-driven multi-agent system for personalized career simulation.
    
    This system uses LangGraph to orchestrate multiple specialized AI agents:
    - **ProfileParser**: Analyzes user profile and creates semantic summary
    - **MarketScout**: Fetches real-time market data using RAG
    - **GapAnalyst**: Compares profile vs market requirements
    - **TimelineSimulator**: Generates 4-6 year career roadmaps
    - **FinancialAdvisor**: Calculates ROI and cost analysis
    - **RiskAssessor**: Assigns success probability scores
    - **DashboardFormatter**: Formats data for frontend visualization
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class SimulationRequest(BaseModel):
    """Request model for career simulation"""
    profile: dict  # CareerProfile data
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile": {
                    "current_education_level": "2nd Year B.Tech",
                    "institution_name": "IIT Delhi",
                    "current_major": "Computer Science",
                    "current_gpa": 8.5,
                    "grading_scale": "10.0",
                    "expected_graduation_year": 2027,
                    "target_career_fields": ["Technology", "AI/ML"],
                    "specific_roles": ["Machine Learning Engineer", "Data Scientist"],
                    "primary_career_goal": "Technical Excellence",
                    "desired_role_level": "Senior IC",
                    "preferred_work_env": ["Startup", "Remote"],
                    "technical_skills": {
                        "Python": "Intermediate",
                        "Machine Learning": "Basic",
                        "SQL": "Intermediate"
                    },
                    "soft_skills": {
                        "Communication": 4,
                        "Problem Solving": 5,
                        "Teamwork": 4
                    },
                    "work_style": "Practical",
                    "risk_tolerance": "Medium",
                    "investment_capacity": "$5k-$20k",
                    "hours_per_week": 25,
                    "current_country": "India",
                    "market_awareness": "Medium",
                    "career_concerns": ["Competition", "Skill Relevance"],
                    "optimism_level": "Balanced"
                }
            }
        }


class SimulationResponse(BaseModel):
    """Response model for career simulation"""
    success: bool
    simulation_id: str
    processing_time_ms: float
    summary: dict
    dashboard_data: Optional[dict] = None
    timeline: Optional[dict] = None
    financial_analysis: Optional[dict] = None
    risk_assessment: Optional[dict] = None
    gap_analysis: Optional[dict] = None
    warnings: list[str] = []
    errors: list[str] = []


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agents: list[str]


# ============ Stage 1: Career Matching Models ============

class CareerFitReasoningResponse(BaseModel):
    """Reasoning details for a career fit"""
    strengths_alignment: list[str] = []
    interest_match: list[str] = []
    skill_transferability: list[str] = []
    growth_potential_reasons: list[str] = []
    market_demand_reasons: list[str] = []
    potential_challenges: list[str] = []
    why_now: str = ""


class CareerFitResponse(BaseModel):
    """Single career fit with detailed reasoning"""
    rank: int
    career_title: str
    career_field: str
    overall_fit_score: float
    skill_fit_score: float
    interest_fit_score: float
    market_fit_score: float
    personality_fit_score: float
    tagline: str
    reasoning: CareerFitReasoningResponse
    typical_salary_range: str
    time_to_entry: str
    difficulty_level: str
    top_3_reasons: list[str]
    key_skills_needed: list[str]
    immediate_next_steps: list[str]


class CareerMatchingResponse(BaseModel):
    """Response for Stage 1: Career Matching"""
    success: bool
    session_id: str
    processing_time_ms: float
    analysis_summary: str
    profile_highlights: list[str]
    career_fits: list[CareerFitResponse]
    methodology_explanation: str
    confidence_level: str
    confidence_reasoning: str
    errors: list[str] = []


class SelectCareerRequest(BaseModel):
    """Request to select a career and start Stage 2"""
    session_id: str
    career_index: int  # 0, 1, or 2


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Career Path Simulator API",
        "version": "1.0.0",
        "description": "AI-driven multi-agent career simulation system",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        agents=[
            "ProfileParser",
            "CareerMatcher",
            "MarketScout",
            "GapAnalyst",
            "TimelineSimulator",
            "FinancialAdvisor",
            "RiskAssessor",
            "DashboardFormatter",
        ],
    )


# ============ Resume Parsing Endpoint ============

class ResumeParseResponse(BaseModel):
    """Response for resume parsing"""
    success: bool
    text: str
    filename: str
    word_count: int
    error: Optional[str] = None


@app.post("/parse-resume", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse uploaded resume (PDF or DOCX) and extract text.
    
    The extracted text will be used by the CareerMatcher to provide
    more personalized career recommendations based on:
    - Work experience and achievements
    - Skills mentioned in the resume
    - Education and certifications
    - Project descriptions
    """
    try:
        # Validate file type
        filename = file.filename or "resume"
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext not in ['pdf', 'docx', 'doc']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PDF or DOCX file."
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size (5MB max)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 5MB."
            )
        
        extracted_text = ""
        
        if file_ext == 'pdf':
            # Parse PDF
            try:
                import pypdf
                pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() or ""
            except ImportError:
                # Fallback: Try PyPDF2
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() or ""
                except ImportError:
                    raise HTTPException(
                        status_code=500,
                        detail="PDF parsing library not available. Please install pypdf or PyPDF2."
                    )
        
        elif file_ext in ['docx', 'doc']:
            # Parse DOCX
            try:
                import docx
                doc = docx.Document(io.BytesIO(content))
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="DOCX parsing library not available. Please install python-docx."
                )
        
        # Clean up text
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume. Please ensure the file is not password protected."
            )
        
        word_count = len(extracted_text.split())
        
        return ResumeParseResponse(
            success=True,
            text=extracted_text,
            filename=filename,
            word_count=word_count,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        )


# ============ Stage 1: Career Matching Endpoint ============

@app.post("/analyze", response_model=CareerMatchingResponse)
async def analyze_career_fits(request: SimulationRequest):
    """
    Stage 1: Analyze profile and return top 3 career fits.
    
    This endpoint runs the ProfileParser and CareerMatcher agents to:
    - Normalize and analyze the user's profile
    - Identify the 3 best-fit careers with detailed reasoning
    - Explain WHY each career is a good fit
    
    The response includes a session_id that must be used in Stage 2
    to select a career and run the full simulation.
    
    Flow: Profile → ProfileParser → CareerMatcher → Response (PAUSE)
    """
    start_time = time.time()
    
    try:
        # Run Stage 1: Career Matching
        result = await run_career_matching_async(request.profile)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Generate session ID
        session_id = f"session_{int(time.time())}_{id(result) % 10000}"
        
        # Store session for Stage 2
        _session_store[session_id] = {
            "state": result,
            "profile": request.profile,
            "created_at": time.time(),
        }
        
        # Extract career matcher result
        matcher_result = result.get("career_matcher_result")
        if not matcher_result:
            raise HTTPException(
                status_code=500,
                detail="Career matching failed to produce results"
            )
        
        # Format career fits for response
        career_fits_response = []
        for fit in matcher_result.career_fits:
            career_fits_response.append(CareerFitResponse(
                rank=fit.rank,
                career_title=fit.career_title,
                career_field=fit.career_field,
                overall_fit_score=fit.overall_fit_score,
                skill_fit_score=fit.skill_fit_score,
                interest_fit_score=fit.interest_fit_score,
                market_fit_score=fit.market_fit_score,
                personality_fit_score=fit.personality_fit_score,
                tagline=fit.tagline,
                reasoning=CareerFitReasoningResponse(
                    strengths_alignment=fit.reasoning.strengths_alignment,
                    interest_match=fit.reasoning.interest_match,
                    skill_transferability=fit.reasoning.skill_transferability,
                    growth_potential_reasons=fit.reasoning.growth_potential_reasons,
                    market_demand_reasons=fit.reasoning.market_demand_reasons,
                    potential_challenges=fit.reasoning.potential_challenges,
                    why_now=fit.reasoning.why_now,
                ),
                typical_salary_range=fit.typical_salary_range,
                time_to_entry=fit.time_to_entry,
                difficulty_level=fit.difficulty_level,
                top_3_reasons=fit.top_3_reasons,
                key_skills_needed=fit.key_skills_needed,
                immediate_next_steps=fit.immediate_next_steps,
            ))
        
        return CareerMatchingResponse(
            success=True,
            session_id=session_id,
            processing_time_ms=processing_time,
            analysis_summary=matcher_result.analysis_summary,
            profile_highlights=matcher_result.profile_highlights,
            career_fits=career_fits_response,
            methodology_explanation=matcher_result.methodology_explanation,
            confidence_level=matcher_result.confidence_level,
            confidence_reasoning=matcher_result.confidence_reasoning,
            errors=result.get("errors", []),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Career analysis failed: {str(e)}"
        )


# ============ Stage 2: Full Simulation Endpoint ============

@app.post("/simulate/selected", response_model=SimulationResponse)
async def simulate_selected_career(request: SelectCareerRequest):
    """
    Stage 2: Run full simulation for the selected career.
    
    After reviewing the 3 career fits from Stage 1, user selects one
    and this endpoint runs the complete analysis pipeline:
    - MarketScout: Fetches real-time market data for the selected career
    - GapAnalyst: Identifies specific gaps with detailed reasoning
    - TimelineSimulator: Creates personalized 4-6 year roadmap
    - FinancialAdvisor: Calculates ROI, costs, and projections
    - RiskAssessor: Evaluates success probability with reasoning
    - DashboardFormatter: Formats data for visualization
    
    All agents provide detailed REASONING for every decision.
    """
    start_time = time.time()
    
    # Get session
    session = _session_store.get(request.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please run /analyze first."
        )
    
    # Validate career index
    if request.career_index < 0 or request.career_index > 2:
        raise HTTPException(
            status_code=400,
            detail="career_index must be 0, 1, or 2"
        )
    
    try:
        # Get state from session
        state = session["state"]
        
        # Run Stage 2: Full Simulation
        result = await run_career_simulation_for_selected_async(state, request.career_index)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Clean up session
        del _session_store[request.session_id]
        
        # Format response
        dashboard_data = result.get("dashboard_data")
        financial = result.get("financial_analysis")
        risk = result.get("risk_assessment")
        gap = result.get("gap_analysis")
        selected = result.get("selected_career")
        
        # Include selected career info in summary
        summary = _extract_summary(result)
        if selected:
            summary["selected_career"] = {
                "title": selected.career_title,
                "field": selected.career_field,
                "fit_score": selected.overall_fit_score,
            }
        
        return SimulationResponse(
            success=True,
            simulation_id=f"sim_{int(time.time())}",
            processing_time_ms=processing_time,
            summary=summary,
            dashboard_data=dashboard_data.model_dump() if dashboard_data else None,
            timeline=_extract_timeline(result),
            financial_analysis=financial.model_dump() if financial else None,
            risk_assessment=risk.model_dump() if risk else None,
            gap_analysis=gap.model_dump() if gap else None,
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


# ============ Legacy Endpoint (Single-Stage) ============


@app.post("/simulate", response_model=SimulationResponse)
async def simulate_career(request: SimulationRequest):
    """
    Run a complete career simulation.
    
    This endpoint orchestrates all 7 agents to generate:
    - Personalized career roadmap (4-6 years)
    - Success probability scoring
    - Financial analysis and ROI
    - Risk assessment
    - Interactive dashboard data
    """
    start_time = time.time()
    
    try:
        # Run the simulation
        result = await run_career_simulation_async(request.profile)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Format response (result is now a dict/TypedDict)
        dashboard_data = result.get("dashboard_data")
        financial = result.get("financial_analysis")
        risk = result.get("risk_assessment")
        gap = result.get("gap_analysis")
        
        response = SimulationResponse(
            success=True,
            simulation_id=f"sim_{int(time.time())}",
            processing_time_ms=processing_time,
            summary=_extract_summary(result),
            dashboard_data=dashboard_data.model_dump() if dashboard_data else None,
            timeline=_extract_timeline(result),
            financial_analysis=financial.model_dump() if financial else None,
            risk_assessment=risk.model_dump() if risk else None,
            gap_analysis=gap.model_dump() if gap else None,
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@app.post("/simulate/sync")
async def simulate_career_sync(request: SimulationRequest):
    """
    Synchronous version of career simulation.
    Use this for debugging or when async is not needed.
    """
    start_time = time.time()
    
    try:
        # Run the simulation synchronously
        result = run_career_simulation(request.profile)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "processing_time_ms": processing_time,
            "result": _state_to_dict(result),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )


@app.get("/graph/info")
async def get_graph_info():
    """Get information about the LangGraph workflow (two-stage process)"""
    return {
        "version": "2.0.0",
        "stages": {
            "stage_1": {
                "name": "Career Matching",
                "description": "Analyze profile and identify top 3 career fits",
                "endpoint": "/analyze",
                "nodes": [
                    {"id": "profile_parser", "name": "ProfileParser", "description": "Analyzes and normalizes user profile"},
                    {"id": "career_matcher", "name": "CareerMatcher", "description": "Identifies 3 best-fit careers with detailed reasoning"},
                ],
                "edges": [
                    {"from": "START", "to": "profile_parser"},
                    {"from": "profile_parser", "to": "career_matcher"},
                    {"from": "career_matcher", "to": "PAUSE"},
                ],
            },
            "stage_2": {
                "name": "Full Simulation",
                "description": "Complete analysis for selected career",
                "endpoint": "/simulate/selected",
                "nodes": [
                    {"id": "market_scout", "name": "MarketScout", "description": "Fetches real-time market data for selected career"},
                    {"id": "gap_analyst", "name": "GapAnalyst", "description": "Identifies skill and experience gaps with reasoning"},
                    {"id": "alternative_suggester", "name": "AlternativePathSuggester", "description": "Suggests alternatives if gap is too large"},
                    {"id": "timeline_simulator", "name": "TimelineSimulator", "description": "Generates year-by-year career paths with reasoning"},
                    {"id": "financial_advisor", "name": "FinancialAdvisor", "description": "Calculates ROI and costs with reasoning"},
                    {"id": "risk_assessor", "name": "RiskAssessor", "description": "Assesses success probability with reasoning"},
                    {"id": "dashboard_formatter", "name": "DashboardFormatter", "description": "Formats data for frontend visualization"},
                ],
                "edges": [
                    {"from": "START", "to": "market_scout"},
                    {"from": "market_scout", "to": "gap_analyst"},
                    {"from": "gap_analyst", "to": "alternative_suggester", "condition": "gap_score > 80"},
                    {"from": "gap_analyst", "to": "timeline_simulator", "condition": "gap_score <= 80"},
                    {"from": "alternative_suggester", "to": "timeline_simulator"},
                    {"from": "timeline_simulator", "to": "financial_advisor", "parallel": True},
                    {"from": "timeline_simulator", "to": "risk_assessor", "parallel": True},
                    {"from": "financial_advisor", "to": "dashboard_formatter"},
                    {"from": "risk_assessor", "to": "dashboard_formatter"},
                    {"from": "dashboard_formatter", "to": "END"},
                ],
            },
        },
        "legacy_endpoint": "/simulate (single-stage, still supported)",
    }


# Helper functions

def _extract_summary(result: dict) -> dict:
    """Extract key summary statistics from simulation result"""
    summary = {}
    
    normalized_profile = result.get("normalized_profile")
    if normalized_profile:
        summary["persona"] = normalized_profile.persona_type
        summary["academic_score"] = normalized_profile.academic_strength_score
        summary["readiness_scores"] = {
            "career": normalized_profile.career_readiness_score,
            "skill": normalized_profile.skill_readiness_score,
            "financial": normalized_profile.financial_readiness_score,
        }
    
    gap_analysis = result.get("gap_analysis")
    if gap_analysis:
        summary["gap_score"] = gap_analysis.overall_gap_score
        summary["gap_category"] = gap_analysis.gap_category
    
    risk_assessment = result.get("risk_assessment")
    if risk_assessment:
        summary["success_probability"] = risk_assessment.success_probability_score
        summary["confidence_interval"] = risk_assessment.confidence_interval
    
    financial_analysis = result.get("financial_analysis")
    if financial_analysis:
        summary["total_investment"] = financial_analysis.total_investment_required
        summary["break_even_year"] = financial_analysis.break_even_year
        summary["roi_5_year"] = financial_analysis.five_year_roi
    
    timeline_simulation = result.get("timeline_simulation")
    if timeline_simulation:
        summary["recommended_path"] = timeline_simulation.recommended_path
        if timeline_simulation.realistic_path:
            summary["timeline_years"] = timeline_simulation.realistic_path.total_years
            summary["target_role"] = timeline_simulation.realistic_path.final_target_role
    
    return summary


def _extract_timeline(result: dict) -> dict | None:
    """Extract timeline simulation data"""
    timeline = result.get("timeline_simulation")
    if not timeline:
        return None
    
    return {
        "recommended_path": timeline.recommended_path,
        "recommendation_reason": timeline.recommendation_reason,
        "alignment_score": timeline.alignment_score,
        "vibe_check_warnings": timeline.vibe_check_warnings,
        "conservative_path": timeline.conservative_path.model_dump() if timeline.conservative_path else None,
        "realistic_path": timeline.realistic_path.model_dump() if timeline.realistic_path else None,
        "ambitious_path": timeline.ambitious_path.model_dump() if timeline.ambitious_path else None,
    }


def _state_to_dict(state: dict) -> dict:
    """Convert CareerSimulationState dict to serializable dictionary"""
    career_profile = state.get("career_profile")
    normalized_profile = state.get("normalized_profile")
    market_insights = state.get("market_insights")
    gap_analysis = state.get("gap_analysis")
    timeline_simulation = state.get("timeline_simulation")
    financial_analysis = state.get("financial_analysis")
    risk_assessment = state.get("risk_assessment")
    dashboard_data = state.get("dashboard_data")
    alternative_careers = state.get("alternative_careers", [])
    
    return {
        "career_profile": career_profile.model_dump() if career_profile else None,
        "normalized_profile": normalized_profile.model_dump() if normalized_profile else None,
        "market_insights": market_insights.model_dump() if market_insights else None,
        "gap_analysis": gap_analysis.model_dump() if gap_analysis else None,
        "alternative_careers": [a.model_dump() for a in alternative_careers],
        "timeline_simulation": timeline_simulation.model_dump() if timeline_simulation else None,
        "financial_analysis": financial_analysis.model_dump() if financial_analysis else None,
        "risk_assessment": risk_assessment.model_dump() if risk_assessment else None,
        "dashboard_data": dashboard_data.model_dump() if dashboard_data else None,
        "simulation_complete": state.get("simulation_complete", False),
        "final_report_summary": state.get("final_report_summary", ""),
        "warnings": state.get("warnings", []),
        "errors": state.get("errors", []),
        "processing_time_ms": state.get("processing_time_ms", {}),
    }


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Career Path Simulator on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
    )
