"""
Career Path Simulator - LangGraph Workflow
Two-Stage Process:
1. Stage 1 (Matching): Profile → ProfileParser → CareerMatcher → PAUSE (returns 3 career fits)
2. Stage 2 (Simulation): Selected Career → MarketScout → GapAnalyst → Timeline/Financial/Risk → Dashboard
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

from .models.state import (
    CareerSimulationState,
    CareerMatcherResult,
    CareerFit,
    CareerFitReasoning,
    create_initial_state,
)
from .models.career_profile import CareerProfile
from .agents.profile_parser import profile_parser_node
from .agents.career_matcher import career_matcher_node, CareerMatcherOutput
from .agents.market_scout import market_scout_node
from .agents.gap_analyst import gap_analyst_node
from .agents.timeline_simulator import timeline_simulator_node
from .agents.financial_advisor import financial_advisor_node
from .agents.risk_assessor import risk_assessor_node
from .agents.dashboard_formatter import dashboard_formatter_node


# ============ Stage 1: Career Matching ============

def build_career_matching_graph() -> StateGraph:
    """
    Build Stage 1 graph: Profile analysis and career matching.
    
    Flow:
    START → ProfileParser → CareerMatcher → END
    
    This graph PAUSES after returning 3 career fits.
    User must select one before Stage 2 begins.
    """
    workflow = StateGraph(CareerSimulationState)
    
    # Add nodes
    workflow.add_node("profile_parser", profile_parser_node)
    workflow.add_node("career_matcher", _career_matcher_wrapper)
    
    # Add edges
    workflow.add_edge(START, "profile_parser")
    workflow.add_edge("profile_parser", "career_matcher")
    workflow.add_edge("career_matcher", END)
    
    return workflow


def _career_matcher_wrapper(state: CareerSimulationState) -> dict:
    """Wrapper to convert CareerMatcherOutput to CareerMatcherResult."""
    from .agents.career_matcher import career_matcher_node
    
    result = career_matcher_node(state)
    
    # Convert the output to state-compatible format
    matcher_output = result.get("career_fits")
    if matcher_output and isinstance(matcher_output, CareerMatcherOutput):
        # Convert Pydantic models to state models
        career_fits = []
        for fit in matcher_output.career_fits:
            career_fit = CareerFit(
                rank=fit.rank,
                career_title=fit.career_title,
                career_field=fit.career_field,
                overall_fit_score=fit.overall_fit_score,
                skill_fit_score=fit.skill_fit_score,
                interest_fit_score=fit.interest_fit_score,
                market_fit_score=fit.market_fit_score,
                personality_fit_score=fit.personality_fit_score,
                tagline=fit.tagline,
                reasoning=CareerFitReasoning(
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
            )
            career_fits.append(career_fit)
        
        matcher_result = CareerMatcherResult(
            analysis_summary=matcher_output.analysis_summary,
            profile_highlights=matcher_output.profile_highlights,
            career_fits=career_fits,
            methodology_explanation=matcher_output.methodology_explanation,
            confidence_level=matcher_output.confidence_level,
            confidence_reasoning=matcher_output.confidence_reasoning,
        )
        
        return {
            "career_matcher_result": matcher_result,
            "stage": "matching_complete",
            "current_node": result.get("current_node", "career_matcher"),
            "processing_time_ms": result.get("processing_time_ms", {}),
        }
    
    return result


# ============ Stage 2: Full Simulation ============

def should_suggest_alternatives(state: CareerSimulationState) -> Literal["suggest_alternatives", "simulate_timeline"]:
    """
    Conditional edge: Route based on gap severity.
    If gap > 80%, suggest alternatives. Otherwise, proceed.
    """
    if state.get("should_suggest_alternatives"):
        return "suggest_alternatives"
    return "simulate_timeline"


def alternative_path_suggester_node(state: CareerSimulationState) -> dict:
    """
    Optional node: Suggests alternative careers when gap is too large.
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from .agents.base import get_llm
    from .models.state import AlternativeCareer
    import re
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a career counselor. When a target career has a very high gap score (>80%), 
suggest 3-5 alternative careers that are more achievable while still aligned with the user's interests.

