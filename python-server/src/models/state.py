"""
Graph State Schema
Defines the shared state that flows through the LangGraph workflow
"""

from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal
from datetime import datetime
import operator

from .career_profile import (
    CareerProfile,
    NormalizedProfile,
    MarketInsights,
)


class SkillGap(BaseModel):
    """Individual skill gap identified"""
    skill_name: str
    current_level: str  # None, Basic, Intermediate, Advanced
    required_level: str
    gap_severity: float  # 0-100
    estimated_time_to_close: str  # "3 months", "1 year"
    recommended_resources: list[str] = Field(default_factory=list)
    reasoning: str = ""  # Why this gap exists and matters
    priority: str = "medium"  # high, medium, low
    learning_path: list[str] = Field(default_factory=list)  # Step-by-step path to close gap


class GapAnalysis(BaseModel):
    """Complete gap analysis between user profile and market requirements"""
    overall_gap_score: float = 0.0  # 0-100, where 100 is maximum gap
    gap_category: str = "manageable"  # "minimal", "manageable", "significant", "severe"
    analysis_reasoning: str = ""  # Overall reasoning for the gap score
    
    # Skill gaps
    technical_skill_gaps: list[SkillGap] = Field(default_factory=list)
    soft_skill_gaps: list[SkillGap] = Field(default_factory=list)
    
    # Education gaps
    education_gap: Optional[str] = None  # e.g., "Requires Master's degree"
    education_gap_reasoning: str = ""
    certification_gaps: list[str] = Field(default_factory=list)
    
    # Experience gaps
    experience_gap_years: float = 0.0
    experience_gap_reasoning: str = ""
    
    # Bottlenecks
    critical_bottlenecks: list[str] = Field(default_factory=list)
    timeline_bottlenecks: list[str] = Field(default_factory=list)
    
    # Strengths (things user already has)
    existing_strengths: list[str] = Field(default_factory=list)
    competitive_advantages: list[str] = Field(default_factory=list)
    
    # Friction points (psychometric mismatches)
    personality_frictions: list[str] = Field(default_factory=list)
    stress_risks: list[str] = Field(default_factory=list)
    
    # Actionable insights
    top_priorities: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list)  # Things that can be done quickly


class YearMilestone(BaseModel):
    """Milestone within a year of the timeline"""
    quarter: int  # 1-4
    title: str
    description: str
    type: str  # "education", "skill", "career", "certification", "project"
    estimated_cost: float = 0.0
    estimated_hours: int = 0
    resources: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    reasoning: str = ""  # Why this milestone is important
    dependencies: list[str] = Field(default_factory=list)  # What must be done first
    risk_if_skipped: str = ""  # What happens if you skip this


class YearPlan(BaseModel):
    """Single year in the career timeline"""
    year_number: int  # 1, 2, 3, 4, 5, 6
    year_label: str  # "Year 1: Foundation Building"
    phase: str  # "Preparation", "Transition", "Growth"
    phase_reasoning: str = ""  # Why this phase at this time
    
    # Key activities
    primary_focus: str
    focus_reasoning: str = ""  # Why this is the focus
    milestones: list[YearMilestone] = Field(default_factory=list)
    
    # Expected outcomes
    expected_role: Optional[str] = None
    expected_salary_range: Optional[str] = None
    key_skills_acquired: list[str] = Field(default_factory=list)
    
    # Progress metrics
    skill_progress_target: dict = Field(default_factory=dict)  # {"Python": 80, "ML": 60}
    
    # Risks and buffers
    potential_setbacks: list[str] = Field(default_factory=list)
    buffer_time_weeks: int = 0
    risk_mitigation: list[str] = Field(default_factory=list)
    
    # Summary
    year_summary: str = ""
    success_indicators: list[str] = Field(default_factory=list)


class CareerPath(BaseModel):
    """Complete career path simulation"""
    path_type: str  # "conservative", "realistic", "ambitious"
    path_label: str  # "The Steady Climb", "The Fast Track"
    
    total_years: int = 5
    yearly_plans: list[YearPlan] = Field(default_factory=list)
    
    # Target outcomes
    final_target_role: str = ""
    final_expected_salary: float = 0.0
    
    # Key milestones summary
    major_milestones: list[str] = Field(default_factory=list)
    
    # Path-specific notes
    assumptions: list[str] = Field(default_factory=list)
    key_decision_points: list[str] = Field(default_factory=list)


