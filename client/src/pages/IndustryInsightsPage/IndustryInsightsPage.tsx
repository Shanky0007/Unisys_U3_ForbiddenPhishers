import React, { useEffect, useState } from "react";
import axios from "axios";
import { backendUrl } from "@/config/backendUrl";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, RefreshCw, TrendingUp, DollarSign, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SalaryRange {
  role: string;
  min: number;
  max: number;
  median: number;
  location?: string;
}

interface SkillTrend {
  skill: string;
  trend: "Rising" | "Stable" | "Declining";
  demandScore: number;
}

interface IndustryInsights {
  salaryRanges: SalaryRange[];
  growthRate: number;
  demandLevel: "High" | "Medium" | "Low";
  topSkills: string[];
  marketOutlook: "Positive" | "Neutral" | "Negative";
  keyTrends: string[];
  recommendedSkills: string[];
  skillTrends: SkillTrend[];
  dataSources: string[];
  generatedBy?: string;
  dataFreshness?: string;
  industry: string;
  lastUpdated: string;
}

const CHART_COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--primary) / 0.8)",
  "hsl(var(--primary) / 0.6)",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
];

export default function IndustryInsightsPage() {
  const [industry, setIndustry] = useState<string>("");
  const [insights, setInsights] = useState<IndustryInsights | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = async (refresh: boolean = false) => {
    if (!industry.trim()) {
      setError("Please enter an industry name");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const endpoint = refresh
        ? `${backendUrl}/api/v1/industry/insights/${encodeURIComponent(industry)}/refresh`
        : `${backendUrl}/api/v1/industry/insights/${encodeURIComponent(industry)}`;

      const response = await axios.get(endpoint);
      setInsights(response.data);
    } catch (err: any) {
      setError(err.response?.data?.details || "Failed to fetch industry insights");
      console.error("Error fetching insights:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDemandColor = (level: string) => {
    switch (level) {
      case "High":
        return "bg-primary text-primary-foreground";
      case "Medium":
        return "bg-secondary text-secondary-foreground";
      case "Low":
        return "bg-muted text-muted-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getOutlookColor = (outlook: string) => {
    switch (outlook) {
      case "Positive":
        return "text-primary";
      case "Neutral":
        return "text-muted-foreground";
      case "Negative":
        return "text-muted-foreground";
      default:
        return "text-muted-foreground";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "Rising":
        return "📈";
      case "Stable":
        return "➡️";
      case "Declining":
        return "📉";
      default:
        return "•";
    }
  };

  // Prepare chart data
  const salaryChartData = insights?.salaryRanges?.slice(0, 10).map((salary) => ({
    role: salary.role.length > 20 ? salary.role.substring(0, 20) + "..." : salary.role,
    min: salary.min / 1000,
    median: salary.median / 1000,
    max: salary.max / 1000,
    location: salary.location || "US",
  }));

  const skillTrendsData = insights?.skillTrends?.map((skill) => ({
    skill: skill.skill,
    demand: skill.demandScore,
    trend: skill.trend,
  }));

  const topSkillsData = insights?.topSkills?.slice(0, 8).map((skill, index) => ({
    name: skill,
    value: 100 - index * 10,
  }));

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center max-w-4xl mx-auto mb-12">
          <Badge variant="secondary" className="mb-4">
            <TrendingUp className="h-3 w-3 mr-1" />
            Real-time Market Analysis
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Industry{' '}
            <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              Insights
            </span>
          </h1>
          <p className="text-lg text-muted-foreground">
            Accurate, real-time data
          </p>
        </div>

        {/* Industry Selector */}
        <Card className="mb-8 max-w-4xl mx-auto shadow-lg">
          <CardContent className="pt-6">
            <div className="flex gap-4 items-center flex-col sm:flex-row">
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !loading) {
                    fetchInsights(false);
                  }
                }}
                placeholder="Enter industry (e.g., software engineering, healthcare, finance)"
                className="flex-1 px-4 py-3 border border-input rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-background w-full"
              />
              <div className="flex gap-2 w-full sm:w-auto">
                <Button
                  onClick={() => fetchInsights(false)}
                  disabled={loading || !industry.trim()}
                  size="lg"
                  className="flex-1 sm:flex-none"
                >
                  {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Search"}
                </Button>
                <Button
                  onClick={() => fetchInsights(true)}
                  disabled={loading || !insights || !industry.trim()}
                  variant="outline"
                  size="lg"
                  className="flex-1 sm:flex-none"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {error && (
          <div className="bg-destructive/10 border-l-4 border-destructive p-4 mb-6 rounded max-w-4xl mx-auto">
            <p className="text-destructive font-medium">{error}</p>
          </div>
        )}

        {loading && !insights && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-lg font-medium mb-2">Searching industry data with Tavily...</p>
            <p className="text-muted-foreground text-sm">This may take 10-15 seconds</p>
          </div>
        )}

        {!loading && !insights && !error && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6">
              <TrendingUp className="h-12 w-12 text-primary" />
            </div>
            <h3 className="text-2xl font-bold mb-3">
              Get Industry Insights
            </h3>
            <p className="text-muted-foreground text-center max-w-md">
              Enter an industry name above and click "Search" to get real-time insights
              including salary data, skill trends, and market analysis.
            </p>
          </div>
        )}

        {insights && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 max-w-6xl mx-auto">
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Growth Rate
                  </CardTitle>
                  <TrendingUp className="h-5 w-5 text-primary" />
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold text-primary">
                    {insights.growthRate}%
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Annual growth</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Demand Level
                  </CardTitle>
                  <Users className="h-5 w-5 text-primary" />
                </CardHeader>
                <CardContent>
                  <Badge className={getDemandColor(insights.demandLevel)}>
                    {insights.demandLevel}
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-2">Market demand</p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Market Outlook
                  </CardTitle>
                  <DollarSign className="h-5 w-5 text-primary" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getOutlookColor(insights.marketOutlook)}`}>
                    {insights.marketOutlook}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Industry forecast</p>
                </CardContent>
              </Card>
            </div>

            {/* Salary Ranges Chart */}
            <Card className="mb-8 max-w-6xl mx-auto hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Salary Ranges by Role (in $1000s)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={salaryChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="role"
                      angle={-45}
                      textAnchor="end"
                      height={120}
                      style={{ fontSize: "12px" }}
                    />
                    <YAxis label={{ value: "Salary ($K)", angle: -90, position: "insideLeft" }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="min" fill={CHART_COLORS[0]} name="Min" />
                    <Bar dataKey="median" fill={CHART_COLORS[1]} name="Median" />
                    <Bar dataKey="max" fill={CHART_COLORS[2]} name="Max" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Skills Trends and Top Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 max-w-6xl mx-auto">
              {/* Skill Trends Chart */}
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl">Skill Demand Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={skillTrendsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="skill"
                        angle={-45}
                        textAnchor="end"
                        height={100}
                        style={{ fontSize: "11px" }}
                      />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="demand"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        name="Demand Score"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Top Skills Pie Chart */}
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl">Top Skills Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={topSkillsData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => entry.name}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {topSkillsData?.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={CHART_COLORS[index % CHART_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recommended Skills & Key Trends */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 max-w-6xl mx-auto">
              {/* Recommended Skills */}
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl">Recommended Skills for Growth</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {insights.recommendedSkills.map((skill, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Key Trends */}
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl">Key Industry Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {insights.keyTrends.map((trend, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-primary mr-2 font-bold">•</span>
                        <span className="text-sm text-muted-foreground">{trend}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Skill Trends Table */}
            <Card className="mb-8 max-w-6xl mx-auto hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Detailed Skill Trends Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left p-3 font-semibold">Skill</th>
                        <th className="text-left p-3 font-semibold">Trend</th>
                        <th className="text-left p-3 font-semibold">Demand Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {insights.skillTrends?.map((skill, index) => (
                        <tr key={index} className="border-b hover:bg-muted/50 transition-colors">
                          <td className="p-3 font-medium">{skill.skill}</td>
                          <td className="p-3">
                            <span className="flex items-center gap-1">
                              {getTrendIcon(skill.trend)} {skill.trend}
                            </span>
                          </td>
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-muted rounded-full h-2">
                                <div
                                  className="bg-primary h-2 rounded-full transition-all"
                                  style={{ width: `${skill.demandScore}%` }}
                                />
                              </div>
                              <span className="text-sm font-medium min-w-[3ch]">{skill.demandScore}</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Data Sources & Metadata */}
            <Card className="max-w-6xl mx-auto hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Data Sources & Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <p>
                    <strong className="text-foreground">Generated By:</strong> {insights.generatedBy}
                  </p>
                  <p>
                    <strong className="text-foreground">Data Freshness:</strong> {insights.dataFreshness}
                  </p>
                  <p>
                    <strong className="text-foreground">Last Updated:</strong>{" "}
                    {new Date(insights.lastUpdated).toLocaleString()}
                  </p>
                  <div>
                    <strong className="text-foreground">Sources:</strong>
                    <ul className="mt-2 space-y-1 ml-4">
                      {insights.dataSources.map((source, index) => (
                        <li key={index} className="text-xs">
                          • {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
