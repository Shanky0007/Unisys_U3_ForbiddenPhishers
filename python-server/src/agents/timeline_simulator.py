"""
Node D: TimelineSimulator Agent
The Core Engine - Generates year-by-year career simulation paths
Uses structured output for reliable data extraction
"""

import time
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..models.state import (
    CareerSimulationState,
    TimelineSimulation,
    CareerPath,
    YearPlan,
    YearMilestone,
)
from .base import get_llm


# Structured output models for LLM response
class MilestoneOutput(BaseModel):
    """A single milestone within a quarter."""
    quarter: int = Field(description="Quarter number (1-4)")
    title: str = Field(description="Short title of the milestone")
    description: str = Field(description="Detailed description of what to accomplish")
    type: str = Field(description="Type: education, skill, career, certification, project, or networking")
    estimated_cost: float = Field(description="Estimated cost in USD")
    estimated_hours: int = Field(description="Estimated hours to complete")
    reasoning: str = Field(default="", description="Why this milestone is important for the career path")
    dependencies: list[str] = Field(default_factory=list, description="What must be completed before this")
    risk_if_skipped: str = Field(default="", description="Consequences of skipping this milestone")


class YearPlanOutput(BaseModel):
    """Plan for a single year."""
    year_number: int = Field(description="Year number (1, 2, 3, etc.)")
    year_label: str = Field(description="Descriptive label like 'Year 1: Foundation Building'")
    phase: str = Field(description="Phase: Preparation, Transition, or Growth")
    primary_focus: str = Field(description="Main focus area for this year")
    phase_reasoning: str = Field(default="", description="Why this phase/focus is appropriate at this point")
    focus_reasoning: str = Field(default="", description="Why this is the right thing to focus on")
    milestones: list[MilestoneOutput] = Field(description="4 milestones, one per quarter")
    expected_role: Optional[str] = Field(default=None, description="Expected role/position by end of year")
    expected_salary_range: Optional[str] = Field(default=None, description="Expected salary range if employed")
    key_skills_acquired: list[str] = Field(description="Skills to be acquired this year")
    skill_progress_target: int = Field(default=25, description="Target skill progress percentage for this year")
    potential_setbacks: list[str] = Field(description="Potential risks/setbacks for this year")
    risk_mitigation: list[str] = Field(default_factory=list, description="How to mitigate the setbacks")
    success_indicators: list[str] = Field(default_factory=list, description="How to know you're on track")
    buffer_time_weeks: int = Field(default=4, description="Buffer time in weeks for unexpected delays")


class CareerPathOutput(BaseModel):
    """A complete career path (conservative, realistic, or ambitious)."""
    path_label: str = Field(description="Creative name for this path")
    total_years: int = Field(description="Total duration in years")
    yearly_plans: list[YearPlanOutput] = Field(description="Detailed plan for each year")
    final_target_role: str = Field(description="Final target role at end of path")
    final_expected_salary: float = Field(description="Expected salary at end of path")
    major_milestones: list[str] = Field(description="Key milestones across the entire path")
    assumptions: list[str] = Field(description="Key assumptions this path makes")
    key_decision_points: list[str] = Field(description="Critical decision points along the way")


class TimelineSimulationOutput(BaseModel):
    """Complete timeline simulation with all three paths."""
    conservative_path: CareerPathOutput = Field(description="Safe, methodical approach with buffer time")
    realistic_path: CareerPathOutput = Field(description="Balanced approach with reasonable expectations")
    ambitious_path: CareerPathOutput = Field(description="Aggressive timeline assuming optimal execution")
    recommended_path: str = Field(description="One of: conservative, realistic, ambitious")
    recommendation_reason: str = Field(description="Why this path is recommended")
    alignment_score: float = Field(description="How well paths align with user preferences (0-100)")
    vibe_check_warnings: list[str] = Field(default_factory=list, description="Personality-career friction warnings")


TIMELINE_SIMULATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert career simulation engine. Generate detailed, realistic year-by-year career roadmaps with comprehensive reasoning.

Generate THREE distinct paths:
1. **CONSERVATIVE PATH**: Safe, methodical approach with buffer time for setbacks (add 1-2 extra years)
2. **REALISTIC PATH**: Balanced approach with reasonable expectations
3. **AMBITIOUS PATH**: Aggressive timeline assuming optimal execution (reduce by 6-12 months)

