"""
Node C: GapAnalyst Agent
The Diagnostic Engine - Compares user profile vs market requirements
Uses structured output for reliable data extraction
"""

import time
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..models.state import CareerSimulationState, GapAnalysis, SkillGap
from .base import get_llm


# Structured output models for LLM response
class SkillGapOutput(BaseModel):
    """A single skill gap identified in the analysis."""
    skill_name: str = Field(description="Name of the skill")
    current_level: str = Field(description="Current proficiency level: None, Basic, Intermediate, Advanced, Expert")
    required_level: str = Field(description="Required proficiency level for the target role")
    gap_severity: float = Field(description="Gap severity score from 0-100")
    estimated_time_to_close: str = Field(description="Estimated time to close this gap, e.g., '3 months', '6 months'")
    recommended_resources: list[str] = Field(default_factory=list, description="List of recommended courses, certifications, or resources")
    reasoning: str = Field(default="", description="Why this gap exists and why it matters for the career transition")
    priority: str = Field(default="medium", description="Priority level: critical, high, medium, low")
    learning_path: list[str] = Field(default_factory=list, description="List of 3-5 sequential learning steps to close this gap, e.g., ['Learn basics via online course', 'Build portfolio project', 'Get certified']")


class GapAnalysisOutput(BaseModel):
    """Complete gap analysis output from LLM."""
    overall_gap_score: float = Field(description="Overall gap score from 0-100, where 0 is no gap and 100 is maximum gap")
    gap_category: str = Field(description="One of: minimal, manageable, significant, severe")
    analysis_reasoning: str = Field(description="Detailed reasoning for the overall gap assessment - explain why this score based on the candidate's profile")
    
    technical_skill_gaps: list[SkillGapOutput] = Field(
        description="List of 4-6 technical skill gaps identified with specific skills like Python, JavaScript, SQL, Cloud, etc."
    )
    soft_skill_gaps: list[SkillGapOutput] = Field(
        description="List of 2-4 soft skill gaps like Communication, Leadership, Problem Solving"
    )
    
    education_gap: Optional[str] = Field(default=None, description="Education gap description if any, or null if none")
    education_gap_reasoning: str = Field(default="", description="Why education gap matters or doesn't for this transition")
    certification_gaps: list[str] = Field(default_factory=list, description="List of required certifications the candidate lacks")
    experience_gap_years: float = Field(default=0, description="Years of experience gap")
    experience_gap_reasoning: str = Field(default="", description="Context for the experience gap")
    
    critical_bottlenecks: list[str] = Field(
        description="2-4 critical issues that could block career progression"
    )
    timeline_bottlenecks: list[str] = Field(
        description="2-3 issues that may extend the career transition timeline"
    )
    
    existing_strengths: list[str] = Field(
        description="3-5 candidate's existing strengths and advantages"
    )
    competitive_advantages: list[str] = Field(
        description="2-4 competitive advantages the candidate has"
    )
    
    personality_frictions: list[str] = Field(
        default_factory=list,
        description="Personality-role mismatches or friction points"
    )
    stress_risks: list[str] = Field(
        default_factory=list,
        description="Potential stress factors based on personality-role mismatch"
    )
    
    top_priorities: list[str] = Field(
        default_factory=list,
        description="Top 3-5 priorities the candidate should focus on immediately"
    )
    quick_wins: list[str] = Field(
        default_factory=list,
        description="2-3 quick wins that can be achieved in the next 2 weeks"
    )


GAP_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert career gap analyst. Your task is to compare a candidate's current profile against market requirements and identify all gaps comprehensively.

You MUST provide detailed analysis WITH REASONING for ALL categories:

1. Technical Skill Gaps (REQUIRED: 4-6 specific skills):
   - For each skill: name, current level, required level, severity (0-100), time to close, and 2-3 specific resources
   - Include REASONING for why this gap exists based on the candidate's background
   - Include PRIORITY level (critical, high, medium, low)
   - Include a step-by-step LEARNING_PATH
   - Be specific: Python, JavaScript, SQL, AWS, Docker, React, etc.

