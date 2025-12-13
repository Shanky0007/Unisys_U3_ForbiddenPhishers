import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle,
  CardFooter 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  Target,
  TrendingUp,
  Clock,
  DollarSign,
  Lightbulb,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  ArrowLeft,
  Loader2,
  Sparkles,
  Brain,
  Briefcase,
  GraduationCap,
  Star,
  Info,
} from 'lucide-react';
import { useSimulationStore } from '@/lib/store';
import { simulateSelectedCareer } from '@/lib/api';
import type { CareerFit } from '@/lib/api';
import { useSelector } from 'react-redux';
import type { RootState } from '@/store/store';


const difficultyColors: Record<string, string> = {
  'Easy': 'bg-green-100 text-green-800',
  'Moderate': 'bg-yellow-100 text-yellow-800',
  'Challenging': 'bg-orange-100 text-orange-800',
  'Very Challenging': 'bg-red-100 text-red-800',
};

const fitScoreColor = (score: number) => {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-orange-600';
};

interface CareerCardProps {
  career: CareerFit;
  isSelected: boolean;
  onSelect: () => void;
  onExplore: () => void;
  index: number;
}

function CareerCard({ career, isSelected, onSelect, onExplore, index }: CareerCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card 
        className={`relative overflow-hidden transition-all duration-300 ${
          isSelected 
            ? 'ring-2 ring-primary shadow-lg scale-[1.02]' 
            : 'hover:shadow-md hover:scale-[1.01]'
        }`}
      >
        {/* Rank Badge */}
        <div className="absolute top-4 right-4">
          <Badge variant={career.rank === 1 ? 'default' : 'secondary'} className="text-lg px-3 py-1">
            #{career.rank}
          </Badge>
        </div>
        
        <CardHeader className="pb-2">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${
              career.rank === 1 ? 'bg-primary/10' : 'bg-muted'
            }`}>
              {career.rank === 1 ? <Star className="w-6 h-6 text-primary" /> :
               career.rank === 2 ? <Target className="w-6 h-6 text-muted-foreground" /> :
               <Briefcase className="w-6 h-6 text-muted-foreground" />}
            </div>
            <div className="flex-1">
              <CardTitle className="text-xl">{career.career_title}</CardTitle>
              <CardDescription className="text-sm mt-1">
                {career.career_field}
              </CardDescription>
            </div>
          </div>
          
          {/* Tagline */}
          <p className="text-sm text-muted-foreground mt-3 italic">
            "{career.tagline}"
          </p>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Fit Scores */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Overall Fit</span>
                <span className={`font-semibold ${fitScoreColor(career.overall_fit_score)}`}>
                  {career.overall_fit_score.toFixed(0)}%
                </span>
              </div>
              <Progress value={career.overall_fit_score} className="h-2" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Skill Match</span>
                <span className={`font-semibold ${fitScoreColor(career.skill_fit_score)}`}>
                  {career.skill_fit_score.toFixed(0)}%
                </span>
              </div>
              <Progress value={career.skill_fit_score} className="h-2" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Interest Match</span>
                <span className={`font-semibold ${fitScoreColor(career.interest_fit_score)}`}>
                  {career.interest_fit_score.toFixed(0)}%
                </span>
              </div>
              <Progress value={career.interest_fit_score} className="h-2" />
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Market Demand</span>
                <span className={`font-semibold ${fitScoreColor(career.market_fit_score)}`}>
                  {career.market_fit_score.toFixed(0)}%
                </span>
              </div>
              <Progress value={career.market_fit_score} className="h-2" />
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <DollarSign className="w-3 h-3" />
              {career.typical_salary_range}
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {career.time_to_entry}
            </Badge>
            <Badge className={difficultyColors[career.difficulty_level] || 'bg-gray-100'}>
              {career.difficulty_level}
            </Badge>
          </div>
          
          {/* Top 3 Reasons */}
          <div className="space-y-2">
            <h4 className="text-sm font-semibold flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              Why This Fits You
            </h4>
            <ul className="space-y-1">
              {career.top_3_reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>{reason}</span>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Expandable Detailed Reasoning */}
          <Accordion type="single" collapsible value={expanded ? 'details' : ''}>
            <AccordionItem value="details" className="border-none">
              <AccordionTrigger 
                className="text-sm py-2"
                onClick={() => setExpanded(!expanded)}
              >
                <span className="flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  View Detailed Reasoning
                </span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  {/* Strengths Alignment */}
                  <div>
                    <h5 className="text-sm font-medium flex items-center gap-2 mb-2">
                      <Brain className="w-4 h-4 text-blue-500" />
                      Your Strengths That Align
                    </h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {career.reasoning.strengths_alignment.map((s, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-green-500">•</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Market Demand Reasons */}
                  <div>
                    <h5 className="text-sm font-medium flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      Market Opportunity
                    </h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {career.reasoning.market_demand_reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-green-500">•</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Growth Potential */}
                  <div>
                    <h5 className="text-sm font-medium flex items-center gap-2 mb-2">
                      <GraduationCap className="w-4 h-4 text-purple-500" />
                      Growth Potential
                    </h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {career.reasoning.growth_potential_reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-purple-500">•</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Potential Challenges */}
                  <div>
                    <h5 className="text-sm font-medium flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-orange-500" />
                      Challenges to Consider
                    </h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {career.reasoning.potential_challenges.map((c, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-orange-500">•</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Why Now */}
                  <Alert>
                    <Lightbulb className="h-4 w-4" />
                    <AlertDescription className="text-sm">
                      <strong>Why Now:</strong> {career.reasoning.why_now}
                    </AlertDescription>
                  </Alert>
                  
                  {/* Key Skills Needed */}
                  <div>
                    <h5 className="text-sm font-medium mb-2">Skills You'll Need</h5>
                    <div className="flex flex-wrap gap-1">
                      {career.key_skills_needed.map((skill, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  {/* Immediate Next Steps */}
                  <div>
                    <h5 className="text-sm font-medium mb-2">Immediate Next Steps</h5>
                    <ol className="text-sm text-muted-foreground space-y-1">
                      {career.immediate_next_steps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="font-semibold text-primary">{i + 1}.</span>
                          {step}
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
        
        <CardFooter className="flex gap-2 pt-4">
          <Button 
            variant={isSelected ? 'default' : 'outline'} 
            className="flex-1"
            onClick={onSelect}
          >
            {isSelected ? (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Selected
              </>
            ) : (
              'Select This Career'
            )}
          </Button>
          <Button 
            variant="secondary"
            onClick={onExplore}
            disabled={!isSelected}
          >
            Explore in Detail
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}

export default function CareerFitsPage() {
  const navigate = useNavigate();
  const { 
    matchingResult, 
    sessionId, 
    selectedCareerIndex,
    selectCareer,
    setResult,
    setLoading,
    setError,
    isLoading,
    loadingStage,
  } = useSimulationStore();
    const accessToken = useSelector((state: RootState) => state.auth.accessToken);
  if (!matchingResult || !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="p-6">
          <p className="text-muted-foreground mb-4">No career analysis found. Please start from the beginning.</p>
          <Button onClick={() => navigate('/simulate')}>
            Start Analysis
          </Button>
        </Card>
      </div>
    );
  }
  
  const handleSelectCareer = (index: number) => {
    const career = matchingResult.career_fits[index];
    selectCareer(index, career);
  };
  
  const handleExploreCareer = async () => {
    if (selectedCareerIndex === null || !sessionId) return;
    
    setLoading(true, 'simulation');
    setError(null);
    
    try {
      const result = await simulateSelectedCareer(sessionId, selectedCareerIndex, accessToken || undefined);
      setResult(result);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Loading Overlay */}
      <AnimatePresence>
        {isLoading && loadingStage === 'simulation' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center"
          >
            <Card className="p-8 max-w-md text-center">
              <Loader2 className="w-12 h-12 animate-spin mx-auto text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">Building Your Career Roadmap</h3>
              <p className="text-muted-foreground text-sm">
                Our AI agents are analyzing market data, creating timelines, and calculating your personalized plan...
              </p>
              <div className="mt-4 space-y-2 text-sm text-left">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span>Fetching market data...</span>
                </div>
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing skill gaps...</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span>Creating timeline...</span>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
      
      <div className="container mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/simulate')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Profile
          </Button>
          
          <div className="text-center max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold mb-3">Your Top Career Matches</h1>
            <p className="text-muted-foreground">
              Based on your profile, our AI has identified these 3 careers as the best fit for you.
              Each comes with detailed reasoning to help you make an informed decision.
            </p>
          </div>
        </div>
        
        {/* Analysis Summary */}
        <Card className="mb-8 bg-primary/5 border-primary/20">
          <CardContent className="py-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <Brain className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-2">Analysis Summary</h3>
                <p className="text-muted-foreground text-sm mb-4">
                  {matchingResult.analysis_summary}
                </p>
                <div className="flex flex-wrap gap-2">
                  {matchingResult.profile_highlights.map((highlight, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {highlight}
                    </Badge>
                  ))}
                </div>
                <div className="mt-4 flex items-center gap-2 text-sm">
                  <Badge variant={
                    matchingResult.confidence_level === 'High' ? 'default' :
                    matchingResult.confidence_level === 'Medium' ? 'secondary' : 'outline'
                  }>
                    {matchingResult.confidence_level} Confidence
                  </Badge>
                  <span className="text-muted-foreground">
                    {matchingResult.confidence_reasoning}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Career Cards */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {matchingResult.career_fits.map((career, index) => (
            <CareerCard
              key={index}
              career={career}
              index={index}
              isSelected={selectedCareerIndex === index}
              onSelect={() => handleSelectCareer(index)}
              onExplore={handleExploreCareer}
            />
          ))}
        </div>
        
        {/* Methodology */}
        <Card className="bg-muted/30">
          <CardContent className="py-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Info className="w-4 h-4" />
              <span>
                <strong>How we calculated this:</strong> {matchingResult.methodology_explanation}
              </span>
            </div>
          </CardContent>
        </Card>
        
        {/* CTA */}
        {selectedCareerIndex !== null && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-0 left-0 right-0 bg-background border-t p-4"
          >
            <div className="container mx-auto flex items-center justify-between">
              <div>
                <p className="font-semibold">
                  Selected: {matchingResult.career_fits[selectedCareerIndex].career_title}
                </p>
                <p className="text-sm text-muted-foreground">
                  Ready to see your complete roadmap?
                </p>
              </div>
              <Button 
                size="lg" 
                onClick={handleExploreCareer}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Full Roadmap
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
