"""
Node F: RiskAssessor Agent
The Probability Engine - Assigns success probability and identifies risks
Uses structured output for reliable data extraction
"""

import time
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..models.state import (
    CareerSimulationState,
    RiskAssessment,
    RiskFactor,
)
from .base import get_llm


# Structured output models for LLM response
class RiskFactorOutput(BaseModel):
    """A single risk factor."""
    factor_name: str = Field(description="Name of the risk factor")
    category: str = Field(description="Category: market, personal, financial, technical")
    severity: str = Field(description="Severity: low, medium, high, critical")
    probability: float = Field(description="Probability of occurrence (0-100)")
    impact_description: str = Field(description="Description of potential impact")
    mitigation_strategy: str = Field(description="Strategy to mitigate this risk")
    reasoning: str = Field(default="", description="Why this risk is relevant for this specific candidate")


class RiskAssessmentOutput(BaseModel):
    """Complete risk assessment output."""
    success_probability_score: float = Field(description="Overall success probability (0-100)")
    success_reasoning: str = Field(description="Detailed explanation of why this probability was assigned based on the candidate's specific profile")
    confidence_interval: str = Field(description="Confidence interval like '60-75%'")
    
    risk_factors: list[RiskFactorOutput] = Field(
        description="4-8 specific risk factors across all categories"
    )
    
    market_risk_score: float = Field(description="Market-related risk score (0-100)")
    market_risk_reasoning: str = Field(default="", description="Why market risk is at this level")
    personal_risk_score: float = Field(description="Personal/lifestyle risk score (0-100)")
    personal_risk_reasoning: str = Field(default="", description="Why personal risk is at this level")
    financial_risk_score: float = Field(description="Financial risk score (0-100)")
    financial_risk_reasoning: str = Field(default="", description="Why financial risk is at this level")
    technical_risk_score: float = Field(description="Technical skill-related risk score (0-100)")
    technical_risk_reasoning: str = Field(default="", description="Why technical risk is at this level")
    
    positive_factors: list[str] = Field(description="4-6 factors working in candidate's favor")
    negative_factors: list[str] = Field(description="3-5 factors working against candidate")
    key_opportunities: list[str] = Field(default_factory=list, description="2-4 opportunities the candidate should capitalize on")
    key_concerns: list[str] = Field(default_factory=list, description="2-4 major concerns that need addressing")
    
    compared_to_average: str = Field(description="How candidate compares: Above average, Average, Below average")
    comparison_reasoning: str = Field(default="", description="Why candidate is above/below average compared to peers")
    peer_success_rate: float = Field(description="Success rate of similar profiles (percentage)")
    
    risk_mitigation_plan: list[str] = Field(description="5-7 priority actions to mitigate risks")
    contingency_plans: list[str] = Field(description="3-5 backup plans if primary path fails")
    recommendations: list[str] = Field(default_factory=list, description="Top 3-5 recommendations based on the analysis")
    
    best_case_scenario: str = Field(default="", description="Description of the best case outcome")
    worst_case_scenario: str = Field(default="", description="Description of the worst case outcome")
    most_likely_scenario: str = Field(default="", description="Description of the most likely outcome")


RISK_ASSESSMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert career risk analyst. Your task is to:

1. Calculate a realistic success probability score (0-100) WITH DETAILED REASONING
2. Identify 4-8 specific risk factors across categories:
   - Market risks (industry changes, job availability, competition)
   - Personal risks (burnout, life events, motivation)
   - Financial risks (costs, income gaps, debt)
   - Technical risks (skill obsolescence, learning curve)
   For each factor, include reasoning for why it applies to THIS specific candidate