class TimelineSimulation(BaseModel):
    """Complete timeline simulation with multiple paths"""
    conservative_path: Optional[CareerPath] = None
    realistic_path: Optional[CareerPath] = None
    ambitious_path: Optional[CareerPath] = None
    
    # Recommended path
    recommended_path: str = "realistic"  # Which path is recommended
    recommendation_reason: str = ""
    
    # Vibe check results (psychometric alignment)
    vibe_check_warnings: list[str] = Field(default_factory=list)
    alignment_score: float = 0.0  # How well the paths align with user preferences


class CostBreakdown(BaseModel):
    """Breakdown of costs for a specific item"""
    item_name: str
    category: str  # "education", "certification", "tools", "living"
    amount: float
    currency: str = "USD"
    is_recurring: bool = False
    frequency: Optional[str] = None  # "monthly", "yearly", "one-time"
    notes: Optional[str] = None


class YearlyFinancials(BaseModel):
    """Financial projection for a single year"""
    year_number: int
    
    # Costs
    total_investment: float = 0.0
    cost_breakdown: list[CostBreakdown] = Field(default_factory=list)
    
    # Income
    expected_income: float = 0.0
    income_source: str = ""  # "Internship", "Part-time", "Full-time job"
    
    # Net position
    net_cash_flow: float = 0.0
    cumulative_investment: float = 0.0
    cumulative_income: float = 0.0


class FinancialAnalysis(BaseModel):
    """Complete financial analysis of the career path"""
    # Cost analysis
    total_investment_required: float = 0.0
    investment_reasoning: str = ""  # Why this amount
    yearly_financials: list[YearlyFinancials] = Field(default_factory=list)
    
    # ROI metrics
    break_even_year: int = 0  # Year when cumulative income > cumulative investment
    break_even_month: int = 0
    break_even_reasoning: str = ""
    five_year_roi: float = 0.0  # Percentage
    five_year_roi_reasoning: str = ""
    ten_year_projected_earnings: float = 0.0
    
    # Salary progression
    salary_milestones: list[dict] = Field(default_factory=list)  # [{year: 1, salary: 60000, reason: "entry level"}]
    
    # Affordability assessment
    affordability_rating: str = "feasible"  # "comfortable", "feasible", "stretch", "unfeasible"
    affordability_reasoning: str = ""
    affordability_notes: list[str] = Field(default_factory=list)
    
    # Recommendations
    cost_saving_opportunities: list[str] = Field(default_factory=list)
    funding_options: list[str] = Field(default_factory=list)
    
    # Comparison with targets
    meets_min_salary_target: bool = False
    years_to_target_salary: int = 0
    salary_target_reasoning: str = ""
    
    # Investment breakdown by category
    investment_by_category: dict = Field(default_factory=dict)  # {"education": 10000, "tools": 2000}


class RiskFactor(BaseModel):
    """Individual risk factor in career path"""
    factor_name: str
    category: str  # "market", "personal", "financial", "technical"
    severity: str  # "low", "medium", "high", "critical"
    probability: float  # 0-100
    impact_description: str
    reasoning: str = ""  # Why this is a risk
    mitigation_strategies: list[str] = Field(default_factory=list)
    early_warning_signs: list[str] = Field(default_factory=list)  # Signs this risk is materializing


class RiskAssessment(BaseModel):
    """Complete risk assessment for career path"""
    # Overall success probability
    success_probability_score: float = 0.0  # 0-100
    success_reasoning: str = ""  # Why this probability
    confidence_interval: str = ""  # "70-85%"
    
    # Risk breakdown
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    
    # Category scores with reasoning
    market_risk_score: float = 0.0
    market_risk_reasoning: str = ""
    personal_risk_score: float = 0.0
    personal_risk_reasoning: str = ""
    financial_risk_score: float = 0.0
    financial_risk_reasoning: str = ""
    technical_risk_score: float = 0.0
    technical_risk_reasoning: str = ""
    
    # Factors affecting success
    positive_factors: list[str] = Field(default_factory=list)
    negative_factors: list[str] = Field(default_factory=list)
    key_opportunities: list[str] = Field(default_factory=list)
    key_concerns: list[str] = Field(default_factory=list)
    
    # Comparative analysis
    compared_to_average: str = ""  # "Above average", "Average", "Below average"
    comparison_reasoning: str = ""
    peer_success_rate: float = 0.0  # What % of similar profiles succeed
    
    # Recommendations
    risk_mitigation_plan: list[str] = Field(default_factory=list)
    contingency_plans: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    
    # Scenario analysis
    best_case_scenario: str = ""
    worst_case_scenario: str = ""
    most_likely_scenario: str = ""


