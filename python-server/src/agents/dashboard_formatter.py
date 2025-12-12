"""
Node G: DashboardFormatter Agent
The UI Mapper - Converts simulation data to frontend-ready format with rich visualizations
"""

import time
import uuid
from ..models.state import (
    CareerSimulationState,
    DashboardData,
    DashboardMilestone,
    SkillNode,
)


def dashboard_formatter_node(state: CareerSimulationState) -> dict:
    """
    Node G: DashboardFormatter
    Converts complex simulation data into structured JSON for frontend.
    
    Generates:
    - Milestones for React Flow roadmap
    - Skill tree data structure
    - Multiple chart datasets (salary, cost/income, skills, risks, gaps)
    - Summary statistics with reasoning
    - Key insights and recommendations
    """
    start_time = time.time()
    
    dashboard = DashboardData()
    
    # Format milestones for roadmap visualization
    dashboard.milestones, dashboard.milestone_connections = _format_milestones(state)
    
    # Format skill tree
    dashboard.skill_nodes = _format_skill_tree(state)
    
    # Generate all chart data
    dashboard.salary_progression = _generate_salary_progression_chart(state)
    dashboard.cost_vs_income = _generate_cost_income_chart(state)
    dashboard.skill_radar = _generate_skill_radar_chart(state)
    dashboard.risk_breakdown = _generate_risk_breakdown_chart(state)
    dashboard.gap_analysis_chart = _generate_gap_analysis_chart(state)
    dashboard.investment_breakdown = _generate_investment_breakdown_chart(state)
    dashboard.timeline_progress = _generate_timeline_progress_chart(state)
    dashboard.monthly_projection = _generate_monthly_projection_chart(state)
    dashboard.path_comparison = _generate_path_comparison_chart(state)
    
    # Success probability gauge
    risk_assessment = state.get("risk_assessment")
    if risk_assessment:
        dashboard.success_probability_gauge = risk_assessment.success_probability_score
    
    # Summary statistics
    dashboard.summary_stats = _generate_summary_stats(state)
    dashboard.key_metrics = _generate_key_metrics(state)
    
    # Timeline events
    dashboard.timeline_events = _generate_timeline_events(state)
    
    # Key insights with reasoning
    dashboard.key_insights = _generate_key_insights(state)
    dashboard.decision_rationale = _generate_decision_rationale(state)
    
    # Recommendations
    dashboard.top_recommendations = _generate_top_recommendations(state)
    dashboard.immediate_actions = _generate_immediate_actions(state)
    
    # Risk indicators
    dashboard.risk_indicators = _generate_risk_indicators(state)
    
    # Selected career summary for context
    dashboard.selected_career_summary = _generate_selected_career_summary(state)
    
    # Generate final report summary
    final_summary = _generate_final_summary(state)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "dashboard_data": dashboard,
        "simulation_complete": True,
        "final_report_summary": final_summary,
        "current_node": "dashboard_formatter",
        "processing_time_ms": {"dashboard_formatter": processing_time},
    }


def _format_milestones(state: CareerSimulationState) -> tuple[list[DashboardMilestone], list[dict]]:
    """Format timeline milestones for React Flow visualization."""
    milestones = []
    connections = []
    
    timeline = state.get("timeline_simulation")
    if not timeline:
        return milestones, connections
    
    # Get the recommended path
    path = timeline.realistic_path
    if timeline.recommended_path == "conservative" and timeline.conservative_path:
        path = timeline.conservative_path
    elif timeline.recommended_path == "ambitious" and timeline.ambitious_path:
        path = timeline.ambitious_path
    
    if not path:
        return milestones, connections
    
    prev_milestone_id = None
    y_offset = 0
    
    for year in path.yearly_plans:
        year_x_base = (year.year_number - 1) * 400
        
        # Add year header milestone
        year_id = f"year_{year.year_number}"
        milestones.append(DashboardMilestone(
            id=year_id,
            title=year.year_label,
            description=year.primary_focus,
            year=year.year_number,
            quarter=0,
            type="year_header",
            status="pending",
            position={"x": year_x_base, "y": 0},
        ))
        
        if prev_milestone_id:
            connections.append({
                "id": f"conn_{prev_milestone_id}_{year_id}",
                "source": prev_milestone_id,
                "target": year_id,
            })
        
        # Add quarterly milestones
        for milestone in year.milestones:
            m_id = f"m_{year.year_number}_{milestone.quarter}_{uuid.uuid4().hex[:6]}"
            x_pos = year_x_base + (milestone.quarter * 80)
            y_pos = 100 + ((milestone.quarter - 1) * 60)
            
            milestones.append(DashboardMilestone(
                id=m_id,
                title=milestone.title,
                description=milestone.description,
                year=year.year_number,
                quarter=milestone.quarter,
                type=milestone.type,
                status="pending",
                position={"x": x_pos, "y": y_pos},
            ))
            
            # Connect to year header
            connections.append({
                "id": f"conn_{year_id}_{m_id}",
                "source": year_id,
                "target": m_id,
            })
        
        prev_milestone_id = year_id
    
    return milestones, connections