3. Provide category-specific risk scores (0-100 each) WITH REASONING
4. List positive factors (what's working for them)
5. List negative factors (challenges to overcome)
6. Identify key opportunities and key concerns
7. Compare to similar candidates WITH EXPLANATION
8. Provide detailed mitigation strategies
9. Create scenarios (best case, worst case, most likely)

IMPORTANT: For SUCCESS_REASONING, explain specifically why you assigned the probability based on:
- Their academic score and career readiness
- Gap severity and how quickly gaps can be closed
- Market conditions for their target role
- Personal factors (risk tolerance, hours available, mentor support)
- Financial situation (can they afford the journey?)

Be balanced - neither overly optimistic nor pessimistic. Base your assessment on real data provided.

NEVER leave arrays empty. Provide specific, actionable insights."""),

    ("human", """Perform a comprehensive risk assessment:

**CANDIDATE PROFILE:**
{profile_summary}

**Resume Context (if available):**
{resume_context}

**KEY METRICS:**
- Academic Strength: {academic_score}/100
- Career Readiness: {career_readiness}/100
- Skill Readiness: {skill_readiness}/100
- Financial Readiness: {financial_readiness}/100

**GAP ANALYSIS:**
- Overall Gap Score: {gap_score}/100
- Gap Category: {gap_category}
- Critical Bottlenecks: {bottlenecks}
- Technical Skill Gaps: {skill_gaps}

**MARKET CONDITIONS:**
- Demand Level: {demand_level}
- Competition Level: {competition_level}
- Growth Outlook: {growth_outlook}

**PERSONAL FACTORS:**
- Risk Tolerance: {risk_tolerance}
- Market Awareness: {market_awareness}
- Has Mentor: {has_mentor}
- Hours Available/Week: {hours_week}
- Key Concerns: {concerns}

**FINANCIAL SITUATION:**
- Investment Capacity: {investment_capacity}
- Affordability Rating: {affordability}
- Total Investment Required: ${total_investment}
- Break-Even Year: {break_even_year}

**CAREER PATH:**
- Target Role: {target_role}
- Timeline: {timeline_years} years
- Expected Final Salary: ${expected_salary}

**IDENTIFIED FRICTIONS:**
{personality_frictions}

Provide a comprehensive risk assessment with:
1. Specific probability score with detailed reasoning explaining WHY
2. Risk factors with individual reasoning
3. Category scores with reasoning
4. Best/worst/most likely scenarios
5. Specific recommendations based on this candidate's situation""")
])


