/**
 * PDF Export Utility for Career Path Simulation Dashboard
 * Generates a comprehensive PDF report with all simulation data and visualizations
 */

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import type { SimulationResponse, CareerFit, CareerProfile, CareerPath } from './api';

// PDF Configuration
const PDF_CONFIG = {
  pageWidth: 210, // A4 width in mm
  pageHeight: 297, // A4 height in mm
  margin: 15,
  headerHeight: 25,
  footerHeight: 15,
  lineHeight: 6,
  titleSize: 18,
  headingSize: 14,
  subHeadingSize: 11,
  bodySize: 9,
  smallSize: 8,
};

// Colors for the PDF (RGB values)
const COLORS = {
  primary: [99, 102, 241], // Indigo
  secondary: [34, 197, 94], // Green
  warning: [245, 158, 11], // Amber
  danger: [239, 68, 68], // Red
  text: [30, 30, 30],
  muted: [120, 120, 120],
  background: [249, 250, 251],
  white: [255, 255, 255],
  border: [229, 231, 235],
};

interface ExportOptions {
  includeCharts?: boolean;
  includeTimeline?: boolean;
  includeFinancials?: boolean;
  includeRisks?: boolean;
  includeSkillGaps?: boolean;
  includeRecommendations?: boolean;
}

export class CareerPDFExporter {
  private pdf: jsPDF;
  private currentY: number;
  private pageNumber: number;

  constructor() {
    this.pdf = new jsPDF('p', 'mm', 'a4');
    this.currentY = PDF_CONFIG.margin;
    this.pageNumber = 1;
  }

  private addNewPage(): void {
    this.pdf.addPage();
    this.pageNumber++;
    this.currentY = PDF_CONFIG.margin;
    this.addHeader();
  }

  private checkPageBreak(neededSpace: number): void {
    if (this.currentY + neededSpace > PDF_CONFIG.pageHeight - PDF_CONFIG.footerHeight - PDF_CONFIG.margin) {
      this.addFooter();
      this.addNewPage();
    }
  }

  private addHeader(): void {
    // Header background
    this.pdf.setFillColor(...COLORS.primary as [number, number, number]);
    this.pdf.rect(0, 0, PDF_CONFIG.pageWidth, PDF_CONFIG.headerHeight, 'F');

    // Logo/Title
    this.pdf.setTextColor(...COLORS.white as [number, number, number]);
    this.pdf.setFontSize(14);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.text('CareerPath', PDF_CONFIG.margin, 12);
    this.pdf.setFontSize(10);
    this.pdf.setFont('helvetica', 'normal');
    this.pdf.text('AI-Powered Career Simulation Report', PDF_CONFIG.margin, 18);

    // Date
    this.pdf.setFontSize(9);
    this.pdf.text(
      `Generated: ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`,
      PDF_CONFIG.pageWidth - PDF_CONFIG.margin - 50,
      15
    );

    this.currentY = PDF_CONFIG.headerHeight + 10;
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
  }

  private addFooter(): void {
    this.pdf.setFontSize(8);
    this.pdf.setTextColor(...COLORS.muted as [number, number, number]);
    this.pdf.text(
      `Page ${this.pageNumber}`,
      PDF_CONFIG.pageWidth / 2,
      PDF_CONFIG.pageHeight - 8,
      { align: 'center' }
    );
    this.pdf.text(
      'CareerPath - Your AI Career Advisor',
      PDF_CONFIG.pageWidth - PDF_CONFIG.margin,
      PDF_CONFIG.pageHeight - 8,
      { align: 'right' }
    );
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
  }

  private addTitle(text: string): void {
    this.checkPageBreak(15);
    this.pdf.setFontSize(PDF_CONFIG.titleSize);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.setTextColor(...COLORS.primary as [number, number, number]);
    this.pdf.text(text, PDF_CONFIG.pageWidth / 2, this.currentY, { align: 'center' });
    this.currentY += 12;
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
  }

