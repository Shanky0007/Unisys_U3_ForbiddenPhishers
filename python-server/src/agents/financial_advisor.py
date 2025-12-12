"""
Node E: FinancialAdvisor Agent
The ROI Calculator - Calculates cost of roadmap vs potential earnings
Uses structured output for reliable data extraction
"""

import time
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from ..models.state import (
    CareerSimulationState,
    FinancialAnalysis,
    YearlyFinancials,
    CostBreakdown,
)
from .base import get_llm


# Structured output models for LLM response
class CostItemOutput(BaseModel):
    """A single cost item."""
    item_name: str = Field(description="Name of the cost item")
    amount: float = Field(description="Cost amount in USD")
    category: str = Field(description="Category: education, certification, tools, living, opportunity")
    is_recurring: bool = Field(description="Whether this is a recurring cost")
    frequency: str = Field(description="Frequency: one-time, monthly, yearly")


class YearlyFinancialsOutput(BaseModel):
    """Financial breakdown for a single year."""
    year_number: int = Field(description="Year number (1, 2, 3, etc.)")
    total_investment: float = Field(description="Total investment for this year in USD")
    costs: list[CostItemOutput] = Field(description="Detailed cost breakdown with 3-6 items")
    expected_income: float = Field(description="Expected income for this year")
    income_source: str = Field(description="Source: None, Internship, Part-time, Full-time, Freelance")
    net_cash_flow: float = Field(description="Net cash flow (income - costs)")
    cumulative_investment: float = Field(description="Running total of all investments")
    cumulative_income: float = Field(description="Running total of all income")


class FinancialAnalysisOutput(BaseModel):
    """Complete financial analysis output."""
    total_investment_required: float = Field(description="Total investment needed over all years")
    investment_reasoning: str = Field(description="Detailed explanation of why this investment is needed and what it covers")
    yearly_financials: list[YearlyFinancialsOutput] = Field(description="Financial breakdown for each year")
    break_even_year: int = Field(description="Year when cumulative income exceeds cumulative investment")
    break_even_month: int = Field(description="Month within break-even year (1-12)")
    break_even_reasoning: str = Field(description="Explanation of why break-even occurs at this point")
    five_year_roi: float = Field(description="Return on investment percentage after 5 years")
    five_year_roi_reasoning: str = Field(description="How this ROI was calculated and what affects it")
    ten_year_projected_earnings: float = Field(description="Projected total earnings over 10 years")
    affordability_rating: str = Field(description="Rating: comfortable, feasible, stretch, unfeasible")
    affordability_reasoning: str = Field(description="Why this affordability rating was assigned")
    affordability_notes: list[str] = Field(description="3-5 notes about affordability")
    cost_saving_opportunities: list[str] = Field(description="3-5 ways to reduce costs")
    funding_options: list[str] = Field(description="3-5 funding options like scholarships, loans, etc.")
    meets_min_salary_target: bool = Field(description="Whether the path meets user's minimum salary target")
    years_to_target_salary: int = Field(description="Years until reaching target salary")
    salary_target_reasoning: str = Field(description="Explanation of salary progression to target")
    salary_milestones: list[dict] = Field(
        default_factory=list, 
        description="List of salary milestone objects. Each object MUST have: year (int), expected_salary (int), role (str), reasoning (str). Example: [{\"year\": 1, \"expected_salary\": 0, \"role\": \"Student\", \"reasoning\": \"Still in education phase\"}, {\"year\": 2, \"expected_salary\": 45000, \"role\": \"Junior Developer\", \"reasoning\": \"Entry-level position\"}]"
    )
    investment_by_category: dict = Field(
        default_factory=dict, 
        description="Dictionary mapping category names to amounts. Example: {\"education\": 15000, \"certifications\": 2000, \"tools\": 1500, \"living_expenses\": 20000}"
    )


FINANCIAL_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial advisor specializing in education ROI and career investment analysis.

Your task is to provide DETAILED financial analysis WITH REASONING including:

1. Total Investment Required - Sum of all costs over the career path WITH EXPLANATION
2. Yearly Financials - For EACH year, provide:
   - 4-6 specific cost items (courses, certifications, tools, books, etc.)
   - Expected income (if any - internships, part-time, full-time)
   - Net cash flow
   - Cumulative totals

