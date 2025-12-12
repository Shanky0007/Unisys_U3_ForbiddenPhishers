"""
Node B: MarketScout Agent
The RAG Retriever - Fetches real-time market data for career fields
"""

import os
import time
from datetime import datetime
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

from ..models.state import CareerSimulationState
from ..models.career_profile import (
    MarketInsights,
    JobMarketInsight,
    MarketRequirement,
    SalaryRange,
)
from .base import get_llm


MARKET_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert labor market analyst with deep knowledge of global job markets, salary trends, and career requirements. 

Your task is to analyze market data and provide accurate, actionable insights for career planning. Be specific about:
- Hard requirements vs nice-to-haves for roles
- Realistic salary ranges by experience level
- Market demand and competition levels
- Required education and certifications

Base your analysis on the search results provided, but also apply your knowledge of general market trends."""),

    ("human", """Analyze the job market for the following career targets:

**Target Roles:** {target_roles}
**Target Fields:** {target_fields}
**Target Country:** {country}
**Willingness to Relocate:** {relocate}

**Search Results (Recent Market Data):**
{search_results}

Provide your analysis in the following structured format for EACH target role:

---
### ROLE: [Role Name]
**FIELD:** [Industry/Field]

**HARD REQUIREMENTS:**
- [Requirement 1]: [Description]
- [Requirement 2]: [Description]

**SOFT REQUIREMENTS (Nice-to-Have):**
- [Requirement 1]: [Description]

**SALARY RANGES ({country}):**
- Entry Level: $XX,XXX - $XX,XXX
- Mid Level: $XX,XXX - $XX,XXX  
- Senior Level: $XX,XXX - $XX,XXX

**MARKET DEMAND:** [Low/Medium/High/Very High]
**GROWTH OUTLOOK:** [Declining/Stable/Growing/Booming]
**COMPETITION LEVEL:** [Low/Medium/High/Intense]

**EDUCATION REQUIREMENTS:**
- Minimum: [Degree level]
- Preferred: [Degree level]
- Relevant Certifications: [List]

**TYPICAL ENTRY EXPERIENCE:** [e.g., "0-2 years", "Internship experience"]

**EMERGING SKILLS:** [Skills becoming more important]
**DECLINING SKILLS:** [Skills becoming less relevant]

---

After analyzing all roles, provide:

**INDUSTRY OVERVIEW:**
[2-3 sentences about overall industry health and trends]

**TOP HIRING COMPANIES:**
[List 5-10 major companies hiring for these roles in the target region]

**ALTERNATIVE ROLES TO CONSIDER:**
[If the target roles are highly competitive, suggest 2-3 related but more accessible roles]""")
])


async def search_market_data(
    roles: list[str],
    fields: list[str],
    country: str,
) -> str:
    """
    Search for market data using Tavily Search API.
    
    Args:
        roles: Target job roles
        fields: Target career fields
        country: Target country for job market
        
    Returns:
        Concatenated search results
    """
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        # Return placeholder data if no API key
        return _get_placeholder_market_data(roles, fields, country)
    
    search_tool = TavilySearchResults(
        max_results=5,
        api_key=api_key,
    )
    
    all_results = []
    
    # Search for each role
    for role in roles[:3]:  # Limit to first 3 roles to manage API calls
        query = f"{role} job requirements salary {country} 2024 2025"
        try:
            results = search_tool.invoke(query)
            if results:
                all_results.append(f"\n### Search results for '{role}':\n")
                for r in results:
                    if isinstance(r, dict):
                        all_results.append(f"- {r.get('content', '')[:500]}\n")
                    else:
                        all_results.append(f"- {str(r)[:500]}\n")
        except Exception as e:
            all_results.append(f"- Error searching for {role}: {str(e)}\n")
    
    # Search for field-level trends
    for field in fields[:2]:
        query = f"{field} industry trends hiring outlook {country} 2025"
        try:
            results = search_tool.invoke(query)
            if results:
                all_results.append(f"\n### Industry trends for '{field}':\n")
                for r in results:
                    if isinstance(r, dict):
                        all_results.append(f"- {r.get('content', '')[:500]}\n")
                    else:
                        all_results.append(f"- {str(r)[:500]}\n")
        except Exception as e:
            all_results.append(f"- Error searching for {field}: {str(e)}\n")
    
    return "".join(all_results) if all_results else _get_placeholder_market_data(roles, fields, country)


def _get_placeholder_market_data(roles: list[str], fields: list[str], country: str) -> str:
    """Return placeholder market data when search is unavailable."""
    return f"""
