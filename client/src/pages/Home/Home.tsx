import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Brain,
  TrendingUp,
  Target,
  DollarSign,
  Shield,
  BarChart3,
  ArrowRight,
  Sparkles,
  Users,
  Zap,
} from 'lucide-react';

const agents = [
  {
    name: 'Profile Parser',
    description: 'Analyzes your profile and creates a semantic understanding',
    icon: Brain,
    color: 'text-purple-500',
  },
  {
    name: 'Market Scout',
    description: 'Fetches real-time market data and trends',
    icon: TrendingUp,
    color: 'text-blue-500',
  },
  {
    name: 'Gap Analyst',
    description: 'Identifies skill gaps and growth opportunities',
    icon: Target,
    color: 'text-orange-500',
  },
  {
    name: 'Timeline Simulator',
    description: 'Creates personalized 4-6 year career roadmaps',
    icon: Zap,
    color: 'text-green-500',
  },
  {
    name: 'Financial Advisor',
    description: 'Calculates ROI and cost analysis',
    icon: DollarSign,
    color: 'text-emerald-500',
  },
  {
    name: 'Risk Assessor',
    description: 'Evaluates success probability and risks',
    icon: Shield,
    color: 'text-red-500',
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <Badge variant="secondary" className="mb-4">
            <Sparkles className="h-3 w-3 mr-1" />
            AI-Powered Career Planning
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
            Your Career Path,{' '}
            <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              Simulated
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Transform uncertainty into clarity with our AI-driven multi-agent system. 
            Get personalized 4-6 year career roadmaps backed by real market data.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" asChild>
              <Link to="/simulate">
                Start Simulation
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/about">
                Learn More
              </Link>
            </Button>
          </div>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 max-w-4xl mx-auto">
          {[
            { label: 'AI Agents', value: '7' },
            { label: 'Year Planning', value: '4-6' },
            { label: 'Success Rate', value: '89%' },
            { label: 'Users Helped', value: '10K+' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-4xl font-bold text-primary">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Powered by 7 Specialized AI Agents</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Each agent focuses on a specific aspect of your career planning, 
            working together to provide comprehensive guidance.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {agents.map((agent) => (
            <Card key={agent.name} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-muted ${agent.color}`}>
                    <agent.icon className="h-5 w-5" />
                  </div>
                  <CardTitle className="text-lg">{agent.name}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm">
                  {agent.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="container mx-auto px-4 py-16 bg-muted/30">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to get your personalized career roadmap
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            {
              step: '01',
              title: 'Share Your Profile',
              description: 'Tell us about your education, skills, interests, and career goals through our intuitive form.',
              icon: Users,
            },
            {
              step: '02',
              title: 'AI Analysis',
              description: 'Our 7 AI agents analyze your profile against real-time market data and generate insights.',
              icon: Brain,
            },
            {
              step: '03',
              title: 'Get Your Roadmap',
              description: 'Receive a detailed 4-6 year career roadmap with timelines, costs, and success probability.',
              icon: BarChart3,
            },
          ].map((item) => (
            <div key={item.step} className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary text-primary-foreground mb-4">
                <item.icon className="h-8 w-8" />
              </div>
              <div className="text-sm font-semibold text-primary mb-2">Step {item.step}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-muted-foreground text-sm">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16">
        <Card className="bg-primary text-primary-foreground max-w-4xl mx-auto">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Plan Your Future?</h2>
            <p className="text-primary-foreground/80 mb-8 max-w-2xl mx-auto">
              Join thousands of students and professionals who have transformed their career uncertainty into a clear, actionable plan.
            </p>
            <Button size="lg" variant="secondary" asChild>
              <Link to="/simulate">
                Start Your Free Simulation
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 mt-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2025 Career Path Simulator. Built with AI & Love.</p>
        </div>
      </footer>
    </div>
  );
}