def _format_skill_tree(state: CareerSimulationState) -> list[SkillNode]:
    """Format skill gaps into a skill tree structure."""
    nodes = []
    
    gap = state.get("gap_analysis")
    normalized = state.get("normalized_profile")
    
    if not gap:
        return nodes
    
    # Map skill levels to numbers
    level_map = {
        "none": 0, "basic": 1, "beginner": 1,
        "intermediate": 2, "advanced": 3, "expert": 4, "master": 5,
    }
    
    # Add technical skill gaps as nodes
    for i, skill_gap in enumerate(gap.technical_skill_gaps):
        current_level = level_map.get(skill_gap.current_level.lower(), 0)
        required_level = level_map.get(skill_gap.required_level.lower(), 3)
        
        nodes.append(SkillNode(
            id=f"skill_{i}",
            name=skill_gap.skill_name,
            current_level=current_level,
            target_level=required_level,
            category="technical",
            resources=skill_gap.recommended_resources,
            estimated_time=skill_gap.estimated_time_to_close,
        ))
    
    # Add soft skill gaps
    for i, skill_gap in enumerate(gap.soft_skill_gaps):
        current_level = level_map.get(skill_gap.current_level.lower(), 0)
        required_level = level_map.get(skill_gap.required_level.lower(), 3)
        
        nodes.append(SkillNode(
            id=f"soft_skill_{i}",
            name=skill_gap.skill_name,
            current_level=current_level,
            target_level=required_level,
            category="soft",
            resources=skill_gap.recommended_resources,
            estimated_time=skill_gap.estimated_time_to_close,
        ))
    
    return nodes


def _generate_salary_progression_chart(state: CareerSimulationState) -> list[dict]:
    """Generate salary progression data for multi-line chart comparing all paths."""
    data = []
    
    timeline = state.get("timeline_simulation")
    if not timeline:
        return data
    
    import re
    
    def extract_salary(salary_str: str, year: int) -> float:
        """Extract average salary from range string."""
        if not salary_str:
            return 50000 + (year * 15000)
        numbers = re.findall(r'[\d,]+', salary_str.replace(",", ""))
        if numbers:
            return sum(float(n.replace(",", "")) for n in numbers) / len(numbers)
        return 50000 + (year * 15000)
    
    # Get max years across all paths
    max_years = 5
    paths = {
        "conservative": timeline.conservative_path,
        "realistic": timeline.realistic_path,
        "ambitious": timeline.ambitious_path,
    }
    
    for year_num in range(1, max_years + 1):
        year_data = {"year": f"Year {year_num}"}
        
        for path_name, path in paths.items():
            if path and path.yearly_plans:
                matching_year = next(
                    (y for y in path.yearly_plans if y.year_number == year_num), 
                    None
                )
                if matching_year:
                    year_data[path_name] = extract_salary(
                        matching_year.expected_salary_range, year_num
                    )
                else:
                    year_data[path_name] = 50000 + (year_num * (15000 if path_name == "conservative" else 20000 if path_name == "realistic" else 25000))
            else:
                year_data[path_name] = 50000 + (year_num * 15000)
        
        data.append(year_data)
    
    return data