class DashboardMilestone(BaseModel):
    """Milestone formatted for frontend visualization"""
    id: str
    title: str
    description: str
    year: int
    quarter: int
    type: str
    status: str = "pending"  # "pending", "in_progress", "completed"
    dependencies: list[str] = Field(default_factory=list)
    position: dict = Field(default_factory=dict)  # {x: 0, y: 0} for React Flow


class SkillNode(BaseModel):
    """Skill node for skill tree visualization"""
    id: str
    name: str
    current_level: int  # 0-5
    target_level: int  # 0-5
    category: str
    prerequisites: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    estimated_time: str = ""


class ChartDataPoint(BaseModel):
    """Data point for charts"""
    label: str
    value: float
    category: Optional[str] = None


class DashboardData(BaseModel):
    """Formatted data for frontend dashboard"""
    # Roadmap visualization (React Flow)
    milestones: list[DashboardMilestone] = Field(default_factory=list)
    milestone_connections: list[dict] = Field(default_factory=list)
    
    # Skill tree
    skill_nodes: list[SkillNode] = Field(default_factory=list)
    
    # Charts data (Recharts)
    salary_progression: list[dict] = Field(default_factory=list)  # Multi-line chart data
    cost_vs_income: list[dict] = Field(default_factory=list)
    skill_radar: list[dict] = Field(default_factory=list)  # Radar chart data
    risk_breakdown: list[dict] = Field(default_factory=list)  # Pie chart data
    gap_analysis_chart: list[dict] = Field(default_factory=list)  # Bar chart for gaps
    timeline_progress: list[dict] = Field(default_factory=list)  # Gantt-style data
    investment_breakdown: list[dict] = Field(default_factory=list)  # Pie chart for costs
    monthly_projection: list[dict] = Field(default_factory=list)  # Detailed monthly data
    
    success_probability_gauge: float = 0.0
    
    # Summary cards
    summary_stats: dict = Field(default_factory=dict)
    key_metrics: list[dict] = Field(default_factory=list)  # [{title, value, change, icon}]
    
    # Timeline data
    timeline_events: list[dict] = Field(default_factory=list)
    
    # Reasoning sections for dashboard
    key_insights: list[dict] = Field(default_factory=list)  # [{title, insight, reasoning, type}]
    decision_rationale: list[dict] = Field(default_factory=list)  # [{decision, why, impact}]
    
    # Recommendations panel
    top_recommendations: list[str] = Field(default_factory=list)
    immediate_actions: list[dict] = Field(default_factory=list)  # [{action, priority, timeframe, impact}]
    
    # Risk indicators
    risk_indicators: list[dict] = Field(default_factory=list)
    
    # Comparison data
    path_comparison: list[dict] = Field(default_factory=list)  # Compare conservative/realistic/ambitious
    
    # Selected career info for context
    selected_career_summary: dict = Field(default_factory=dict)


class AlternativeCareer(BaseModel):
    """Alternative career suggestion when gap is too large"""
    role_title: str
    field: str
    similarity_to_original: float  # 0-100
    reasons_suggested: list[str] = Field(default_factory=list)
    gap_score: float  # Lower is better
    transition_difficulty: str  # "Easy", "Moderate", "Challenging"


# ============ Career Matcher Models (Stage 1) ============

class CareerFitReasoning(BaseModel):
    """Detailed reasoning for why a career is a good fit"""
    strengths_alignment: list[str] = Field(default_factory=list)
    interest_match: list[str] = Field(default_factory=list)
    skill_transferability: list[str] = Field(default_factory=list)
    growth_potential_reasons: list[str] = Field(default_factory=list)
    market_demand_reasons: list[str] = Field(default_factory=list)
    potential_challenges: list[str] = Field(default_factory=list)
    why_now: str = ""


