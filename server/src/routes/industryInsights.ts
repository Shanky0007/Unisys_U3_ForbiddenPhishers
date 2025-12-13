import express, { Router, Request, Response } from "express";
import axios from "axios";
import OpenAI from "openai";

// Initialize router
const router: Router = express.Router();

// Lazy initialization of OpenAI client
let openai: OpenAI | null = null;

const getOpenAIClient = (): OpenAI => {
  if (!openai) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error("OPENAI_API_KEY is not set in environment variables");
    }

    openai = new OpenAI({
      apiKey: apiKey,
    });
  }
  return openai;
};

interface SearchResult {
  title: string;
  content: string;
  url: string;
  score?: number;
}

interface TavilySearchResponse {
  results: Array<{
    title: string;
    content: string;
    url: string;
    score: number;
  }>;
  query: string;
}

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
}

/**
 * Perform Tavily Search to get recent industry data
 * @param {string} industry - The industry to search for
 * @returns {Array} - Array of search results
 */
const performTavilySearch = async (industry: string): Promise<SearchResult[]> => {
  try {
    const tavilyApiKey = process.env.TAVILY_API_KEY;
    
    if (!tavilyApiKey) {
      console.error("TAVILY_API_KEY is not set in environment variables");
      return [];
    }

    const queries = [
      `${industry} industry salary ranges trends 2025`,
      `${industry} industry growth rate statistics market analysis 2025`,
      `${industry} top skills demand trends 2025`,
      `${industry} job market outlook career opportunities 2025`,
    ];

    const searchResults: SearchResult[] = [];

    for (const query of queries) {
      try {
        const response = await axios.post<TavilySearchResponse>(
          "https://api.tavily.com/search",
          {
            api_key: tavilyApiKey,
            query: query,
            search_depth: "advanced",
            max_results: 5,
            include_answer: false,
            include_raw_content: false,
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (response.data.results) {
          searchResults.push(
            ...response.data.results.map((item) => ({
              title: item.title,
              content: item.content,
              url: item.url,
              score: item.score,
            }))
          );
        }
      } catch (queryError) {
        console.error(`Error searching for query "${query}":`, (queryError as any).message);
        // Continue with other queries even if one fails
      }
    }

    console.log(`✅ Tavily search completed: ${searchResults.length} results found`);
    return searchResults;
  } catch (error) {
    console.error(
      "Tavily Search API error:",
      (error as any).response?.data || (error as any).message
    );
    return [];
  }
};

/**
 * Generate industry insights using OpenAI with Tavily Search results
 * @param {string} industry - The industry to analyze
 * @returns {Object} - JSON object with industry insights
 */
const generateAIInsights = async (industry: string): Promise<IndustryInsights> => {
  try {
    // First, get real-time data from Tavily Search
    console.log(`🔍 Fetching real-time data for ${industry} industry via Tavily...`);
    const searchResults = await performTavilySearch(industry);

    // Prepare context from search results
    const searchContext =
      searchResults.length > 0
        ? searchResults
            .map(
              (result, index) =>
                `Source ${index + 1} (Relevance: ${result.score?.toFixed(2) || "N/A"}): ${result.title}\n${
                  result.content
                }\nURL: ${result.url}`
            )
            .join("\n\n")
        : "No recent search results available.";

    // Create enhanced prompt with search results
    const prompt = `You are an expert industry analyst. Based on the following real-time search results from Tavily (an AI-powered search engine), analyze the ${industry} industry and provide detailed, accurate insights.

REAL-TIME SEARCH RESULTS:
${searchContext}

Using the above real-time data and your knowledge, provide a comprehensive analysis in the following JSON format ONLY:

{
  "salaryRanges": [
    { "role": "string", "min": number, "max": number, "median": number, "location": "string" }
  ],
  "growthRate": number,
  "demandLevel": "High" | "Medium" | "Low",
  "topSkills": ["skill1", "skill2"],
  "marketOutlook": "Positive" | "Neutral" | "Negative",
  "keyTrends": ["trend1", "trend2"],
  "recommendedSkills": ["skill1", "skill2"],
  "skillTrends": [
    { "skill": "string", "trend": "Rising" | "Stable" | "Declining", "demandScore": number }
  ],
  "dataSources": ["source1", "source2"]
}

REQUIREMENTS:
- Include at least 10-15 common roles for salary ranges with accurate 2025 data
- Growth rate should be a percentage based on latest industry reports
- Include at least 10-12 top skills and key trends
- Include at least 10-12 recommended skills for career growth
- Include skill trends with demand scores (0-100) for visualization in charts
- List actual data sources/URLs used from the search results
- Provide location-specific salary data (US, Global, Europe, Asia, etc.)
- Be specific with numbers, percentages, and currency (USD)
- Focus on accuracy based on the search results provided
- Ensure salary numbers are realistic for 2025

Return ONLY the JSON object, no additional text or markdown formatting.`;

    // Call OpenAI API
    console.log("🤖 Generating insights with OpenAI...");
    const client = getOpenAIClient();
    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are an expert industry analyst who provides accurate, data-driven insights based on real-time information. You always return valid JSON without any additional formatting.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      temperature: 0.3,
      max_tokens: 4000,
      response_format: { type: "json_object" },
    });

    const responseText = completion.choices[0].message.content;
    if (!responseText) {
      throw new Error("OpenAI response was empty");
    }
    console.log("✅ OpenAI response received, parsing JSON...");

    // Parse and return the JSON
    const insights: IndustryInsights = JSON.parse(responseText);

    // Add metadata
    insights.generatedBy = "OpenAI with Tavily Search";
    insights.dataFreshness = "Real-time";

    return insights;
  } catch (error) {
    console.error("❌ Error generating AI insights:", error);

    // If search fails, use OpenAI with general knowledge
    if ((error as any).message?.includes("Tavily") || (error as any).message?.includes("TAVILY")) {
      console.log("⚠️ Falling back to OpenAI without search results...");
      return await generateInsightsWithoutSearch(industry);
    }

    throw new Error("Failed to generate industry insights: " + (error as any).message);
  }
};