def _generate_cost_income_chart(state: CareerSimulationState) -> list[dict]:
    """Generate cost vs income bar chart data."""
    data = []
    
    financial = state.get("financial_analysis")
    if not financial or not financial.yearly_financials:
        return data
    
    for year_fin in financial.yearly_financials:
        data.append({
            "year": f"Year {year_fin.year_number}",
            "investment": year_fin.total_investment,
            "income": year_fin.expected_income,
            "net": year_fin.net_cash_flow,
            "cumulative_investment": year_fin.cumulative_investment,
            "cumulative_income": year_fin.cumulative_income,
        })
    
    return data


def _generate_skill_radar_chart(state: CareerSimulationState) -> list[dict]:
    """Generate skill radar chart data with current vs required levels."""
    data = []
    
    gap = state.get("gap_analysis")
    if not gap:
        return data
    
    # Map levels to percentages
    level_to_pct = {
        "none": 0, "basic": 25, "beginner": 25,
        "intermediate": 50, "advanced": 75, "expert": 100,
    }
    
    # Add top 6 technical skills
    for skill_gap in gap.technical_skill_gaps[:6]:
        current = level_to_pct.get(skill_gap.current_level.lower(), 0)
        required = level_to_pct.get(skill_gap.required_level.lower(), 75)
        
        data.append({
            "skill": skill_gap.skill_name[:12],
            "current": current,
            "required": required,
            "fullName": skill_gap.skill_name,
        })
    
    return data


def _generate_risk_breakdown_chart(state: CareerSimulationState) -> list[dict]:
    """Generate risk breakdown pie chart data."""
    risk = state.get("risk_assessment")
    if not risk:
        return []
    
    return [
        {"name": "Market Risk", "value": risk.market_risk_score, "fill": "#8884d8"},
        {"name": "Personal Risk", "value": risk.personal_risk_score, "fill": "#82ca9d"},
        {"name": "Financial Risk", "value": risk.financial_risk_score, "fill": "#ffc658"},
        {"name": "Technical Risk", "value": risk.technical_risk_score, "fill": "#ff7300"},
    ]


def _generate_gap_analysis_chart(state: CareerSimulationState) -> list[dict]:
    """Generate gap analysis bar chart showing severity of each gap."""
    data = []
    
    gap = state.get("gap_analysis")
    if not gap:
        return data
    
    for skill_gap in gap.technical_skill_gaps[:8]:
        data.append({
            "skill": skill_gap.skill_name[:15],
            "gap": skill_gap.gap_severity,
            "priority": skill_gap.priority if hasattr(skill_gap, 'priority') else "medium",
            "time": skill_gap.estimated_time_to_close,
        })
    
    return data


def _generate_investment_breakdown_chart(state: CareerSimulationState) -> list[dict]:
    """Generate investment breakdown pie chart."""
    financial = state.get("financial_analysis")
    if not financial:
        return []
    
    # Aggregate costs by category
    categories = {}
    for year_fin in financial.yearly_financials:
        for cost in year_fin.cost_breakdown:
            cat = cost.category.title()
            categories[cat] = categories.get(cat, 0) + cost.amount
    
    colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00C49F", "#FFBB28"]
    return [
        {"name": cat, "value": amount, "fill": colors[i % len(colors)]}
        for i, (cat, amount) in enumerate(categories.items())
    ]


def _generate_timeline_progress_chart(state: CareerSimulationState) -> list[dict]:
    """Generate timeline progress data for Gantt-style chart."""
    data = []
    
    timeline = state.get("timeline_simulation")
    if not timeline or not timeline.realistic_path:
        return data
    
    path = timeline.realistic_path
    
    for year in path.yearly_plans:
        for milestone in year.milestones:
            data.append({
                "task": milestone.title[:30],
                "year": year.year_number,
                "quarter": milestone.quarter,
                "type": milestone.type,
                "duration": milestone.estimated_hours,
                "cost": milestone.estimated_cost,
            })
    
    return data


def _generate_monthly_projection_chart(state: CareerSimulationState) -> list[dict]:
    """Generate detailed monthly projection for first 2 years."""
    data = []
    
    financial = state.get("financial_analysis")
    if not financial or not financial.yearly_financials:
        return data
    
    for year_fin in financial.yearly_financials[:2]:
        monthly_cost = year_fin.total_investment / 12
        monthly_income = year_fin.expected_income / 12
        
        for month in range(1, 13):
            month_num = (year_fin.year_number - 1) * 12 + month
            data.append({
                "month": f"M{month_num}",
                "cost": round(monthly_cost, 0),
                "income": round(monthly_income, 0),
                "net": round(monthly_income - monthly_cost, 0),
            })
    
    return data


