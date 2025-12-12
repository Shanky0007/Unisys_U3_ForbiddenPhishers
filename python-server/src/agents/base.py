"""
Base Agent Module
Shared utilities and base classes for all agents
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv

load_dotenv()


def get_llm(
    model_type: str = None,
    model_name: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """
    Get configured LLM instance.
    
    Args:
        model_type: "groq", "openai", or "anthropic"
        model_name: Specific model name (optional)
        temperature: Model temperature
        
    Returns:
        Configured chat model instance
    """
    # Use default from env if not specified
    if model_type is None:
        model_type = os.getenv("DEFAULT_LLM_TYPE", "groq")
    
    if model_type == "groq":
        return ChatGroq(
            model=model_name or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            temperature=temperature,
            api_key=os.getenv("GROQ_API_KEY"),
        )
    elif model_type == "openai":
        return ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif model_type == "anthropic":
        return ChatAnthropic(
            model=model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


# Default LLM for agents
DEFAULT_LLM_TYPE = os.getenv("DEFAULT_LLM_TYPE", "groq")


class AgentConfig:
    """Configuration for agents"""
    
    # Model settings
    llm_type: str = DEFAULT_LLM_TYPE
    temperature: float = 0.7
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Timeout settings
    timeout_seconds: int = 60


# Mapping of major fields to typically associated technical skills
MAJOR_TO_SKILLS_MAP = {
    # Computer Science & Engineering
    "computer science": ["Programming", "Data Structures", "Algorithms", "Software Development"],
    "cs": ["Programming", "Data Structures", "Algorithms", "Software Development"],
    "software engineering": ["Programming", "Software Development", "System Design", "Testing"],
    "information technology": ["Programming", "Networking", "Database Management", "System Administration"],
    "it": ["Programming", "Networking", "Database Management", "System Administration"],
    "data science": ["Python", "Statistics", "Machine Learning", "Data Analysis"],
    "artificial intelligence": ["Python", "Machine Learning", "Deep Learning", "Mathematics"],
    "ai": ["Python", "Machine Learning", "Deep Learning", "Mathematics"],
    "machine learning": ["Python", "Statistics", "Deep Learning", "Mathematics"],
    "cybersecurity": ["Networking", "Security Tools", "Linux", "Cryptography"],
    
    # Engineering
    "electrical engineering": ["Circuit Design", "Electronics", "Signal Processing", "MATLAB"],
    "ee": ["Circuit Design", "Electronics", "Signal Processing", "MATLAB"],
    "mechanical engineering": ["CAD", "Thermodynamics", "Materials Science", "Manufacturing"],
    "me": ["CAD", "Thermodynamics", "Materials Science", "Manufacturing"],
    "civil engineering": ["AutoCAD", "Structural Analysis", "Project Management", "Surveying"],
    "chemical engineering": ["Process Design", "Chemistry", "MATLAB", "Process Control"],
    
    # Business & Management
    "business administration": ["Business Strategy", "Management", "Financial Analysis", "Marketing"],
    "mba": ["Business Strategy", "Leadership", "Financial Analysis", "Operations"],
    "finance": ["Financial Modeling", "Excel", "Accounting", "Investment Analysis"],
    "marketing": ["Digital Marketing", "Market Research", "Analytics", "Content Strategy"],
    "economics": ["Statistical Analysis", "Economic Modeling", "Data Analysis", "Research"],
    
    # Sciences
    "physics": ["Mathematics", "Data Analysis", "Programming", "Research Methods"],
    "chemistry": ["Lab Techniques", "Data Analysis", "Research Methods", "Technical Writing"],
    "biology": ["Lab Techniques", "Data Analysis", "Research Methods", "Bioinformatics"],
    "mathematics": ["Mathematical Modeling", "Statistics", "Programming", "Problem Solving"],
    
    # Healthcare
    "medicine": ["Clinical Skills", "Patient Care", "Medical Knowledge", "Research"],
    "nursing": ["Patient Care", "Clinical Skills", "Healthcare Management", "Communication"],
    "pharmacy": ["Pharmaceutical Knowledge", "Patient Counseling", "Healthcare Regulations", "Chemistry"],
    
    # Design & Arts
    "graphic design": ["Adobe Creative Suite", "UI Design", "Visual Communication", "Typography"],
    "ux design": ["User Research", "Wireframing", "Prototyping", "Usability Testing"],
    "ui design": ["Visual Design", "Prototyping", "Design Systems", "HTML/CSS"],
}

# Grading scale normalization
GRADING_SCALES = {
    "4.0": {"max": 4.0, "excellent": 3.7, "good": 3.0, "average": 2.5},
    "10.0": {"max": 10.0, "excellent": 9.0, "good": 7.5, "average": 6.0},
    "percentage": {"max": 100.0, "excellent": 85.0, "good": 70.0, "average": 55.0},
    "cgpa_10": {"max": 10.0, "excellent": 9.0, "good": 7.5, "average": 6.0},
    "gpa_4": {"max": 4.0, "excellent": 3.7, "good": 3.0, "average": 2.5},
}


def normalize_gpa(gpa: float, scale: str) -> float:
    """
    Normalize GPA to 0-100 scale.
    
    Args:
        gpa: Raw GPA value
        scale: Grading scale identifier
        
    Returns:
        Normalized GPA (0-100)
    """
    scale_lower = scale.lower() if scale else "4.0"
    
    # Find matching scale
    for scale_key, values in GRADING_SCALES.items():
        if scale_key in scale_lower or scale_lower in scale_key:
            return (gpa / values["max"]) * 100
    
    # Default to 4.0 scale
    return (gpa / 4.0) * 100


def infer_skills_from_major(major: str) -> list[str]:
    """
    Infer likely technical skills from academic major.
    
    Args:
        major: Academic major name
        
    Returns:
        List of inferred skills
    """
    if not major:
        return []
    
    major_lower = major.lower().strip()
    
    for key, skills in MAJOR_TO_SKILLS_MAP.items():
        if key in major_lower or major_lower in key:
            return skills
    
    return []


# Persona classification rules
PERSONA_RULES = {
    "high_potential_low_resource": {
        "conditions": ["high_academic", "low_budget"],
        "label": "High-Potential, Low-Resource Student",
        "traits": ["Academically strong", "Budget-conscious", "Scholarship candidate"],
    },
    "career_switcher": {
        "conditions": ["has_experience", "different_field"],
        "label": "Career Switcher",
        "traits": ["Transferable skills", "Industry experience", "Clear motivation"],
    },
    "fast_tracker": {
        "conditions": ["high_academic", "high_ambition", "high_risk_tolerance"],
        "label": "Fast-Track Ambitious",
        "traits": ["High achiever", "Risk-taker", "Growth-oriented"],
    },
    "steady_climber": {
        "conditions": ["moderate_academic", "low_risk_tolerance", "structured_preference"],
        "label": "Steady Climber",
        "traits": ["Methodical", "Risk-averse", "Stability-focused"],
    },
    "explorer": {
        "conditions": ["multiple_interests", "undecided_field"],
        "label": "Career Explorer",
        "traits": ["Curious", "Versatile", "Discovery-oriented"],
    },
}


def calculate_age(date_of_birth) -> Optional[int]:
    """Calculate age from date of birth."""
    if not date_of_birth:
        return None
    
    from datetime import datetime
    
    if isinstance(date_of_birth, str):
        try:
            date_of_birth = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    today = datetime.now()
    age = today.year - date_of_birth.year
    
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    
    return age
