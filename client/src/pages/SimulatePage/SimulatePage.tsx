import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  ArrowLeft,
  ArrowRight,
  Loader2,
  GraduationCap,
  Target,
  Briefcase,
  Brain,
  Wallet,
  AlertCircle,
  X,
  Plus,
  FileUp,
  Trash2,
  CheckCircle2,
} from 'lucide-react';
import { useSimulationStore } from '@/lib/store';
import { analyzeCareerFits } from '@/lib/api';
import type { CareerProfile } from '@/lib/api';

const STEPS = [
  { id: 0, title: 'Academic Background', icon: GraduationCap },
  { id: 1, title: 'Career Goals', icon: Target },
  { id: 2, title: 'Skills & Interests', icon: Brain },
  { id: 3, title: 'Work Preferences', icon: Briefcase },
  { id: 4, title: 'Resources & Constraints', icon: Wallet },
];

const EDUCATION_LEVELS = [
  'High School Senior',
  '1st Year B.Tech/B.E.',
  '2nd Year B.Tech/B.E.',
  '3rd Year B.Tech/B.E.',
  '4th Year B.Tech/B.E.',
  'Recent Graduate',
  'Working Professional',
  'Masters Student',
  'PhD Student',
];

const CAREER_FIELDS = [
  'Technology',
  'AI/ML',
  'Data Science',
  'Finance',
  'Healthcare',
  'Consulting',
  'Marketing',
  'Design',
  'Research',
  'Education',
  'Entrepreneurship',
];

const ROLES = [
  'Software Engineer',
  'Data Scientist',
  'ML Engineer',
  'Product Manager',
  'UX Designer',
  'Business Analyst',
  'Consultant',
  'Research Scientist',
  'Quantitative Analyst',
  'DevOps Engineer',
  'Full Stack Developer',
];

const CAREER_GOALS = [
  'Maximize Earnings',
  'Work-Life Balance',
  'Technical Excellence',
  'Leadership & Management',
  'Entrepreneurship',
  'Social Impact',
  'Creative Freedom',
  'Job Security',
];

const ROLE_LEVELS = [
  'Entry Level',
  'Mid-Level IC',
  'Senior IC',
  'Team Lead',
  'Manager',
  'Director',
  'Executive',
];

const WORK_ENVIRONMENTS = [
  'Startup',
  'Corporate',
  'Remote',
  'Hybrid',
  'FAANG',
  'Government',
  'Non-Profit',
  'Freelance',
];

const SKILL_LEVELS = ['None', 'Basic', 'Intermediate', 'Advanced', 'Expert'];

const COMMON_SKILLS = [
  'Python',
  'JavaScript',
  'SQL',
  'Machine Learning',
  'Data Analysis',
  'React',
  'Cloud (AWS/GCP)',
  'Docker',
  'Git',
  'Problem Solving',
];

const INVESTMENT_CAPACITIES = [
  'Less than $5k',
  '$5k - $20k',
  '$20k - $50k',
  'More than $50k',
];