def _generate_path_comparison_chart(state: CareerSimulationState) -> list[dict]:
    """Generate path comparison data as rows with metrics across all three paths."""
    timeline = state.get("timeline_simulation")
    if not timeline:
        return []
    
    # Get data from each path
    conservative = timeline.conservative_path
    realistic = timeline.realistic_path
    ambitious = timeline.ambitious_path
    
    if not conservative or not realistic or not ambitious:
        return []
    
    # Format salary for display
    def format_salary(val):
        if val >= 1000000:
            return f"${val/1000000:.1f}M"
        elif val >= 1000:
            return f"${val/1000:.0f}K"
        return f"${val:.0f}"
    
    # Build comparison table rows
    comparison = [
        {
            "metric": "Timeline",
            "conservative": f"{conservative.total_years} years",
            "realistic": f"{realistic.total_years} years",
            "ambitious": f"{ambitious.total_years} years",
        },
        {
            "metric": "Final Salary",
            "conservative": format_salary(conservative.final_expected_salary),
            "realistic": format_salary(realistic.final_expected_salary),
            "ambitious": format_salary(ambitious.final_expected_salary),
        },
        {
            "metric": "Risk Level",
            "conservative": "Low",
            "realistic": "Medium",
            "ambitious": "High",
        },
        {
            "metric": "Success Rate",
            "conservative": f"{conservative.success_probability:.0f}%" if hasattr(conservative, 'success_probability') else "85%",
            "realistic": f"{realistic.success_probability:.0f}%" if hasattr(realistic, 'success_probability') else "70%",
            "ambitious": f"{ambitious.success_probability:.0f}%" if hasattr(ambitious, 'success_probability') else "50%",
        },
        {
            "metric": "Recommended",
            "conservative": "✓" if timeline.recommended_path == "conservative" else "",
            "realistic": "✓" if timeline.recommended_path == "realistic" else "",
            "ambitious": "✓" if timeline.recommended_path == "ambitious" else "",
        },
    ]
    
    return comparison


def _generate_summary_stats(state: CareerSimulationState) -> dict:
    """Generate summary statistics for dashboard cards."""
    stats = {}
    
    risk = state.get("risk_assessment")
    if risk:
        stats["success_probability"] = f"{risk.success_probability_score:.0f}%"
        stats["confidence_interval"] = risk.confidence_interval
        stats["compared_to_average"] = risk.compared_to_average
    
    financial = state.get("financial_analysis")
    if financial:
        stats["total_investment"] = f"${financial.total_investment_required:,.0f}"
        stats["break_even_year"] = f"Year {financial.break_even_year}"
        stats["roi_5_year"] = f"{financial.five_year_roi:.0f}%"
        stats["affordability"] = financial.affordability_rating.title()
    
    gap = state.get("gap_analysis")
    if gap:
        stats["gap_score"] = f"{gap.overall_gap_score:.0f}/100"
        stats["gap_category"] = gap.gap_category.title()
        stats["skill_gaps_count"] = len(gap.technical_skill_gaps)
    
    timeline = state.get("timeline_simulation")
    if timeline and timeline.realistic_path:
        path = timeline.realistic_path
        stats["timeline_years"] = f"{path.total_years} Years"
        stats["target_role"] = path.final_target_role
        stats["expected_salary"] = f"${path.final_expected_salary:,.0f}"
    
    normalized = state.get("normalized_profile")
    if normalized:
        stats["persona"] = normalized.persona_type
        stats["academic_score"] = f"{normalized.academic_strength_score:.0f}/100"
    
    return stats