For EACH year, provide:
- 4 milestones (one per quarter) with specific activities, costs, and time estimates
- **Phase reasoning**: Why this phase (Preparation/Transition/Growth) is appropriate now
- **Focus reasoning**: Why this is the right thing to focus on at this stage
- Expected role and salary if employed
- Skills to be acquired
- Risk mitigation strategies
- Success indicators to track progress
- Potential setbacks to watch for

For EACH milestone, provide:
- **Reasoning**: Why this milestone is critical for career progression
- **Dependencies**: What must be completed before this milestone
- **Risk if skipped**: Consequences of not completing this milestone

Be SPECIFIC:
- Name actual courses (Coursera, Udemy, etc.)
- Mention specific certifications (AWS, Google, etc.)
- Include networking activities
- Provide realistic cost estimates
- Include job search activities where appropriate

CRITICAL: Every decision must be justified with clear reasoning based on the user's profile, market conditions, and career goals.

NEVER leave arrays empty. Each year must have 4 milestones."""),

    ("human", """Generate a {simulation_years}-year career simulation with detailed reasoning:

**CANDIDATE SUMMARY:**
{profile_summary}

**CURRENT POSITION:**
- Education Level: {education_level}
- Years to Graduation: {years_to_grad}
- Current Skills: {current_skills}

**TARGET:**
- Target Roles: {target_roles}
- Primary Career Goal: {career_goal}
- Desired Level: {desired_level}

**GAP ANALYSIS:**
- Overall Gap Score: {gap_score}/100
- Critical Gaps: {critical_gaps}
- Key Skill Gaps: {skill_gaps}
- Education Gap: {education_gap}

**CONSTRAINTS:**
- Hours Available/Week: {hours_week}
- Learning Mode: {learning_mode}
- Investment Capacity: {investment}
- Risk Tolerance: {risk_tolerance}
- Optimism Level: {optimism}

**MARKET CONDITIONS:**
- Demand Level: {demand_level}
- Competition: {competition_level}
- Entry Salary Range: {entry_salary}
- Senior Salary Range: {senior_salary}

**PERSONALITY FACTORS:**
- Work Style: {work_style}
- Role Preference: {role_preference}
- Identified Frictions: {frictions}

