import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format, formatDistanceToNow } from "date-fns";

// Import Lucide icons
import {
  Briefcase as BriefcaseIcon,
  LineChart,
  TrendingUp,
  TrendingDown,
  Brain,
} from "lucide-react";

// Define types
interface SalaryRange {
  role: string;
  min: number;
  max: number;
  median: number;
  location?: string;
}

interface IndustryInsights {
  salaryRanges: SalaryRange[];
  growthRate: number;
  demandLevel: "High" | "Medium" | "Low";
  topSkills: string[];
  marketOutlook: "Positive" | "Neutral" | "Negative";
  keyTrends: string[];
  recommendedSkills: string[];
  dataSources: string[];
  industry?: string;
  lastUpdated?: Date | string;
  nextUpdate?: Date | string;
  generatedBy?: string;
  dataFreshness?: string;
}

interface DashboardViewProps {
  insights: IndustryInsights;
}

interface IndustryInsightsComponentProps {
  apiUrl?: string;
  defaultIndustry?: string;
  showTitle?: boolean;
  className?: string;
}

/**
 * DashboardView - Component to display industry insights visually
 */
const DashboardView: React.FC<DashboardViewProps> = ({ insights }) => {
  // Transform salary data for the chart
  const salaryData = insights.salaryRanges.map((range) => ({
    name: range.role,
    min: range.min / 1000,
    max: range.max / 1000,
    median: range.median / 1000,
  }));

  const getDemandLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "high":
        return "bg-[#46704A]"; // Using the brand color from the site
      case "medium":
        return "bg-[#6B8F60]";
      case "low":
        return "bg-[#A9B782]";
      default:
        return "bg-[#E4D7B4]";
    }
  };

  const getMarketOutlookInfo = (outlook: string) => {
    switch (outlook.toLowerCase()) {
      case "positive":
        return { icon: TrendingUp, color: "text-[#46704A]" };
      case "neutral":
        return { icon: LineChart, color: "text-[#6B8F60]" };
      case "negative":
        return { icon: TrendingDown, color: "text-[#A9B782]" };
      default:
        return { icon: LineChart, color: "text-[#E4D7B4]" };
    }
  };

  const outlookInfo = getMarketOutlookInfo(insights.marketOutlook);
  const OutlookIcon = outlookInfo.icon;
  const outlookColor = outlookInfo.color;

  // Format dates using date-fns
  const lastUpdatedDate = format(new Date(insights.lastUpdated || new Date()), "dd/MM/yyyy");
  const nextUpdateDistance = formatDistanceToNow(
    new Date(insights.nextUpdate || new Date()),
    { addSuffix: true }
  );

  return (
    <div className="space-y-6 bg-white rounded-2xl p-6 border-2 border-[#E4D7B4] shadow-sm w-full">
      <div className="flex justify-between items-center mb-4">
        <span className="px-3 py-1 bg-[#F9F6EE] border border-[#E4D7B4] rounded-full text-sm text-[#335441]">
          Last updated: {lastUpdatedDate}
        </span>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-[#F9F6EE] rounded-2xl p-5 border-2 border-[#E4D7B4] shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between pb-2">
            <h3 className="text-sm font-medium text-[#335441]">Market Outlook</h3>
            <OutlookIcon className={`h-5 w-5 ${outlookColor}`} />
          </div>
          <div className="text-2xl font-bold text-[#335441]">{insights.marketOutlook}</div>
          <p className="text-xs text-[#6B8F60] mt-1">
            Next update {nextUpdateDistance}
          </p>
        </div>

        <div className="bg-[#F9F6EE] rounded-2xl p-5 border-2 border-[#E4D7B4] shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between pb-2">
            <h3 className="text-sm font-medium text-[#335441]">Industry Growth</h3>
            <TrendingUp className="h-5 w-5 text-[#46704A]" />
          </div>
          <div className="text-2xl font-bold text-[#335441]">
            {insights.growthRate.toFixed(1)}%
          </div>
          <div className="w-full bg-[#E4D7B4] rounded-full h-2.5 mt-2 overflow-hidden">
            <div
              className="bg-[#46704A] h-2.5 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(insights.growthRate * 2, 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-[#F9F6EE] rounded-2xl p-5 border-2 border-[#E4D7B4] shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between pb-2">
            <h3 className="text-sm font-medium text-[#335441]">Demand Level</h3>
            <BriefcaseIcon className="h-5 w-5 text-[#46704A]" />
          </div>
          <div className="text-2xl font-bold text-[#335441]">{insights.demandLevel}</div>
          <div
            className={`h-2.5 w-full rounded-full mt-2 ${getDemandLevelColor(
              insights.demandLevel
            )}`}
          ></div>
        </div>

        <div className="bg-[#F9F6EE] rounded-2xl p-5 border-2 border-[#E4D7B4] shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center justify-between pb-2">
            <h3 className="text-sm font-medium text-[#335441]">Top Skills</h3>
            <Brain className="h-5 w-5 text-[#46704A]" />
          </div>
          <div className="flex flex-wrap gap-2 max-h-20 overflow-y-auto">
            {insights.topSkills.slice(0, 8).map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white border border-[#E4D7B4] text-sm rounded-full text-[#335441]"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Salary Ranges Chart */}
      <div className="bg-[#F9F6EE] rounded-2xl p-6 border-2 border-[#E4D7B4] shadow-sm mb-8 w-full">
        <div className="mb-4 pb-4 border-b border-[#E4D7B4]">
          <h2 className="text-xl font-bold text-[#335441]">Salary Ranges by Role</h2>
          <p className="text-sm text-[#6B8F60]">
            Displaying minimum, median, and maximum salaries (in thousands)
          </p>
        </div>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={salaryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E4D7B4" />
              <XAxis dataKey="name" stroke="#335441" />
              <YAxis stroke="#335441" />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-white border border-[#E4D7B4] rounded-lg p-3 shadow-lg z-50">
                        <p className="font-bold text-[#335441]">{label}</p>
                        {payload.map((item, index) => (
                          <p key={index} className="text-sm text-[#6B8F60]">
                            {item.name}: ${item.value}K
                          </p>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="min" fill="#A9B782" name="Min Salary (K)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="median" fill="#46704A" name="Median Salary (K)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="max" fill="#335441" name="Max Salary (K)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Industry Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        <div className="bg-[#F9F6EE] rounded-2xl p-6 border-2 border-[#E4D7B4] shadow-sm w-full">
          <div className="mb-4 pb-4 border-b border-[#E4D7B4]">
            <h2 className="text-xl font-bold text-[#335441]">Key Industry Trends</h2>
            <p className="text-sm text-[#6B8F60]">
              Current trends shaping the industry
            </p>
          </div>
          <div className="p-2">
            <ul className="space-y-4 max-h-80 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-[#46704A] scrollbar-track-[#E4D7B4] scrollbar-rounded">
              {insights.keyTrends.slice(0, 6).map((trend, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="h-2.5 w-2.5 mt-1.5 rounded-full bg-[#46704A]" />
                  <span className="text-[#335441]">{trend}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="bg-[#F9F6EE] rounded-2xl p-6 border-2 border-[#E4D7B4] shadow-sm w-full">
          <div className="mb-4 pb-4 border-b border-[#E4D7B4]">
            <h2 className="text-xl font-bold text-[#335441]">Recommended Skills</h2>
            <p className="text-sm text-[#6B8F60]">
              Skills to consider developing
            </p>
          </div>
          <div className="p-2 flex flex-wrap gap-2 max-h-80 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-[#46704A] scrollbar-track-[#E4D7B4] scrollbar-rounded">
            {insights.recommendedSkills.slice(0, 12).map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1.5 bg-white border border-[#E4D7B4] text-sm rounded-full text-[#335441] shadow-sm hover:shadow-md transition-shadow duration-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * IndustryInsightsComponent - Main embeddable component
 */
const IndustryInsightsComponent: React.FC<IndustryInsightsComponentProps> = ({
  apiUrl = "http://localhost:3000/api/industry",
  defaultIndustry = "",
  showTitle = true,
  className = "",
}) => {
  const [insights, setInsights] = useState<IndustryInsights | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [industry, setIndustry] = useState<string>(defaultIndustry);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Fetch insights for the given industry
  const fetchInsights = async (industryName: string) => {
    if (!industryName.trim()) {
      setError("Please enter an industry name");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${apiUrl}/insights/${industryName}`);

      if (!response.ok) {
        throw new Error("Failed to fetch industry insights");
      }

      const data = await response.json();
      setInsights(data);
    } catch (err) {
      setError("Failed to load industry insights. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (industry.trim()) {
      fetchInsights(industry);
    }
  };

  // Handle manually refreshing insights
  const handleRefresh = async () => {
    if (!industry.trim()) return;

    try {
      setRefreshing(true);
      const response = await fetch(`${apiUrl}/insights/${industry}/refresh`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to refresh insights");
      }

      const data = await response.json();
      setInsights(data);
    } catch (err) {
      setError("Failed to refresh insights. Please try again.");
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className={`min-h-screen bg-[#F9F6EE] ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-12">
          {showTitle && (
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold text-[#335441] mb-4">
                Industry Insights
              </h1>
              <p className="text-lg text-[#6B8F60] max-w-2xl mx-auto">
                Get AI-powered analysis of current industry trends, salaries, and career opportunities
              </p>
            </div>
          )}

          <div className="w-full max-w-3xl mx-auto mb-12">
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 w-full">
              <input
                type="text"
                placeholder="Enter industry (e.g., Software Development)"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="flex-1 px-5 py-3 border-2 border-[#E4D7B4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#46704A] focus:border-transparent text-[#335441] bg-white shadow-sm"
                disabled={loading || refreshing}
              />
              <button
                type="submit"
                disabled={loading || refreshing || !industry.trim()}
                className="px-6 py-3 bg-[#335441] text-white rounded-xl disabled:bg-[#A9B782] hover:bg-[#46704A] transition-colors duration-300 font-medium shadow-md w-full sm:w-auto"
              >
                {loading ? "Loading..." : "Get Insights"}
              </button>
            </form>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700 max-w-3xl mx-auto text-center w-full">
              {error}
            </div>
          )}

          {insights && (
            <div className="space-y-6 w-full max-w-7xl mx-auto mb-12 animate-fade-in">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 className="text-2xl md:text-3xl font-bold text-center sm:text-left text-[#335441]">
                  {industry} Industry Insights
                </h2>
                <button
                  className="px-5 py-2.5 bg-[#46704A] text-white rounded-xl disabled:bg-[#A9B782] hover:bg-[#335441] transition-colors duration-300 font-medium w-full sm:w-auto"
                  onClick={handleRefresh}
                  disabled={refreshing}
                >
                  {refreshing ? "Refreshing..." : "Refresh Insights"}
                </button>
              </div>

              <DashboardView insights={insights} />
            </div>
          )}

          {!insights && !loading && !error && (
            <div className="text-center py-16 w-full">
              <div className="inline-block bg-[#46704A] p-4 rounded-full mb-6 text-white">
                <Brain className="h-12 w-12" />
              </div>
              <h3 className="text-2xl font-bold text-[#335441] mb-2">Get Industry Insights</h3>
              <p className="text-lg text-[#6B8F60] max-w-md mx-auto">
                Enter an industry above to get AI-powered insights on trends, salaries, and career opportunities
              </p>
            </div>
          )}

          {loading && !insights && (
            <div className="text-center py-16 w-full animate-pulse">
              <div className="inline-block bg-[#46704A] p-4 rounded-full mb-6 text-white">
                <Brain className="h-12 w-12" />
              </div>
              <h3 className="text-2xl font-bold text-[#335441] mb-2">Generating Insights</h3>
              <p className="text-lg text-[#6B8F60] max-w-md mx-auto">
                Analyzing data for {industry} industry...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IndustryInsightsComponent;