def _generate_key_metrics(state: CareerSimulationState) -> list[dict]:
    """Generate key metrics for metric cards."""
    metrics = []
    
    risk = state.get("risk_assessment")
    if risk:
        metrics.append({
            "title": "Success Rate",
            "value": f"{risk.success_probability_score:.0f}%",
            "description": risk.success_reasoning[:100] if hasattr(risk, 'success_reasoning') and risk.success_reasoning else "Based on profile analysis",
            "type": "success",
            "icon": "target",
        })
    
    financial = state.get("financial_analysis")
    if financial:
        metrics.append({
            "title": "Total Investment",
            "value": f"${financial.total_investment_required:,.0f}",
            "description": financial.investment_reasoning[:100] if hasattr(financial, 'investment_reasoning') and financial.investment_reasoning else "Courses, certifications, and tools",
            "type": "financial",
            "icon": "dollar",
        })
        metrics.append({
            "title": "5-Year ROI",
            "value": f"{financial.five_year_roi:.0f}%",
            "description": financial.five_year_roi_reasoning[:100] if hasattr(financial, 'five_year_roi_reasoning') and financial.five_year_roi_reasoning else "Return on your investment",
            "type": "roi",
            "icon": "trending",
        })
    
    timeline = state.get("timeline_simulation")
    if timeline and timeline.realistic_path:
        metrics.append({
            "title": "Timeline",
            "value": f"{timeline.realistic_path.total_years} Years",
            "description": timeline.recommendation_reason[:100] if timeline.recommendation_reason else "Estimated time to target role",
            "type": "timeline",
            "icon": "calendar",
        })
    
    return metrics


def _generate_timeline_events(state: CareerSimulationState) -> list[dict]:
    """Generate timeline events list."""
    events = []
    
    timeline = state.get("timeline_simulation")
    if not timeline or not timeline.realistic_path:
        return events
    
    path = timeline.realistic_path
    
    for year in path.yearly_plans:
        # Add year as event
        events.append({
            "id": f"year_{year.year_number}",
            "title": year.year_label,
            "description": year.primary_focus,
            "year": year.year_number,
            "phase": year.phase,
            "type": "year",
            "expected_role": year.expected_role,
            "expected_salary": year.expected_salary_range,
            "reasoning": year.phase_reasoning if hasattr(year, 'phase_reasoning') else "",
        })
        
        # Add milestones
        for m in year.milestones:
            events.append({
                "id": f"milestone_{year.year_number}_{m.quarter}",
                "title": m.title,
                "description": m.description,
                "year": year.year_number,
                "quarter": m.quarter,
                "type": m.type,
                "cost": m.estimated_cost,
                "hours": m.estimated_hours,
                "reasoning": m.reasoning if hasattr(m, 'reasoning') else "",
            })
    
    return events


def _generate_key_insights(state: CareerSimulationState) -> list[dict]:
    """Generate key insights with reasoning."""
    insights = []
    
    gap = state.get("gap_analysis")
    if gap:
        insights.append({
            "title": "Skills Gap Assessment",
            "insight": f"Overall gap score: {gap.overall_gap_score:.0f}/100 ({gap.gap_category})",
            "reasoning": gap.analysis_reasoning if hasattr(gap, 'analysis_reasoning') and gap.analysis_reasoning else "Based on comparison with market requirements",
            "type": "gap",
            "priority": "high" if gap.overall_gap_score > 50 else "medium",
        })
        
        if gap.existing_strengths:
            insights.append({
                "title": "Your Strengths",
                "insight": ", ".join(gap.existing_strengths[:3]),
                "reasoning": "These will help accelerate your career transition",
                "type": "strength",
                "priority": "positive",
            })
    
    risk = state.get("risk_assessment")
    if risk:
        insights.append({
            "title": "Success Probability",
            "insight": f"{risk.success_probability_score:.0f}% chance of success ({risk.confidence_interval})",
            "reasoning": risk.success_reasoning if hasattr(risk, 'success_reasoning') and risk.success_reasoning else "Based on comprehensive risk analysis",
            "type": "risk",
            "priority": "high" if risk.success_probability_score < 60 else "medium",
        })
        
        if hasattr(risk, 'key_opportunities') and risk.key_opportunities:
            insights.append({
                "title": "Key Opportunities",
                "insight": risk.key_opportunities[0] if risk.key_opportunities else "Market is favorable",
                "reasoning": "Factors working in your favor",
                "type": "opportunity",
                "priority": "positive",
            })
    
    financial = state.get("financial_analysis")
    if financial:
        insights.append({
            "title": "Financial Outlook",
            "insight": f"Break-even in Year {financial.break_even_year} with {financial.five_year_roi:.0f}% 5-year ROI",
            "reasoning": financial.break_even_reasoning if hasattr(financial, 'break_even_reasoning') and financial.break_even_reasoning else "Based on investment vs income projections",
            "type": "financial",
            "priority": "medium",
        })
    
    return insights


