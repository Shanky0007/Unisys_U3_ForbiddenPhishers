"""
Career Profile Schema
Pydantic models for user career profile data collected from frontend
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LanguageProficiency(BaseModel):
    """Language proficiency entry"""
    language: str
    proficiency: str  # Native, Fluent, Intermediate, Basic


class CareerProfile(BaseModel):
    """
    Complete user career profile collected from frontend form.
    Maps to Prisma CareerProfile model.
    """
    id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Phase 1: Core Identity & Academic Foundation
    # Demographics
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    current_country: Optional[str] = None
    current_city: Optional[str] = None
    nationality: Optional[str] = None
    languages_spoken: Optional[list[LanguageProficiency]] = None
    
    # Academic Status
    current_education_level: Optional[str] = None  # High School Senior, 1st Year B.Tech, etc.
    institution_name: Optional[str] = None
    current_major: Optional[str] = None
    current_gpa: Optional[float] = None
    grading_scale: Optional[str] = None  # 4.0, 10.0, Percentage
    expected_graduation_year: Optional[int] = None
    
    # Past Academic Background
    high_school_stream: Optional[str] = None  # Science-PCM, Science-PCB, Commerce, Arts
    key_subjects_strength: list[str] = Field(default_factory=list)
    key_subjects_interest: list[str] = Field(default_factory=list)
    standardized_test_scores: Optional[dict[str, float]] = None  # {SAT: 1450, JEE: 5000}
    
    # Phase 2: Career Aspirations & Goals
    target_career_fields: list[str] = Field(default_factory=list)  # Technology, Healthcare
    specific_roles: list[str] = Field(default_factory=list)  # Software Engineer, Data Scientist
    known_job_title: Optional[str] = None
    known_company_industry: Optional[str] = None
    
    # Long-Term Vision
    primary_career_goal: Optional[str] = None  # Maximize Earnings, Work-Life Balance
    desired_role_level: Optional[str] = None  # Senior IC, Team Lead, Manager, Executive
    preferred_work_env: list[str] = Field(default_factory=list)  # Startup, Corporate, Remote
    willingness_to_relocate: Optional[str] = None  # Yes, No, Within Country, International
    
    # Phase 3: Skills, Interests & Personality
    # Self-Assessed Skills
    technical_skills: Optional[dict[str, str]] = None  # {Python: "Advanced", JavaScript: "Intermediate"}
    soft_skills: Optional[dict[str, int]] = None  # {Communication: 4, Leadership: 3} (1-5 scale)
    
    # Interests & Passions
    subjects_of_interest: list[str] = Field(default_factory=list)
    hobbies_activities: list[str] = Field(default_factory=list)
    enjoyable_project_desc: Optional[str] = None
    
    # Work-Preference Psychometrics
    work_preference: Optional[str] = None  # People, Data, Things
    work_style: Optional[str] = None  # Theoretical, Practical
    role_preference: Optional[str] = None  # Structured, Dynamic
    risk_tolerance: Optional[str] = None  # Low, Medium, High
    learning_style: list[str] = Field(default_factory=list)  # Visual, Auditory, Reading, Kinesthetic
    
    # Phase 4: Constraints & Resources
    # Financial Parameters
    investment_capacity: Optional[str] = None  # <$5k, $5k-$20k, $20k-$50k, >$50k
    financial_dependents: Optional[bool] = None
    financial_details: Optional[str] = None
    target_min_salary: Optional[float] = None
    
    # Time & Commitment
    hours_per_week: Optional[int] = None
    preferred_learning_mode: list[str] = Field(default_factory=list)  # Full-time, Part-time, Bootcamp
    desired_workforce_timeline: Optional[str] = None  # After graduation, After masters
    
    # Support System
    has_mentor: Optional[bool] = None
    institution_guidance_quality: Optional[int] = None  # 1-5 rating
    
    # Phase 5: Market Awareness & Risk Profile
    market_awareness: Optional[str] = None  # Low, Medium, High
    career_concerns: list[str] = Field(default_factory=list)  # Competition, Tech Change, Job Security
    
    # Resume Data (optional)
    resume_text: Optional[str] = None  # Extracted text from uploaded resume
    resume_filename: Optional[str] = None  # Original filename of uploaded resume
    
    # Simulation Customization
    optimism_level: Optional[str] = None  # Optimistic, Balanced, Conservative
    priority_weights: Optional[dict[str, float]] = None  # {salary: 0.4, security: 0.3, fulfillment: 0.3}
    
    # Optional Uploads (S3 URLs)
    resume_url: Optional[str] = None
    certificate_urls: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class NormalizedProfile(BaseModel):
    """
    Normalized and enriched user profile after processing by ProfileParser.
    Contains inferred and standardized data.
    """
    # Original profile reference
    raw_profile: CareerProfile
    
    # Normalized scores (0-100 scale)
    normalized_gpa: float = 0.0
    academic_strength_score: float = 0.0
    
    # Inferred skills (from major, projects, etc.)
    inferred_technical_skills: dict[str, str] = Field(default_factory=dict)
    combined_technical_skills: dict[str, str] = Field(default_factory=dict)
    
    # User persona classification
    persona_type: str = ""  # e.g., "High-Potential, Low-Resource Student"
    persona_traits: list[str] = Field(default_factory=list)
    
    # Readiness indicators
    career_readiness_score: float = 0.0
    financial_readiness_score: float = 0.0
    skill_readiness_score: float = 0.0
    
    # Age and timeline calculations
    current_age: Optional[int] = None
    years_to_graduation: Optional[int] = None
    
    # Summary text for LLM context
    profile_summary: str = ""


class MarketRequirement(BaseModel):
    """Single market requirement for a role"""
    skill_or_qualification: str
    importance: str  # "Required", "Preferred", "Nice-to-have"
    description: Optional[str] = None


class SalaryRange(BaseModel):
    """Salary range information"""
    currency: str = "USD"
    entry_level_min: float = 0.0
    entry_level_max: float = 0.0
    mid_level_min: float = 0.0
    mid_level_max: float = 0.0
    senior_level_min: float = 0.0
    senior_level_max: float = 0.0
    location_factor: float = 1.0  # Multiplier for location


class JobMarketInsight(BaseModel):
    """Market insights for a specific role"""
    role_title: str
    field: str
    
    # Requirements
    hard_requirements: list[MarketRequirement] = Field(default_factory=list)
    soft_requirements: list[MarketRequirement] = Field(default_factory=list)
    
    # Salary data
    salary_range: Optional[SalaryRange] = None
    
    # Market conditions
    demand_level: str = "Medium"  # Low, Medium, High, Very High
    growth_outlook: str = "Stable"  # Declining, Stable, Growing, Booming
    competition_level: str = "Medium"  # Low, Medium, High, Intense
    
    # Education requirements
    min_education: str = ""  # Bachelor's, Master's, PhD
    preferred_education: str = ""
    relevant_certifications: list[str] = Field(default_factory=list)
    
    # Experience requirements
    typical_entry_experience: str = ""  # "0-1 years", "1-3 years"
    
    # Industry trends
    emerging_skills: list[str] = Field(default_factory=list)
    declining_skills: list[str] = Field(default_factory=list)


class MarketInsights(BaseModel):
    """Aggregated market insights from MarketScout"""
    target_roles: list[JobMarketInsight] = Field(default_factory=list)
    alternative_roles: list[JobMarketInsight] = Field(default_factory=list)
    
    # Regional factors
    target_country: str = ""
    regional_demand_modifier: float = 1.0
    
    # Industry overview
    industry_health: str = "Stable"
    top_hiring_companies: list[str] = Field(default_factory=list)
    
    # Data freshness
    data_timestamp: Optional[datetime] = None
    data_sources: list[str] = Field(default_factory=list)