For each alternative, provide detailed reasoning about:
1. Why this is a better fit given current skills
2. How it relates to original interests  
3. The realistic path to entry
4. Expected challenges and how to overcome them"""),
        
        ("human", """Gap score: {gap_score}/100 for {target_career}

Profile: {profile_summary}
Skills: {current_skills}
Original Target: {target_roles} in {target_fields}

Key Gaps:
{key_gaps}

Suggest 3-5 alternatives with detailed reasoning:

ALTERNATIVE 1:
- ROLE: [Role]
- FIELD: [Field]
- SIMILARITY: [0-100%]
- REASONING: [Detailed 2-3 sentence explanation]
- GAP SCORE: [0-100]
- TRANSITION: [Easy/Moderate/Challenging]
- PATH TO ENTRY: [Brief roadmap]""")
    ])
    
    profile = state["career_profile"]
    normalized = state.get("normalized_profile")
    gap = state.get("gap_analysis")
    selected = state.get("selected_career")
    
    key_gaps = []
    if gap:
        if gap.education_gap:
            key_gaps.append(f"Education: {gap.education_gap}")
        for skill in gap.technical_skill_gaps[:3]:
            key_gaps.append(f"Skill: {skill.skill_name} ({skill.gap_severity}/100)")
        for bottleneck in gap.critical_bottlenecks[:2]:
            key_gaps.append(f"Bottleneck: {bottleneck}")
    
    llm = get_llm(temperature=0.5)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({
        "gap_score": gap.overall_gap_score if gap else 85,
        "target_career": selected.career_title if selected else "Target Role",
        "profile_summary": normalized.profile_summary if normalized else "Not available",
        "current_skills": str(normalized.combined_technical_skills) if normalized else "Not assessed",
        "target_roles": selected.career_title if selected else ", ".join(profile.specific_roles) if profile.specific_roles else "Not specified",
        "target_fields": selected.career_field if selected else ", ".join(profile.target_career_fields) if profile.target_career_fields else "Not specified",
        "key_gaps": "\n".join(key_gaps) if key_gaps else "Multiple significant gaps",
    })
    
    alternatives = _parse_alternatives(response)
    
    warnings = [
        f"High gap score ({gap.overall_gap_score:.0f}/100) detected for {selected.career_title if selected else 'target career'}. "
        "Alternative career paths have been suggested alongside your original target."
    ]
    
    return {
        "alternative_careers": alternatives,
        "warnings": warnings,
        "current_node": "alternative_suggester",
    }


def _parse_alternatives(response: str) -> list:
    """Parse alternative career suggestions from LLM response."""
    from .models.state import AlternativeCareer
    import re
    
    alternatives = []
    sections = re.split(r'ALTERNATIVE\s*\d+:', response, flags=re.IGNORECASE)
    
    for section in sections[1:]:
        alt = AlternativeCareer(
            role_title="",
            field="",
            similarity_to_original=50.0,
            gap_score=50.0,
            transition_difficulty="Moderate",
        )
        
        lines = section.split("\n")
        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue
            
            key, value = line.split(":", 1)
            key = key.strip().upper().lstrip("-")
            value = value.strip().strip("[]")
            
            if "ROLE" in key:
                alt.role_title = value
            elif "FIELD" in key:
                alt.field = value
            elif "SIMILARITY" in key:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    alt.similarity_to_original = float(numbers[0])
            elif "REASONING" in key:
                alt.reasons_suggested = [r.strip() for r in value.split(".") if r.strip()]
            elif "GAP" in key and "SCORE" in key:
                numbers = re.findall(r'\d+(?:\.\d+)?', value)
                if numbers:
                    alt.gap_score = float(numbers[0])
            elif "TRANSITION" in key:
                if value in ["Easy", "Moderate", "Challenging"]:
                    alt.transition_difficulty = value
        
        if alt.role_title:
            alternatives.append(alt)
    
    return alternatives[:5]


def build_simulation_graph() -> StateGraph:
    """
    Build Stage 2 graph: Full career simulation for selected career.
    
    Flow:
    START → MarketScout → GapAnalyst 
        → Conditional: alternatives or timeline
        → TimelineSimulator → Parallel(Financial, Risk) → Dashboard → END
    """
    workflow = StateGraph(CareerSimulationState)
    
    # Add all nodes
    workflow.add_node("market_scout", market_scout_node)
    workflow.add_node("gap_analyst", gap_analyst_node)
    workflow.add_node("alternative_suggester", alternative_path_suggester_node)
    workflow.add_node("timeline_simulator", timeline_simulator_node)
    workflow.add_node("financial_advisor", financial_advisor_node)
    workflow.add_node("risk_assessor", risk_assessor_node)
    workflow.add_node("dashboard_formatter", dashboard_formatter_node)
    
    # Add edges
    workflow.add_edge(START, "market_scout")
    workflow.add_edge("market_scout", "gap_analyst")
    
    # Conditional edge based on gap severity
    workflow.add_conditional_edges(
        "gap_analyst",
        should_suggest_alternatives,
        {
            "suggest_alternatives": "alternative_suggester",
            "simulate_timeline": "timeline_simulator",
        }
    )
    
    workflow.add_edge("alternative_suggester", "timeline_simulator")
    
    # Parallel execution of financial and risk assessment
    workflow.add_edge("timeline_simulator", "financial_advisor")
    workflow.add_edge("timeline_simulator", "risk_assessor")
    
    # Converge to dashboard
    workflow.add_edge("financial_advisor", "dashboard_formatter")
    workflow.add_edge("risk_assessor", "dashboard_formatter")
    
    workflow.add_edge("dashboard_formatter", END)
    
    return workflow


# ============ Combined Graph (Legacy Support) ============

def build_career_simulator_graph() -> StateGraph:
    """
    Build complete graph for legacy single-stage simulation.
    
    Flow:
    START → ProfileParser → MarketScout → GapAnalyst
        → Conditional → TimelineSimulator → Parallel(Financial, Risk)
        → Dashboard → END
    """
    workflow = StateGraph(CareerSimulationState)
    
    # Add all nodes
    workflow.add_node("profile_parser", profile_parser_node)
    workflow.add_node("market_scout", market_scout_node)
    workflow.add_node("gap_analyst", gap_analyst_node)
    workflow.add_node("alternative_suggester", alternative_path_suggester_node)
    workflow.add_node("timeline_simulator", timeline_simulator_node)
    workflow.add_node("financial_advisor", financial_advisor_node)
    workflow.add_node("risk_assessor", risk_assessor_node)
    workflow.add_node("dashboard_formatter", dashboard_formatter_node)
    
    # Add edges
    workflow.add_edge(START, "profile_parser")
    workflow.add_edge("profile_parser", "market_scout")
    workflow.add_edge("market_scout", "gap_analyst")
    
    workflow.add_conditional_edges(
        "gap_analyst",
        should_suggest_alternatives,
        {
            "suggest_alternatives": "alternative_suggester",
            "simulate_timeline": "timeline_simulator",
        }
    )
    
    workflow.add_edge("alternative_suggester", "timeline_simulator")
    workflow.add_edge("timeline_simulator", "financial_advisor")
    workflow.add_edge("timeline_simulator", "risk_assessor")
    workflow.add_edge("financial_advisor", "dashboard_formatter")
    workflow.add_edge("risk_assessor", "dashboard_formatter")
    workflow.add_edge("dashboard_formatter", END)
    
    return workflow


# ============ Graph Compilation ============

def compile_career_matching():
    """Compile Stage 1 graph."""
    workflow = build_career_matching_graph()
    return workflow.compile()


def compile_career_simulation():
    """Compile Stage 2 graph."""
    workflow = build_simulation_graph()
    return workflow.compile()


def compile_career_simulator():
    """Compile legacy combined graph."""
    workflow = build_career_simulator_graph()
    return workflow.compile()


# ============ Execution Functions ============

def run_career_matching(profile_data: dict) -> CareerSimulationState:
    """
    Stage 1: Run career matching to get top 3 fits.
    
    Args:
        profile_data: Dictionary containing CareerProfile fields
        
    Returns:
        State with career_matcher_result containing 3 career fits
    """
    profile = CareerProfile(**profile_data)
    initial_state = create_initial_state(profile)
    
    graph = compile_career_matching()
    result = graph.invoke(initial_state)
    
    return result


async def run_career_matching_async(profile_data: dict) -> CareerSimulationState:
    """Stage 1 async: Get top 3 career fits."""
    profile = CareerProfile(**profile_data)
    initial_state = create_initial_state(profile)
    
    graph = compile_career_matching()
    result = await graph.ainvoke(initial_state)
    
    return result


def run_career_simulation_for_selected(state: CareerSimulationState, career_index: int) -> CareerSimulationState:
    """
    Stage 2: Run full simulation for selected career.
    
    Args:
        state: State from Stage 1 with career_matcher_result
        career_index: Index of selected career (0, 1, or 2)
        
    Returns:
        Complete simulation state with all analysis
    """
    # Get the selected career
    matcher_result = state.get("career_matcher_result")
    if not matcher_result or not matcher_result.career_fits:
        raise ValueError("No career fits available. Run Stage 1 first.")
    
    if career_index < 0 or career_index >= len(matcher_result.career_fits):
        raise ValueError(f"Invalid career index: {career_index}")
    
    selected_career = matcher_result.career_fits[career_index]
    
    # Update state with selection
    state["selected_career_index"] = career_index
    state["selected_career"] = selected_career
    state["stage"] = "simulation"
    
    # Update profile with selected career as target
    profile = state["career_profile"]
    profile.specific_roles = [selected_career.career_title]
    profile.target_career_fields = [selected_career.career_field]
    
    # Run Stage 2
    graph = compile_career_simulation()
    result = graph.invoke(state)
    
    return result


async def run_career_simulation_for_selected_async(
    state: CareerSimulationState, 
    career_index: int
) -> CareerSimulationState:
    """Stage 2 async: Full simulation for selected career."""
    matcher_result = state.get("career_matcher_result")
    if not matcher_result or not matcher_result.career_fits:
        raise ValueError("No career fits available. Run Stage 1 first.")
    
    if career_index < 0 or career_index >= len(matcher_result.career_fits):
        raise ValueError(f"Invalid career index: {career_index}")
    
    selected_career = matcher_result.career_fits[career_index]
    
    state["selected_career_index"] = career_index
    state["selected_career"] = selected_career
    state["stage"] = "simulation"
    
    profile = state["career_profile"]
    profile.specific_roles = [selected_career.career_title]
    profile.target_career_fields = [selected_career.career_field]
    
    graph = compile_career_simulation()
    result = await graph.ainvoke(state)
    
    return result


# Legacy functions
def run_career_simulation(profile_data: dict) -> CareerSimulationState:
    """Legacy: Run complete single-stage simulation."""
    profile = CareerProfile(**profile_data)
    initial_state = create_initial_state(profile)
    
    graph = compile_career_simulator()
    result = graph.invoke(initial_state)
    
    return result


async def run_career_simulation_async(profile_data: dict) -> CareerSimulationState:
    """Legacy async: Run complete single-stage simulation."""
    profile = CareerProfile(**profile_data)
    initial_state = create_initial_state(profile)
    
    graph = compile_career_simulator()
    result = await graph.ainvoke(initial_state)
    
    return result


# Export compiled graphs
career_simulator = compile_career_simulator()
career_matcher = compile_career_matching()
career_simulation = compile_career_simulation()
