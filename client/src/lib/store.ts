import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CareerProfile, SimulationResponse, CareerMatchingResponse, CareerFit } from './api';

interface SimulationStore {
  // Form state
  profile: Partial<CareerProfile>;
  currentStep: number;
  
  // Stage 1: Career Matching state
  matchingResult: CareerMatchingResponse | null;
  sessionId: string | null;
  selectedCareerIndex: number | null;
  selectedCareer: CareerFit | null;
  
  // Stage 2: Simulation state
  isLoading: boolean;
  loadingStage: 'matching' | 'simulation' | null;
  result: SimulationResponse | null;
  error: string | null;
  
  // Actions
  setProfile: (profile: Partial<CareerProfile>) => void;
  updateProfile: (updates: Partial<CareerProfile>) => void;
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setLoading: (loading: boolean, stage?: 'matching' | 'simulation') => void;
  setMatchingResult: (result: CareerMatchingResponse | null) => void;
  selectCareer: (index: number, career: CareerFit) => void;
  setResult: (result: SimulationResponse | null) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  resetToCareerSelection: () => void;
}

const initialProfile: Partial<CareerProfile> = {
  current_education_level: '',
  institution_name: '',
  current_major: '',
  current_gpa: undefined,
  grading_scale: '10.0',
  expected_graduation_year: new Date().getFullYear() + 2,
  target_career_fields: [],
  specific_roles: [],
  primary_career_goal: '',
  desired_role_level: '',
  preferred_work_env: [],
  technical_skills: {},
  soft_skills: {},
  work_style: '',
  risk_tolerance: 'Medium',
  investment_capacity: '',
  hours_per_week: 20,
  current_country: '',
  market_awareness: 'Medium',
  career_concerns: [],
  optimism_level: 'Balanced',
};

export const useSimulationStore = create<SimulationStore>()(
  persist(
    (set) => ({
      profile: initialProfile,
      currentStep: 0,
      matchingResult: null,
      sessionId: null,
      selectedCareerIndex: null,
      selectedCareer: null,
      isLoading: false,
      loadingStage: null,
      result: null,
      error: null,
      
      setProfile: (profile) => set({ profile }),
      updateProfile: (updates) => set((state) => ({ 
        profile: { ...state.profile, ...updates } 
      })),
      setCurrentStep: (step) => set({ currentStep: step }),
      nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
      prevStep: () => set((state) => ({ currentStep: Math.max(0, state.currentStep - 1) })),
      setLoading: (loading, stage) => set({ isLoading: loading, loadingStage: stage || null }),
      setMatchingResult: (result) => set({ 
        matchingResult: result, 
        sessionId: result?.session_id || null 
      }),
      selectCareer: (index, career) => set({ 
        selectedCareerIndex: index, 
        selectedCareer: career 
      }),
      setResult: (result) => set({ result }),
      setError: (error) => set({ error }),
      reset: () => set({ 
        profile: initialProfile, 
        currentStep: 0,
        matchingResult: null,
        sessionId: null,
        selectedCareerIndex: null,
        selectedCareer: null,
        result: null, 
        error: null 
      }),
      resetToCareerSelection: () => set({
        selectedCareerIndex: null,
        selectedCareer: null,
        result: null,
        error: null,
      }),
    }),
    {
      name: 'career-simulation-storage',
      partialize: (state) => ({ 
        profile: state.profile,
        currentStep: state.currentStep,
        matchingResult: state.matchingResult,
        sessionId: state.sessionId,
      }),
    }
  )
);