def risk_assessor_node(state: CareerSimulationState) -> dict:
    """
    Node F: RiskAssessor
    Assigns success probability and identifies risk factors.
    Uses structured output for reliable data extraction.
    """
    start_time = time.time()
    
    profile = state["career_profile"]
    normalized = state.get("normalized_profile")
    market = state.get("market_insights")
    gap = state.get("gap_analysis")
    financial = state.get("financial_analysis")
    timeline = state.get("timeline_simulation")
    
    # Get market conditions
    demand_level = "Medium"
    competition_level = "Medium"
    growth_outlook = "Stable"
    
    if market and market.target_roles:
        role = market.target_roles[0]
        demand_level = role.demand_level
        competition_level = role.competition_level
        growth_outlook = role.growth_outlook
    
    # Format bottlenecks
    bottlenecks = "None identified"
    if gap and gap.critical_bottlenecks:
        bottlenecks = "; ".join(gap.critical_bottlenecks[:3])
    
    # Format skill gaps
    skill_gaps = "Not assessed"
    if gap and gap.technical_skill_gaps:
        skill_gaps = ", ".join([f"{g.skill_name} ({g.gap_severity}/100)" for g in gap.technical_skill_gaps[:5]])
    
    # Format frictions
    frictions = "None identified"
    if gap and gap.personality_frictions:
        frictions = "; ".join(gap.personality_frictions[:3])
    
    # Get career path info
    career_path = None
    if timeline:
        if timeline.recommended_path == "conservative":
            career_path = timeline.conservative_path
        elif timeline.recommended_path == "ambitious":
            career_path = timeline.ambitious_path
        else:
            career_path = timeline.realistic_path
    
    target_role = career_path.final_target_role if career_path else "Software Engineer"
    timeline_years = career_path.total_years if career_path else 5
    expected_salary = career_path.final_expected_salary if career_path else 100000
    
    # Get resume context if available
    resume_context = profile.resume_text if hasattr(profile, 'resume_text') and profile.resume_text else "No resume provided"
    
    # Get LLM with structured output
    llm = get_llm(temperature=0.3)
    
    try:
        structured_llm = llm.with_structured_output(RiskAssessmentOutput)
        chain = RISK_ASSESSMENT_PROMPT | structured_llm
        
        assessment_output: RiskAssessmentOutput = chain.invoke({
            "profile_summary": normalized.profile_summary if normalized else "Profile not available",
            "resume_context": resume_context,
            "academic_score": round(normalized.academic_strength_score, 1) if normalized else 50,
            "career_readiness": round(normalized.career_readiness_score, 1) if normalized else 50,
            "skill_readiness": round(normalized.skill_readiness_score, 1) if normalized else 50,
            "financial_readiness": round(normalized.financial_readiness_score, 1) if normalized else 50,
            "gap_score": round(gap.overall_gap_score, 1) if gap else 50,
            "gap_category": gap.gap_category if gap else "significant",
            "bottlenecks": bottlenecks,
            "skill_gaps": skill_gaps,
            "demand_level": demand_level,
            "competition_level": competition_level,
            "growth_outlook": growth_outlook,
            "risk_tolerance": profile.risk_tolerance or "Medium",
            "market_awareness": profile.market_awareness or "Medium",
            "has_mentor": "Yes" if profile.has_mentor else "No",
            "hours_week": profile.hours_per_week or 20,
            "concerns": ", ".join(profile.career_concerns[:3]) if profile.career_concerns else "General career uncertainty",
            "investment_capacity": profile.investment_capacity or "Medium",
            "affordability": financial.affordability_rating if financial else "feasible",
            "total_investment": financial.total_investment_required if financial else 15000,
            "break_even_year": financial.break_even_year if financial else 3,
            "target_role": target_role,
            "timeline_years": timeline_years,
            "expected_salary": expected_salary,
            "personality_frictions": frictions,
        })
        
        # Convert to RiskAssessment model
        risk_assessment = _convert_to_risk_assessment(assessment_output)
        
    except Exception as e:
        # Fallback if structured output fails
        print(f"Structured output failed, using fallback: {e}")
        risk_assessment = _create_fallback_risk_assessment(profile, normalized, gap, financial)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "risk_assessment": risk_assessment,
        "current_node": "risk_assessor",
        "processing_time_ms": {"risk_assessor": processing_time},
    }


def _convert_to_risk_assessment(output: RiskAssessmentOutput) -> RiskAssessment:
    """Convert structured LLM output to RiskAssessment model."""
    assessment = RiskAssessment(
        success_probability_score=output.success_probability_score,
        success_reasoning=output.success_reasoning,
        confidence_interval=output.confidence_interval,
        market_risk_score=output.market_risk_score,
        market_risk_reasoning=output.market_risk_reasoning,
        personal_risk_score=output.personal_risk_score,
        personal_risk_reasoning=output.personal_risk_reasoning,
        financial_risk_score=output.financial_risk_score,
        financial_risk_reasoning=output.financial_risk_reasoning,
        technical_risk_score=output.technical_risk_score,
        technical_risk_reasoning=output.technical_risk_reasoning,
        positive_factors=output.positive_factors,
        negative_factors=output.negative_factors,
        key_opportunities=output.key_opportunities,
        key_concerns=output.key_concerns,
        compared_to_average=output.compared_to_average,
        comparison_reasoning=output.comparison_reasoning,
        peer_success_rate=output.peer_success_rate,
        risk_mitigation_plan=output.risk_mitigation_plan,
        contingency_plans=output.contingency_plans,
        recommendations=output.recommendations,
        best_case_scenario=output.best_case_scenario,
        worst_case_scenario=output.worst_case_scenario,
        most_likely_scenario=output.most_likely_scenario,
    )
    
    # Convert risk factors with reasoning
    for rf in output.risk_factors:
        assessment.risk_factors.append(RiskFactor(
            factor_name=rf.factor_name,
            category=rf.category,
            severity=rf.severity,
            probability=rf.probability,
            impact_description=rf.impact_description,
            mitigation_strategies=[rf.mitigation_strategy] if rf.mitigation_strategy else [],
            reasoning=rf.reasoning if hasattr(rf, 'reasoning') else "",
        ))
    
    return assessment


