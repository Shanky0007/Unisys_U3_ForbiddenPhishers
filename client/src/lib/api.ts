/**
 * API Service Layer
 * Handles all communication with the Career Path Simulator backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SimulationRequest {
  profile: CareerProfile;
}

export interface CareerProfile {
  // Phase 1: Core Identity & Academic Foundation
  date_of_birth?: string;
  gender?: string;
  current_country?: string;
  current_city?: string;
  nationality?: string;
  languages_spoken?: LanguageProficiency[];

  // Academic Status
  current_education_level?: string;
  institution_name?: string;
  current_major?: string;
  current_gpa?: number;
  grading_scale?: string;
  expected_graduation_year?: number;

  // Past Academic Background
  high_school_stream?: string;
  key_subjects_strength?: string[];
  key_subjects_interest?: string[];
  standardized_test_scores?: Record<string, number>;

  // Phase 2: Career Aspirations & Goals
  target_career_fields?: string[];
  specific_roles?: string[];
  known_job_title?: string;
  known_company_industry?: string;

  // Long-Term Vision
  primary_career_goal?: string;
  desired_role_level?: string;
  preferred_work_env?: string[];
  willingness_to_relocate?: string;

  // Phase 3: Skills, Interests & Personality
  technical_skills?: Record<string, string>;
  soft_skills?: Record<string, number>;

  // Interests & Passions
  subjects_of_interest?: string[];
  hobbies_activities?: string[];
  enjoyable_project_desc?: string;

  // Work-Preference Psychometrics
  work_preference?: string;
  work_style?: string;
  role_preference?: string;
  risk_tolerance?: string;
  learning_style?: string[];

  // Phase 4: Constraints & Resources
  investment_capacity?: string;
  financial_dependents?: boolean;
  financial_details?: string;
  target_min_salary?: number;

  // Time & Commitment
  hours_per_week?: number;
  preferred_learning_mode?: string[];
  desired_workforce_timeline?: string;

  // Support System
  has_mentor?: boolean;
  institution_guidance_quality?: number;

  // Phase 5: Market Awareness & Risk Profile
  market_awareness?: string;
  career_concerns?: string[];

  // Resume Data (optional)
  resume_text?: string;
  resume_filename?: string;

  // Simulation Customization
  optimism_level?: string;
  priority_weights?: Record<string, number>;
}

export interface LanguageProficiency {
  language: string;
  proficiency: string;
}

export interface SimulationResponse {
  success: boolean;
  simulation_id: string;
  processing_time_ms: number;
  summary: SimulationSummary;
  dashboard_data?: DashboardData;
  timeline?: TimelineData;
  financial_analysis?: FinancialAnalysis;
  risk_assessment?: RiskAssessment;
  gap_analysis?: GapAnalysis;
  warnings: string[];
  errors: string[];
}

export interface SimulationSummary {
  target_role?: string;
  timeline_years?: number;
  success_probability?: number;
  total_investment?: number;
  expected_salary?: number;
  recommended_path?: string;
  key_milestones?: string[];
}

export interface DashboardData {
  milestones: DashboardMilestone[];
  skill_nodes: SkillNode[];
  salary_progression: SalaryDataPoint[];
  skill_radar: SkillRadarData[];
  risk_breakdown: RiskBreakdownData[];
  gap_analysis_chart: { category: string; gap: number }[];
  investment_breakdown: { name: string; value: number }[];
  monthly_projection: { month: string; income: number; expenses: number; net: number }[];
  timeline_progress: { year: number; phase: string; progress: number }[];
  path_comparison: { metric: string; conservative: string | number; realistic: string | number; ambitious: string | number }[];
  key_insights: { title: string; insight: string; reasoning: string; type: string }[];
  decision_rationale: { decision: string; why: string; impact: string }[];
  top_recommendations: string[];
  immediate_actions: { action: string; priority: string; timeframe: string; impact: string }[];
  risk_indicators: { name: string; level: string; trend: string }[];
  key_metrics: { title: string; value: string | number; change?: string; icon?: string }[];
  selected_career_summary: Record<string, unknown>;
  summary: Record<string, unknown>;
}

export interface DashboardMilestone {
  id: string;
  label: string;
  description: string;
  year: number;
  quarter: number;
  type: string;
  status: string;
  position: { x: number; y: number };
}

export interface SkillNode {
  id: string;
  name: string;
  category: string;
  current_level: number;
  target_level: number;
  importance: string;
}

export interface SalaryDataPoint {
  year: number;
  conservative: number;
  realistic: number;
  ambitious: number;
}

export interface SkillRadarData {
  skill: string;
  current: number;
  required: number;
}

export interface RiskBreakdownData {
  name: string;
  category?: string;
  value: number;
  score?: number;
  fill: string;
}

export interface TimelineData {
  conservative_path?: CareerPath;
  realistic_path?: CareerPath;
  ambitious_path?: CareerPath;
  recommended_path: string;
  recommendation_reason: string;
  vibe_check_warnings: string[];
  alignment_score: number;
}

export interface CareerPath {
  path_type: string;
  path_label: string;
  total_years: number;
  yearly_plans: YearPlan[];
  final_target_role: string;
  final_expected_salary: number;
  major_milestones: string[];
  assumptions: string[];
  key_decision_points: string[];
}

export interface YearPlan {
  year_number: number;
  year_label: string;
  phase: string;
  primary_focus: string;
  phase_reasoning?: string;
  focus_reasoning?: string;
  milestones: YearMilestone[];
  expected_role?: string;
  expected_salary_range?: string;
  key_skills_acquired: string[];
  skill_progress_target?: Record<string, number>;
  potential_setbacks: string[];
  risk_mitigation?: string[];
  success_indicators?: string[];
  buffer_time_weeks: number;
  year_summary: string;
}

export interface YearMilestone {
  quarter: number;
  title: string;
  description: string;
  type: string;
  estimated_cost: number;
  estimated_hours: number;
  resources: string[];
  success_metrics: string[];
  reasoning?: string;
  dependencies?: string[];
  risk_if_skipped?: string;
}

export interface FinancialAnalysis {
  total_investment_required: number;
  yearly_financials: YearlyFinancials[];
  break_even_year: number;
  break_even_month: number;
  five_year_roi: number;
  ten_year_projected_earnings: number;
  affordability_rating: string;
  affordability_notes: string[];
  cost_saving_opportunities: string[];
  funding_options: string[];
  meets_min_salary_target: boolean;
  years_to_target_salary: number;
  // New reasoning fields
  investment_reasoning?: string;
  break_even_reasoning?: string;
  five_year_roi_reasoning?: string;
  affordability_reasoning?: string;
  salary_target_reasoning?: string;
  salary_milestones?: { year: number; expected_salary: number; role: string; reasoning: string }[];
  investment_by_category?: { category: string; amount: number; percentage: number }[];
}

export interface YearlyFinancials {
  year_number: number;
  total_investment: number;
  cost_breakdown: CostBreakdown[];
  expected_income: number;
  income_source: string;
  net_cash_flow: number;
  cumulative_investment: number;
  cumulative_income: number;
}

export interface CostBreakdown {
  item_name: string;
  category: string;
  amount: number;
  currency: string;
  is_recurring: boolean;
  frequency?: string;
  notes?: string;
}

export interface RiskAssessment {
  success_probability_score: number;
  confidence_interval: string;
  risk_factors: RiskFactor[];
  market_risk_score: number;
  personal_risk_score: number;
  financial_risk_score: number;
  technical_risk_score: number;
  overall_risk_rating: string;
  key_concerns: string[];
  key_opportunities: string[];
  recommendations: string[];
  // New reasoning fields
  success_reasoning?: string;
  market_risk_reasoning?: string;
  personal_risk_reasoning?: string;
  financial_risk_reasoning?: string;
  technical_risk_reasoning?: string;
  comparison_reasoning?: string;
  best_case_scenario?: string;
  worst_case_scenario?: string;
  most_likely_scenario?: string;
}

export interface RiskFactor {
  factor_name: string;
  category: string;
  severity: string;
  probability: number;
  impact_description: string;
  mitigation_strategies: string[];
  reasoning?: string;
}

export interface GapAnalysis {
  overall_gap_score: number;
  gap_category: string;
  technical_skill_gaps: SkillGap[];
  soft_skill_gaps: SkillGap[];
  education_gap?: string;
  certification_gaps: string[];
  experience_gap_years: number;
  critical_bottlenecks: string[];
  timeline_bottlenecks: string[];
  existing_strengths: string[];
  competitive_advantages: string[];
  personality_frictions: string[];
  stress_risks: string[];
  // New reasoning fields
  analysis_reasoning?: string;
  education_gap_score?: number;
  education_gap_reasoning?: string;
  experience_gap_score?: number;
  experience_gap_reasoning?: string;
  top_priorities?: string[];
  quick_wins?: string[];
}

export interface SkillGap {
  skill_name: string;
  current_level: string;
  required_level: string;
  gap_severity: number;
  estimated_time_to_close: string;
  recommended_resources: string[];
  // New reasoning fields
  reasoning?: string;
  priority?: string;
  learning_path?: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  agents: string[];
}

// ============ Stage 1: Career Matching Types ============

export interface CareerFitReasoning {
  strengths_alignment: string[];
  interest_match: string[];
  skill_transferability: string[];
  growth_potential_reasons: string[];
  market_demand_reasons: string[];
  potential_challenges: string[];
  why_now: string;
}

export interface CareerFit {
  rank: number;
  career_title: string;
  career_field: string;
  overall_fit_score: number;
  skill_fit_score: number;
  interest_fit_score: number;
  market_fit_score: number;
  personality_fit_score: number;
  tagline: string;
  reasoning: CareerFitReasoning;
  typical_salary_range: string;
  time_to_entry: string;
  difficulty_level: string;
  top_3_reasons: string[];
  key_skills_needed: string[];
  immediate_next_steps: string[];
}

export interface CareerMatchingResponse {
  success: boolean;
  session_id: string;
  processing_time_ms: number;
  analysis_summary: string;
  profile_highlights: string[];
  career_fits: CareerFit[];
  methodology_explanation: string;
  confidence_level: string;
  confidence_reasoning: string;
  errors: string[];
}

// API Functions

// ============ Stage 1: Analyze Career Fits ============
export async function analyzeCareerFits(profile: CareerProfile): Promise<CareerMatchingResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ profile }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Career analysis failed');
  }

  return response.json();
}

// ============ Stage 2: Simulate Selected Career ============
export async function simulateSelectedCareer(
  sessionId: string, 
  careerIndex: number
): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE_URL}/simulate/selected`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      session_id: sessionId, 
      career_index: careerIndex 
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Simulation failed');
  }

  return response.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Backend is not available');
  }
  return response.json();
}

// Legacy single-stage simulation
export async function runSimulation(profile: CareerProfile): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE_URL}/simulate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ profile }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Simulation failed');
  }

  return response.json();
}

export async function getGraphInfo(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}/graph/info`);
  if (!response.ok) {
    throw new Error('Failed to fetch graph info');
  }
  return response.json();
}
