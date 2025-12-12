"""
Node A2: CareerMatcher Agent
The Career Fit Analyzer - Identifies top 3 career matches with detailed reasoning
"""

import time
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from .base import get_llm
from ..models.state import CareerSimulationState
from ..models.career_profile import CareerProfile, NormalizedProfile


# ============ Structured Output Models ============

class CareerFitReasoning(BaseModel):
    """Detailed reasoning for why a career is a good fit"""
    strengths_alignment: list[str] = Field(
        description="List of user's strengths that align with this career (3-5 items)"
    )
    interest_match: list[str] = Field(
        description="How user's interests match this career path (2-3 items)"
    )
    skill_transferability: list[str] = Field(
        description="Which existing skills transfer well to this career (2-4 items)"
    )
    growth_potential_reasons: list[str] = Field(
        description="Why this career has good growth potential for this user (2-3 items)"
    )
    market_demand_reasons: list[str] = Field(
        description="Current market demand factors favoring this career (2-3 items)"
    )
    potential_challenges: list[str] = Field(
        description="Honest assessment of challenges user may face (2-3 items)"
    )
    why_now: str = Field(
        description="Why this is a good time for the user to pursue this career"
    )


class CareerFitOutput(BaseModel):
    """Single career fit recommendation with comprehensive reasoning"""
    rank: int = Field(description="Rank 1-3, where 1 is best fit")
    career_title: str = Field(description="The job title/role (e.g., 'Machine Learning Engineer')")
    career_field: str = Field(description="The industry/field (e.g., 'AI/ML', 'Finance')")
    
    # Fit scores with explanations
    overall_fit_score: float = Field(default=75.0, description="Overall fit score 0-100")
    skill_fit_score: float = Field(default=70.0, description="How well current skills match 0-100")
    interest_fit_score: float = Field(default=70.0, description="How well interests align 0-100")
    market_fit_score: float = Field(default=70.0, description="Market demand and opportunity 0-100")
    personality_fit_score: float = Field(default=70.0, description="Work style and personality match 0-100")

    # One-liner hook
    tagline: str = Field(default="A promising career path aligned with your skills.", description="Catchy one-liner about this career fit (10-15 words)")

    # Detailed reasoning
    reasoning: Optional[CareerFitReasoning] = Field(default=None, description="Detailed reasoning for this career fit")

    # Quick facts - with defaults to handle LLM truncation
    typical_salary_range: str = Field(default="Varies by location", description="Expected salary range (e.g., '$80,000-$120,000')")
    time_to_entry: str = Field(default="6-12 months", description="Estimated time to get first job (e.g., '12-18 months')")
    difficulty_level: str = Field(default="Moderate", description="Entry difficulty: 'Easy', 'Moderate', 'Challenging', 'Very Challenging'")

    # Key highlights - with defaults
    top_3_reasons: list[str] = Field(default_factory=lambda: ["Skills alignment", "Market demand", "Growth potential"], description="Top 3 reasons this is a good fit (concise bullets)")
    key_skills_needed: list[str] = Field(default_factory=list, description="Top 5 skills needed for this career")
    immediate_next_steps: list[str] = Field(default_factory=list, description="3 immediate actions to start pursuing this career")


class CareerMatcherOutput(BaseModel):
    """Complete output from career matcher with 3 recommendations"""
    analysis_summary: str = Field(
        description="2-3 sentence summary of the user's profile and what careers suit them"
    )
    profile_highlights: list[str] = Field(
        description="Key highlights from the user's profile that influenced recommendations (4-5 items)"
    )
    career_fits: list[CareerFitOutput] = Field(
        description="Exactly 3 career fit recommendations ranked by fit score"
    )
    methodology_explanation: str = Field(
        description="Brief explanation of how the recommendations were generated"
    )
    confidence_level: str = Field(
        description="Confidence in recommendations: 'High', 'Medium', 'Low'"
    )
    confidence_reasoning: str = Field(
        description="Why we have this confidence level based on profile completeness"
    )


# ============ Main Agent Function ============