export default function SimulatePage() {
  const navigate = useNavigate();
  const {
    profile,
    updateProfile,
    currentStep,
    setCurrentStep,
    isLoading,
    setLoading,
    setMatchingResult,
    setError,
  } = useSimulationStore();

  const [customRole, setCustomRole] = useState('');
  const [customSkill, setCustomSkill] = useState('');
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [isParsingResume, setIsParsingResume] = useState(false);

  const progress = ((currentStep + 1) / STEPS.length) * 100;

  // Handle resume file upload and parse text
  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setResumeError('File size must be less than 5MB');
      return;
    }

    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
    if (!validTypes.includes(file.type)) {
      setResumeError('Please upload a PDF or DOCX file');
      return;
    }

    setResumeError(null);
    setIsParsingResume(true);

    try {
      // For now, we'll read the file and send it to backend for parsing
      // The backend will extract text from PDF/DOCX
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/parse-resume', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to parse resume');
      }

      const data = await response.json();
      updateProfile({ 
        resume_text: data.text,
        resume_filename: file.name 
      });
    } catch (err) {
      console.error('Resume parsing error:', err);
      setResumeError('Failed to parse resume. Please try again or enter your information manually.');
    } finally {
      setIsParsingResume(false);
      // Reset file input
      e.target.value = '';
    }
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true, 'matching');
    setError(null);

    try {
      // Stage 1: Analyze and get top 3 career fits
      const result = await analyzeCareerFits(profile as CareerProfile);
      setMatchingResult(result);
      navigate('/career-fits');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Career analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const addRole = (role: string) => {
    if (role && !profile.specific_roles?.includes(role)) {
      updateProfile({
        specific_roles: [...(profile.specific_roles || []), role],
      });
    }
  };

  const removeRole = (role: string) => {
    updateProfile({
      specific_roles: profile.specific_roles?.filter((r) => r !== role),
    });
  };

  const toggleCareerField = (field: string) => {
    const fields = profile.target_career_fields || [];
    if (fields.includes(field)) {
      updateProfile({ target_career_fields: fields.filter((f) => f !== field) });
    } else {
      updateProfile({ target_career_fields: [...fields, field] });
    }
  };

  const toggleWorkEnv = (env: string) => {
    const envs = profile.preferred_work_env || [];
    if (envs.includes(env)) {
      updateProfile({ preferred_work_env: envs.filter((e) => e !== env) });
    } else {
      updateProfile({ preferred_work_env: [...envs, env] });
    }
  };

  const updateSkill = (skill: string, level: string) => {
    const skills = { ...(profile.technical_skills || {}) };
    if (level === 'None') {
      delete skills[skill];
    } else {
      skills[skill] = level;
    }
    updateProfile({ technical_skills: skills });
  };

  const addCustomSkill = () => {
    if (customSkill && !profile.technical_skills?.[customSkill]) {
      updateProfile({
        technical_skills: {
          ...(profile.technical_skills || {}),
          [customSkill]: 'Basic',
        },
      });
      setCustomSkill('');
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="education">Current Education Level *</Label>
                <Select
                  value={profile.current_education_level || ''}
                  onValueChange={(v) => updateProfile({ current_education_level: v })}
                >
                  <SelectTrigger id="education">
                    <SelectValue placeholder="Select your education level" />
                  </SelectTrigger>
                  <SelectContent>
                    {EDUCATION_LEVELS.map((level) => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="institution">Institution Name</Label>
                <Input
                  id="institution"
                  placeholder="e.g., IIT Delhi, Stanford University"
                  value={profile.institution_name || ''}
                  onChange={(e) => updateProfile({ institution_name: e.target.value })}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="major">Current Major/Field *</Label>
                <Input
                  id="major"
                  placeholder="e.g., Computer Science, Electrical Engineering"
                  value={profile.current_major || ''}
                  onChange={(e) => updateProfile({ current_major: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="graduation">Expected Graduation Year</Label>
                <Input
                  id="graduation"
                  type="number"
                  placeholder="e.g., 2027"
                  value={profile.expected_graduation_year || ''}
                  onChange={(e) =>
                    updateProfile({ expected_graduation_year: parseInt(e.target.value) || undefined })
                  }
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="gpa">Current GPA/CGPA</Label>
                <Input
                  id="gpa"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 8.5"
                  value={profile.current_gpa || ''}
                  onChange={(e) =>
                    updateProfile({ current_gpa: parseFloat(e.target.value) || undefined })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="scale">Grading Scale</Label>
                <Select
                  value={profile.grading_scale || '10.0'}
                  onValueChange={(v) => updateProfile({ grading_scale: v })}
                >
                  <SelectTrigger id="scale">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="4.0">4.0 Scale</SelectItem>
                    <SelectItem value="10.0">10.0 Scale</SelectItem>
                    <SelectItem value="100">Percentage</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="country">Current Country</Label>
              <Input
                id="country"
                placeholder="e.g., India, USA"
                value={profile.current_country || ''}
                onChange={(e) => updateProfile({ current_country: e.target.value })}
              />
            </div>

            <Separator className="my-6" />

            {/* Resume Upload Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Label>Upload Resume (Optional)</Label>
                <Badge variant="outline" className="text-xs">PDF or DOCX</Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Upload your resume for more personalized career recommendations. Our AI will analyze your experience, skills, and achievements to find the best career fits.
              </p>
              
              {profile.resume_text ? (
                <div className="flex items-center gap-3 p-4 border rounded-lg bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800">
                  <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-green-800 dark:text-green-200">Resume uploaded</p>
                    <p className="text-sm text-green-600 dark:text-green-400 truncate">
                      {profile.resume_filename || 'Resume.pdf'}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-100"
                    onClick={() => updateProfile({ resume_text: undefined, resume_filename: undefined })}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ) : isParsingResume ? (
                <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg bg-muted/30">
                  <Loader2 className="h-10 w-10 text-primary animate-spin mb-3" />
                  <span className="font-medium">Parsing resume...</span>
                  <span className="text-sm text-muted-foreground mt-1">Extracting your information</span>
                </div>
              ) : (
                <label
                  htmlFor="resume-upload"
                  className="flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg cursor-pointer hover:border-primary hover:bg-muted/50 transition-colors"
                >
                  <FileUp className="h-10 w-10 text-muted-foreground mb-3" />
                  <span className="font-medium">Click to upload resume</span>
                  <span className="text-sm text-muted-foreground mt-1">PDF or DOCX (max 5MB)</span>
                  <input
                    id="resume-upload"
                    type="file"
                    accept=".pdf,.docx,.doc"
                    className="hidden"
                    onChange={handleResumeUpload}
                  />
                </label>
              )}
              
              {resumeError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{resumeError}</AlertDescription>
                </Alert>
              )}
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label>Target Career Fields *</Label>
              <p className="text-sm text-muted-foreground">Select all that interest you</p>
              <div className="flex flex-wrap gap-2">
                {CAREER_FIELDS.map((field) => (
                  <Badge
                    key={field}
                    variant={profile.target_career_fields?.includes(field) ? 'default' : 'outline'}
                    className="cursor-pointer py-2 px-3"
                    onClick={() => toggleCareerField(field)}
                  >
                    {field}
                  </Badge>
                ))}
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <Label>Specific Roles You're Targeting</Label>
              <div className="flex flex-wrap gap-2 mb-3">
                {profile.specific_roles?.map((role) => (
                  <Badge key={role} variant="secondary" className="py-1 px-2">
                    {role}
                    <button
                      onClick={() => removeRole(role)}
                      className="ml-2 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                {ROLES.filter((r) => !profile.specific_roles?.includes(r)).map((role) => (
                  <Badge
                    key={role}
                    variant="outline"
                    className="cursor-pointer py-1 px-2 hover:bg-secondary"
                    onClick={() => addRole(role)}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    {role}
                  </Badge>
                ))}
              </div>
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Add custom role..."
                  value={customRole}
                  onChange={(e) => setCustomRole(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      addRole(customRole);
                      setCustomRole('');
                    }
                  }}
                />
                <Button
                  variant="outline"
                  onClick={() => {
                    addRole(customRole);
                    setCustomRole('');
                  }}
                >
                  Add
                </Button>
              </div>
            </div>

            <Separator />

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Primary Career Goal *</Label>
                <Select
                  value={profile.primary_career_goal || ''}
                  onValueChange={(v) => updateProfile({ primary_career_goal: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="What matters most to you?" />
                  </SelectTrigger>
                  <SelectContent>
                    {CAREER_GOALS.map((goal) => (
                      <SelectItem key={goal} value={goal}>
                        {goal}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Desired Role Level</Label>
                <Select
                  value={profile.desired_role_level || ''}
                  onValueChange={(v) => updateProfile({ desired_role_level: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Where do you want to be?" />
                  </SelectTrigger>
                  <SelectContent>
                    {ROLE_LEVELS.map((level) => (
                      <SelectItem key={level} value={level}>
                        {level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label>Technical Skills</Label>
              <p className="text-sm text-muted-foreground">Rate your proficiency in each skill</p>
              <div className="space-y-3">
                {[...COMMON_SKILLS, ...Object.keys(profile.technical_skills || {}).filter(
                  (s) => !COMMON_SKILLS.includes(s)
                )].map((skill) => (
                  <div key={skill} className="flex items-center gap-4">
                    <span className="w-36 text-sm">{skill}</span>
                    <Select
                      value={profile.technical_skills?.[skill] || 'None'}
                      onValueChange={(v) => updateSkill(skill, v)}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {SKILL_LEVELS.map((level) => (
                          <SelectItem key={level} value={level}>
                            {level}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <Input
                  placeholder="Add custom skill..."
                  value={customSkill}
                  onChange={(e) => setCustomSkill(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') addCustomSkill();
                  }}
                />
                <Button variant="outline" onClick={addCustomSkill}>
                  Add Skill
                </Button>
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <Label>Soft Skills (Rate 1-5)</Label>
              {['Communication', 'Problem Solving', 'Leadership', 'Teamwork', 'Creativity'].map(
                (skill) => (
                  <div key={skill} className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">{skill}</span>
                      <span className="text-sm text-muted-foreground">
                        {profile.soft_skills?.[skill] || 3}/5
                      </span>
                    </div>
                    <Slider
                      value={[profile.soft_skills?.[skill] || 3]}
                      min={1}
                      max={5}
                      step={1}
                      onValueChange={([v]) =>
                        updateProfile({
                          soft_skills: { ...(profile.soft_skills || {}), [skill]: v },
                        })
                      }
                    />
                  </div>
                )
              )}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label>Preferred Work Environments</Label>
              <div className="flex flex-wrap gap-2">
                {WORK_ENVIRONMENTS.map((env) => (
                  <Badge
                    key={env}
                    variant={profile.preferred_work_env?.includes(env) ? 'default' : 'outline'}
                    className="cursor-pointer py-2 px-3"
                    onClick={() => toggleWorkEnv(env)}
                  >
                    {env}
                  </Badge>
                ))}
              </div>
            </div>

            <Separator />

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Work Style</Label>
                <Select
                  value={profile.work_style || ''}
                  onValueChange={(v) => updateProfile({ work_style: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="How do you prefer to work?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Theoretical">Theoretical - Research & Analysis</SelectItem>
                    <SelectItem value="Practical">Practical - Hands-on Building</SelectItem>
                    <SelectItem value="Mixed">Mixed - Both</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Role Preference</Label>
                <Select
                  value={profile.role_preference || ''}
                  onValueChange={(v) => updateProfile({ role_preference: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="What type of role do you prefer?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Structured">Structured - Clear processes</SelectItem>
                    <SelectItem value="Dynamic">Dynamic - Fast-paced, changing</SelectItem>
                    <SelectItem value="Flexible">Flexible - Mix of both</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Risk Tolerance</Label>
                <Select
                  value={profile.risk_tolerance || 'Medium'}
                  onValueChange={(v) => updateProfile({ risk_tolerance: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Low">Low - Prefer stability</SelectItem>
                    <SelectItem value="Medium">Medium - Balanced</SelectItem>
                    <SelectItem value="High">High - Willing to take risks</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Market Awareness</Label>
                <Select
                  value={profile.market_awareness || 'Medium'}
                  onValueChange={(v) => updateProfile({ market_awareness: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Low">Low - Not very informed</SelectItem>
                    <SelectItem value="Medium">Medium - Somewhat informed</SelectItem>
                    <SelectItem value="High">High - Very well informed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Optimism Level for Simulation</Label>
              <Select
                value={profile.optimism_level || 'Balanced'}
                onValueChange={(v) => updateProfile({ optimism_level: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Conservative">Conservative - Show worst-case scenarios</SelectItem>
                  <SelectItem value="Balanced">Balanced - Realistic projections</SelectItem>
                  <SelectItem value="Optimistic">Optimistic - Show best-case scenarios</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Investment Capacity</Label>
                <Select
                  value={profile.investment_capacity || ''}
                  onValueChange={(v) => updateProfile({ investment_capacity: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="How much can you invest?" />
                  </SelectTrigger>
                  <SelectContent>
                    {INVESTMENT_CAPACITIES.map((cap) => (
                      <SelectItem key={cap} value={cap}>
                        {cap}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Target Minimum Salary (Annual USD)</Label>
                <Input
                  type="number"
                  placeholder="e.g., 100000"
                  value={profile.target_min_salary || ''}
                  onChange={(e) =>
                    updateProfile({ target_min_salary: parseFloat(e.target.value) || undefined })
                  }
                />
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Hours Available Per Week for Upskilling</Label>
                  <span className="text-sm text-muted-foreground">
                    {profile.hours_per_week || 20} hours
                  </span>
                </div>
                <Slider
                  value={[profile.hours_per_week || 20]}
                  min={5}
                  max={50}
                  step={5}
                  onValueChange={([v]) => updateProfile({ hours_per_week: v })}
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="mentor"
                  checked={profile.has_mentor || false}
                  onCheckedChange={(checked) => updateProfile({ has_mentor: checked as boolean })}
                />
                <Label htmlFor="mentor">I have access to a mentor or career guidance</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="dependents"
                  checked={profile.financial_dependents || false}
                  onCheckedChange={(checked) =>
                    updateProfile({ financial_dependents: checked as boolean })
                  }
                />
                <Label htmlFor="dependents">I have financial dependents</Label>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Additional Context (Optional)</Label>
              <Textarea
                placeholder="Any other information that might be relevant for your career planning..."
                value={profile.financial_details || ''}
                onChange={(e) => updateProfile({ financial_details: e.target.value })}
                rows={4}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/')} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-3xl font-bold mb-2">Career Simulation</h1>
          <p className="text-muted-foreground">
            Tell us about yourself so we can create your personalized career roadmap
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-muted-foreground">
              Step {currentStep + 1} of {STEPS.length}
            </span>
            <span className="text-sm text-muted-foreground">{Math.round(progress)}% complete</span>
          </div>
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between mt-4">
            {STEPS.map((step, index) => (
              <button
                key={step.id}
                onClick={() => setCurrentStep(index)}
                className={`flex flex-col items-center gap-1 transition-colors ${
                  index === currentStep
                    ? 'text-primary'
                    : index < currentStep
                    ? 'text-muted-foreground'
                    : 'text-muted-foreground/50'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    index === currentStep
                      ? 'bg-primary text-primary-foreground'
                      : index < currentStep
                      ? 'bg-primary/20 text-primary'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  <step.icon className="h-4 w-4" />
                </div>
                <span className="text-xs hidden md:block">{step.title}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Form Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {(() => {
                const StepIcon = STEPS[currentStep].icon;
                return <StepIcon className="h-5 w-5" />;
              })()}
              {STEPS[currentStep].title}
            </CardTitle>
            <CardDescription>
              {currentStep === 0 && 'Tell us about your educational background'}
              {currentStep === 1 && 'What are your career aspirations?'}
              {currentStep === 2 && 'What skills do you have and what interests you?'}
              {currentStep === 3 && 'How do you prefer to work?'}
              {currentStep === 4 && 'What resources do you have available?'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderStep()}

            {/* Navigation */}
            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                onClick={handlePrev}
                disabled={currentStep === 0}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>

              {currentStep < STEPS.length - 1 ? (
                <Button onClick={handleNext}>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <Button onClick={handleSubmit} disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Simulating...
                    </>
                  ) : (
                    <>
                      Run Simulation
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </>
                  )}
                </Button>
              )}
            </div>

            {useSimulationStore.getState().error && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{useSimulationStore.getState().error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