Generate detailed career paths with specific milestones, costs, and timelines for each quarter of each year.""")
])


def timeline_simulator_node(state: CareerSimulationState) -> dict:
    """
    Node D: TimelineSimulator
    Generates year-by-year career simulation with multiple paths.
    Uses structured output for reliable data extraction.
    """
    start_time = time.time()
    
    profile = state["career_profile"]
    normalized = state.get("normalized_profile")
    market = state.get("market_insights")
    gap = state.get("gap_analysis")
    
    # Determine simulation length based on gap
    if gap and gap.overall_gap_score > 70:
        simulation_years = 6
    elif gap and gap.overall_gap_score > 40:
        simulation_years = 5
    else:
        simulation_years = 4
    
    # Get salary ranges from market
    entry_salary = "$50,000 - $80,000"
    senior_salary = "$120,000 - $180,000"
    demand_level = "Medium"
    competition_level = "Medium"
    
    if market and market.target_roles:
        role = market.target_roles[0]
        if role.salary_range:
            entry_salary = f"${role.salary_range.entry_level_min:,.0f} - ${role.salary_range.entry_level_max:,.0f}"
            senior_salary = f"${role.salary_range.senior_level_min:,.0f} - ${role.salary_range.senior_level_max:,.0f}"
        demand_level = role.demand_level
        competition_level = role.competition_level
    
    # Format skill gaps
    skill_gaps = "Not assessed"
    if gap and gap.technical_skill_gaps:
        skill_gaps = ", ".join([g.skill_name for g in gap.technical_skill_gaps[:5]])
    
    # Format critical gaps
    critical_gaps = "None identified"
    if gap and gap.critical_bottlenecks:
        critical_gaps = "; ".join(gap.critical_bottlenecks[:3])
    
    # Format frictions
    frictions = "None identified"
    if gap and (gap.personality_frictions or gap.stress_risks):
        all_frictions = gap.personality_frictions + gap.stress_risks
        frictions = "; ".join(all_frictions[:3])
    
    # Get LLM with structured output
    llm = get_llm(temperature=0.5)
    
    try:
        structured_llm = llm.with_structured_output(TimelineSimulationOutput)
        chain = TIMELINE_SIMULATION_PROMPT | structured_llm
        
        simulation_output: TimelineSimulationOutput = chain.invoke({
            "simulation_years": simulation_years,
            "profile_summary": normalized.profile_summary if normalized else "Profile not available",
            "education_level": profile.current_education_level or "Not specified",
            "years_to_grad": normalized.years_to_graduation if normalized else "Unknown",
            "current_skills": str(normalized.combined_technical_skills) if normalized else "Not assessed",
            "target_roles": ", ".join(profile.specific_roles) if profile.specific_roles else "Software Engineer",
            "career_goal": profile.primary_career_goal or "Career advancement",
            "desired_level": profile.desired_role_level or "Senior IC",
            "gap_score": round(gap.overall_gap_score, 1) if gap else 50,
            "critical_gaps": critical_gaps,
            "skill_gaps": skill_gaps,
            "education_gap": gap.education_gap if gap and gap.education_gap else "None",
            "hours_week": profile.hours_per_week or 20,
            "learning_mode": ", ".join(profile.preferred_learning_mode) if profile.preferred_learning_mode else "Self-paced",
            "investment": profile.investment_capacity or "Medium ($5,000-15,000)",
            "risk_tolerance": profile.risk_tolerance or "Medium",
            "optimism": profile.optimism_level or "Balanced",
            "demand_level": demand_level,
            "competition_level": competition_level,
            "entry_salary": entry_salary,
            "senior_salary": senior_salary,
            "work_style": profile.work_style or "Balanced",
            "role_preference": profile.role_preference or "Flexible",
            "frictions": frictions,
        })
        
        # Convert to TimelineSimulation model
        timeline_simulation = _convert_to_timeline_simulation(simulation_output)
        
    except Exception as e:
        # Fallback if structured output fails
        print(f"Structured output failed, using fallback: {e}")
        target_role = profile.specific_roles[0] if profile.specific_roles else "Software Engineer"
        timeline_simulation = _create_fallback_simulation(simulation_years, target_role, gap)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "timeline_simulation": timeline_simulation,
        "current_node": "timeline_simulator",
        "processing_time_ms": {"timeline_simulator": processing_time},
    }


def _convert_to_timeline_simulation(output: TimelineSimulationOutput) -> TimelineSimulation:
    """Convert structured LLM output to TimelineSimulation model."""
    simulation = TimelineSimulation(
        recommended_path=output.recommended_path,
        recommendation_reason=output.recommendation_reason,
        alignment_score=output.alignment_score,
        vibe_check_warnings=output.vibe_check_warnings,
    )
    
    # Convert paths
    simulation.conservative_path = _convert_career_path(output.conservative_path, "conservative")
    simulation.realistic_path = _convert_career_path(output.realistic_path, "realistic")
    simulation.ambitious_path = _convert_career_path(output.ambitious_path, "ambitious")
    
    return simulation


def _convert_career_path(path_output: CareerPathOutput, path_type: str) -> CareerPath:
    """Convert CareerPathOutput to CareerPath model."""
    path = CareerPath(
        path_type=path_type,
        path_label=path_output.path_label,
        total_years=path_output.total_years,
        final_target_role=path_output.final_target_role,
        final_expected_salary=path_output.final_expected_salary,
        major_milestones=path_output.major_milestones,
        assumptions=path_output.assumptions,
        key_decision_points=path_output.key_decision_points,
    )
    
    # Convert yearly plans
    for year_output in path_output.yearly_plans:
        # Convert skill_progress_target int to dict format
        skill_target_int = getattr(year_output, 'skill_progress_target', 25)
        skill_progress_dict = {"overall": skill_target_int}
        
        year_plan = YearPlan(
            year_number=year_output.year_number,
            year_label=year_output.year_label,
            phase=year_output.phase,
            primary_focus=year_output.primary_focus,
            phase_reasoning=getattr(year_output, 'phase_reasoning', ''),
            focus_reasoning=getattr(year_output, 'focus_reasoning', ''),
            expected_role=year_output.expected_role,
            expected_salary_range=year_output.expected_salary_range,
            key_skills_acquired=year_output.key_skills_acquired,
            skill_progress_target=skill_progress_dict,
            potential_setbacks=year_output.potential_setbacks,
            risk_mitigation=getattr(year_output, 'risk_mitigation', []),
            success_indicators=getattr(year_output, 'success_indicators', []),
            buffer_time_weeks=year_output.buffer_time_weeks,
        )
        
        # Convert milestones with reasoning
        for m in year_output.milestones:
            year_plan.milestones.append(YearMilestone(
                quarter=m.quarter,
                title=m.title,
                description=m.description,
                type=m.type,
                estimated_cost=m.estimated_cost,
                estimated_hours=m.estimated_hours,
                reasoning=getattr(m, 'reasoning', ''),
                dependencies=getattr(m, 'dependencies', []),
                risk_if_skipped=getattr(m, 'risk_if_skipped', ''),
            ))
        
        path.yearly_plans.append(year_plan)
    
    return path


def _create_fallback_simulation(total_years: int, target_role: str, gap) -> TimelineSimulation:
    """Create a fallback timeline simulation when LLM fails."""
    simulation = TimelineSimulation(
        recommended_path="realistic",
        recommendation_reason="Based on your profile, the realistic path provides the best balance of speed and risk management.",
        alignment_score=75.0,
        vibe_check_warnings=[
            "Ensure you allocate time for practical projects alongside theoretical learning",
            "Consider joining tech communities early for networking opportunities"
        ],
    )
    
    # Create all three paths
    for path_type in ["conservative", "realistic", "ambitious"]:
        path = _create_fallback_path(path_type, total_years, target_role, gap)
        if path_type == "conservative":
            simulation.conservative_path = path
        elif path_type == "realistic":
            simulation.realistic_path = path
        else:
            simulation.ambitious_path = path
    
    return simulation


def _create_fallback_path(path_type: str, total_years: int, target_role: str, gap) -> CareerPath:
    """Create a fallback career path."""
    # Adjust years based on path type
    if path_type == "conservative":
        years = total_years + 1
        salary_mult = 0.9
    elif path_type == "ambitious":
        years = max(total_years - 1, 3)
        salary_mult = 1.1
    else:
        years = total_years
        salary_mult = 1.0
    
    path = CareerPath(
        path_type=path_type,
        path_label=f"The {path_type.title()} {target_role} Path",
        total_years=years,
        final_target_role=f"Senior {target_role}",
        final_expected_salary=130000 * salary_mult,
        major_milestones=[
            "Complete foundational skills development",
            "Land first internship or entry-level position",
            "Earn industry certifications",
            "Transition to target role",
            "Achieve senior-level expertise"
        ],
        assumptions=[
            f"Dedicated {20 if path_type == 'conservative' else 30 if path_type == 'ambitious' else 25} hours/week for learning",
            "Consistent progress without major life disruptions",
            "Access to learning resources and mentorship"
        ],
        key_decision_points=[
            "Year 1: Choose specialization track",
            "Year 2: Decide on certification path",
            f"Year {years-1}: Evaluate career trajectory and adjust if needed"
        ],
    )
    
    # Create yearly plans
    phases = {1: "Preparation", 2: "Transition", 3: "Transition", 4: "Growth", 5: "Growth", 6: "Mastery"}
    
    for year_num in range(1, years + 1):
        phase = phases.get(year_num, "Growth")
        year_plan = YearPlan(
            year_number=year_num,
            year_label=f"Year {year_num}: {phase} Phase",
            phase=phase,
            primary_focus=_get_year_focus(year_num, target_role),
            expected_role=_get_expected_role(year_num, target_role),
            expected_salary_range=_get_expected_salary(year_num, salary_mult),
            key_skills_acquired=_get_year_skills(year_num, target_role),
            potential_setbacks=[
                "Learning curve may be steeper than expected",
                "Job market fluctuations",
                "Competing priorities with current commitments"
            ],
            buffer_time_weeks=6 if path_type == "conservative" else 2 if path_type == "ambitious" else 4,
        )
        
        # Add quarterly milestones
        for q in range(1, 5):
            milestone = _create_milestone(year_num, q, target_role, path_type)
            year_plan.milestones.append(milestone)
        
        path.yearly_plans.append(year_plan)
    
    return path


def _get_year_focus(year: int, role: str) -> str:
    focuses = {
        1: f"Build foundational skills for {role} career",
        2: "Develop practical experience through projects and internships",
        3: "Earn certifications and expand professional network",
        4: "Secure full-time position and establish industry presence",
        5: "Advance to senior responsibilities and leadership",
        6: "Achieve expertise and mentor others"
    }
    return focuses.get(year, f"Continue growth as {role}")


def _get_expected_role(year: int, target_role: str) -> str:
    roles = {
        1: "Student / Learner",
        2: "Intern / Junior Developer",
        3: f"Junior {target_role}",
        4: f"{target_role}",
        5: f"Senior {target_role}",
        6: f"Lead {target_role}"
    }
    return roles.get(year, target_role)


def _get_expected_salary(year: int, mult: float) -> str:
    salaries = {
        1: None,
        2: "$30,000 - $50,000 (internship/part-time)",
        3: "$55,000 - $75,000",
        4: "$75,000 - $95,000",
        5: "$95,000 - $130,000",
        6: "$130,000 - $160,000"
    }
    return salaries.get(year)


def _get_year_skills(year: int, role: str) -> list[str]:
    skills_by_year = {
        1: ["Python/JavaScript basics", "Git fundamentals", "Data structures", "HTML/CSS"],
        2: ["Frameworks (React/Django)", "Databases (SQL/NoSQL)", "REST APIs", "Testing"],
        3: ["Cloud services (AWS/GCP)", "CI/CD pipelines", "System design basics", "Agile/Scrum"],
        4: ["Advanced system design", "Performance optimization", "Security practices", "Technical leadership"],
        5: ["Architecture patterns", "Team mentoring", "Technical planning", "Cross-functional collaboration"],
        6: ["Strategic planning", "Organization-wide impact", "Industry expertise", "Innovation leadership"]
    }
    return skills_by_year.get(year, ["Continued professional development"])


def _create_milestone(year: int, quarter: int, role: str, path_type: str) -> YearMilestone:
    """Create a milestone for a specific year and quarter."""
    # Base milestones templates by year
    milestones_template = {
        1: {
            1: ("Complete Python Fundamentals", "Finish Codecademy Python course and build 3 small projects", "education", 50, 60),
            2: ("Master Data Structures", "Complete data structures course on Coursera, practice 50+ LeetCode problems", "skill", 100, 80),
            3: ("Build Portfolio Project", "Create a full-stack web application showcasing your skills", "project", 0, 100),
            4: ("Learn Cloud Basics", "Complete AWS Cloud Practitioner preparation", "certification", 200, 60),
        },
        2: {
            1: ("Start Internship Search", "Apply to 30+ internships, optimize LinkedIn, prepare for interviews", "career", 50, 40),
            2: ("Earn AWS Certification", "Pass AWS Cloud Practitioner exam", "certification", 150, 40),
            3: ("Complete Summer Internship", "Gain hands-on industry experience at a tech company", "career", 0, 480),
            4: ("Build Advanced Project", "Create a complex project using new skills from internship", "project", 100, 80),
        },
        3: {
            1: ("Deepen Technical Skills", "Master advanced concepts in your specialization", "skill", 200, 100),
            2: ("Expand Network", "Attend 3+ tech meetups, connect with 20+ professionals", "networking", 100, 30),
            3: ("Job Search Preparation", "Update resume, practice system design, mock interviews", "career", 50, 60),
            4: ("Land Entry-Level Position", "Secure first full-time role in target field", "career", 0, 80),
        },
        4: {
            1: ("Onboard Successfully", "Complete onboarding, understand codebase, ship first feature", "career", 0, 480),
            2: ("Lead Small Project", "Take ownership of a feature or small project", "career", 0, 480),
            3: ("Earn Advanced Certification", "Complete professional-level certification", "certification", 300, 60),
            4: ("Prepare for Promotion", "Document achievements, seek feedback, set growth goals", "career", 0, 40),
        },
        5: {
            1: ("Achieve Senior Promotion", "Demonstrate senior-level impact and get promoted", "career", 0, 480),
            2: ("Mentor Junior Developers", "Guide 2-3 junior team members", "skill", 0, 40),
            3: ("Lead Major Initiative", "Own and deliver a significant project", "career", 0, 480),
            4: ("Industry Recognition", "Speak at meetup or publish technical content", "networking", 200, 60),
        },
        6: {
            1: ("Strategic Technical Leadership", "Influence technical direction of team/org", "career", 0, 480),
            2: ("Build External Presence", "Conference speaking or open source leadership", "networking", 500, 80),
            3: ("Mentor Future Leaders", "Develop leadership skills in team members", "skill", 0, 40),
            4: ("Evaluate Next Steps", "Assess career trajectory - IC track vs management", "career", 0, 20),
        }
    }
    
    template = milestones_template.get(year, milestones_template[5])
    title, desc, type_, cost, hours = template.get(quarter, ("Continue Growth", "Focus on professional development", "skill", 0, 40))
    
    # Adjust for path type
    if path_type == "conservative":
        hours = int(hours * 0.8)
    elif path_type == "ambitious":
        hours = int(hours * 1.2)
    
    return YearMilestone(
        quarter=quarter,
        title=title,
        description=desc,
        type=type_,
        estimated_cost=cost,
        estimated_hours=hours,
    )