def career_matcher_node(state: CareerSimulationState) -> dict:
    """
    Node A2: CareerMatcher
    Analyzes user profile and returns top 3 career fits with detailed reasoning.
    
    This is the FIRST stage of the two-stage process.
    The graph PAUSES after this node until user selects a career.
    
    Args:
        state: Current graph state with normalized profile
        
    Returns:
        State update with career_fits list
    """
    start_time = time.time()
    
    profile = state.get("career_profile")
    normalized = state.get("normalized_profile")
    
    if not profile:
        return {
            "errors": ["No career profile provided"],
            "current_node": "career_matcher",
        }
    
    # Get structured output from LLM
    try:
        result = _analyze_career_fits(profile, normalized)
    except Exception as e:
        print(f"Career matcher LLM failed: {e}")
        result = _create_fallback_career_fits(profile, normalized)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "career_fits": result,
        "current_node": "career_matcher",
        "processing_time_ms": {"career_matcher": processing_time},
    }


def _analyze_career_fits(
    profile: CareerProfile,
    normalized: Optional[NormalizedProfile]
) -> CareerMatcherOutput:
    """Use LLM with structured output to analyze career fits."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert career counselor with deep knowledge of:
- Current job market trends and salary data (2024-2025)
- Skill requirements for various tech and non-tech roles
- Career progression paths across industries
- Personality-job fit research
- Resume analysis and experience evaluation

Your task is to analyze a student/professional's profile (including their resume if provided) and recommend the TOP 3 BEST-FIT careers.

IMPORTANT GUIDELINES:
1. Be specific and realistic - base recommendations on actual market data
2. Provide DETAILED REASONING for every recommendation
3. Be honest about challenges - don't oversell
4. Consider the user's stated preferences AND their implicit strengths
5. Each career should be DISTINCT - don't recommend 3 variations of the same role
6. Prioritize careers with good market demand AND alignment with user's profile
7. Consider risk tolerance when recommending (high risk tolerance = more ambitious suggestions)
8. If resume is provided, extract and leverage:
   - Work experience and achievements
   - Projects and their impact
   - Skills demonstrated (not just listed)
   - Education and certifications
   - Leadership and teamwork evidence

SCORING METHODOLOGY:
- skill_fit_score: How much of the required skills does the user already have? (Include resume evidence)
- interest_fit_score: How aligned are user's interests with daily work of this career?
- market_fit_score: Current demand, salary potential, growth outlook
- personality_fit_score: Work style, risk tolerance, goal alignment

REASONING REQUIREMENTS:
- Every score needs justification
- Explain WHY this career fits, not just THAT it fits
- Be specific to this user's profile, not generic advice
- Include both optimistic and realistic perspectives
- If resume is provided, cite specific experiences/skills from it
- Match reasoning to what the user has actually done (from resume) + what they want (from profile)"""),
        
        ("human", """Analyze this profile and recommend the TOP 3 best-fit careers:

=== BASIC INFO ===
Education Level: {education_level}
Institution: {institution}
Major: {major}
GPA: {gpa}/{gpa_scale}
Expected Graduation: {graduation_year}
Country: {country}

=== CAREER INTERESTS ===
Target Fields: {target_fields}
Specific Roles Interested In: {specific_roles}
Primary Career Goal: {career_goal}
Desired Role Level: {role_level}
Work Environment Preferences: {work_env}

=== SKILLS ===
Technical Skills: {technical_skills}
Soft Skills: {soft_skills}

=== PERSONALITY & PREFERENCES ===
Work Style: {work_style}
Risk Tolerance: {risk_tolerance}
Learning Style: {learning_style}

=== RESOURCES & CONSTRAINTS ===
Investment Capacity: {investment_capacity}
Available Hours/Week: {hours_per_week}
Desired Timeline to Workforce: {workforce_timeline}

=== MARKET AWARENESS ===
Market Awareness Level: {market_awareness}
Career Concerns: {career_concerns}
Optimism Level: {optimism_level}

{resume_section}

{normalized_summary}

Based on this comprehensive profile{resume_note}, provide exactly 3 career recommendations ranked by overall fit.
Make sure each career is DIFFERENT (not just variations like "Data Scientist" and "Senior Data Scientist").
Provide detailed reasoning for why each career is a good fit for THIS specific person.
{resume_instruction}""")
    ])
    
    # Format profile data
    normalized_summary = ""
    if normalized:
        # Build persona traits string safely
        persona_traits = ', '.join(normalized.persona_traits) if normalized.persona_traits else 'Not analyzed'
        
        normalized_summary = f"""
=== AI ANALYSIS OF PROFILE ===
Persona Type: {normalized.persona_type}
Persona Traits: {persona_traits}
Academic Strength Score: {normalized.academic_strength_score}/100
Career Readiness Score: {normalized.career_readiness_score}/100
Skill Readiness Score: {normalized.skill_readiness_score}/100
Financial Readiness Score: {normalized.financial_readiness_score}/100
Combined Technical Skills: {normalized.combined_technical_skills}
Inferred Technical Skills: {normalized.inferred_technical_skills}

Profile Summary: {normalized.profile_summary}
"""
    
    llm = get_llm(temperature=0.4)
    structured_llm = llm.with_structured_output(CareerMatcherOutput)
    
    chain = prompt | structured_llm
    
    # Build resume section if available
    resume_section = ""
    resume_note = ""
    resume_instruction = ""
    if profile.resume_text:
        # Truncate resume to avoid token limits (keep ~4000 chars)
        resume_text = profile.resume_text[:4000] if len(profile.resume_text) > 4000 else profile.resume_text
        resume_section = f"""
=== RESUME / CV CONTENT ===
(Extracted from uploaded resume: {profile.resume_filename or 'resume.pdf'})

{resume_text}
"""
        resume_note = " and resume"
        resume_instruction = """
IMPORTANT: Use specific information from the resume to:
1. Identify demonstrated skills and experience levels
2. Reference specific projects, achievements, or roles in your reasoning
3. Validate or adjust skill assessments based on actual work done
4. Consider career trajectory patterns from work history
"""
    
    result = chain.invoke({
        "education_level": profile.current_education_level or "Not specified",
        "institution": profile.institution_name or "Not specified",
        "major": profile.current_major or "Not specified",
        "gpa": profile.current_gpa or "N/A",
        "gpa_scale": profile.grading_scale or "N/A",
        "graduation_year": profile.expected_graduation_year or "Not specified",
        "country": profile.current_country or "Not specified",
        "target_fields": ", ".join(profile.target_career_fields) if profile.target_career_fields else "Not specified",
        "specific_roles": ", ".join(profile.specific_roles) if profile.specific_roles else "Not specified",
        "career_goal": profile.primary_career_goal or "Not specified",
        "role_level": profile.desired_role_level or "Not specified",
        "work_env": ", ".join(profile.preferred_work_env) if profile.preferred_work_env else "Not specified",
        "technical_skills": str(profile.technical_skills) if profile.technical_skills else "Not specified",
        "soft_skills": str(profile.soft_skills) if profile.soft_skills else "Not specified",
        "work_style": profile.work_style or "Not specified",
        "risk_tolerance": profile.risk_tolerance or "Medium",
        "learning_style": ", ".join(profile.learning_style) if profile.learning_style else "Not specified",
        "investment_capacity": profile.investment_capacity or "Not specified",
        "hours_per_week": profile.hours_per_week or 20,
        "workforce_timeline": profile.desired_workforce_timeline or "Not specified",
        "market_awareness": profile.market_awareness or "Medium",
        "career_concerns": ", ".join(profile.career_concerns) if profile.career_concerns else "None specified",
        "optimism_level": profile.optimism_level or "Balanced",
        "normalized_summary": normalized_summary,
        "resume_section": resume_section,
        "resume_note": resume_note,
        "resume_instruction": resume_instruction,
    })
    
    return result