class CareerFit(BaseModel):
    """Single career fit recommendation with comprehensive reasoning"""
    rank: int = 1
    career_title: str = ""
    career_field: str = ""
    
    # Fit scores
    overall_fit_score: float = 0.0
    skill_fit_score: float = 0.0
    interest_fit_score: float = 0.0
    market_fit_score: float = 0.0
    personality_fit_score: float = 0.0
    
    # Description
    tagline: str = ""
    
    # Detailed reasoning
    reasoning: CareerFitReasoning = Field(default_factory=CareerFitReasoning)
    
    # Quick facts
    typical_salary_range: str = ""
    time_to_entry: str = ""
    difficulty_level: str = "Moderate"
    
    # Key highlights
    top_3_reasons: list[str] = Field(default_factory=list)
    key_skills_needed: list[str] = Field(default_factory=list)
    immediate_next_steps: list[str] = Field(default_factory=list)


class CareerMatcherResult(BaseModel):
    """Complete result from career matcher (Stage 1)"""
    analysis_summary: str = ""
    profile_highlights: list[str] = Field(default_factory=list)
    career_fits: list[CareerFit] = Field(default_factory=list)
    methodology_explanation: str = ""
    confidence_level: str = "Medium"
    confidence_reasoning: str = ""


# ============ Reasoning Models for Detailed Analysis ============

class ReasoningPoint(BaseModel):
    """Single reasoning point with explanation"""
    point: str
    explanation: str
    confidence: float = 0.8  # 0-1
    supporting_data: list[str] = Field(default_factory=list)


class DecisionReasoning(BaseModel):
    """Reasoning behind a specific decision or recommendation"""
    decision: str
    reasons_for: list[ReasoningPoint] = Field(default_factory=list)
    reasons_against: list[ReasoningPoint] = Field(default_factory=list)
    conclusion: str = ""
    confidence_score: float = 0.0


def merge_dicts(left: dict | None, right: dict | None) -> dict:
    """Merge two dicts, right takes precedence."""
    if left is None:
        return right or {}
    if right is None:
        return left
    return {**left, **right}


def last_value(left: str | None, right: str | None) -> str:
    """Take the last value for string fields."""
    return right if right else (left or "")


# Using TypedDict for LangGraph state with proper reducer support
from typing import TypedDict


class CareerSimulationState(TypedDict, total=False):
    """
    Main state object for the LangGraph workflow.
    This flows through all nodes and accumulates results.
    
    Two-Stage Process:
    - Stage 1: Profile → CareerMatcher (returns 3 career fits, PAUSES)
    - Stage 2: User selects career → Full simulation (Gap, Timeline, Financial, Risk)
    """
    # Input
    career_profile: CareerProfile
    
    # Stage 1: Career Matching
    career_matcher_result: CareerMatcherResult | None
    selected_career_index: int  # Which of the 3 fits was selected (0, 1, or 2)
    selected_career: CareerFit | None
    stage: str  # "matching" or "simulation"
    
    # Node A: ProfileParser output
    normalized_profile: NormalizedProfile | None
    
    # Node B: MarketScout output
    market_insights: MarketInsights | None
    
    # Node C: GapAnalyst output
    gap_analysis: GapAnalysis | None
    
    # Alternative path (if gap too large)
    alternative_careers: list[AlternativeCareer]
    should_suggest_alternatives: bool
    
    # Node D: TimelineSimulator output
    timeline_simulation: TimelineSimulation | None
    
    # Node E: FinancialAdvisor output
    financial_analysis: FinancialAnalysis | None
    
    # Node F: RiskAssessor output
    risk_assessment: RiskAssessment | None
    
    # Node G: DashboardFormatter output
    dashboard_data: DashboardData | None
    
    # Workflow metadata - Use Annotated for fields that can be updated in parallel
    current_node: Annotated[str, last_value]
    errors: Annotated[list[str], operator.add]
    warnings: Annotated[list[str], operator.add]
    processing_time_ms: Annotated[dict[str, float], merge_dicts]
    
    # Final output
    simulation_complete: bool
    final_report_summary: str


def create_initial_state(profile: CareerProfile) -> CareerSimulationState:
    """Create initial state with default values."""
    return CareerSimulationState(
        career_profile=profile,
        career_matcher_result=None,
        selected_career_index=-1,
        selected_career=None,
        stage="matching",
        normalized_profile=None,
        market_insights=None,
        gap_analysis=None,
        alternative_careers=[],
        should_suggest_alternatives=False,
        timeline_simulation=None,
        financial_analysis=None,
        risk_assessment=None,
        dashboard_data=None,
        current_node="start",
        errors=[],
        warnings=[],
        processing_time_ms={},
        simulation_complete=False,
        final_report_summary="",
    )