3. Break-Even Analysis - When does income exceed investment? EXPLAIN WHY at this point
4. ROI Metrics - 5-year ROI percentage WITH CALCULATION REASONING, 10-year projected earnings
5. Affordability Assessment - Based on user's investment capacity WITH REASONING
6. Cost-Saving Opportunities - At least 3-5 specific suggestions
7. Funding Options - Scholarships, loans, employer sponsorship, etc.
8. Salary Milestones - List expected salary at each year
9. Investment by Category - Breakdown showing how much goes to education, tools, certs, etc.

Be SPECIFIC with cost estimates:
- Online courses: $50-500 each
- Bootcamps: $5,000-20,000
- Certifications: $150-500 exam fees
- Tools/subscriptions: $20-100/month
- Books/materials: $30-100 each

IMPORTANT: For each major number (total investment, ROI, break-even), provide detailed reasoning explaining:
- How you calculated it
- What factors influenced it
- How it relates to the candidate's specific situation

NEVER leave arrays empty. Provide realistic, detailed breakdowns."""),

    ("human", """Perform a comprehensive financial analysis:

**USER FINANCIAL PROFILE:**
- Investment Capacity: {investment_capacity}
- Has Financial Dependents: {has_dependents}
- Target Minimum Salary: ${target_salary}
- Country: {country}

**CAREER PATH:**
{career_path_summary}

**MARKET SALARY DATA:**
- Entry Level: {entry_salary}
- Mid Level: {mid_salary}
- Senior Level: {senior_salary}

**GAP ANALYSIS SUMMARY:**
- Key Skills to Develop: {skill_gaps}
- Certifications Needed: {cert_gaps}

**TIMELINE:**
- Total Years: {total_years}
- Target Role: {target_role}