  private addSectionTitle(text: string): void {
    this.checkPageBreak(20);
    this.currentY += 5;
    
    // Section divider line
    this.pdf.setDrawColor(...COLORS.primary as [number, number, number]);
    this.pdf.setLineWidth(0.5);
    this.pdf.line(PDF_CONFIG.margin, this.currentY, PDF_CONFIG.pageWidth - PDF_CONFIG.margin, this.currentY);
    this.currentY += 8;

    this.pdf.setFontSize(PDF_CONFIG.headingSize);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.setTextColor(...COLORS.primary as [number, number, number]);
    this.pdf.text(text, PDF_CONFIG.margin, this.currentY);
    this.currentY += 10;
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
  }

  private addSubHeading(text: string): void {
    this.checkPageBreak(12);
    this.pdf.setFontSize(PDF_CONFIG.subHeadingSize);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.text(text, PDF_CONFIG.margin, this.currentY);
    this.currentY += 7;
    this.pdf.setFont('helvetica', 'normal');
  }

  private addParagraph(text: string, indent: number = 0): void {
    this.pdf.setFontSize(PDF_CONFIG.bodySize);
    this.pdf.setFont('helvetica', 'normal');
    
    const maxWidth = PDF_CONFIG.pageWidth - (2 * PDF_CONFIG.margin) - indent;
    const lines = this.pdf.splitTextToSize(text, maxWidth);
    
    lines.forEach((line: string) => {
      this.checkPageBreak(6);
      this.pdf.text(line, PDF_CONFIG.margin + indent, this.currentY);
      this.currentY += PDF_CONFIG.lineHeight;
    });
  }

  private addBulletPoint(text: string, indent: number = 5): void {
    this.checkPageBreak(6);
    this.pdf.setFontSize(PDF_CONFIG.bodySize);
    this.pdf.text('•', PDF_CONFIG.margin + indent, this.currentY);
    
    const maxWidth = PDF_CONFIG.pageWidth - (2 * PDF_CONFIG.margin) - indent - 5;
    const lines = this.pdf.splitTextToSize(text, maxWidth);
    
    lines.forEach((line: string, index: number) => {
      if (index > 0) this.checkPageBreak(6);
      this.pdf.text(line, PDF_CONFIG.margin + indent + 5, this.currentY);
      this.currentY += PDF_CONFIG.lineHeight;
    });
  }

  private addKeyValue(key: string, value: string | number, highlightValue: boolean = false): void {
    this.checkPageBreak(7);
    this.pdf.setFontSize(PDF_CONFIG.bodySize);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.text(`${key}:`, PDF_CONFIG.margin, this.currentY);
    this.pdf.setFont('helvetica', 'normal');
    
    if (highlightValue) {
      this.pdf.setTextColor(...COLORS.primary as [number, number, number]);
    }
    this.pdf.text(String(value), PDF_CONFIG.margin + 55, this.currentY);
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
    this.currentY += PDF_CONFIG.lineHeight;
  }

  private addStatCard(label: string, value: string, x: number, y: number, width: number = 42): void {
    // Card background
    this.pdf.setFillColor(...COLORS.background as [number, number, number]);
    this.pdf.setDrawColor(...COLORS.border as [number, number, number]);
    this.pdf.roundedRect(x, y, width, 22, 2, 2, 'FD');
    
    // Value
    this.pdf.setFontSize(12);
    this.pdf.setFont('helvetica', 'bold');
    this.pdf.setTextColor(...COLORS.primary as [number, number, number]);
    this.pdf.text(value, x + width / 2, y + 10, { align: 'center' });
    
    // Label
    this.pdf.setFontSize(7);
    this.pdf.setFont('helvetica', 'normal');
    this.pdf.setTextColor(...COLORS.muted as [number, number, number]);
    this.pdf.text(label, x + width / 2, y + 18, { align: 'center' });
    
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
  }