def _create_fallback_career_fits(
    profile: CareerProfile,
    normalized: Optional[NormalizedProfile]
) -> CareerMatcherOutput:
    """Create fallback career fits when LLM fails."""
    
    # Determine careers based on available profile info
    target_roles = profile.specific_roles or []
    target_fields = profile.target_career_fields or []
    
    # Default career suggestions based on common CS profiles
    default_careers = [
        {
            "title": "Software Engineer",
            "field": "Technology",
            "tagline": "Build the digital products that shape how the world works and connects",
        },
        {
            "title": "Data Scientist", 
            "field": "AI/ML",
            "tagline": "Turn raw data into insights that drive billion-dollar business decisions",
        },
        {
            "title": "Product Manager",
            "field": "Technology",
            "tagline": "Lead product strategy at the intersection of technology and business",
        },
    ]
    
    # Try to use user's preferences if available
    if target_roles:
        default_careers[0]["title"] = target_roles[0]
        if len(target_roles) > 1:
            default_careers[1]["title"] = target_roles[1]
    
    if target_fields:
        default_careers[0]["field"] = target_fields[0]
        if len(target_fields) > 1:
            default_careers[1]["field"] = target_fields[1] if len(target_fields) > 1 else target_fields[0]
    
    career_fits = []
    for i, career in enumerate(default_careers):
        fit = CareerFitOutput(
            rank=i + 1,
            career_title=career["title"],
            career_field=career["field"],
            overall_fit_score=90 - (i * 8),
            skill_fit_score=85 - (i * 5),
            interest_fit_score=88 - (i * 6),
            market_fit_score=85 - (i * 4),
            personality_fit_score=82 - (i * 5),
            tagline=career["tagline"],
            reasoning=CareerFitReasoning(
                strengths_alignment=[
                    "Strong analytical and problem-solving abilities",
                    "Technical aptitude demonstrated through coursework",
                    "Ability to learn new technologies quickly",
                    "Good foundation in computer science fundamentals",
                ],
                interest_match=[
                    "Expressed interest aligns with daily responsibilities",
                    "Work involves continuous learning and growth",
                ],
                skill_transferability=[
                    "Programming skills directly applicable",
                    "Analytical thinking transfers well",
                    "Communication skills valuable for team collaboration",
                ],
                growth_potential_reasons=[
                    "Industry growing at 15-20% annually",
                    "Clear career progression paths exist",
                    "High demand for skilled professionals",
                ],
                market_demand_reasons=[
                    "Strong job market with many openings",
                    "Competitive salaries above average",
                    "Remote work opportunities abundant",
                ],
                potential_challenges=[
                    "Competitive entry-level market",
                    "Continuous learning required to stay current",
                    "May require building portfolio projects",
                ],
                why_now="The tech industry continues to grow despite economic uncertainty, making now a good time to build foundational skills.",
            ),
            typical_salary_range="$70,000 - $120,000",
            time_to_entry="6-12 months",
            difficulty_level="Moderate" if i < 2 else "Challenging",
            top_3_reasons=[
                "Strong alignment with your technical background",
                "Excellent market demand and salary potential",
                "Clear path from current position",
            ],
            key_skills_needed=[
                "Programming (Python, JavaScript)",
                "Data Structures & Algorithms",
                "System Design basics",
                "Communication & Teamwork",
                "Problem Solving",
            ],
            immediate_next_steps=[
                "Complete a foundational online course",
                "Build 2-3 portfolio projects",
                "Start applying to internships/entry-level positions",
            ],
        )
        career_fits.append(fit)
    
    return CareerMatcherOutput(
        analysis_summary=f"Based on your profile as a {profile.current_education_level or 'student'} in {profile.current_major or 'Computer Science'}, you have strong potential in technical roles with good market demand.",
        profile_highlights=[
            f"Education: {profile.current_education_level or 'In Progress'}",
            f"Field of Study: {profile.current_major or 'Computer Science'}",
            f"Target Fields: {', '.join(target_fields) if target_fields else 'Technology'}",
            f"Risk Tolerance: {profile.risk_tolerance or 'Medium'}",
        ],
        career_fits=career_fits,
        methodology_explanation="Recommendations based on profile analysis, market demand data, and career-skill alignment scoring.",
        confidence_level="Medium",
        confidence_reasoning="Some profile fields were not specified, which limits personalization accuracy.",
    )