/**
 * Fallback method: Generate insights using OpenAI without search results
 * @param {string} industry - The industry to analyze
 * @returns {Object} - JSON object with industry insights
 */
const generateInsightsWithoutSearch = async (industry: string): Promise<IndustryInsights> => {
  const prompt = `Analyze the current state of the ${industry} industry and provide detailed insights in the following JSON format:

{
  "salaryRanges": [
    { "role": "string", "min": number, "max": number, "median": number, "location": "string" }
  ],
  "growthRate": number,
  "demandLevel": "High" | "Medium" | "Low",
  "topSkills": ["skill1", "skill2"],
  "marketOutlook": "Positive" | "Neutral" | "Negative",
  "keyTrends": ["trend1", "trend2"],
  "recommendedSkills": ["skill1", "skill2"],
  "skillTrends": [
    { "skill": "string", "trend": "Rising" | "Stable" | "Declining", "demandScore": number }
  ],
  "dataSources": ["OpenAI Knowledge Base"]
}

Include at least 10-15 roles with 2025 salary estimates, 10-12 skills and trends, and skill trends for charts. Return ONLY JSON.`;

  const client = getOpenAIClient();
  const completion = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: "You are an expert industry analyst. Return valid JSON only.",
      },
      {
        role: "user",
        content: prompt,
      },
    ],
    temperature: 0.3,
    max_tokens: 4000,
    response_format: { type: "json_object" },
  });

  const responseContent = completion.choices[0].message.content;
  if (!responseContent) {
    throw new Error("OpenAI response was empty in fallback function");
  }
  const insights: IndustryInsights = JSON.parse(responseContent);
  insights.generatedBy = "OpenAI";
  insights.dataFreshness = "AI Knowledge Base";

  return insights;
};

// GET endpoint to get industry insights
router.get("/insights/:industry", async (req: Request, res: Response) => {
  try {
    const { industry } = req.params;

    console.log(`\n🔍 Generating new insights for ${industry}...`);
    const insights = await generateAIInsights(industry);

    // Add industry name and timestamps to response
    const result = {
      ...insights,
      industry: industry.toLowerCase(),
      lastUpdated: new Date(),
      nextUpdate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    };

    console.log(`✅ Successfully generated insights for ${industry}\n`);
    res.json(result);
  } catch (error) {
    console.error("❌ Error fetching industry insights:", error);
    res.status(500).json({
      error: "Failed to fetch industry insights",
      details: (error as any).message,
    });
  }
});

// POST endpoint to refresh industry insights (same functionality now)
router.post("/insights/:industry/refresh", async (req: Request, res: Response) => {
  try {
    const { industry } = req.params;

    console.log(`\n🔄 Generating fresh insights for ${industry}...`);
    const insights = await generateAIInsights(industry);

    // Add industry name and timestamps to response
    const result = {
      ...insights,
      industry: industry.toLowerCase(),
      lastUpdated: new Date(),
      nextUpdate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    };

    console.log(`✅ Successfully refreshed insights for ${industry}\n`);
    res.json(result);
  } catch (error) {
    console.error("❌ Error refreshing industry insights:", error);
    res.status(500).json({
      error: "Failed to refresh industry insights",
      details: (error as any).message,
    });
  }
});

// Simple health check endpoint
router.get("/health", (req: Request, res: Response) => {
  res.json({ 
    status: "OK", 
    message: "Industry Insights API is running",
    searchProvider: "Tavily",
    aiProvider: "OpenAI"
  });
});

export default router;