def _generate_decision_rationale(state: CareerSimulationState) -> list[dict]:
    """Generate decision rationale for key decisions."""
    rationale = []
    
    timeline = state.get("timeline_simulation")
    if timeline:
        rationale.append({
            "decision": f"Recommended Path: {timeline.recommended_path.title()}",
            "why": timeline.recommendation_reason or "Based on your profile and risk tolerance",
            "impact": "This path balances achievability with your career goals",
        })
    
    selected = state.get("selected_career")
    if selected:
        rationale.append({
            "decision": f"Target Career: {selected.career_title}",
            "why": selected.reasoning.why_now if selected.reasoning else "Best fit based on your profile",
            "impact": f"Expected salary: {selected.typical_salary_range}",
        })
    
    return rationale


def _generate_top_recommendations(state: CareerSimulationState) -> list[str]:
    """Generate top recommendations."""
    recommendations = []
    
    risk = state.get("risk_assessment")
    if risk and hasattr(risk, 'recommendations') and risk.recommendations:
        recommendations.extend(risk.recommendations[:3])
    elif risk and risk.risk_mitigation_plan:
        recommendations.extend(risk.risk_mitigation_plan[:3])
    
    gap = state.get("gap_analysis")
    if gap and hasattr(gap, 'top_priorities') and gap.top_priorities:
        recommendations.extend(gap.top_priorities[:2])
    
    return recommendations[:5]


def _generate_immediate_actions(state: CareerSimulationState) -> list[dict]:
    """Generate immediate action items."""
    actions = []
    
    gap = state.get("gap_analysis")
    if gap:
        # Add quick wins
        if hasattr(gap, 'quick_wins') and gap.quick_wins:
            for qw in gap.quick_wins[:2]:
                actions.append({
                    "action": qw,
                    "priority": "high",
                    "timeframe": "This week",
                    "impact": "Quick progress boost",
                })
        
        # Add first skill to work on
        if gap.technical_skill_gaps:
            top_gap = gap.technical_skill_gaps[0]
            actions.append({
                "action": f"Start learning {top_gap.skill_name}",
                "priority": "high",
                "timeframe": top_gap.estimated_time_to_close,
                "impact": f"Close {top_gap.gap_severity:.0f}% gap",
            })
    
    timeline = state.get("timeline_simulation")
    if timeline and timeline.realistic_path:
        path = timeline.realistic_path
        if path.yearly_plans and path.yearly_plans[0].milestones:
            first_milestone = path.yearly_plans[0].milestones[0]
            actions.append({
                "action": first_milestone.title,
                "priority": "medium",
                "timeframe": f"Q{first_milestone.quarter}",
                "impact": first_milestone.description[:50],
            })
    
    return actions[:5]


def _generate_risk_indicators(state: CareerSimulationState) -> list[dict]:
    """Generate risk indicator data."""
    indicators = []
    
    risk = state.get("risk_assessment")
    if not risk:
        return indicators
    
    for rf in risk.risk_factors[:6]:
        indicators.append({
            "name": rf.factor_name,
            "category": rf.category,
            "severity": rf.severity,
            "probability": rf.probability,
            "impact": rf.impact_description,
            "reasoning": rf.reasoning if hasattr(rf, 'reasoning') else "",
            "mitigation": rf.mitigation_strategies[0] if rf.mitigation_strategies else "",
        })
    
    return indicators


def _generate_selected_career_summary(state: CareerSimulationState) -> dict:
    """Generate selected career summary for context."""
    selected = state.get("selected_career")
    if not selected:
        return {}
    
    return {
        "title": selected.career_title,
        "field": selected.career_field,
        "fit_score": selected.overall_fit_score,
        "skill_fit": selected.skill_fit_score,
        "interest_fit": selected.interest_fit_score,
        "market_fit": selected.market_fit_score,
        "salary_range": selected.typical_salary_range,
        "time_to_entry": selected.time_to_entry,
        "top_reasons": selected.top_3_reasons,
    }