def _create_fallback_risk_assessment(profile, normalized, gap, financial) -> RiskAssessment:
    """Create a fallback risk assessment when LLM fails."""
    # Calculate base success probability
    base_prob = 60.0
    if normalized:
        base_prob = (normalized.academic_strength_score + normalized.career_readiness_score + normalized.skill_readiness_score) / 3
    
    if gap:
        # Adjust based on gap
        gap_penalty = gap.overall_gap_score * 0.3
        base_prob = max(30, base_prob - gap_penalty + 20)
    
    assessment = RiskAssessment(
        success_probability_score=round(base_prob, 1),
        confidence_interval=f"{max(20, base_prob - 10):.0f}-{min(95, base_prob + 15):.0f}%",
        market_risk_score=35.0,
        personal_risk_score=40.0,
        financial_risk_score=45.0,
        technical_risk_score=50.0,
        positive_factors=[
            "Clear career goals and target role identified",
            "Strong educational foundation in relevant field",
            "High motivation and commitment to career change",
            "Growing market demand for target skills",
            "Reasonable timeline with achievable milestones"
        ],
        negative_factors=[
            "Gap between current skills and market requirements",
            "Limited hands-on industry experience",
            "Competitive job market for entry-level positions",
            "Financial investment required for skill development"
        ],
        compared_to_average="Average",
        peer_success_rate=65.0,
        risk_mitigation_plan=[
            "Start with foundational skills immediately - don't wait for perfect conditions",
            "Build portfolio projects to demonstrate practical abilities",
            "Network actively through LinkedIn, meetups, and industry events",
            "Seek internship opportunities for real-world experience",
            "Get certifications to validate skills to employers",
            "Find a mentor in your target field for guidance",
            "Apply to multiple positions and track responses to improve approach"
        ],
        contingency_plans=[
            "If primary role is too competitive, consider adjacent roles as stepping stones",
            "Freelance work can build portfolio while searching for full-time positions",
            "Consider contract/consulting roles which may have lower barriers to entry",
            "Pivot to related field if market conditions change significantly",
            "Part-time roles can provide income while continuing skill development"
        ],
    )
    
    # Add risk factors
    risk_factors = [
        ("Market Saturation", "market", "medium", 45, 
         "High competition for entry-level positions in the target field",
         "Differentiate through specialized skills, unique projects, or niche expertise"),
        ("Skill Obsolescence", "technical", "medium", 40,
         "Technology skills may become outdated during the transition period",
         "Focus on fundamentals and continuously learn emerging technologies"),
        ("Financial Pressure", "financial", "medium", 50,
         "Investment in education/training may strain finances during transition",
         "Create budget plan, explore scholarships, and maintain emergency fund"),
        ("Burnout Risk", "personal", "medium", 35,
         "Balancing learning, work, and personal life may lead to exhaustion",
         "Set realistic pace, take breaks, and prioritize self-care"),
        ("Economic Downturn", "market", "low", 25,
         "Recession could reduce hiring and extend job search timeline",
         "Build emergency savings and develop recession-resistant skills"),
        ("Imposter Syndrome", "personal", "high", 60,
         "Self-doubt may impact confidence during interviews and early career",
         "Document achievements, seek feedback, and connect with peer support groups")
    ]
    
    for name, cat, sev, prob, impact, mitigation in risk_factors:
        assessment.risk_factors.append(RiskFactor(
            factor_name=name,
            category=cat,
            severity=sev,
            probability=prob,
            impact_description=impact,
            mitigation_strategy=mitigation,
        ))
    
    return assessment
