import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import {
  Brain,
  TrendingUp,
  Target,
  DollarSign,
  Shield,
  BarChart3,
  ArrowRight,
  Users,
  Zap,
  Play,
  Compass,
} from 'lucide-react';

const agents = [
  {
    name: 'Profile Parser',
    role: 'The Context Builder',
    description: 'Analyzes your academic profile, skills, and interests to create a comprehensive semantic understanding of your career potential.',
    icon: Brain,
    gradient: 'from-slate-600 to-slate-800',
  },
  {
    name: 'Career Matcher',
    role: 'The Fit Analyzer',
    description: 'Identifies your top 3 career matches with detailed reasoning based on your strengths, interests, and market alignment.',
    icon: Compass,
    gradient: 'from-slate-700 to-slate-900',
  },
  {
    name: 'Market Scout',
    role: 'The Data Fetcher',
    description: 'Fetches real-time job market data, salary trends, and industry insights to ground your career decisions in reality.',
    icon: TrendingUp,
    gradient: 'from-zinc-600 to-zinc-800',
  },
  {
    name: 'Gap Analyst',
    role: 'The Skill Mapper',
    description: 'Identifies skill gaps between your current profile and target roles, with actionable learning recommendations.',
    icon: Target,
    gradient: 'from-neutral-600 to-neutral-800',
  },
  {
    name: 'Timeline Simulator',
    role: 'The Roadmap Creator',
    description: 'Creates personalized 4-6 year career roadmaps with detailed milestones, timelines, and achievement markers.',
    icon: Zap,
    gradient: 'from-stone-600 to-stone-800',
  },
  {
    name: 'Financial Advisor',
    role: 'The ROI Calculator',
    description: 'Calculates comprehensive cost analysis, expected ROI, and financial projections for each career path.',
    icon: DollarSign,
    gradient: 'from-gray-600 to-gray-800',
  },
  {
    name: 'Risk Assessor',
    role: 'The Success Predictor',
    description: 'Evaluates success probability, identifies potential risks, and provides mitigation strategies for your chosen path.',
    icon: Shield,
    gradient: 'from-slate-500 to-slate-700',
  },
];

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const fadeInScale = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const cardHover = {
  rest: { scale: 1, y: 0 },
  hover: { scale: 1.02, y: -5 },
};

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-primary/3 to-blue-500/3 rounded-full blur-3xl"
          animate={{
            rotate: [0, 360],
          }}
          transition={{
            duration: 60,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20 md:py-28">
        <motion.div
          className="text-center max-w-4xl mx-auto"
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <motion.h1
            className="text-5xl md:text-7xl font-bold tracking-tight mb-8"
            variants={fadeInUp}
          >
            Your Career Path,{' '}
            <span className="relative">
              <span className="bg-gradient-to-r from-primary via-blue-500 to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                Simulated
              </span>
              <motion.span
                className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-primary to-blue-500 rounded-full"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: 0.8, duration: 0.6, ease: "easeOut" }}
              />
            </span>
          </motion.h1>
          
          <motion.p
            className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed"
            variants={fadeInUp}
          >
            Transform uncertainty into clarity with our AI-driven multi-agent system. 
            Get personalized 4-6 year career roadmaps backed by real market data.
          </motion.p>
          
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center"
            variants={fadeInUp}
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button size="lg" className="text-lg px-8 py-6 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all duration-300" asChild>
                <Link to="/simulate">
                  <Play className="mr-2 h-5 w-5" />
                  Start Simulation
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-2 hover:bg-muted/50 transition-all duration-300" asChild>
                <Link to="/about">
                  Learn More
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-4xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          {[
            { label: 'AI Agents', value: '7', suffix: '' },
            { label: 'Year Planning', value: '4-6', suffix: '' },
            { label: 'Success Rate', value: '89', suffix: '%' },
            { label: 'Users Helped', value: '10K', suffix: '+' },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              className="text-center p-6 rounded-2xl bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/30 transition-colors duration-300"
              variants={fadeInScale}
              whileHover={{ scale: 1.05, y: -5 }}
            >
              <motion.div
                className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent"
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 + 0.3, type: "spring" }}
                viewport={{ once: true }}
              >
                {stat.value}{stat.suffix}
              </motion.div>
              <div className="text-sm text-muted-foreground mt-2 font-medium">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-20">
        <motion.div
          className="text-center mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          <motion.h2 className="text-4xl md:text-5xl font-bold mb-6" variants={fadeInUp}>
            Meet Our{' '}
            <span className="bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
              7 AI Agents
            </span>
          </motion.h2>
          <motion.p className="text-muted-foreground max-w-2xl mx-auto text-lg" variants={fadeInUp}>
            A sophisticated multi-agent system where each specialist focuses on a critical aspect 
            of your career planning journey.
          </motion.p>
        </motion.div>

        {/* First row - 4 agents */}
        <motion.div
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-7xl mx-auto mb-5"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={staggerContainer}
        >
          {agents.slice(0, 4).map((agent) => (
            <motion.div
              key={agent.name}
              variants={fadeInUp}
              initial="rest"
              whileHover="hover"
            >
              <motion.div variants={cardHover} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="h-full border border-border/50 bg-card hover:bg-muted/30 transition-all duration-300 cursor-pointer group overflow-hidden relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${agent.gradient} opacity-0 group-hover:opacity-[0.03] transition-opacity duration-300`} />
                  <CardHeader className="pb-3">
                    <div className="flex items-start gap-4">
                      <motion.div
                        className={`p-3 rounded-lg bg-gradient-to-br ${agent.gradient} text-white shadow-lg group-hover:shadow-xl transition-all duration-300`}
                        whileHover={{ scale: 1.05 }}
                        transition={{ duration: 0.2 }}
                      >
                        <agent.icon className="h-5 w-5" />
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base font-semibold leading-tight">{agent.name}</CardTitle>
                        <p className="text-xs text-muted-foreground mt-1 font-medium">{agent.role}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="text-sm leading-relaxed text-muted-foreground/90">
                      {agent.description}
                    </CardDescription>
                  </CardContent>
                  <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-foreground/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </Card>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>

        {/* Second row - 3 agents centered */}
        <motion.div
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 max-w-5xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={staggerContainer}
        >
          {agents.slice(4, 7).map((agent) => (
            <motion.div
              key={agent.name}
              variants={fadeInUp}
              initial="rest"
              whileHover="hover"
            >
              <motion.div variants={cardHover} transition={{ type: "spring", stiffness: 300 }}>
                <Card className="h-full border border-border/50 bg-card hover:bg-muted/30 transition-all duration-300 cursor-pointer group overflow-hidden relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${agent.gradient} opacity-0 group-hover:opacity-[0.03] transition-opacity duration-300`} />
                  <CardHeader className="pb-3">
                    <div className="flex items-start gap-4">
                      <motion.div
                        className={`p-3 rounded-lg bg-gradient-to-br ${agent.gradient} text-white shadow-lg group-hover:shadow-xl transition-all duration-300`}
                        whileHover={{ scale: 1.05 }}
                        transition={{ duration: 0.2 }}
                      >
                        <agent.icon className="h-5 w-5" />
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base font-semibold leading-tight">{agent.name}</CardTitle>
                        <p className="text-xs text-muted-foreground mt-1 font-medium">{agent.role}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="text-sm leading-relaxed text-muted-foreground/90">
                      {agent.description}
                    </CardDescription>
                  </CardContent>
                  <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-foreground/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </Card>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* How It Works */}
      <div className="container mx-auto px-4 py-20">
        <div className="bg-gradient-to-br from-muted/50 to-muted/30 rounded-3xl p-8 md:p-16 backdrop-blur-sm border border-border/50">
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.h2 className="text-4xl md:text-5xl font-bold mb-6" variants={fadeInUp}>
              How It Works
            </motion.h2>
            <motion.p className="text-muted-foreground max-w-2xl mx-auto text-lg" variants={fadeInUp}>
              Three simple steps to get your personalized career roadmap
            </motion.p>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto relative"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-16 left-[20%] right-[20%] h-0.5 bg-gradient-to-r from-primary/50 via-blue-500/50 to-primary/50" />

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
            ].map((item, index) => (
              <motion.div
                key={item.step}
                className="text-center relative z-10"
                variants={fadeInUp}
              >
                <motion.div
                  className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-blue-500 text-primary-foreground mb-6 shadow-lg shadow-primary/25"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <item.icon className="h-10 w-10" />
                </motion.div>
                <motion.div
                  className="text-sm font-bold text-primary mb-3 tracking-wider"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  transition={{ delay: index * 0.2 + 0.5 }}
                  viewport={{ once: true }}
                >
                  STEP {item.step}
                </motion.div>
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{item.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* CTA Section */}
      <motion.div
        className="container mx-auto px-4 py-20"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={fadeInUp}
      >
        <motion.div
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Card className="bg-gradient-to-r from-primary via-primary/90 to-blue-600 text-primary-foreground max-w-4xl mx-auto overflow-hidden relative">
            {/* Animated background pattern */}
            <motion.div
              className="absolute inset-0 opacity-10"
              style={{
                backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                backgroundSize: '32px 32px',
              }}
              animate={{ x: [0, 32], y: [0, 32] }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            />
            
            <CardContent className="p-12 md:p-16 text-center relative z-10">
              <motion.h2
                className="text-3xl md:text-4xl font-bold mb-6"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                viewport={{ once: true }}
              >
                Ready to Plan Your Future?
              </motion.h2>
              <motion.p
                className="text-primary-foreground/90 mb-10 max-w-2xl mx-auto text-lg"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                viewport={{ once: true }}
              >
                Join thousands of students and professionals who have transformed their career uncertainty into a clear, actionable plan.
              </motion.p>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button size="lg" variant="secondary" className="text-lg px-8 py-6 shadow-xl hover:shadow-2xl transition-all duration-300" asChild>
                  <Link to="/simulate">
                    Start Your Free Simulation
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Footer */}
      <motion.footer
        className="border-t py-12 mt-8"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="container mx-auto px-4 text-center">
          <motion.p
            className="text-muted-foreground"
            whileHover={{ scale: 1.02 }}
          >
            © 2025 <span className="font-semibold text-foreground">CareerPath</span>
          </motion.p>
        </div>
      </motion.footer>
    </div>
  );
}
