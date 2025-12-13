import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  ArrowLeft,
  Target,
  TrendingUp,
  DollarSign,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Award,
  Briefcase,
  GraduationCap,
  ChevronRight,
  RotateCcw,
  Share2,
  Lightbulb,
  AlertCircle,
  Sparkles,
  Brain,
  Zap,
  Heart,
  Star,
  ArrowRight,
  Info,
  MessageSquare,
  Loader2,
  FileText,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useSimulationStore } from '@/lib/store';
import type { CareerPath } from '@/lib/api';
import EmbedPopupAgentClient from '@/components/embed-popup/agent-client';
import { APP_CONFIG_DEFAULTS } from '@/app-config';
import { exportDashboardToPDF } from '@/lib/pdfExport';

// Color schemes
const COLORS = {
  primary: '#8884d8',
  secondary: '#82ca9d', 
  tertiary: '#ffc658',
  quaternary: '#ff7300',
  danger: '#ef4444',
  warning: '#f59e0b',
  success: '#22c55e',
  info: '#3b82f6',
};

const PIE_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#ef4444', '#3b82f6'];

export default function DashboardPage() {
  const navigate = useNavigate();
  const { result, reset, profile, selectedCareer, resetToCareerSelection } = useSimulationStore();
  const [activePathType, setActivePathType] = useState<string>('realistic');
  const [isExporting, setIsExporting] = useState<boolean>(false);

  useEffect(() => {
    if (!result) {
      navigate('/simulate');
    }
  }, [result, navigate]);

  useEffect(() => {
    if (result?.timeline?.recommended_path) {
      setActivePathType(result.timeline.recommended_path);
    }
  }, [result]);

  // PDF Export Handler
  const handleExportPDF = async () => {
    if (!result) return;
    
    setIsExporting(true);
    try {
      await exportDashboardToPDF(result, profile, selectedCareer, {
        includeTimeline: true,
        includeFinancials: true,
        includeRisks: true,
        includeSkillGaps: true,
        includeRecommendations: true,
      });
    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setIsExporting(false);
    }
  };

  if (!result) {
    return null;
  }

  const {
    summary,
    dashboard_data,
    timeline,
    financial_analysis,
    risk_assessment,
    gap_analysis,
    warnings,
  } = result;

  // Enhanced data extraction
  const salaryData = dashboard_data?.salary_progression || [];
  const skillRadarData = dashboard_data?.skill_radar || [];
  const riskBreakdownData = dashboard_data?.risk_breakdown || [];
  const gapAnalysisChart = dashboard_data?.gap_analysis_chart || [];
  const investmentBreakdown = dashboard_data?.investment_breakdown || [];
  const pathComparison = dashboard_data?.path_comparison || [];
  const keyInsights = dashboard_data?.key_insights || [];
  const decisionRationale = dashboard_data?.decision_rationale || [];
  const topRecommendations = dashboard_data?.top_recommendations || [];
  const immediateActions = dashboard_data?.immediate_actions || [];
  
  // Fallback risk breakdown if not available from dashboard_data
  const riskBreakdown = riskBreakdownData.length > 0 ? riskBreakdownData : (risk_assessment
    ? [
        { name: 'Market', value: risk_assessment.market_risk_score, fill: COLORS.primary },
        { name: 'Personal', value: risk_assessment.personal_risk_score, fill: COLORS.secondary },
        { name: 'Financial', value: risk_assessment.financial_risk_score, fill: COLORS.tertiary },
        { name: 'Technical', value: risk_assessment.technical_risk_score, fill: COLORS.quaternary },
      ]
    : []);

  const handleNewSimulation = () => {
    reset();
    navigate('/simulate');
  };

  const getPath = (pathType: string): CareerPath | undefined => {
    if (!timeline) return undefined;
    if (pathType === 'conservative') return timeline.conservative_path;
    if (pathType === 'realistic') return timeline.realistic_path;
    if (pathType === 'ambitious') return timeline.ambitious_path;
    return undefined;
  };

  const recommendedPath = timeline ? getPath(timeline.recommended_path) : undefined;
  const activePath = timeline ? getPath(activePathType) : undefined;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <Button variant="ghost" asChild className="mb-2">
              <Link to="/">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Link>
            </Button>
            <h1 className="text-3xl font-bold">Your Career Roadmap</h1>
            <p className="text-muted-foreground">
              Personalized simulation
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleNewSimulation}>
              <RotateCcw className="h-4 w-4 mr-2" />
              New Simulation
            </Button>
            <Button 
              variant="outline" 
              onClick={handleExportPDF}
              disabled={isExporting}
              className="min-w-[120px]"
            >
              {isExporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  Export PDF
                </>
              )}
            </Button>
            <Button variant="outline">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>

        {/* Warnings */}
        {warnings && warnings.length > 0 && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Vibe Check Warnings</AlertTitle>
            <AlertDescription>
              <ul className="list-disc list-inside mt-2">
                {warnings.map((warning, i) => (
                  <li key={i}>{warning}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {/* Selected Career Card with Reasoning */}
        {selectedCareer && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <Card className="border-2 border-primary/30 bg-gradient-to-r from-primary/5 to-background">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-primary/10">
                      <Target className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{selectedCareer.career_title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                          {selectedCareer.overall_fit_score}% Match
                        </Badge>
                        <span>Your Selected Career Path</span>
                      </CardDescription>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => {
                    resetToCareerSelection();
                    navigate('/career-fits');
                  }}>
                    Change Selection
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <Accordion type="single" collapsible className="w-full">
                  <AccordionItem value="why-chosen" className="border-none">
                    <AccordionTrigger className="hover:no-underline py-3">
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Brain className="h-4 w-4 text-purple-500" />
                        Why This Career Fits You
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="grid md:grid-cols-2 gap-4 pt-2">
                        {/* Strengths Match */}
                        <div className="p-4 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                          <div className="flex items-center gap-2 mb-3">
                            <Zap className="h-4 w-4 text-emerald-600" />
                            <span className="font-medium text-emerald-700 dark:text-emerald-300">Your Strengths Alignment</span>
                          </div>
                          <ul className="space-y-2">
                            {selectedCareer.reasoning.strengths_alignment.map((strength: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-sm">
                                <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                                <span>{strength}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Interest Alignment */}
                        <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                          <div className="flex items-center gap-2 mb-3">
                            <Heart className="h-4 w-4 text-blue-600" />
                            <span className="font-medium text-blue-700 dark:text-blue-300">Interest Match</span>
                          </div>
                          <ul className="space-y-2">
                            {selectedCareer.reasoning.interest_match.map((interest: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-sm">
                                <Star className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                                <span>{interest}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Why Now */}
                        <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
                          <div className="flex items-center gap-2 mb-3">
                            <Sparkles className="h-4 w-4 text-amber-600" />
                            <span className="font-medium text-amber-700 dark:text-amber-300">Why Now Is The Right Time</span>
                          </div>
                          <p className="text-sm">{selectedCareer.reasoning.why_now}</p>
                          <div className="mt-2 space-y-1">
                            {selectedCareer.reasoning.market_demand_reasons.map((reason: string, i: number) => (
                              <div key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                                <ArrowRight className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
                                <span>{reason}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Potential Challenges */}
                        <div className="p-4 rounded-lg bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800">
                          <div className="flex items-center gap-2 mb-3">
                            <Info className="h-4 w-4 text-rose-600" />
                            <span className="font-medium text-rose-700 dark:text-rose-300">Challenges to Prepare For</span>
                          </div>
                          <ul className="space-y-2">
                            {selectedCareer.reasoning.potential_challenges.map((challenge: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-sm">
                                <AlertTriangle className="h-4 w-4 text-rose-500 flex-shrink-0 mt-0.5" />
                                <span>{challenge}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Fit Scores Breakdown */}
                      <div className="mt-4 p-4 rounded-lg bg-muted/50">
                        <h5 className="font-medium mb-3 flex items-center gap-2">
                          <MessageSquare className="h-4 w-4" />
                          Detailed Fit Breakdown
                        </h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-emerald-600">{selectedCareer.skill_fit_score}%</div>
                            <div className="text-xs text-muted-foreground">Skill Fit</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">{selectedCareer.interest_fit_score}%</div>
                            <div className="text-xs text-muted-foreground">Interest Fit</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">{selectedCareer.market_fit_score}%</div>
                            <div className="text-xs text-muted-foreground">Market Fit</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-amber-600">{selectedCareer.personality_fit_score}%</div>
                            <div className="text-xs text-muted-foreground">Personality Fit</div>
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900">
                  <Target className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold">
                    {risk_assessment?.success_probability_score?.toFixed(0) || summary?.success_probability || '--'}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900">
                  <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Timeline</p>
                  <p className="text-2xl font-bold">
                    {recommendedPath?.total_years || summary?.timeline_years || '--'} Years
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-900">
                  <DollarSign className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Investment</p>
                  <p className="text-2xl font-bold">
                    ${((financial_analysis?.total_investment_required || 0) / 1000).toFixed(0)}K
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900">
                  <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Expected Salary</p>
                  <p className="text-2xl font-bold">
                    ${((recommendedPath?.final_expected_salary || 0) / 1000).toFixed(0)}K
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="timeline" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
            <TabsTrigger value="skills">Skills Gap</TabsTrigger>
            <TabsTrigger value="financial">Financial</TabsTrigger>
            <TabsTrigger value="risks">Risks</TabsTrigger>
            <TabsTrigger value="insights">Insights</TabsTrigger>
          </TabsList>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Path Selector */}
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="text-lg">Career Paths</CardTitle>
                  <CardDescription>Choose your preferred pace</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {['conservative', 'realistic', 'ambitious'].map((pathType) => {
                    const path = getPath(pathType);
                    if (!path) return null;
                    const isRecommended = timeline?.recommended_path === pathType;
                    const isActive = activePathType === pathType;
                    return (
                      <div
                        key={pathType}
                        onClick={() => setActivePathType(pathType)}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                          isActive
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold capitalize">{pathType}</span>
                          <div className="flex gap-1">
                            {isActive && (
                              <Badge variant="outline" className="text-xs">
                                Viewing
                              </Badge>
                            )}
                            {isRecommended && (
                              <Badge variant="default" className="text-xs">
                                Recommended
                              </Badge>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{path.path_label}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{path.total_years} years</span>
                          <span>${(path.final_expected_salary / 1000).toFixed(0)}K</span>
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Timeline Details */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg">Year-by-Year Roadmap</CardTitle>
                  <CardDescription>
                    {activePath?.path_label || recommendedPath?.path_label || 'Your career journey'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[500px] pr-4">
                    <div className="space-y-6">
                      {(activePath || recommendedPath)?.yearly_plans?.map((year, index) => (
                        <div key={year.year_number} className="relative">
                          {index !== ((activePath || recommendedPath)?.yearly_plans?.length || 0) - 1 && (
                            <div className="absolute left-4 top-12 bottom-0 w-0.5 bg-border" />
                          )}
                          <div className="flex gap-4">
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                              {year.year_number}
                            </div>
                            <div className="flex-1 pb-6">
                              <div className="flex items-center gap-2 mb-1">
                                <h4 className="font-semibold">{year.year_label}</h4>
                                <Badge variant="outline" className="text-xs">
                                  {year.phase}
                                </Badge>
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">
                                {year.primary_focus}
                              </p>
                              
                              {/* Phase & Focus Reasoning */}
                              {(year.phase_reasoning || year.focus_reasoning) && (
                                <Accordion type="single" collapsible className="mb-3">
                                  <AccordionItem value="reasoning" className="border-none">
                                    <AccordionTrigger className="hover:no-underline py-1 text-xs">
                                      <span className="flex items-center gap-1 text-muted-foreground">
                                        <Brain className="h-3 w-3" />
                                        Why this phase?
                                      </span>
                                    </AccordionTrigger>
                                    <AccordionContent className="text-xs text-muted-foreground pb-2">
                                      {year.phase_reasoning && <p className="mb-1">{year.phase_reasoning}</p>}
                                      {year.focus_reasoning && <p>{year.focus_reasoning}</p>}
                                    </AccordionContent>
                                  </AccordionItem>
                                </Accordion>
                              )}

                              {/* Milestones */}
                              <div className="space-y-2">
                                {year.milestones?.map((milestone, mIndex) => (
                                  <Accordion key={mIndex} type="single" collapsible>
                                    <AccordionItem value={`milestone-${mIndex}`} className="border rounded bg-muted/50">
                                      <AccordionTrigger className="hover:no-underline px-2 py-2">
                                        <div className="flex items-start gap-2 text-sm text-left">
                                          <div className="flex-shrink-0 mt-0.5">
                                            {milestone.type === 'education' && (
                                              <GraduationCap className="h-4 w-4 text-blue-500" />
                                            )}
                                            {milestone.type === 'skill' && (
                                              <Award className="h-4 w-4 text-green-500" />
                                            )}
                                            {milestone.type === 'career' && (
                                              <Briefcase className="h-4 w-4 text-purple-500" />
                                            )}
                                            {milestone.type === 'certification' && (
                                              <CheckCircle2 className="h-4 w-4 text-orange-500" />
                                            )}
                                            {!['education', 'skill', 'career', 'certification'].includes(
                                              milestone.type
                                            ) && <ChevronRight className="h-4 w-4" />}
                                          </div>
                                          <div>
                                            <span className="font-medium">{milestone.title}</span>
                                            <p className="text-xs text-muted-foreground">
                                              Q{milestone.quarter} •{' '}
                                              {milestone.estimated_hours > 0 &&
                                                `${milestone.estimated_hours}h`}
                                              {milestone.estimated_cost > 0 &&
                                                ` • $${milestone.estimated_cost.toLocaleString()}`}
                                            </p>
                                          </div>
                                        </div>
                                      </AccordionTrigger>
                                      <AccordionContent className="px-3 pb-3">
                                        <p className="text-sm mb-2">{milestone.description}</p>
                                        {milestone.reasoning && (
                                          <div className="p-2 bg-background rounded border mb-2">
                                            <p className="text-xs text-muted-foreground">
                                              <Brain className="h-3 w-3 inline mr-1" />
                                              <strong>Why important:</strong> {milestone.reasoning}
                                            </p>
                                          </div>
                                        )}
                                        {milestone.dependencies && milestone.dependencies.length > 0 && (
                                          <div className="mb-2">
                                            <p className="text-xs font-medium">Prerequisites:</p>
                                            <ul className="text-xs text-muted-foreground">
                                              {milestone.dependencies.map((dep, j) => (
                                                <li key={j}>• {dep}</li>
                                              ))}
                                            </ul>
                                          </div>
                                        )}
                                        {milestone.risk_if_skipped && (
                                          <div className="p-2 bg-red-50 dark:bg-red-950/30 rounded border border-red-200 dark:border-red-800">
                                            <p className="text-xs text-red-700 dark:text-red-300">
                                              <AlertTriangle className="h-3 w-3 inline mr-1" />
                                              <strong>Risk if skipped:</strong> {milestone.risk_if_skipped}
                                            </p>
                                          </div>
                                        )}
                                      </AccordionContent>
                                    </AccordionItem>
                                  </Accordion>
                                ))}
                              </div>

                              {/* Success Indicators */}
                              {year.success_indicators && year.success_indicators.length > 0 && (
                                <div className="mt-3 p-2 bg-green-50 dark:bg-green-950/30 rounded border border-green-200 dark:border-green-800">
                                  <p className="text-xs font-medium text-green-700 dark:text-green-300 mb-1">
                                    Success Indicators:
                                  </p>
                                  <ul className="text-xs text-muted-foreground">
                                    {year.success_indicators.slice(0, 3).map((indicator, i) => (
                                      <li key={i}>✓ {indicator}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Expected Outcome */}
                              {year.expected_role && (
                                <div className="mt-3 p-2 bg-primary/5 rounded text-sm">
                                  <span className="text-muted-foreground">Expected: </span>
                                  <span className="font-medium">{year.expected_role}</span>
                                  {year.expected_salary_range && (
                                    <span className="text-muted-foreground">
                                      {' '}
                                      • {year.expected_salary_range}
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            {/* Salary Projection Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Salary Projection</CardTitle>
                <CardDescription>Expected earnings across different paths</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={salaryData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis tickFormatter={(v) => `$${v / 1000}K`} />
                      <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="conservative"
                        stroke="#82ca9d"
                        name="Conservative"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="realistic"
                        stroke="#8884d8"
                        name="Realistic"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="ambitious"
                        stroke="#ffc658"
                        name="Ambitious"
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Skills Gap Tab */}
          <TabsContent value="skills" className="space-y-6">
            {/* Gap Analysis Reasoning */}
            {gap_analysis?.analysis_reasoning && (
              <Alert className="border-blue-200 bg-blue-50 dark:bg-blue-950/30">
                <Brain className="h-4 w-4 text-blue-600" />
                <AlertTitle>Gap Analysis Summary</AlertTitle>
                <AlertDescription className="mt-2">
                  {gap_analysis.analysis_reasoning}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Radar Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Skills Radar</CardTitle>
                  <CardDescription>Current vs Required skill levels</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={skillRadarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="skill" tick={{ fontSize: 12 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} />
                        <Radar
                          name="Current"
                          dataKey="current"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.3}
                        />
                        <Radar
                          name="Required"
                          dataKey="required"
                          stroke="#82ca9d"
                          fill="#82ca9d"
                          fillOpacity={0.3}
                        />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Gap Overview with Reasoning */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Gap Overview</CardTitle>
                  <CardDescription>
                    Overall gap score:{' '}
                    <span
                      className={`font-bold ${
                        (gap_analysis?.overall_gap_score || 0) > 60
                          ? 'text-red-500'
                          : (gap_analysis?.overall_gap_score || 0) > 30
                          ? 'text-yellow-500'
                          : 'text-green-500'
                      }`}
                    >
                      {gap_analysis?.overall_gap_score?.toFixed(0) || 0}%
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Gap Level</span>
                      <Badge
                        variant={
                          gap_analysis?.gap_category === 'severe'
                            ? 'destructive'
                            : gap_analysis?.gap_category === 'significant'
                            ? 'default'
                            : 'secondary'
                        }
                      >
                        {gap_analysis?.gap_category || 'Unknown'}
                      </Badge>
                    </div>
                    <Progress value={100 - (gap_analysis?.overall_gap_score || 0)} />
                  </div>

                  <Separator />

                  {/* Quick Wins */}
                  {gap_analysis?.quick_wins && gap_analysis.quick_wins.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 flex items-center gap-2">
                        <Zap className="h-4 w-4 text-green-500" />
                        Quick Wins
                      </h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        {gap_analysis.quick_wins.map((win: string, i: number) => (
                          <li key={i} className="flex items-start gap-2">
                            <CheckCircle2 className="h-3 w-3 text-green-500 flex-shrink-0 mt-1" />
                            <span>{win}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Separator />

                  {/* Top Priorities */}
                  {gap_analysis?.top_priorities && gap_analysis.top_priorities.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 flex items-center gap-2">
                        <Target className="h-4 w-4 text-orange-500" />
                        Top Priorities
                      </h4>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        {gap_analysis.top_priorities.map((priority: string, i: number) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-orange-500 font-semibold">{i + 1}.</span>
                            <span>{priority}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Separator />

                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      Critical Bottlenecks
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {gap_analysis?.critical_bottlenecks?.map((b, i) => (
                        <li key={i}>• {b}</li>
                      )) || <li>No critical bottlenecks identified</li>}
                    </ul>
                  </div>

                  <Separator />

                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      Your Strengths
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {gap_analysis?.existing_strengths?.map((s, i) => (
                        <li key={i}>• {s}</li>
                      )) || <li>Building your foundation</li>}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Gap Analysis Bar Chart */}
            {gapAnalysisChart.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Gap Analysis by Category</CardTitle>
                  <CardDescription>Education, Experience, and Certification gaps compared</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={gapAnalysisChart} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" domain={[0, 100]} />
                        <YAxis type="category" dataKey="category" width={100} />
                        <Tooltip formatter={(v: number) => `${v}% gap`} />
                        <Bar dataKey="gap" fill={COLORS.primary} name="Gap Score" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Skill Gaps Detail with Reasoning */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Technical Skill Gaps</CardTitle>
                <CardDescription>Skills you need to develop with learning paths</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  {gap_analysis?.technical_skill_gaps?.map((gap, i) => (
                    <div key={i} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{gap.skill_name}</h4>
                        <div className="flex gap-2">
                          {gap.priority && (
                            <Badge variant="outline" className="text-xs">
                              {gap.priority}
                            </Badge>
                          )}
                          <Badge
                            variant={
                              gap.gap_severity > 70
                                ? 'destructive'
                                : gap.gap_severity > 40
                                ? 'default'
                                : 'secondary'
                            }
                          >
                            {gap.gap_severity.toFixed(0)}% gap
                          </Badge>
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground mb-2">
                        <span>{gap.current_level}</span>
                        <span className="mx-2">→</span>
                        <span className="text-foreground">{gap.required_level}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{gap.estimated_time_to_close}</span>
                      </div>
                      
                      {/* Reasoning */}
                      {gap.reasoning && (
                        <div className="mt-2 pt-2 border-t">
                          <p className="text-xs text-muted-foreground italic">
                            <Brain className="h-3 w-3 inline mr-1" />
                            {gap.reasoning}
                          </p>
                        </div>
                      )}
                      
                      {/* Learning Path */}
                      {gap.learning_path && gap.learning_path.length > 0 && (
                        <div className="mt-2 pt-2 border-t">
                          <p className="text-xs font-medium mb-1">Learning Path:</p>
                          <div className="flex flex-wrap gap-1">
                            {gap.learning_path.slice(0, 3).map((step: string, j: number) => (
                              <Badge key={j} variant="outline" className="text-xs">
                                {j + 1}. {step}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {gap.recommended_resources?.length > 0 && (
                        <div className="mt-2 pt-2 border-t">
                          <p className="text-xs font-medium mb-1">Resources:</p>
                          <p className="text-xs text-muted-foreground">
                            {gap.recommended_resources.slice(0, 2).join(', ')}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Education & Experience Gap Reasoning */}
            <div className="grid lg:grid-cols-2 gap-6">
              {gap_analysis?.education_gap_reasoning && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <GraduationCap className="h-5 w-5" />
                      Education Gap
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between items-center mb-4">
                      <span>Gap Level</span>
                      <Badge variant={(gap_analysis.education_gap_score || 0) > 50 ? 'destructive' : 'secondary'}>
                        {gap_analysis.education_gap_score?.toFixed(0)}%
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{gap_analysis.education_gap_reasoning}</p>
                  </CardContent>
                </Card>
              )}
              
              {gap_analysis?.experience_gap_reasoning && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Briefcase className="h-5 w-5" />
                      Experience Gap
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between items-center mb-4">
                      <span>Gap Level</span>
                      <Badge variant={(gap_analysis.experience_gap_score || 0) > 50 ? 'destructive' : 'secondary'}>
                        {gap_analysis.experience_gap_score?.toFixed(0)}%
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{gap_analysis.experience_gap_reasoning}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Financial Tab */}
          <TabsContent value="financial" className="space-y-6">
            {/* Investment Reasoning */}
            {financial_analysis?.investment_reasoning && (
              <Alert className="border-green-200 bg-green-50 dark:bg-green-950/30">
                <DollarSign className="h-4 w-4 text-green-600" />
                <AlertTitle>Investment Analysis</AlertTitle>
                <AlertDescription className="mt-2">
                  {financial_analysis.investment_reasoning}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <DollarSign className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">Total Investment</p>
                    <p className="text-3xl font-bold">
                      ${financial_analysis?.total_investment_required?.toLocaleString() || 0}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">5-Year ROI</p>
                    <p className="text-3xl font-bold text-green-600">
                      {financial_analysis?.five_year_roi?.toFixed(0) || 0}%
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Calendar className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">Break-even</p>
                    <p className="text-3xl font-bold">
                      Year {financial_analysis?.break_even_year || '--'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Target className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">10-Year Earnings</p>
                    <p className="text-3xl font-bold text-blue-600">
                      ${((financial_analysis?.ten_year_projected_earnings || 0) / 1000000).toFixed(1)}M
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Break-even Reasoning */}
            {financial_analysis?.break_even_reasoning && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-500" />
                    Break-even Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{financial_analysis.break_even_reasoning}</p>
                </CardContent>
              </Card>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Investment Breakdown Pie Chart */}
              {investmentBreakdown.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Investment Breakdown</CardTitle>
                    <CardDescription>Where your money goes</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={investmentBreakdown}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            dataKey="value"
                            label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                          >
                            {investmentBreakdown.map((_entry, index) => (
                              <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Yearly Financials Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Yearly Cash Flow</CardTitle>
                  <CardDescription>Investment vs Income over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={financial_analysis?.yearly_financials || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year_number" />
                        <YAxis tickFormatter={(v) => `$${v / 1000}K`} />
                        <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
                        <Legend />
                        <Bar dataKey="total_investment" name="Investment" fill="#ff7300" />
                        <Bar dataKey="expected_income" name="Income" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Salary Milestones */}
            {financial_analysis?.salary_milestones && financial_analysis.salary_milestones.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Salary Progression Milestones</CardTitle>
                  <CardDescription>Expected salary growth over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {financial_analysis.salary_milestones.map((milestone, i) => (
                      <div key={i} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold">Year {milestone.year}: {milestone.role}</h4>
                            <p className="text-2xl font-bold text-green-600">
                              ${milestone.expected_salary?.toLocaleString()}/year
                            </p>
                          </div>
                          <Badge variant="outline">Year {milestone.year}</Badge>
                        </div>
                        {milestone.reasoning && (
                          <p className="text-sm text-muted-foreground mt-2 italic">
                            <Brain className="h-3 w-3 inline mr-1" />
                            {milestone.reasoning}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Financial Details */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Affordability Assessment</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Rating</span>
                    <Badge
                      variant={
                        financial_analysis?.affordability_rating === 'unfeasible'
                          ? 'destructive'
                          : financial_analysis?.affordability_rating === 'stretch'
                          ? 'default'
                          : 'secondary'
                      }
                    >
                      {financial_analysis?.affordability_rating || 'Unknown'}
                    </Badge>
                  </div>
                  
                  {/* Affordability Reasoning */}
                  {financial_analysis?.affordability_reasoning && (
                    <div className="p-3 bg-muted/50 rounded-lg">
                      <p className="text-sm text-muted-foreground italic">
                        <Brain className="h-3 w-3 inline mr-1" />
                        {financial_analysis.affordability_reasoning}
                      </p>
                    </div>
                  )}
                  
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-2">Notes</h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {financial_analysis?.affordability_notes?.map((note, i) => (
                        <li key={i}>• {note}</li>
                      )) || <li>No specific notes</li>}
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Funding Options</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {financial_analysis?.funding_options?.map((option, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        {option}
                      </li>
                    )) || <li className="text-muted-foreground">No funding options suggested</li>}
                  </ul>
                  <Separator className="my-4" />
                  <h4 className="font-medium mb-2">Cost Saving Tips</h4>
                  <ul className="space-y-2">
                    {financial_analysis?.cost_saving_opportunities?.map((tip, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Lightbulb className="h-4 w-4 text-yellow-500" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* ROI Analysis */}
            {financial_analysis?.five_year_roi_reasoning && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-500" />
                    ROI Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{financial_analysis.five_year_roi_reasoning}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Risks Tab */}
          <TabsContent value="risks" className="space-y-6">
            {/* Success Reasoning */}
            {risk_assessment?.success_reasoning && (
              <Alert className="border-purple-200 bg-purple-50 dark:bg-purple-950/30">
                <Target className="h-4 w-4 text-purple-600" />
                <AlertTitle>Success Analysis</AlertTitle>
                <AlertDescription className="mt-2">
                  {risk_assessment.success_reasoning}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Risk Overview */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Risk Overview</CardTitle>
                  <CardDescription>
                    Success Probability:{' '}
                    <span className="font-bold text-primary">
                      {risk_assessment?.success_probability_score?.toFixed(0) || '--'}%
                    </span>
                    {risk_assessment?.confidence_interval && (
                      <span className="text-muted-foreground">
                        {' '}
                        ({risk_assessment.confidence_interval})
                      </span>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[250px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={riskBreakdown as Array<{ name: string; value: number; fill: string }>}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${(value ?? 0).toFixed(0)}`}
                        >
                          {riskBreakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center gap-4 mt-4">
                    {riskBreakdown.map((item) => (
                      <div key={item.name} className="flex items-center gap-2 text-sm">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.fill }}
                        />
                        <span>{item.name}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Key Concerns & Opportunities */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Key Concerns & Opportunities</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      Key Concerns
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {risk_assessment?.key_concerns?.map((concern, i) => (
                        <li key={i}>• {concern}</li>
                      )) || <li>No major concerns identified</li>}
                    </ul>
                  </div>
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      Key Opportunities
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {risk_assessment?.key_opportunities?.map((opp, i) => (
                        <li key={i}>• {opp}</li>
                      )) || <li>Many opportunities await</li>}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Risk Category Reasoning */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {risk_assessment?.market_risk_reasoning && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Market Risk
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">{risk_assessment.market_risk_score}/100</div>
                    <p className="text-xs text-muted-foreground">{risk_assessment.market_risk_reasoning}</p>
                  </CardContent>
                </Card>
              )}
              {risk_assessment?.personal_risk_reasoning && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Info className="h-4 w-4" />
                      Personal Risk
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">{risk_assessment.personal_risk_score}/100</div>
                    <p className="text-xs text-muted-foreground">{risk_assessment.personal_risk_reasoning}</p>
                  </CardContent>
                </Card>
              )}
              {risk_assessment?.financial_risk_reasoning && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      Financial Risk
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">{risk_assessment.financial_risk_score}/100</div>
                    <p className="text-xs text-muted-foreground">{risk_assessment.financial_risk_reasoning}</p>
                  </CardContent>
                </Card>
              )}
              {risk_assessment?.technical_risk_reasoning && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Award className="h-4 w-4" />
                      Technical Risk
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold mb-2">{risk_assessment.technical_risk_score}/100</div>
                    <p className="text-xs text-muted-foreground">{risk_assessment.technical_risk_reasoning}</p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Scenarios */}
            {(risk_assessment?.best_case_scenario || risk_assessment?.worst_case_scenario || risk_assessment?.most_likely_scenario) && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Scenario Analysis</CardTitle>
                  <CardDescription>Possible outcomes based on your profile</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-4">
                    {risk_assessment.best_case_scenario && (
                      <div className="p-4 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800">
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="h-4 w-4 text-green-600" />
                          <span className="font-medium text-green-700 dark:text-green-300">Best Case</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{risk_assessment.best_case_scenario}</p>
                      </div>
                    )}
                    {risk_assessment.most_likely_scenario && (
                      <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                        <div className="flex items-center gap-2 mb-2">
                          <Target className="h-4 w-4 text-blue-600" />
                          <span className="font-medium text-blue-700 dark:text-blue-300">Most Likely</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{risk_assessment.most_likely_scenario}</p>
                      </div>
                    )}
                    {risk_assessment.worst_case_scenario && (
                      <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                          <span className="font-medium text-red-700 dark:text-red-300">Worst Case</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{risk_assessment.worst_case_scenario}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Risk Factors */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Factors & Mitigation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  {risk_assessment?.risk_factors?.map((risk, i) => (
                    <div key={i} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{risk.factor_name}</h4>
                        <Badge
                          variant={
                            risk.severity === 'critical'
                              ? 'destructive'
                              : risk.severity === 'high'
                              ? 'destructive'
                              : risk.severity === 'medium'
                              ? 'default'
                              : 'secondary'
                          }
                        >
                          {risk.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{risk.impact_description}</p>
                      
                      {/* Risk Reasoning */}
                      {risk.reasoning && (
                        <p className="text-xs text-muted-foreground italic mb-2">
                          <Brain className="h-3 w-3 inline mr-1" />
                          {risk.reasoning}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-2 text-xs mb-2">
                        <span
                          className="font-medium"
                          style={{
                            color:
                              risk.probability > 70
                                ? '#ef4444'
                                : risk.probability > 40
                                ? '#f59e0b'
                                : '#22c55e',
                          }}
                        >
                          {risk.probability}% probability
                        </span>
                        <span className="text-muted-foreground">• {risk.category}</span>
                      </div>
                      {risk.mitigation_strategies?.length > 0 && (
                        <div className="pt-2 border-t">
                          <p className="text-xs font-medium mb-1">Mitigation:</p>
                          <ul className="text-xs text-muted-foreground">
                            {risk.mitigation_strategies.slice(0, 2).map((s, j) => (
                              <li key={j}>• {s}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            {/* Key Insights */}
            {keyInsights.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-yellow-500" />
                    Key Insights
                  </CardTitle>
                  <CardDescription>Important findings from your simulation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    {keyInsights.map((insight, i) => (
                      <div key={i} className={`p-4 rounded-lg border ${
                        insight.type === 'positive' ? 'bg-green-50 dark:bg-green-950/30 border-green-200' :
                        insight.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-950/30 border-yellow-200' :
                        insight.type === 'critical' ? 'bg-red-50 dark:bg-red-950/30 border-red-200' :
                        'bg-blue-50 dark:bg-blue-950/30 border-blue-200'
                      }`}>
                        <h4 className="font-medium mb-2">{insight.title}</h4>
                        <p className="text-sm mb-2">{insight.insight}</p>
                        {insight.reasoning && (
                          <p className="text-xs text-muted-foreground italic">
                            <Brain className="h-3 w-3 inline mr-1" />
                            {insight.reasoning}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Immediate Actions */}
            {immediateActions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Zap className="h-5 w-5 text-orange-500" />
                    Immediate Actions
                  </CardTitle>
                  <CardDescription>What to do right now</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {immediateActions.map((action, i) => (
                      <div key={i} className="flex items-start gap-4 p-3 border rounded-lg">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          action.priority === 'high' ? 'bg-red-100 text-red-700' :
                          action.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {i + 1}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{action.action}</span>
                            <Badge variant="outline" className="text-xs">{action.timeframe}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">Impact: {action.impact}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Path Comparison Table */}
            {pathComparison.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Path Comparison</CardTitle>
                  <CardDescription>Compare different career approaches</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2 font-medium">Metric</th>
                          <th className="text-center p-2 font-medium text-green-600">Conservative</th>
                          <th className="text-center p-2 font-medium text-blue-600">Realistic</th>
                          <th className="text-center p-2 font-medium text-orange-600">Ambitious</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pathComparison.map((row, i) => (
                          <tr key={i} className="border-b">
                            <td className="p-2 font-medium">{row.metric}</td>
                            <td className="text-center p-2">{row.conservative}</td>
                            <td className="text-center p-2">{row.realistic}</td>
                            <td className="text-center p-2">{row.ambitious}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {(topRecommendations.length > 0 ? topRecommendations : risk_assessment?.recommendations)?.map((rec, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm font-medium">
                          {i + 1}
                        </div>
                        <span className="text-sm">{rec}</span>
                      </li>
                    )) || (
                      <li className="text-muted-foreground">No specific recommendations</li>
                    )}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Decision Points</CardTitle>
                  <CardDescription>Key decisions you'll need to make</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {recommendedPath?.key_decision_points?.map((point, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm">
                        <Target className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                        <span>{point}</span>
                      </li>
                    )) || (
                      <li className="text-muted-foreground">No key decision points identified</li>
                    )}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Decision Rationale */}
            {decisionRationale.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-500" />
                    Why These Recommendations?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {decisionRationale.map((item, i) => (
                      <div key={i} className="p-4 border rounded-lg">
                        <h4 className="font-medium mb-2">{item.decision}</h4>
                        <p className="text-sm text-muted-foreground mb-2">{item.why}</p>
                        <Badge variant="outline">Impact: {item.impact}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Major Milestones */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Major Milestones</CardTitle>
                <CardDescription>Key achievements along your journey</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {recommendedPath?.major_milestones?.map((milestone, i) => (
                    <Badge key={i} variant="outline" className="py-2 px-3">
                      <Award className="h-3 w-3 mr-2" />
                      {milestone}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Assumptions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Assumptions</CardTitle>
                <CardDescription>This simulation assumes the following</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  {recommendedPath?.assumptions?.map((assumption, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <AlertTriangle className="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                      {assumption}
                    </li>
                  )) || <li>Standard assumptions applied</li>}
                </ul>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      <EmbedPopupAgentClient appConfig={APP_CONFIG_DEFAULTS} />
    </div>
  );
}