  private addProgressBar(label: string, value: number, maxValue: number = 100): void {
    this.checkPageBreak(15);
    
    const barWidth = 100;
    const barHeight = 6;
    const x = PDF_CONFIG.margin;
    
    // Label
    this.pdf.setFontSize(PDF_CONFIG.smallSize);
    this.pdf.text(label, x, this.currentY);
    this.pdf.text(`${value}%`, x + barWidth + 5, this.currentY);
    this.currentY += 3;
    
    // Background bar
    this.pdf.setFillColor(...COLORS.border as [number, number, number]);
    this.pdf.roundedRect(x, this.currentY, barWidth, barHeight, 1, 1, 'F');
    
    // Progress bar
    const progressWidth = (value / maxValue) * barWidth;
    const progressColor = value >= 70 ? COLORS.secondary : value >= 40 ? COLORS.warning : COLORS.danger;
    this.pdf.setFillColor(...progressColor as [number, number, number]);
    this.pdf.roundedRect(x, this.currentY, progressWidth, barHeight, 1, 1, 'F');
    
    this.currentY += barHeight + 5;
  }

  private addTable(headers: string[], rows: string[][], columnWidths: number[]): void {
    const startX = PDF_CONFIG.margin;
    let startY = this.currentY;
    const rowHeight = 8;
    const cellPadding = 2;
    
    // Header
    this.pdf.setFillColor(...COLORS.primary as [number, number, number]);
    this.pdf.rect(startX, startY, columnWidths.reduce((a, b) => a + b, 0), rowHeight, 'F');
    
    this.pdf.setTextColor(...COLORS.white as [number, number, number]);
    this.pdf.setFontSize(PDF_CONFIG.smallSize);
    this.pdf.setFont('helvetica', 'bold');
    
    let currentX = startX;
    headers.forEach((header, i) => {
      this.pdf.text(header, currentX + cellPadding, startY + 5.5);
      currentX += columnWidths[i];
    });
    
    startY += rowHeight;
    this.pdf.setTextColor(...COLORS.text as [number, number, number]);
    this.pdf.setFont('helvetica', 'normal');
    
    // Rows
    rows.forEach((row, rowIndex) => {
      this.checkPageBreak(rowHeight + 5);
      
      // Alternating row colors
      if (rowIndex % 2 === 0) {
        this.pdf.setFillColor(...COLORS.background as [number, number, number]);
        this.pdf.rect(startX, startY, columnWidths.reduce((a, b) => a + b, 0), rowHeight, 'F');
      }
      
      currentX = startX;
      row.forEach((cell, i) => {
        const truncatedText = cell.length > 30 ? cell.substring(0, 27) + '...' : cell;
        this.pdf.text(truncatedText, currentX + cellPadding, startY + 5.5);
        currentX += columnWidths[i];
      });
      
      startY += rowHeight;
    });
    
    this.currentY = startY + 5;
  }