2. Soft Skill Gaps (REQUIRED: 2-4 skills):
   - Communication, Leadership, Problem Solving, Teamwork, etc.
   - Include reasoning and priority

3. Education & Certification Gaps:
   - What degrees or certifications are missing
   - Include reasoning for why they matter

4. Critical Bottlenecks (REQUIRED: 2-4 items):
   - Major blockers to career success

5. Timeline Bottlenecks (REQUIRED: 2-3 items):
   - What will slow down the transition

6. Existing Strengths (REQUIRED: 3-5 items):
   - What the candidate already has going for them

7. Competitive Advantages (REQUIRED: 2-4 items):
   - Unique advantages over other candidates

8. Top Priorities (REQUIRED: 3-5 items):
   - What the candidate should focus on first

9. Quick Wins (REQUIRED: 2-3 items):
   - Things that can be achieved in 2 weeks

IMPORTANT: For the ANALYSIS_REASONING field, provide a detailed explanation of why you assigned the overall gap score based on:
- The candidate's current skills vs market requirements
- Their academic background and GPA
- Their work style and preferences alignment with the target role
- Resume context if available

Be thorough, specific, and constructive. NEVER leave arrays empty."""),

    ("human", """Perform a comprehensive gap analysis:

**CANDIDATE PROFILE:**
{profile_summary}

**Resume Context (if available):**
{resume_context}

**Academic Details:**
- Academic Strength Score: {academic_score}/100
- Normalized GPA: {gpa}/100
- Institution: {institution}
- Years to Graduation: {years_to_grad}

**Current Skills:**
- Technical Skills: {tech_skills}
- Soft Skills: {soft_skills}

**Psychometrics:**
- Work Preference: {work_preference}
- Work Style: {work_style}
- Role Preference: {role_preference}
- Risk Tolerance: {risk_tolerance}

**TARGET ROLES:** {target_roles}

**MARKET REQUIREMENTS:**
{market_requirements}

**MARKET CONDITIONS:**
- Demand Level: {demand_level}
- Competition Level: {competition_level}
- Required Education: {required_education}