Provide detailed financial projections with:
1. Specific cost items for each year
2. Investment reasoning explaining what the money goes toward
3. Break-even reasoning showing when and why income exceeds costs
4. ROI reasoning with calculation methodology
5. Affordability reasoning based on the user's capacity
6. Salary milestones showing progression""")
])


def financial_advisor_node(state: CareerSimulationState) -> dict:
    """
    Node E: FinancialAdvisor
    Calculates the cost of the career roadmap vs potential earnings.
    Uses structured output for reliable data extraction.
    """
    start_time = time.time()
    
    profile = state["career_profile"]
    market = state.get("market_insights")
    timeline = state.get("timeline_simulation")
    gap = state.get("gap_analysis")
    
    # Get the recommended path (or realistic if not available)
    career_path = None
    if timeline:
        if timeline.recommended_path == "conservative" and timeline.conservative_path:
            career_path = timeline.conservative_path
        elif timeline.recommended_path == "ambitious" and timeline.ambitious_path:
            career_path = timeline.ambitious_path
        elif timeline.realistic_path:
            career_path = timeline.realistic_path
    
    # Format career path summary
    career_path_summary = _format_career_path(career_path)
    
    # Get salary data
    entry_salary = "50000 - 80000"
    mid_salary = "80000 - 120000"
    senior_salary = "120000 - 180000"
    
    if market and market.target_roles:
        role = market.target_roles[0]
        if role.salary_range:
            entry_salary = f"{role.salary_range.entry_level_min:.0f} - {role.salary_range.entry_level_max:.0f}"
            mid_salary = f"{role.salary_range.mid_level_min:.0f} - {role.salary_range.mid_level_max:.0f}"
            senior_salary = f"{role.salary_range.senior_level_min:.0f} - {role.salary_range.senior_level_max:.0f}"
    
    # Format gaps
    skill_gaps = "General skill development needed"
    cert_gaps = "Industry certifications"
    if gap:
        if gap.technical_skill_gaps:
            skill_gaps = ", ".join([g.skill_name for g in gap.technical_skill_gaps[:5]])
        if gap.certification_gaps:
            cert_gaps = ", ".join(gap.certification_gaps)
    
    total_years = career_path.total_years if career_path else 5
    target_role = career_path.final_target_role if career_path else "Software Engineer"
    
    # Get LLM with structured output
    llm = get_llm(temperature=0.3)
    
    try:
        structured_llm = llm.with_structured_output(FinancialAnalysisOutput)
        chain = FINANCIAL_ANALYSIS_PROMPT | structured_llm
        
        analysis_output: FinancialAnalysisOutput = chain.invoke({
            "investment_capacity": profile.investment_capacity or "Medium ($5,000 - $15,000)",
            "has_dependents": "Yes" if profile.financial_dependents else "No",
            "target_salary": profile.target_min_salary or 80000,
            "country": profile.current_country or "United States",
            "career_path_summary": career_path_summary,
            "entry_salary": entry_salary,
            "mid_salary": mid_salary,
            "senior_salary": senior_salary,
            "skill_gaps": skill_gaps,
            "cert_gaps": cert_gaps,
            "total_years": total_years,
            "target_role": target_role,
        })
        
        # Convert to FinancialAnalysis model
        financial_analysis = _convert_to_financial_analysis(analysis_output)
        
    except Exception as e:
        # Fallback if structured output fails
        print(f"Structured output failed, using fallback: {e}")
        financial_analysis = _create_fallback_financial_analysis(career_path, profile, gap)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "financial_analysis": financial_analysis,
        "current_node": "financial_advisor",
        "processing_time_ms": {"financial_advisor": processing_time},
    }


def _convert_to_financial_analysis(output: FinancialAnalysisOutput) -> FinancialAnalysis:
    """Convert structured LLM output to FinancialAnalysis model."""
    # Safely handle salary_milestones - convert to proper format if needed
    salary_milestones = []
    if output.salary_milestones:
        for item in output.salary_milestones:
            if isinstance(item, dict):
                salary_milestones.append(item)
            elif isinstance(item, str):
                # Parse string format like "Year 1: $50,000"
                try:
                    parts = item.replace('$', '').replace(',', '').split(':')
                    if len(parts) >= 2:
                        year = int(''.join(filter(str.isdigit, parts[0])))
                        salary = int(float(''.join(filter(lambda c: c.isdigit() or c == '.', parts[1]))))
                        salary_milestones.append({
                            "year": year,
                            "expected_salary": salary,
                            "role": f"Year {year} Role",
                            "reasoning": "Parsed from string format"
                        })
                except:
                    pass
    
    # Safely handle investment_by_category - convert list to dict if needed
    investment_by_category = {}
    if isinstance(output.investment_by_category, dict):
        investment_by_category = output.investment_by_category
    elif isinstance(output.investment_by_category, list):
        for item in output.investment_by_category:
            if isinstance(item, dict) and 'name' in item and 'value' in item:
                investment_by_category[item['name']] = item['value']
            elif isinstance(item, dict) and 'category' in item and 'amount' in item:
                investment_by_category[item['category']] = item['amount']
    
    analysis = FinancialAnalysis(
        total_investment_required=output.total_investment_required,
        investment_reasoning=output.investment_reasoning,
        break_even_year=output.break_even_year,
        break_even_month=output.break_even_month,
        break_even_reasoning=output.break_even_reasoning,
        five_year_roi=output.five_year_roi,
        five_year_roi_reasoning=output.five_year_roi_reasoning,
        ten_year_projected_earnings=output.ten_year_projected_earnings,
        affordability_rating=output.affordability_rating,
        affordability_reasoning=output.affordability_reasoning,
        affordability_notes=output.affordability_notes,
        cost_saving_opportunities=output.cost_saving_opportunities,
        funding_options=output.funding_options,
        meets_min_salary_target=output.meets_min_salary_target,
        years_to_target_salary=output.years_to_target_salary,
        salary_target_reasoning=output.salary_target_reasoning,
        salary_milestones=salary_milestones,
        investment_by_category=investment_by_category,
    )
    
    # Convert yearly financials
    for yf in output.yearly_financials:
        yearly = YearlyFinancials(
            year_number=yf.year_number,
            total_investment=yf.total_investment,
            expected_income=yf.expected_income,
            income_source=yf.income_source,
            net_cash_flow=yf.net_cash_flow,
            cumulative_investment=yf.cumulative_investment,
            cumulative_income=yf.cumulative_income,
        )
        
        # Convert cost breakdown
        for cost in yf.costs:
            yearly.cost_breakdown.append(CostBreakdown(
                item_name=cost.item_name,
                amount=cost.amount,
                category=cost.category,
                is_recurring=cost.is_recurring,
                frequency=cost.frequency,
            ))
        
        analysis.yearly_financials.append(yearly)
    
    return analysis


def _create_fallback_financial_analysis(career_path, profile, gap) -> FinancialAnalysis:
    """Create a fallback financial analysis when LLM fails."""
    total_years = career_path.total_years if career_path else 5
    
    analysis = FinancialAnalysis(
        total_investment_required=15000.0,
        break_even_year=2,
        break_even_month=8,
        five_year_roi=450.0,
        ten_year_projected_earnings=850000.0,
        affordability_rating="feasible",
        affordability_notes=[
            "Total investment is within typical range for career transition",
            "Early income from internships can offset some costs",
            "Consider employer tuition reimbursement programs",
            "Investment pays back within 2-3 years of full-time employment"
        ],
        cost_saving_opportunities=[
            "Use free resources: freeCodeCamp, The Odin Project, CS50",
            "Look for scholarship programs from tech companies",
            "Take advantage of free tiers: AWS, GCP, Azure",
            "Use student discounts for tools and software",
            "Join study groups to share resource costs"
        ],
        funding_options=[
            "Income Share Agreements (ISAs) - Pay after getting job",
            "Tech company scholarships (Google, Meta, AWS)",
            "Government workforce development grants",
            "Low-interest student loans",
            "Employer tuition reimbursement programs"
        ],
        meets_min_salary_target=True,
        years_to_target_salary=3,
    )
    
    # Create yearly financials
    cumulative_investment = 0
    cumulative_income = 0
    
    for year in range(1, total_years + 1):
        if year == 1:
            costs = [
                ("Online Courses (Coursera, Udemy)", 500, "education", False, "one-time"),
                ("Books and Learning Materials", 200, "education", False, "one-time"),
                ("Cloud Platform Credits", 100, "tools", True, "yearly"),
                ("Development Tools", 150, "tools", True, "yearly"),
                ("Certification Prep Materials", 250, "certification", False, "one-time"),
            ]
            total_invest = sum(c[1] for c in costs)
            income = 0
            income_source = "None"
        elif year == 2:
            costs = [
                ("Advanced Courses", 400, "education", False, "one-time"),
                ("AWS Certification Exam", 150, "certification", False, "one-time"),
                ("Professional Tools", 200, "tools", True, "yearly"),
                ("Networking Events", 100, "networking", False, "one-time"),
            ]
            total_invest = sum(c[1] for c in costs)
            income = 25000  # Internship
            income_source = "Internship"
        elif year == 3:
            costs = [
                ("Professional Certification", 300, "certification", False, "one-time"),
                ("Conference Attendance", 500, "networking", False, "one-time"),
                ("Premium Tools", 300, "tools", True, "yearly"),
            ]
            total_invest = sum(c[1] for c in costs)
            income = 65000
            income_source = "Full-time"
        elif year == 4:
            costs = [
                ("Advanced Training", 800, "education", False, "one-time"),
                ("Leadership Development", 400, "skill", False, "one-time"),
            ]
            total_invest = sum(c[1] for c in costs)
            income = 85000
            income_source = "Full-time"
        else:
            costs = [
                ("Continued Education", 500, "education", False, "one-time"),
                ("Industry Certifications", 400, "certification", False, "one-time"),
            ]
            total_invest = sum(c[1] for c in costs)
            income = 110000
            income_source = "Full-time"
        
        cumulative_investment += total_invest
        cumulative_income += income
        
        yearly = YearlyFinancials(
            year_number=year,
            total_investment=total_invest,
            expected_income=income,
            income_source=income_source,
            net_cash_flow=income - total_invest,
            cumulative_investment=cumulative_investment,
            cumulative_income=cumulative_income,
        )
        
        for item, amount, cat, recurring, freq in costs:
            yearly.cost_breakdown.append(CostBreakdown(
                item_name=item,
                amount=amount,
                category=cat,
                is_recurring=recurring,
                frequency=freq,
            ))
        
        analysis.yearly_financials.append(yearly)
    
    analysis.total_investment_required = cumulative_investment
    
    return analysis


def _format_career_path(career_path) -> str:
    """Format career path for prompt."""
    if not career_path:
        return """Standard 5-year career path:
Year 1: Skill building and foundational learning
Year 2: Internship and practical experience
Year 3: Entry-level position
Year 4: Growth and advancement
Year 5: Senior role achievement"""
    
    lines = [f"**{career_path.path_label}** ({career_path.total_years} years)"]
    lines.append(f"Final Target: {career_path.final_target_role}")
    lines.append(f"Expected Final Salary: ${career_path.final_expected_salary:,.0f}")
    lines.append("")
    
    for year in career_path.yearly_plans:
        lines.append(f"**{year.year_label}**")
        lines.append(f"- Focus: {year.primary_focus}")
        if year.expected_role:
            lines.append(f"- Role: {year.expected_role}")
        if year.expected_salary_range:
            lines.append(f"- Salary: {year.expected_salary_range}")
        if year.milestones:
            lines.append("- Key Activities:")
            for m in year.milestones[:2]:
                lines.append(f"  * {m.title} (${m.estimated_cost}, {m.estimated_hours}h)")
        lines.append("")
    
    return "\n".join(lines)