  // Main export method
  async exportToPDF(
    result: SimulationResponse,
    profile: CareerProfile | null,
    selectedCareer: CareerFit | null,
    options: ExportOptions = {}
  ): Promise<void> {
    const {
      includeTimeline = true,
      includeFinancials = true,
      includeRisks = true,
      includeSkillGaps = true,
      includeRecommendations = true,
    } = options;

    // Initialize PDF
    this.addHeader();

    // Cover Page
    this.addTitle('Career Simulation Report');
    this.currentY += 10;

    // Selected Career Overview
    if (selectedCareer) {
      this.addSectionTitle('🎯 Your Selected Career Path');
      this.addKeyValue('Career', selectedCareer.career_title, true);
      this.addKeyValue('Field', selectedCareer.career_field);
      this.addKeyValue('Overall Match Score', `${selectedCareer.overall_fit_score}%`);
      this.addKeyValue('Time to Entry', selectedCareer.time_to_entry);
      this.addKeyValue('Difficulty Level', selectedCareer.difficulty_level);
      this.addKeyValue('Salary Range', selectedCareer.typical_salary_range);
      this.currentY += 5;

      // Fit Scores
      this.addSubHeading('Fit Score Breakdown');
      this.addProgressBar('Skill Fit', selectedCareer.skill_fit_score);
      this.addProgressBar('Interest Fit', selectedCareer.interest_fit_score);
      this.addProgressBar('Market Fit', selectedCareer.market_fit_score);
      this.addProgressBar('Personality Fit', selectedCareer.personality_fit_score);

      // Why This Career
      if (selectedCareer.reasoning) {
        this.currentY += 5;
        this.addSubHeading('Why This Career Fits You');
        
        if (selectedCareer.reasoning.strengths_alignment?.length > 0) {
          this.addParagraph('Strengths Alignment:', 0);
          selectedCareer.reasoning.strengths_alignment.forEach(s => this.addBulletPoint(s));
        }
        
        if (selectedCareer.reasoning.interest_match?.length > 0) {
          this.addParagraph('Interest Match:', 0);
          selectedCareer.reasoning.interest_match.forEach(s => this.addBulletPoint(s));
        }

        if (selectedCareer.reasoning.why_now) {
          this.addParagraph(`Why Now: ${selectedCareer.reasoning.why_now}`, 0);
        }
      }
    }

    // Executive Summary
    this.addSectionTitle('📊 Executive Summary');
    
    const summary = result.summary;
    const timeline = result.timeline;
    const financial = result.financial_analysis;
    const risk = result.risk_assessment;
    
    // Summary Stats in a row
    const cardY = this.currentY;
    if (summary?.target_role) this.addStatCard('Target Role', summary.target_role.substring(0, 15), PDF_CONFIG.margin, cardY, 45);
    if (summary?.timeline_years) this.addStatCard('Timeline', `${summary.timeline_years} Years`, PDF_CONFIG.margin + 47, cardY);
    if (risk?.success_probability_score) this.addStatCard('Success Rate', `${risk.success_probability_score.toFixed(0)}%`, PDF_CONFIG.margin + 91, cardY);
    if (financial?.total_investment_required) this.addStatCard('Investment', `$${(financial.total_investment_required / 1000).toFixed(0)}K`, PDF_CONFIG.margin + 135, cardY);
    this.currentY = cardY + 28;

    // Key Milestones
    if (summary?.key_milestones?.length) {
      this.addSubHeading('Key Milestones');
      summary.key_milestones.forEach(m => this.addBulletPoint(m));
    }

    // Warnings
    if (result.warnings?.length > 0) {
      this.currentY += 5;
      this.addSubHeading('⚠️ Important Warnings');
      this.pdf.setTextColor(...COLORS.warning as [number, number, number]);
      result.warnings.forEach(w => this.addBulletPoint(w));
      this.pdf.setTextColor(...COLORS.text as [number, number, number]);
    }

    // Timeline Section
    if (includeTimeline && timeline) {
      this.addNewPage();
      this.addSectionTitle('📅 Career Timeline');
      
      this.addKeyValue('Recommended Path', timeline.recommended_path.charAt(0).toUpperCase() + timeline.recommended_path.slice(1), true);
      this.addKeyValue('Recommendation Reason', timeline.recommendation_reason);
      this.addKeyValue('Alignment Score', `${timeline.alignment_score}%`);
      
      // Year by Year Plans
      const recommendedPath = this.getRecommendedPath(timeline);
      if (recommendedPath?.yearly_plans) {
        this.currentY += 5;
        this.addSubHeading(`Year-by-Year Roadmap (${recommendedPath.path_label})`);
        
        recommendedPath.yearly_plans.forEach(year => {
          this.checkPageBreak(40);
          
          // Year header
          this.pdf.setFillColor(...COLORS.primary as [number, number, number]);
          this.pdf.roundedRect(PDF_CONFIG.margin, this.currentY, 20, 8, 2, 2, 'F');
          this.pdf.setTextColor(...COLORS.white as [number, number, number]);
          this.pdf.setFontSize(PDF_CONFIG.bodySize);
          this.pdf.setFont('helvetica', 'bold');
          this.pdf.text(`Year ${year.year_number}`, PDF_CONFIG.margin + 3, this.currentY + 5.5);
          
          this.pdf.setTextColor(...COLORS.text as [number, number, number]);
          this.pdf.text(year.year_label, PDF_CONFIG.margin + 25, this.currentY + 5.5);
          this.currentY += 12;
          
          this.pdf.setFont('helvetica', 'normal');
          this.addParagraph(`Focus: ${year.primary_focus}`, 5);
          this.addParagraph(`Phase: ${year.phase}`, 5);
          
          if (year.expected_role) {
            this.addParagraph(`Expected Role: ${year.expected_role}`, 5);
          }
          if (year.expected_salary_range) {
            this.addParagraph(`Expected Salary: ${year.expected_salary_range}`, 5);
          }
          
          // Key milestones for the year
          if (year.milestones?.length > 0) {
            this.addParagraph('Key Milestones:', 5);
            year.milestones.slice(0, 4).forEach(m => {
              this.addBulletPoint(`Q${m.quarter}: ${m.title}`, 10);
            });
          }
          
          this.currentY += 5;
        });
      }
    }

    // Skills Gap Section
    if (includeSkillGaps && result.gap_analysis) {
      this.addNewPage();
      this.addSectionTitle('🎯 Skills Gap Analysis');
      
      const gap = result.gap_analysis;
      
      this.addKeyValue('Overall Gap Score', `${gap.overall_gap_score?.toFixed(0)}%`);
      this.addKeyValue('Gap Category', gap.gap_category || 'Moderate');
      this.addKeyValue('Experience Gap', `${gap.experience_gap_years || 0} years`);
      
      if (gap.analysis_reasoning) {
        this.currentY += 3;
        this.addParagraph(gap.analysis_reasoning);
      }
      
      // Technical Skill Gaps
      if (gap.technical_skill_gaps?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Technical Skills to Develop');
        
        const headers = ['Skill', 'Current', 'Required', 'Gap', 'Time'];
        const rows = gap.technical_skill_gaps.slice(0, 8).map(skill => [
          skill.skill_name,
          skill.current_level,
          skill.required_level,
          `${skill.gap_severity.toFixed(0)}%`,
          skill.estimated_time_to_close
        ]);
        this.addTable(headers, rows, [40, 30, 30, 20, 35]);
      }
      
      // Soft Skill Gaps
      if (gap.soft_skill_gaps?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Soft Skills to Develop');
        gap.soft_skill_gaps.slice(0, 5).forEach(skill => {
          this.addBulletPoint(`${skill.skill_name}: ${skill.current_level} → ${skill.required_level} (${skill.estimated_time_to_close})`);
        });
      }
      
      // Existing Strengths
      if (gap.existing_strengths?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Your Existing Strengths');
        gap.existing_strengths.forEach(s => this.addBulletPoint(s));
      }
      
      // Critical Bottlenecks
      if (gap.critical_bottlenecks?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Critical Bottlenecks');
        this.pdf.setTextColor(...COLORS.warning as [number, number, number]);
        gap.critical_bottlenecks.forEach(b => this.addBulletPoint(b));
        this.pdf.setTextColor(...COLORS.text as [number, number, number]);
      }
    }

    // Financial Section
    if (includeFinancials && financial) {
      this.addNewPage();
      this.addSectionTitle('💰 Financial Analysis');
      
      // Financial Stats
      const finCardY = this.currentY;
      this.addStatCard('Total Investment', `$${(financial.total_investment_required / 1000).toFixed(0)}K`, PDF_CONFIG.margin, finCardY);
      this.addStatCard('5-Year ROI', `${financial.five_year_roi?.toFixed(0)}%`, PDF_CONFIG.margin + 44, finCardY);
      this.addStatCard('Break-even', `Year ${financial.break_even_year}`, PDF_CONFIG.margin + 88, finCardY);
      this.addStatCard('10-Yr Earnings', `$${(financial.ten_year_projected_earnings / 1000000).toFixed(1)}M`, PDF_CONFIG.margin + 132, finCardY);
      this.currentY = finCardY + 30;
      
      // Affordability
      this.addKeyValue('Affordability Rating', financial.affordability_rating || 'Moderate');
      if (financial.affordability_reasoning) {
        this.addParagraph(financial.affordability_reasoning);
      }
      
      // Yearly Financials Table
      if (financial.yearly_financials?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Yearly Financial Breakdown');
        
        const headers = ['Year', 'Investment', 'Income', 'Net Flow', 'Cumulative'];
        const rows = financial.yearly_financials.slice(0, 6).map(yf => [
          `Year ${yf.year_number}`,
          `$${yf.total_investment.toLocaleString()}`,
          `$${yf.expected_income.toLocaleString()}`,
          `$${yf.net_cash_flow.toLocaleString()}`,
          `$${yf.cumulative_investment.toLocaleString()}`
        ]);
        this.addTable(headers, rows, [25, 35, 35, 35, 35]);
      }
      
      // Funding Options
      if (financial.funding_options?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Funding Options');
        financial.funding_options.forEach(f => this.addBulletPoint(f));
      }
      
      // Cost Saving Tips
      if (financial.cost_saving_opportunities?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Cost Saving Opportunities');
        financial.cost_saving_opportunities.forEach(c => this.addBulletPoint(c));
      }
    }

    // Risk Assessment Section
    if (includeRisks && risk) {
      this.addNewPage();
      this.addSectionTitle('⚠️ Risk Assessment');
      
      // Risk Overview
      this.addKeyValue('Success Probability', `${risk.success_probability_score?.toFixed(0)}%`, true);
      this.addKeyValue('Confidence Interval', risk.confidence_interval || 'Medium');
      this.addKeyValue('Overall Risk Rating', risk.overall_risk_rating || 'Moderate');
      
      if (risk.success_reasoning) {
        this.currentY += 3;
        this.addParagraph(risk.success_reasoning);
      }
      
      // Risk Scores
      this.currentY += 5;
      this.addSubHeading('Risk Score Breakdown');
      this.addProgressBar('Market Risk', risk.market_risk_score || 0);
      this.addProgressBar('Personal Risk', risk.personal_risk_score || 0);
      this.addProgressBar('Financial Risk', risk.financial_risk_score || 0);
      this.addProgressBar('Technical Risk', risk.technical_risk_score || 0);
      
      // Scenarios
      if (risk.best_case_scenario || risk.most_likely_scenario || risk.worst_case_scenario) {
        this.currentY += 5;
        this.addSubHeading('Scenario Analysis');
        if (risk.best_case_scenario) {
          this.addParagraph(`Best Case: ${risk.best_case_scenario}`);
        }
        if (risk.most_likely_scenario) {
          this.addParagraph(`Most Likely: ${risk.most_likely_scenario}`);
        }
        if (risk.worst_case_scenario) {
          this.addParagraph(`Worst Case: ${risk.worst_case_scenario}`);
        }
      }
      
      // Key Concerns
      if (risk.key_concerns?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Key Concerns');
        this.pdf.setTextColor(...COLORS.danger as [number, number, number]);
        risk.key_concerns.forEach(c => this.addBulletPoint(c));
        this.pdf.setTextColor(...COLORS.text as [number, number, number]);
      }
      
      // Key Opportunities
      if (risk.key_opportunities?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Key Opportunities');
        this.pdf.setTextColor(...COLORS.secondary as [number, number, number]);
        risk.key_opportunities.forEach(o => this.addBulletPoint(o));
        this.pdf.setTextColor(...COLORS.text as [number, number, number]);
      }
      
      // Risk Factors Table
      if (risk.risk_factors?.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Detailed Risk Factors');
        
        const headers = ['Risk Factor', 'Category', 'Severity', 'Probability'];
        const rows = risk.risk_factors.slice(0, 8).map(rf => [
          rf.factor_name,
          rf.category,
          rf.severity,
          `${rf.probability}%`
        ]);
        this.addTable(headers, rows, [50, 35, 30, 30]);
      }
    }

    // Recommendations Section
    if (includeRecommendations) {
      this.addNewPage();
      this.addSectionTitle('💡 Recommendations & Next Steps');
      
      // Dashboard Data insights
      const dashData = result.dashboard_data;
      
      // Top Recommendations
      if (dashData?.top_recommendations && dashData.top_recommendations.length > 0) {
        this.addSubHeading('Top Recommendations');
        dashData.top_recommendations.forEach((rec: string, i: number) => {
          this.addBulletPoint(`${i + 1}. ${rec}`);
        });
      } else if (risk?.recommendations && risk.recommendations.length > 0) {
        this.addSubHeading('Top Recommendations');
        risk.recommendations.forEach((rec: string, i: number) => {
          this.addBulletPoint(`${i + 1}. ${rec}`);
        });
      }
      
      // Immediate Actions
      if (dashData?.immediate_actions && dashData.immediate_actions.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Immediate Actions');
        dashData.immediate_actions.forEach((action: { action: string; timeframe: string; priority: string }, i: number) => {
          this.addBulletPoint(`${i + 1}. ${action.action} (${action.timeframe}) - ${action.priority} priority`);
        });
      }
      
      // Key Insights
      if (dashData?.key_insights && dashData.key_insights.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Key Insights');
        dashData.key_insights.slice(0, 6).forEach((insight: { title: string; insight: string }) => {
          this.checkPageBreak(15);
          this.addParagraph(`${insight.title}: ${insight.insight}`);
        });
      }
      
      // Decision Points
      const recPath = timeline ? this.getRecommendedPath(timeline) : null;
      if (recPath && recPath.key_decision_points && recPath.key_decision_points.length > 0) {
        this.currentY += 5;
        this.addSubHeading('Key Decision Points');
        recPath.key_decision_points.forEach((d: string) => this.addBulletPoint(d));
      }
    }

    // Final page - Profile Summary
    this.addNewPage();
    this.addSectionTitle('👤 Profile Summary');
    
    if (profile) {
      if (profile.current_education_level) this.addKeyValue('Education Level', profile.current_education_level);
      if (profile.current_major) this.addKeyValue('Major', profile.current_major);
      if (profile.institution_name) this.addKeyValue('Institution', profile.institution_name);
      if (profile.target_career_fields?.length) this.addKeyValue('Target Fields', profile.target_career_fields.join(', '));
      if (profile.primary_career_goal) this.addKeyValue('Primary Goal', profile.primary_career_goal);
      if (profile.desired_role_level) this.addKeyValue('Desired Level', profile.desired_role_level);
      if (profile.risk_tolerance) this.addKeyValue('Risk Tolerance', profile.risk_tolerance);
      if (profile.investment_capacity) this.addKeyValue('Investment Capacity', profile.investment_capacity);
      if (profile.hours_per_week) this.addKeyValue('Available Hours/Week', profile.hours_per_week);
    }

    // Disclaimer
    this.currentY += 10;
    this.pdf.setFontSize(PDF_CONFIG.smallSize);
    this.pdf.setTextColor(...COLORS.muted as [number, number, number]);
    this.addParagraph('Disclaimer: This report is generated by AI-powered analysis and should be used as guidance only. Actual results may vary based on market conditions, personal effort, and other factors. Please consult with career professionals for personalized advice.');

    // Add final footer
    this.addFooter();

    // Save the PDF
    const fileName = `CareerPath_Report_${selectedCareer?.career_title?.replace(/\s+/g, '_') || 'Simulation'}_${new Date().toISOString().split('T')[0]}.pdf`;
    this.pdf.save(fileName);
  }

  private getRecommendedPath(timeline: any): CareerPath | null {
    if (!timeline) return null;
    const pathType = timeline.recommended_path;
    if (pathType === 'conservative') return timeline.conservative_path;
    if (pathType === 'realistic') return timeline.realistic_path;
    if (pathType === 'ambitious') return timeline.ambitious_path;
    return timeline.realistic_path;
  }

  // Export charts as images
  async captureChartAsImage(elementId: string): Promise<string | null> {
    try {
      const element = document.getElementById(elementId);
      if (!element) return null;
      
      const canvas = await html2canvas(element, {
        backgroundColor: '#ffffff',
        scale: 2,
      });
      
      return canvas.toDataURL('image/png');
    } catch (error) {
      console.error('Error capturing chart:', error);
      return null;
    }
  }
}

// Helper function for quick export
export async function exportDashboardToPDF(
  result: SimulationResponse,
  profile: CareerProfile | null,
  selectedCareer: CareerFit | null,
  options?: ExportOptions
): Promise<void> {
  const exporter = new CareerPDFExporter();
  await exporter.exportToPDF(result, profile, selectedCareer, options);
}