Analyze thoroughly and provide a complete gap analysis with detailed reasoning for each assessment. Be specific with skill names, resources, priorities, and time estimates.""")
])


def gap_analyst_node(state: CareerSimulationState) -> dict:
    """
    Node C: GapAnalyst
    Compares user profile against market requirements to identify gaps.
    Uses structured output for reliable data extraction.
    """
    start_time = time.time()
    
    normalized = state.get("normalized_profile")
    market = state.get("market_insights")
    profile = state["career_profile"]
    
    # Format market requirements
    market_requirements = _format_market_requirements(market)
    target_roles = ", ".join(profile.specific_roles) if profile.specific_roles else "Software Engineer"
    
    # Get primary role demand/competition
    demand_level = "Medium"
    competition_level = "Medium"
    required_education = "Bachelor's"
    
    if market and market.target_roles:
        primary_role = market.target_roles[0]
        demand_level = primary_role.demand_level
        competition_level = primary_role.competition_level
        required_education = primary_role.min_education or "Bachelor's"
    
    # Get resume context if available
    resume_context = profile.resume_text if hasattr(profile, 'resume_text') and profile.resume_text else "No resume provided"
    
    # Get LLM with structured output
    llm = get_llm(temperature=0.3)
    
    try:
        structured_llm = llm.with_structured_output(GapAnalysisOutput)
        chain = GAP_ANALYSIS_PROMPT | structured_llm
        
        analysis_output: GapAnalysisOutput = chain.invoke({
            "profile_summary": normalized.profile_summary if normalized else "Profile not available",
            "resume_context": resume_context,
            "academic_score": round(normalized.academic_strength_score, 1) if normalized else 50,
            "gpa": round(normalized.normalized_gpa, 1) if normalized else 50,
            "tech_skills": str(normalized.combined_technical_skills) if normalized else "Not assessed",
            "soft_skills": str(profile.soft_skills) if profile.soft_skills else "Not assessed",
            "institution": profile.institution_name or "Not specified",
            "years_to_grad": normalized.years_to_graduation if normalized else "Unknown",
            "work_preference": profile.work_preference or "Not specified",
            "work_style": profile.work_style or "Not specified",
            "role_preference": profile.role_preference or "Not specified",
            "risk_tolerance": profile.risk_tolerance or "Medium",
            "target_roles": target_roles,
            "market_requirements": market_requirements,
            "demand_level": demand_level,
            "competition_level": competition_level,
            "required_education": required_education,
        })
        
        # Convert to GapAnalysis model
        gap_analysis = _convert_to_gap_analysis(analysis_output)
        
    except Exception as e:
        # Fallback to default analysis if structured output fails
        print(f"Structured output failed, using fallback: {e}")
        gap_analysis = _create_fallback_gap_analysis(profile, normalized, market, target_roles)
    
    # Add vibe check for psychometric mismatches
    vibe_issues = _perform_vibe_check(profile, market)
    gap_analysis.personality_frictions.extend(vibe_issues["frictions"])
    gap_analysis.stress_risks.extend(vibe_issues["stress_risks"])
    
    # Determine if we should suggest alternatives (gap > 80%)
    should_suggest_alternatives = gap_analysis.overall_gap_score > 80
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "gap_analysis": gap_analysis,
        "should_suggest_alternatives": should_suggest_alternatives,
        "current_node": "gap_analyst",
        "processing_time_ms": {"gap_analyst": processing_time},
    }


def _convert_to_gap_analysis(output: GapAnalysisOutput) -> GapAnalysis:
    """Convert structured LLM output to GapAnalysis model."""
    gap_analysis = GapAnalysis(
        overall_gap_score=output.overall_gap_score,
        gap_category=output.gap_category,
        analysis_reasoning=output.analysis_reasoning,
        education_gap=output.education_gap,
        education_gap_reasoning=output.education_gap_reasoning,
        certification_gaps=output.certification_gaps,
        experience_gap_years=output.experience_gap_years,
        experience_gap_reasoning=output.experience_gap_reasoning,
        critical_bottlenecks=output.critical_bottlenecks,
        timeline_bottlenecks=output.timeline_bottlenecks,
        existing_strengths=output.existing_strengths,
        competitive_advantages=output.competitive_advantages,
        personality_frictions=output.personality_frictions,
        stress_risks=output.stress_risks,
        top_priorities=output.top_priorities,
        quick_wins=output.quick_wins,
    )
    
    # Convert skill gaps with reasoning
    for sg in output.technical_skill_gaps:
        # Handle learning_path - ensure it's a list
        learning_path = sg.learning_path
        if isinstance(learning_path, str):
            # Split string into list if it's a string
            learning_path = [step.strip() for step in learning_path.split('\n') if step.strip()]
            if len(learning_path) <= 1 and learning_path:
                # Try splitting by numbered items like "1. Step one 2. Step two"
                import re
                learning_path = re.split(r'\d+\.\s*', learning_path[0])
                learning_path = [step.strip() for step in learning_path if step.strip()]
        
        gap_analysis.technical_skill_gaps.append(SkillGap(
            skill_name=sg.skill_name,
            current_level=sg.current_level,
            required_level=sg.required_level,
            gap_severity=sg.gap_severity,
            estimated_time_to_close=sg.estimated_time_to_close,
            recommended_resources=sg.recommended_resources,
            reasoning=sg.reasoning,
            priority=sg.priority,
            learning_path=learning_path if isinstance(learning_path, list) else [],
        ))
    
    for sg in output.soft_skill_gaps:
        # Handle learning_path - ensure it's a list
        learning_path = sg.learning_path
        if isinstance(learning_path, str):
            learning_path = [step.strip() for step in learning_path.split('\n') if step.strip()]
            if len(learning_path) <= 1 and learning_path:
                import re
                learning_path = re.split(r'\d+\.\s*', learning_path[0])
                learning_path = [step.strip() for step in learning_path if step.strip()]
        
        gap_analysis.soft_skill_gaps.append(SkillGap(
            skill_name=sg.skill_name,
            current_level=sg.current_level,
            required_level=sg.required_level,
            gap_severity=sg.gap_severity,
            estimated_time_to_close=sg.estimated_time_to_close,
            recommended_resources=sg.recommended_resources,
            reasoning=sg.reasoning,
            priority=sg.priority,
            learning_path=learning_path if isinstance(learning_path, list) else [],
        ))
    
    # Ensure gap category matches score
    score = gap_analysis.overall_gap_score
    if score < 20:
        gap_analysis.gap_category = "minimal"
    elif score < 50:
        gap_analysis.gap_category = "manageable"
    elif score < 80:
        gap_analysis.gap_category = "significant"
    else:
        gap_analysis.gap_category = "severe"
    
    return gap_analysis


def _create_fallback_gap_analysis(profile, normalized, market, target_role: str) -> GapAnalysis:
    """Create a fallback gap analysis when LLM fails."""
    gap_analysis = GapAnalysis(
        overall_gap_score=55.0,
        gap_category="significant",
    )
    
    # Add default technical skill gaps based on target role
    default_skills = [
        ("Python", "Intermediate", "Advanced", 50, "3 months", ["Codecademy Python Course", "LeetCode Practice", "Real Python Tutorials"]),
        ("Data Structures & Algorithms", "Basic", "Advanced", 65, "4 months", ["Coursera Data Structures", "HackerRank", "NeetCode 150"]),
        ("System Design", "None", "Intermediate", 70, "6 months", ["System Design Primer", "Educative.io", "ByteByteGo"]),
        ("Cloud Services (AWS/GCP)", "None", "Intermediate", 60, "3 months", ["AWS Certified Cloud Practitioner", "A Cloud Guru", "AWS Free Tier Labs"]),
        ("Git & Version Control", "Basic", "Advanced", 40, "1 month", ["Git Documentation", "GitHub Learning Lab", "Atlassian Git Tutorial"]),
        ("SQL & Databases", "Basic", "Intermediate", 45, "2 months", ["SQLZoo", "Mode Analytics SQL Tutorial", "PostgreSQL Exercises"]),
    ]
    
    for skill_name, current, required, severity, time_est, resources in default_skills:
        gap_analysis.technical_skill_gaps.append(SkillGap(
            skill_name=skill_name,
            current_level=current,
            required_level=required,
            gap_severity=severity,
            estimated_time_to_close=time_est,
            recommended_resources=resources,
        ))
    
    # Add default soft skill gaps
    soft_skills = [
        ("Technical Communication", "Intermediate", "Advanced", 45, "Ongoing", ["Toastmasters", "Technical Writing Course", "Documentation Practice"]),
        ("Problem Solving", "Intermediate", "Expert", 55, "6 months", ["Critical Thinking Course", "Case Study Practice", "Mock Interviews"]),
        ("Team Collaboration", "Basic", "Advanced", 50, "3 months", ["Agile/Scrum Certification", "Open Source Contributions", "Pair Programming"]),
    ]
    
    for skill_name, current, required, severity, time_est, resources in soft_skills:
        gap_analysis.soft_skill_gaps.append(SkillGap(
            skill_name=skill_name,
            current_level=current,
            required_level=required,
            gap_severity=severity,
            estimated_time_to_close=time_est,
            recommended_resources=resources,
        ))
    
    gap_analysis.certification_gaps = ["AWS Cloud Practitioner", "Professional Scrum Master I"]
    gap_analysis.experience_gap_years = 1.5
    gap_analysis.critical_bottlenecks = [
        "Limited hands-on project experience in production environments",
        "No industry internship experience",
        "Gap in system design and architecture knowledge",
    ]
    gap_analysis.timeline_bottlenecks = [
        "Learning curve for advanced technologies requires dedicated time",
        "Building professional network in the industry takes 6-12 months",
        "Portfolio projects need time to demonstrate competency",
    ]
    gap_analysis.existing_strengths = [
        "Strong educational foundation in computer science fundamentals",
        "Clear career goals and high motivation",
        "Good foundational programming knowledge",
        "Academic projects provide starting portfolio",
    ]
    gap_analysis.competitive_advantages = [
        "Fresh perspective and adaptability to new technologies",
        "Current academic knowledge of latest industry trends",
        "Lower salary expectations make you attractive for entry-level roles",
    ]
    
    return gap_analysis


def _format_market_requirements(market) -> str:
    """Format market insights into readable requirements."""
    if not market or not market.target_roles:
        return """Standard Software Engineer Requirements:
- Bachelor's in CS or related field
- Proficiency in at least one programming language (Python, Java, JavaScript)
- Understanding of data structures and algorithms
- Knowledge of databases (SQL/NoSQL)
- Version control (Git)
- Problem-solving and analytical skills
- Team collaboration experience"""
    
    lines = []
    for role in market.target_roles:
        lines.append(f"\n### {role.role_title}")
        
        if role.hard_requirements:
            lines.append("**Hard Requirements:**")
            for req in role.hard_requirements:
                lines.append(f"- {req.skill_or_qualification}: {req.description or 'Required'}")
        
        if role.soft_requirements:
            lines.append("**Preferred:**")
            for req in role.soft_requirements:
                lines.append(f"- {req.skill_or_qualification}: {req.description or 'Preferred'}")
        
        if role.relevant_certifications:
            lines.append(f"**Certifications:** {', '.join(role.relevant_certifications)}")
        
        if role.emerging_skills:
            lines.append(f"**Emerging Skills:** {', '.join(role.emerging_skills)}")
    
    return "\n".join(lines) if lines else "Standard industry requirements apply"


def _perform_vibe_check(profile, market) -> dict:
    """
    Perform psychometric "vibe check" to identify personality-role mismatches.
    Returns dict with frictions and stress_risks lists.
    """
    frictions = []
    stress_risks = []
    
    # Theory vs Practical mismatch
    if profile.work_style:
        work_style_lower = profile.work_style.lower()
        target_roles = [r.lower() for r in (profile.specific_roles or [])]
        
        if "theor" in work_style_lower:
            practical_roles = ["engineer", "developer", "technician", "craftsman", "operator"]
            if any(any(pr in role for pr in practical_roles) for role in target_roles):
                frictions.append(
                    "Your theoretical work style may conflict with the hands-on nature of the target role. "
                    "Consider roles with more research/analysis components or plan to develop practical skills."
                )
    
    # Risk tolerance vs work environment
    if profile.risk_tolerance and profile.preferred_work_env:
        risk_lower = profile.risk_tolerance.lower()
        env_lower = [e.lower() for e in profile.preferred_work_env]
        
        if "low" in risk_lower and any("startup" in e for e in env_lower):
            stress_risks.append(
                "STRESS RISK: You prefer low-risk situations but are targeting startup environments, "
                "which typically involve high uncertainty and job insecurity."
            )
            frictions.append(
                "Low risk tolerance conflicts with startup preference. Consider established companies "
                "with innovation teams for a balance of stability and dynamic work."
            )
        
        if "high" in risk_lower and any("corporate" in e for e in env_lower):
            frictions.append(
                "Your high risk tolerance may lead to frustration in traditional corporate environments. "
                "Look for innovation/R&D teams or intrapreneurship programs within large companies."
            )
    
    # Structured vs Dynamic role preference
    if profile.role_preference:
        role_pref_lower = profile.role_preference.lower()
        target_roles = [r.lower() for r in (profile.specific_roles or [])]
        
        dynamic_roles = ["consultant", "entrepreneur", "founder", "freelance", "creative"]
        if "structured" in role_pref_lower:
            if any(any(dr in role for dr in dynamic_roles) for role in target_roles):
                frictions.append(
                    "You prefer structured roles but are targeting dynamic/fluid positions. "
                    "This may cause discomfort with ambiguity."
                )
                stress_risks.append(
                    "ADAPTABILITY STRESS: Structured preference + dynamic role may cause anxiety "
                    "around unclear expectations and changing priorities."
                )
    
    return {"frictions": frictions, "stress_risks": stress_risks}