def _generate_final_summary(state: CareerSimulationState) -> str:
    """Generate a final summary text for the report."""
    profile = state["career_profile"]
    normalized = state.get("normalized_profile")
    timeline = state.get("timeline_simulation")
    risk = state.get("risk_assessment")
    financial = state.get("financial_analysis")
    selected = state.get("selected_career")
    
    summary_parts = []
    
    # Header
    if selected:
        target_role = selected.career_title
    elif profile.specific_roles:
        target_role = profile.specific_roles[0]
    else:
        target_role = "your target role"
    
    summary_parts.append(f"# Career Path Simulation Report: {target_role}\n")
    
    # Persona
    if normalized:
        summary_parts.append(f"**Your Profile Type:** {normalized.persona_type}\n")
    
    # Success probability with reasoning
    if risk:
        summary_parts.append(
            f"**Success Probability:** {risk.success_probability_score:.0f}% "
            f"(Confidence: {risk.confidence_interval})\n"
        )
        if hasattr(risk, 'success_reasoning') and risk.success_reasoning:
            summary_parts.append(f"*Why:* {risk.success_reasoning}\n")
    
    # Career fit summary
    if selected:
        summary_parts.append(
            f"\n## Selected Career: {selected.career_title}\n"
            f"- **Overall Fit:** {selected.overall_fit_score:.0f}%\n"
            f"- **Salary Range:** {selected.typical_salary_range}\n"
            f"- **Time to Entry:** {selected.time_to_entry}\n"
        )
        if selected.top_3_reasons:
            summary_parts.append("**Top Reasons:**\n")
            for reason in selected.top_3_reasons:
                summary_parts.append(f"  - {reason}\n")
    
    # Timeline overview
    if timeline and timeline.realistic_path:
        path = timeline.realistic_path
        summary_parts.append(
            f"\n## Recommended Path: {path.path_label}\n"
            f"- **Duration:** {path.total_years} years\n"
            f"- **Target Role:** {path.final_target_role}\n"
            f"- **Expected Salary:** ${path.final_expected_salary:,.0f}\n"
        )
        if timeline.recommendation_reason:
            summary_parts.append(f"*Why this path:* {timeline.recommendation_reason}\n")
    
    # Financial summary with reasoning
    if financial:
        summary_parts.append(
            f"\n## Financial Summary\n"
            f"- **Total Investment:** ${financial.total_investment_required:,.0f}\n"
            f"- **Break-Even Point:** Year {financial.break_even_year}\n"
            f"- **5-Year ROI:** {financial.five_year_roi:.0f}%\n"
            f"- **Affordability:** {financial.affordability_rating.title()}\n"
        )
        if hasattr(financial, 'investment_reasoning') and financial.investment_reasoning:
            summary_parts.append(f"*Investment rationale:* {financial.investment_reasoning}\n")
    
    # Key risks with reasoning
    if risk and risk.risk_factors:
        summary_parts.append("\n## Key Risks\n")
        for rf in risk.risk_factors[:3]:
            summary_parts.append(f"- **{rf.factor_name}** ({rf.severity}): {rf.impact_description}\n")
            if rf.mitigation_strategies:
                summary_parts.append(f"  *Mitigation:* {rf.mitigation_strategies[0]}\n")
    
    # Scenarios
    if risk:
        if hasattr(risk, 'best_case_scenario') and risk.best_case_scenario:
            summary_parts.append(f"\n**Best Case:** {risk.best_case_scenario}\n")
        if hasattr(risk, 'most_likely_scenario') and risk.most_likely_scenario:
            summary_parts.append(f"**Most Likely:** {risk.most_likely_scenario}\n")
        if hasattr(risk, 'worst_case_scenario') and risk.worst_case_scenario:
            summary_parts.append(f"**Worst Case:** {risk.worst_case_scenario}\n")
    
    # Vibe check warnings
    if timeline and timeline.vibe_check_warnings:
        summary_parts.append("\n## Important Considerations\n")
        for warning in timeline.vibe_check_warnings[:3]:
            summary_parts.append(f"- {warning}\n")
    
    return "".join(summary_parts)