### General Market Data (Placeholder - Live search unavailable)

**Target Roles:** {', '.join(roles)}
**Target Fields:** {', '.join(fields)}
**Country:** {country}

Note: This is placeholder data. For accurate market insights, please configure TAVILY_API_KEY.

General trends for technology roles:
- Software Engineers remain in high demand globally
- Data Science and AI/ML roles are growing rapidly
- Remote work opportunities have expanded significantly
- Entry-level positions are competitive but available
- Certifications in cloud (AWS, Azure, GCP) are increasingly valuable
- Typical salary range for entry-level tech in US: $60,000 - $100,000
- Typical salary range for mid-level tech in US: $100,000 - $150,000
- Typical salary range for senior tech in US: $150,000 - $250,000+

Common requirements:
- Bachelor's degree in related field (often required)
- Portfolio of projects (strongly preferred)
- Internship experience (preferred for entry-level)
- Strong problem-solving skills
- Communication and teamwork abilities
"""


def market_scout_node(state: CareerSimulationState) -> dict:
    """
    Node B: MarketScout
    Fetches real-time market data and analyzes job market conditions.
    
    Responsibilities:
    - Search for current job market data
    - Identify salary ranges by location
    - Determine hard vs soft requirements
    - Assess market demand and competition
    
    Args:
        state: Current graph state with normalized_profile
        
    Returns:
        State update with market_insights
    """
    start_time = time.time()
    
    profile = state["career_profile"]
    normalized = state.get("normalized_profile")
    
    # Get target roles and fields
    target_roles = profile.specific_roles or ["Software Engineer"]
    target_fields = profile.target_career_fields or ["Technology"]
    country = profile.current_country or "United States"
    relocate = profile.willingness_to_relocate or "Within Country"
    
    # Search for market data (sync version)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    search_results = loop.run_until_complete(
        search_market_data(target_roles, target_fields, country)
    )
    
    # Get LLM analysis
    llm = get_llm(temperature=0.3)
    chain = MARKET_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    analysis = chain.invoke({
        "target_roles": ", ".join(target_roles),
        "target_fields": ", ".join(target_fields),
        "country": country,
        "relocate": relocate,
        "search_results": search_results,
    })
    
    # Parse the analysis into structured format
    market_insights = _parse_market_analysis(analysis, target_roles, target_fields, country)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "market_insights": market_insights,
        "current_node": "market_scout",
        "processing_time_ms": {"market_scout": processing_time},
    }


def _parse_market_analysis(
    analysis: str,
    target_roles: list[str],
    target_fields: list[str],
    country: str,
) -> MarketInsights:
    """Parse LLM market analysis into structured MarketInsights."""
    
    target_role_insights = []
    alternative_role_insights = []
    top_companies = []
    industry_health = "Stable"
    
    # Split by role sections
    role_sections = analysis.split("### ROLE:")
    
    for section in role_sections[1:]:  # Skip first empty section
        insight = _parse_role_section(section, country)
        if insight:
            # Check if it's a target role or alternative
            if any(role.lower() in insight.role_title.lower() for role in target_roles):
                target_role_insights.append(insight)
            else:
                alternative_role_insights.append(insight)
    
    # If no structured roles found, create default insights for target roles
    if not target_role_insights:
        for role in target_roles:
            field = target_fields[0] if target_fields else "Technology"
            target_role_insights.append(_create_default_insight(role, field, country))
    
    # Extract industry overview and companies
    if "INDUSTRY OVERVIEW:" in analysis.upper():
        overview_start = analysis.upper().find("INDUSTRY OVERVIEW:")
        overview_section = analysis[overview_start:overview_start + 500]
        if "growing" in overview_section.lower() or "booming" in overview_section.lower():
            industry_health = "Growing"
        elif "declining" in overview_section.lower():
            industry_health = "Declining"
    
    if "TOP HIRING COMPANIES:" in analysis.upper():
        companies_start = analysis.upper().find("TOP HIRING COMPANIES:")
        companies_section = analysis[companies_start:companies_start + 300]
        # Extract company names (simple heuristic)
        lines = companies_section.split("\n")
        for line in lines[1:6]:
            company = line.strip().strip("-•").strip()
            if company and len(company) > 2:
                top_companies.append(company)
    
    return MarketInsights(
        target_roles=target_role_insights,
        alternative_roles=alternative_role_insights[:3],  # Limit alternatives
        target_country=country,
        regional_demand_modifier=_get_regional_modifier(country),
        industry_health=industry_health,
        top_hiring_companies=top_companies[:10],
        data_timestamp=datetime.now(),
        data_sources=["Tavily Search", "LLM Analysis"],
    )


def _parse_role_section(section: str, country: str) -> Optional[JobMarketInsight]:
    """Parse a single role section from the analysis."""
    lines = section.split("\n")
    
    if not lines:
        return None
    
    # Extract role name from first line
    role_title = lines[0].strip().strip("[]")
    if not role_title:
        return None
    
    insight = JobMarketInsight(
        role_title=role_title,
        field="",
    )
    
    current_section = None
    
    for line in lines:
        line_upper = line.upper().strip()
        line_stripped = line.strip()
        
        # Identify sections
        if "**FIELD:**" in line_upper or "FIELD:" in line_upper:
            insight.field = line_stripped.split(":")[-1].strip().strip("*[]")
        
        elif "HARD REQUIREMENTS" in line_upper:
            current_section = "hard"
        elif "SOFT REQUIREMENTS" in line_upper or "NICE-TO-HAVE" in line_upper:
            current_section = "soft"
        elif "SALARY" in line_upper:
            current_section = "salary"
        elif "MARKET DEMAND" in line_upper:
            demand = line_stripped.split(":")[-1].strip().strip("*[]")
            insight.demand_level = _normalize_level(demand)
        elif "GROWTH OUTLOOK" in line_upper:
            outlook = line_stripped.split(":")[-1].strip().strip("*[]")
            insight.growth_outlook = _normalize_outlook(outlook)
        elif "COMPETITION LEVEL" in line_upper:
            comp = line_stripped.split(":")[-1].strip().strip("*[]")
            insight.competition_level = _normalize_level(comp)
        elif "EDUCATION REQUIREMENTS" in line_upper:
            current_section = "education"
        elif "TYPICAL ENTRY" in line_upper:
            insight.typical_entry_experience = line_stripped.split(":")[-1].strip().strip("*[]")
        elif "EMERGING SKILLS" in line_upper:
            skills = line_stripped.split(":")[-1].strip().strip("*[]")
            insight.emerging_skills = [s.strip() for s in skills.split(",")]
        elif "DECLINING SKILLS" in line_upper:
            skills = line_stripped.split(":")[-1].strip().strip("*[]")
            insight.declining_skills = [s.strip() for s in skills.split(",")]
        
        # Parse section content
        elif current_section and line_stripped.startswith("-"):
            content = line_stripped.lstrip("-•").strip()
            
            if current_section == "hard":
                insight.hard_requirements.append(MarketRequirement(
                    skill_or_qualification=content.split(":")[0].strip(),
                    importance="Required",
                    description=content.split(":")[-1].strip() if ":" in content else None,
                ))
            elif current_section == "soft":
                insight.soft_requirements.append(MarketRequirement(
                    skill_or_qualification=content.split(":")[0].strip(),
                    importance="Preferred",
                    description=content.split(":")[-1].strip() if ":" in content else None,
                ))
            elif current_section == "salary":
                insight.salary_range = _parse_salary_line(content, insight.salary_range, country)
            elif current_section == "education":
                if "minimum" in content.lower():
                    insight.min_education = content.split(":")[-1].strip()
                elif "preferred" in content.lower():
                    insight.preferred_education = content.split(":")[-1].strip()
                elif "certification" in content.lower():
                    certs = content.split(":")[-1].strip()
                    insight.relevant_certifications = [c.strip() for c in certs.split(",")]
    
    return insight


def _parse_salary_line(
    line: str,
    current_range: Optional[SalaryRange],
    country: str,
) -> SalaryRange:
    """Parse salary information from a line."""
    import re
    
    if current_range is None:
        current_range = SalaryRange(currency=_get_currency(country))
    
    # Find numbers in the line
    numbers = re.findall(r'[\d,]+(?:\.\d+)?', line.replace(",", ""))
    numbers = [float(n) for n in numbers if n]
    
    line_lower = line.lower()
    
    if len(numbers) >= 2:
        min_val, max_val = numbers[0], numbers[1]
        
        if "entry" in line_lower:
            current_range.entry_level_min = min_val
            current_range.entry_level_max = max_val
        elif "mid" in line_lower:
            current_range.mid_level_min = min_val
            current_range.mid_level_max = max_val
        elif "senior" in line_lower:
            current_range.senior_level_min = min_val
            current_range.senior_level_max = max_val
    
    return current_range


def _normalize_level(level: str) -> str:
    """Normalize demand/competition level."""
    level_lower = level.lower()
    if "very high" in level_lower or "intense" in level_lower:
        return "Very High"
    elif "high" in level_lower:
        return "High"
    elif "low" in level_lower:
        return "Low"
    return "Medium"


def _normalize_outlook(outlook: str) -> str:
    """Normalize growth outlook."""
    outlook_lower = outlook.lower()
    if "boom" in outlook_lower:
        return "Booming"
    elif "grow" in outlook_lower:
        return "Growing"
    elif "declin" in outlook_lower:
        return "Declining"
    return "Stable"


def _get_currency(country: str) -> str:
    """Get currency code for country."""
    currency_map = {
        "united states": "USD",
        "usa": "USD",
        "india": "INR",
        "united kingdom": "GBP",
        "uk": "GBP",
        "canada": "CAD",
        "australia": "AUD",
        "germany": "EUR",
        "france": "EUR",
        "japan": "JPY",
        "china": "CNY",
        "singapore": "SGD",
    }
    return currency_map.get(country.lower(), "USD")


def _get_regional_modifier(country: str) -> float:
    """Get salary modifier based on region."""
    modifier_map = {
        "united states": 1.0,
        "usa": 1.0,
        "switzerland": 1.3,
        "singapore": 0.9,
        "united kingdom": 0.85,
        "uk": 0.85,
        "germany": 0.75,
        "canada": 0.8,
        "australia": 0.85,
        "india": 0.25,
        "china": 0.4,
    }
    return modifier_map.get(country.lower(), 0.7)


def _create_default_insight(role: str, field: str, country: str) -> JobMarketInsight:
    """Create default market insight when parsing fails."""
    return JobMarketInsight(
        role_title=role,
        field=field,
        hard_requirements=[
            MarketRequirement(
                skill_or_qualification="Bachelor's Degree",
                importance="Required",
                description="In related field",
            ),
        ],
        soft_requirements=[
            MarketRequirement(
                skill_or_qualification="Relevant Projects/Portfolio",
                importance="Preferred",
            ),
        ],
        salary_range=SalaryRange(
            currency=_get_currency(country),
            entry_level_min=50000 * _get_regional_modifier(country),
            entry_level_max=80000 * _get_regional_modifier(country),
            mid_level_min=80000 * _get_regional_modifier(country),
            mid_level_max=120000 * _get_regional_modifier(country),
            senior_level_min=120000 * _get_regional_modifier(country),
            senior_level_max=180000 * _get_regional_modifier(country),
        ),
        demand_level="Medium",
        growth_outlook="Stable",
        competition_level="Medium",
        min_education="Bachelor's",
        preferred_education="Master's",
        typical_entry_experience="0-2 years",
    )
