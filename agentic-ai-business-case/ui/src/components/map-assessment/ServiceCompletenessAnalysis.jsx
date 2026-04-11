import { useState, useEffect } from 'react';
import {
  Container,
  Header,
  SpaceBetween,
  FormField,
  Button,
  Alert,
  ExpandableSection,
  Box,
  Spinner,
  Badge,
  ColumnLayout,
  Toggle,
  Textarea,
  Table,
  ProgressBar,
  Grid,
  StatusIndicator,
  Input,
  Tabs
} from '@cloudscape-design/components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getApiUrl } from '../../utils/apiConfig.js';
import { useMapAssessment } from '../../contexts/MapAssessmentContext.jsx';

const SERVICE_ANALYSIS_PROMPT = `I need you to analyze an AWS Pricing Calculator CSV file for a cloud migration and provide a comprehensive service completeness analysis and gap identification.

**Context:**
- This is a cloud migration infrastructure assessment
- Customers typically underestimate non-compute infrastructure by 10x
- We need to identify missing services across 6 critical categories to ensure production-ready, well-architected solutions

**Analysis Required:**

1. **INFRASTRUCTURE VALIDATION**
- Extract and calculate total infrastructure costs from the CSV
- Break down costs by service category:
  * Compute (EC2, Fargate, Lambda, etc.)
  * Storage (S3, EBS, EFS, FSx, etc.)
  * Database (RDS, Aurora, DynamoDB, etc.)
  * Network (ALB, NLB, CloudFront, Route 53, Data Transfer, etc.)
  * Security (KMS, WAF, GuardDuty, Secrets Manager, etc.)
  * Monitoring (CloudWatch, CloudTrail, X-Ray, etc.)
- Calculate compute vs non-compute ratio
- Compare against production-ready benchmark (56% compute, 44% non-compute)

2. **GAP ANALYSIS - 6 CRITICAL CATEGORIES**

**Category 1: Backup & Recovery**
- Check for: AWS Backup services (including EFS Backup, VMware Backup, Timestream Backup, Storage Gateway Backup, FSx Backup, S3 Backup, Redshift Backup, RDS Backup, EBS Backup, DynamoDB Backup, Aurora Backup, Neptune Backup, DocumentDB Backup, SAP HANA Backup, Aurora DSQL Backup), EBS snapshots, S3 Glacier, cross-region backup replication
- IMPORTANT: If ANY of these backup services are present (DynamoDB Backup, Aurora Backup, RDS Backup, etc.), AWS Backup IS included - do NOT flag as missing
- Common gap: Customers plan database compute but forget backup storage
- Expected: 2-3% of total infrastructure costs
- Questions: "What's your backup retention policy? Do you need cross-region backups?"

**Category 2: Storage Infrastructure**
- Check for: S3 (all tiers), EFS, FSx (Windows/Lustre/NetApp/OpenZFS), Storage Gateway, EBS volumes
- Common gap: Customers plan S3 Standard but miss FSx, Storage Gateway, S3 Intelligent-Tiering
- Expected: 25-30% of total infrastructure costs
- Questions: "Do you have Windows file shares? Need hybrid storage connectivity?"

**Category 3: DR/HA Configuration**
- Check for: Multi-AZ deployments, cross-region replication, Elastic Disaster Recovery, Route 53 health checks
- Common gap: Customers plan single-region only, no DR orchestration
- Expected: 1-2% of total infrastructure costs
- Questions: "What's your RTO/RPO? Need disaster recovery in another region?"

**Category 4: Network Services**
- Check for: ALB/NLB, CloudFront, Route 53, Transit Gateway, Direct Connect, VPN, Data Transfer, Public IPv4, NAT Gateway, Network Firewall
- Common gap: Customers plan load balancers but miss CDN, DNS, data transfer costs, IPv4 addressing
- Expected: 10-15% of total infrastructure costs
- Questions: "Do you serve content globally? How much outbound traffic? How many public IPs? Even though CCOE/central team is managing networking, the increase in traffic wrt NAT Gateway, Transit Gateway Attachment should be included, isn't it?"

**Category 5: Observability & Monitoring**
- Check for: CloudWatch (metrics, logs, alarms), CloudTrail, X-Ray, VPC Flow Logs, Config, Systems Manager
- Common gap: Customers assume monitoring is "free" or "included"
- Expected: 2-4% of total infrastructure costs
- Questions: "What monitoring tools do you use today? Need audit logging for compliance? Even if 3rd party tools are going to be used, are they not integrated by using cloudwatch & Kinesis which means you need to hold data for short duration in AWS monitoring services?"

**Category 6: Security & Compliance**
- Check for: KMS, WAF, Shield, GuardDuty, Security Hub, Secrets Manager, Certificate Manager, Network Firewall, Macie
- Common gap: Customers include only KMS, miss application-layer security and credential management
- Expected: 2-4% of total infrastructure costs
- Questions: "What compliance frameworks apply? How do you manage secrets/credentials? How about encryption at rest and encryption in transit & certificate management?"

3. **OUTPUT FORMAT**

Provide the analysis in this structure:

**A. INFRASTRUCTURE COMPLETENESS SUMMARY**
\`\`\`
Total Annual Infrastructure Cost: $XXX,XXX
Breakdown:
- Compute: $XXX,XXX (XX%)
- Storage: $XXX,XXX (XX%)
- Database: $XXX,XXX (XX%)
- Network: $XXX,XXX (XX%)
- Security: $XXX,XXX (XX%)
- Monitoring: $XXX,XXX (XX%)

Compute vs Non-Compute Ratio: XX% / XX%
Production-Ready Benchmark: 56% / 44%
Assessment: [Complete / Incomplete / Needs Review]
\`\`\`

**B. SERVICE GAP ANALYSIS BY CATEGORY**

For each of the 6 categories, provide:
\`\`\`
Category: [Name]
Status: [Complete / Partial / Missing]
Current Cost: $XXX,XXX (XX% of total)
Expected Cost: $XXX,XXX (XX% of total)
Gap: $XXX,XXX
Services Found: [List]
Services Missing: [List with estimated cost impact]
Priority: [High / Medium / Low]
Questions to Ask Customer: [Specific questions]
\`\`\`

**C. MISSING SERVICES SUMMARY**

Create a prioritized table:
| Priority | Service | Category | Estimated Cost | Why It's Missing | Questions to Ask |
|----------|---------|----------|----------------|------------------|------------------|
| HIGH     | ...     | ...      | $XX,XXX        | ...              | ...              |

**D. RECOMMENDATIONS**

Provide specific, actionable recommendations:
1. Immediate Actions (High Priority)
2. Secondary Review (Medium Priority)
3. Future Consideration (Low Priority)

**E. ESTIMATED ADDITIONAL INFRASTRUCTURE NEEDED**
\`\`\`
Conservative Estimate: $XXX,XXX - $XXX,XXX/year
Realistic Estimate: $XXX,XXX - $XXX,XXX/year
\`\`\`

**F. COMPLETENESS RED FLAGS**

List any red flags found:
- No backup services (check for ANY service ending in "Backup" like DynamoDB Backup, Aurora Backup, RDS Backup, etc.)
- No CDN for web applications
- Security services <1% of total costs
- etc.

**G. NEXT STEPS**

Provide 5-7 specific action items for engaging with the customer.

4. **KEY COMPLETENESS CHECKS**

Flag these red flags:
- No backup services (check for: AWS Backup, DynamoDB Backup, Aurora Backup, RDS Backup, EBS Backup, or any other *Backup service - if ANY are present, backup IS included)
- No CDN (CloudFront) for web applications
- No DNS service (Route 53)
- No WAF for web applications
- No Secrets Manager for credential management
- No CloudTrail for audit logging
- Data transfer costs seem too low (<5% of total)
- Security services <1% of total costs
- No monitoring beyond basic CloudWatch
- Compute >80% of total (non-compute severely underestimated)

**Please analyze the provided CSV data and provide the complete analysis following this format.**`;

function ServiceCompletenessAnalysis() {
  const {
    serviceAnalysisData,
    setServiceAnalysisData,
    resetServiceAnalysis
  } = useMapAssessment();

  const [calculatorUrl, setCalculatorUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [calcLoading, setCalcLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [error, setError] = useState(null);
  const [calcError, setCalcError] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState('');

  // Results
  const [calculatorData, setCalculatorData] = useState(serviceAnalysisData?.calculatorData || null);
  const [analysis, setAnalysis] = useState(serviceAnalysisData?.analysis || null);

  // Prompt customization
  const [customPrompt, setCustomPrompt] = useState(SERVICE_ANALYSIS_PROMPT);
  const [useCustomPrompt, setUseCustomPrompt] = useState(false);

  // Results tab
  const [activeResultTab, setActiveResultTab] = useState('calculator-review');

  // Load existing data from context on mount
  useEffect(() => {
    if (serviceAnalysisData?.analysis) {
      setAnalysis(serviceAnalysisData.analysis);
    }
    if (serviceAnalysisData?.calculatorData) {
      setCalculatorData(serviceAnalysisData.calculatorData);
    }
  }, []);

  // Load saved custom prompt from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('map_custom_prompt_service_analysis');
    if (saved) {
      setCustomPrompt(saved);
      setUseCustomPrompt(true);
    }
  }, []);

  const saveCustomPrompt = () => {
    localStorage.setItem('map_custom_prompt_service_analysis', customPrompt);
    alert('Custom prompt saved successfully!');
  };

  const resetPrompt = () => {
    if (confirm('Reset prompt to default? This cannot be undone.')) {
      setCustomPrompt(SERVICE_ANALYSIS_PROMPT);
      setUseCustomPrompt(false);
      localStorage.removeItem('map_custom_prompt_service_analysis');
      alert('Prompt reset to default!');
    }
  };

  const formatCurrency = (amount) => {
    const currency = calculatorData?.is_esc ? 'EUR' : 'USD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0
    }).format(amount);
  };

  const parseExclusionBreakdown = (breakdownString) => {
    if (!breakdownString) return null;
    try {
      const jsonString = breakdownString
        .replace(/'/g, '"')
        .replace(/None/g, 'null')
        .replace(/True/g, 'true')
        .replace(/False/g, 'false');
      return JSON.parse(jsonString);
    } catch {
      return null;
    }
  };

  const handleAnalyze = async () => {
    if (!calculatorUrl.trim()) {
      setError('Please enter an AWS Calculator URL');
      return;
    }

    setLoading(true);
    setError(null);
    setCalcError(null);
    setAnalysisError(null);
    setCalcLoading(true);
    setAnalysisLoading(false);
    setLoadingStatus('Fetching calculator data...');

    let calcData = null;

    try {
      // Step 1: Fetch calculator data from URL
      const calcResponse = await fetch(getApiUrl('/map/service-completeness/analyze-url'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ calculator_url: calculatorUrl })
      });

      const calcResult = await calcResponse.json();
      if (calcResult.success) {
        calcData = calcResult;
        setCalculatorData(calcResult);
      } else {
        setCalcError(calcResult.message || 'Calculator URL analysis failed');
      }
    } catch (err) {
      setCalcError(err.message || 'Failed to fetch calculator data');
    }
    setCalcLoading(false);

    // Step 2: Run AI analysis using the calculator data (only if step 1 succeeded)
    if (calcData) {
      setAnalysisLoading(true);
      setLoadingStatus('Running AI analysis...');

      try {
        const prompt = useCustomPrompt ? customPrompt : SERVICE_ANALYSIS_PROMPT;
        const services = calcData.services || [];
        const currencySymbol = calcData.is_esc ? '€' : '$';
        const currencyCode = calcData.is_esc ? 'EUR' : 'USD';

        // Generate services summary for AI analysis
        const servicesSummary = services.map(s =>
          `${s.service_name}, ${s.region}, ${s.description}, Monthly: ${currencySymbol}${s.monthly_cost}, Annual: ${currencySymbol}${s.monthly_cost * 12}`
        ).join('\n');
        
        // Add currency context to the prompt
        const currencyNote = calcData.is_esc 
          ? `\n\n**IMPORTANT: This is a European Sovereign Cloud (ESC) calculator. All costs are in EUR (€). Use € symbol for all currency values in your analysis, not $.** \n`
          : '';
        
        const csvBlob = new Blob(
          [`Service,Region,Description,Monthly Cost (${currencyCode}),Annual Cost (${currencyCode})\n${servicesSummary}`],
          { type: 'text/csv' }
        );
        const analysisFormData = new FormData();
        analysisFormData.append('file', csvBlob, 'calculator_services.csv');
        analysisFormData.append('custom_prompt', prompt + currencyNote);

        const analysisResponse = await fetch(getApiUrl('/map/service-analysis/analyze'), {
          method: 'POST',
          body: analysisFormData
        });

        const analysisResult = await analysisResponse.json();
        if (analysisResult.success) {
          setAnalysis(analysisResult.analysis);
          setServiceAnalysisData({
            analysis: analysisResult.analysis,
            calculatorData: calcData
          });
        } else {
          setAnalysisError(analysisResult.message || 'Missing services analysis failed');
          // Still save calculator data even if analysis fails
          setServiceAnalysisData({
            analysis: '',
            calculatorData: calcData
          });
        }
      } catch (err) {
        setAnalysisError(err.message || 'AI analysis failed');
        setServiceAnalysisData({
          analysis: '',
          calculatorData: calcData
        });
      }
      setAnalysisLoading(false);
    } else {
      // Save empty context if calculator fetch failed
      setServiceAnalysisData({ analysis: '', calculatorData: null });
    }

    setLoading(false);
    setLoadingStatus('');
  };

  const handleReset = () => {
    setCalculatorData(null);
    setAnalysis(null);
    setCalculatorUrl('');
    setError(null);
    setCalcError(null);
    setAnalysisError(null);
    resetServiceAnalysis();
  };

  const handleDownloadAnalysis = () => {
    if (!calculatorData) return;
    const blob = new Blob([JSON.stringify(calculatorData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'calculator_analysis.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadOptimizationReport = () => {
    if (!calculatorData) return;
    const services = calculatorData.services || [];
    const optimizableServices = services.filter(s => s.ec2_sp_annual_savings > 0);
    if (optimizableServices.length === 0) return;

    const parseConfigSummary = (config, field) => {
      if (!config) return '-';
      const match = config.match(new RegExp(`${field}\\s*\\(([^)]+)\\)`));
      return match ? match[1] : '-';
    };

    const currencySymbol = calculatorData.is_esc ? '€' : '$';
    const headers = [
      'Service Name', 'Description', 'Region',
      'Instance Type', 'Operating System',
      `Monthly Cost (${currencySymbol})`, `Annual SP Savings (${currencySymbol})`,
      `SP Hourly Rate (${currencySymbol})`, 'Plan Type'
    ];

    const rows = optimizableServices.map(s => [
      s.service_name?.trim() || '-',
      s.description || '-',
      s.region || '-',
      parseConfigSummary(s.config_summary, 'Advance EC2 instance'),
      parseConfigSummary(s.config_summary, 'Operating system'),
      s.monthly_cost?.toFixed(2) || '0.00',
      s.ec2_sp_annual_savings?.toFixed(2) || '0.00',
      s.ec2_sp_hourly_rate?.toFixed(5) || '0.00000',
      s.ec2_sp_plan_type || '-'
    ]);

    const totalSavings = optimizableServices.reduce((sum, s) => sum + (s.ec2_sp_annual_savings || 0), 0);
    rows.push(['TOTAL', '', '', '', '', '', totalSavings.toFixed(2), '', '']);

    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ec2_savings_plan_optimization_report.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadMarkdown = (content, filename) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const hasResults = calculatorData || analysis;

  // ---- Calculator Review Dashboard ----

  const renderDashboardGrid = () => {
    if (!calculatorData) return null;
    const services = calculatorData.services || [];
    const pathways = calculatorData.modernizationPathways || {};
    const totalARR = pathways.totalARR || 0;

    // Calculate ARR before exclusions
    const annualARRBeforeExclusions = services.reduce(
      (sum, s) => sum + ((s.monthly_cost * 12) + (s.upfront_cost || 0)), 0
    );

    // Excluded services
    const excludedServices = services.filter(s => s.monthly_always_excluded > 0);
    const totalExcluded = excludedServices.reduce((sum, s) => {
      const breakdown = parseExclusionBreakdown(s.exclusion_breakdown);
      return sum + (breakdown?.arr !== undefined ? breakdown.arr : s.monthly_always_excluded * 12);
    }, 0);
    const excludedPercentage = annualARRBeforeExclusions > 0
      ? (totalExcluded / annualARRBeforeExclusions) * 100
      : 0;

    // SP savings
    const totalSPSavings = services.reduce((sum, s) => sum + (s.ec2_sp_annual_savings || 0), 0);
    const totalDeductions = totalExcluded + totalSPSavings;
    const qualifiedARR = annualARRBeforeExclusions - totalDeductions;
    const nonOptimizedPct = totalARR > 0 ? (totalSPSavings / totalARR) * 100 : 0;
    const optimizableCount = services.filter(s => s.ec2_sp_annual_savings > 0).length;

    // Group excluded by type
    const excludedByType = {};
    excludedServices.forEach(service => {
      const breakdown = parseExclusionBreakdown(service.exclusion_breakdown);
      if (!breakdown) return;
      const type = breakdown.type || 'other';
      if (!excludedByType[type]) {
        excludedByType[type] = { totalAnnual: 0, services: [] };
      }
      const annualAmount = breakdown.arr !== undefined
        ? breakdown.arr
        : service.monthly_always_excluded * 12;
      excludedByType[type].totalAnnual += annualAmount;
      excludedByType[type].services.push({ name: service.service_name, breakdown });
    });

    return (
      <Container header={<Header variant="h2">Dashboard Overview</Header>}>
        <Grid gridDefinition={[{ colspan: 4 }, { colspan: 4 }, { colspan: 4 }]}>
          {/* Column 1: ARR Qualification */}
          <Container>
            <Box variant="h3" color="text-status-info">ARR Qualification</Box>
            <SpaceBetween size="s">
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Calculator Provided ARR</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold">
                  {formatCurrency(annualARRBeforeExclusions)}
                </Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Excluded Services</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  ({formatCurrency(totalExcluded)})
                </Box>
                <Box variant="small" color="text-status-inactive">
                  Data Transfer, Support, Glacier
                </Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Non-Optimized ARR</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  ({formatCurrency(totalSPSavings)})
                </Box>
                <Box variant="small" color="text-status-inactive">
                  EC2 Savings Plans Opportunity
                </Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Total Deductions</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  ({formatCurrency(totalDeductions)})
                </Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Qualified ARR</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-success">
                  {formatCurrency(qualifiedARR)}
                </Box>
              </div>
            </SpaceBetween>
          </Container>

          {/* Column 2: Excluded Services */}
          <Container>
            <Box variant="h3" color="text-status-info">Excluded Services</Box>
            <SpaceBetween size="s">
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Total Excluded</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  {formatCurrency(totalExcluded)}
                </Box>
                <Box variant="small" color="text-status-inactive">
                  ({excludedPercentage.toFixed(1)}% of ARR)
                </Box>
              </div>
              {Object.keys(excludedByType).length > 0 && (
                <div>
                  <Box variant="awsui-key-label">
                    <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Breakdown</span>
                  </Box>
                  <SpaceBetween size="xs">
                    {Object.entries(excludedByType).map(([type, data]) => (
                      <Box key={type}>
                        <Box variant="strong">
                          {type === 'aws_support' ? 'AWS Support' :
                           type === 'data_transfer' ? 'AWS Data Transfer Out' :
                           type === 'glacier_deep_archive' ? 'Amazon S3 Glacier Deep Archive' :
                           type === 'cloudfront_data_transfer' ? 'CloudFront Data Transfer Out' : type}
                        </Box>
                        <Box color="text-status-error">
                          {formatCurrency(data.totalAnnual)}
                        </Box>
                        {data.services[0]?.breakdown?.reason && (
                          <Box variant="small" color="text-status-inactive">
                            {data.services[0].breakdown.reason}
                          </Box>
                        )}
                      </Box>
                    ))}
                  </SpaceBetween>
                </div>
              )}
            </SpaceBetween>
          </Container>

          {/* Column 3: Optimization Opportunities */}
          <Container>
            <Box variant="h3" color="text-status-info">Optimization Opportunities</Box>
            <SpaceBetween size="s">
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Potential ARR Savings</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  {formatCurrency(totalSPSavings)}
                </Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Non-Optimized %</span>
                </Box>
                <Box fontSize="heading-l" fontWeight="bold" color="text-status-error">
                  {nonOptimizedPct.toFixed(1)}%
                </Box>
                <Box variant="small" color="text-status-inactive">of Total ARR</Box>
              </div>
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>EC2 Savings Plans</span>
                </Box>
                <Box color="text-status-info">
                  {optimizableCount} service{optimizableCount !== 1 ? 's' : ''} optimizable
                </Box>
              </div>
              {optimizableCount > 0 ? (
                <Button iconName="download" variant="normal" onClick={handleDownloadOptimizationReport}>
                  Download Optimization Report
                </Button>
              ) : (
                <Box color="text-status-inactive" fontSize="body-s">
                  No EC2 Savings Plan opportunities found
                </Box>
              )}
            </SpaceBetween>
          </Container>
        </Grid>
      </Container>
    );
  };

  const renderModernizationIndex = () => {
    if (!calculatorData) return null;
    const pathways = calculatorData.modernizationPathways || {};
    const totalARR = pathways.totalARR || 0;
    const modernARR = pathways.modernARR || 0;
    // Use backend-calculated index (uses qualified ARR as denominator)
    const modernPct = pathways.modernizationIndex || (totalARR > 0 ? (modernARR / totalARR) * 100 : 0);

    return (
      <Container header={<Header variant="h3">Overall Modernization Score</Header>}>
        <SpaceBetween size="m">
          <Box fontSize="display-l" fontWeight="bold" textAlign="center">
            {modernPct.toFixed(1)}%
          </Box>
          <ProgressBar
            value={modernPct}
            label="Modernization Index"
            description={`Modern ARR: ${formatCurrency(modernARR)} / Qualified ARR: ${formatCurrency(totalARR - (calculatorData.services || []).reduce((sum, s) => sum + (s.monthly_always_excluded * 12 || 0), 0))}`}
            variant="standalone"
          />
          <ColumnLayout columns={2} variant="text-grid">
            <div>
              <Box variant="awsui-key-label">Modern ARR</Box>
              <Box fontSize="heading-m" fontWeight="bold" color="text-status-success">
                {formatCurrency(modernARR)}
              </Box>
            </div>
            <div>
              <Box variant="awsui-key-label">Non-Modern ARR</Box>
              <Box fontSize="heading-m" fontWeight="bold" color="text-status-info">
                {formatCurrency(totalARR - modernARR)}
              </Box>
            </div>
          </ColumnLayout>
          <div>
            <Box variant="awsui-key-label">Total Modern ARR</Box>
            <Box fontSize="heading-l" fontWeight="bold" color="text-status-success">
              {formatCurrency(modernARR)}
            </Box>
          </div>
        </SpaceBetween>
      </Container>
    );
  };

  const renderServicesTable = () => {
    if (!calculatorData) return null;
    const services = calculatorData.services || [];

    return (
      <Table
        columnDefinitions={[
          {
            id: 'service_name',
            header: 'Service',
            cell: item => item.service_name,
            sortingField: 'service_name',
            width: 220
          },
          {
            id: 'service_code',
            header: 'Service Code',
            cell: item => item.service_code || '-'
          },
          {
            id: 'pathway',
            header: 'Modernization Pathway',
            cell: item => {
              if (item.monthly_always_excluded > 0) {
                return <Badge color="red">Excluded</Badge>;
              }
              return (
                <Badge color={item.modernization_pathway !== 'Non Modern' ? 'blue' : 'grey'}>
                  {item.modernization_pathway || '-'}
                </Badge>
              );
            }
          },
          {
            id: 'monthly_cost',
            header: 'Monthly Cost',
            cell: item => formatCurrency(item.monthly_cost),
            sortingField: 'monthly_cost'
          },
          {
            id: 'annual_cost',
            header: 'Annual Cost',
            cell: item => formatCurrency(item.monthly_cost * 12 + (item.upfront_cost || 0)),
            sortingField: 'monthly_cost'
          },
          {
            id: 'line_items',
            header: 'Line Items',
            cell: item => item.line_item_count || item.lineItems || '-'
          }
        ]}
        items={services}
        sortingDisabled={false}
        variant="embedded"
        stripedRows
        stickyHeader
        empty={
          <Box textAlign="center" color="inherit" padding="l">
            No services found in the calculator.
          </Box>
        }
        header={
          <Header counter={`(${services.length})`}>
            Services Breakdown
          </Header>
        }
      />
    );
  };

  // ---- Main Render ----
  return (
    <SpaceBetween size="l">
      <Container
        header={
          <Header
            variant="h1"
            description="Analyze your AWS Pricing Calculator for infrastructure completeness and missing services"
            actions={
              <SpaceBetween direction="horizontal" size="xs">
                {hasResults && (
                  <>
                    <Button onClick={handleDownloadAnalysis} iconName="download" disabled={!calculatorData}>
                      Download Analysis
                    </Button>
                    <Button onClick={handleReset}>Reset</Button>
                  </>
                )}
              </SpaceBetween>
            }
          >
            Service Completeness Analysis
          </Header>
        }
      >
        <SpaceBetween size="m">
          <Alert type="info">
            <SpaceBetween size="xs">
              <Box variant="strong">Comprehensive Infrastructure Analysis</Box>
              <Box>
                Paste your AWS Pricing Calculator URL to get both a structured calculator review dashboard
                and an AI-powered missing services analysis. This identifies gaps across 6 critical categories:
                Backup & Recovery, Storage, DR/HA, Network, Observability, and Security.
              </Box>
              <ColumnLayout columns={3} variant="text-grid">
                <div>
                  <Box variant="awsui-key-label">Production-Ready Benchmark</Box>
                  <Box>56% Compute / 44% Non-Compute</Box>
                </div>
                <div>
                  <Box variant="awsui-key-label">Typical Gap</Box>
                  <Box>10-40% of infrastructure missing</Box>
                </div>
                <div>
                  <Box variant="awsui-key-label">Analysis Time</Box>
                  <Box>2-3 minutes</Box>
                </div>
              </ColumnLayout>
            </SpaceBetween>
          </Alert>

          {/* URL Input Section */}
          {!hasResults && (
            <SpaceBetween size="l">
              <FormField
                label="AWS Pricing Calculator URL"
                description="Paste the share URL from AWS Pricing Calculator (supports standard AWS and European Sovereign Cloud)"
              >
                <Input
                  value={calculatorUrl}
                  onChange={({ detail }) => setCalculatorUrl(detail.value)}
                  placeholder="https://calculator.aws/#/estimate?id=... or https://pricing.calculator.aws.eu/..."
                />
              </FormField>

              {/* Custom Prompt & Coverage Section */}
              <ExpandableSection headerText="Customize Analysis Prompt" variant="default">
                <Grid gridDefinition={[{ colspan: 7 }, { colspan: 5 }]}>
                  {/* Left: Prompt editor */}
                  <SpaceBetween size="m">
                    <Alert type="info">
                      Toggle to customize the prompt used for the missing services analysis.
                      Your custom prompt will be saved for future analyses.
                    </Alert>
                    <FormField>
                      <Toggle
                        checked={useCustomPrompt}
                        onChange={({ detail }) => setUseCustomPrompt(detail.checked)}
                      >
                        <Box variant="strong">Use Custom Prompt</Box>
                      </Toggle>
                    </FormField>
                    <FormField
                      label="Service Analysis Prompt"
                      description={useCustomPrompt ? 'Edit the prompt below to customize the analysis' : 'Default prompt (toggle above to edit)'}
                    >
                      <Textarea
                        value={customPrompt}
                        onChange={({ detail }) => setCustomPrompt(detail.value)}
                        rows={20}
                        disabled={!useCustomPrompt}
                      />
                    </FormField>
                    <SpaceBetween direction="horizontal" size="xs">
                      <Button variant="primary" onClick={saveCustomPrompt} disabled={!useCustomPrompt}>
                        Save Custom Prompt
                      </Button>
                      <Button onClick={resetPrompt}>Reset to Default</Button>
                    </SpaceBetween>
                  </SpaceBetween>

                  {/* Right: What This Analysis Covers */}
                  <Container header={<Header variant="h3">What This Analysis Covers</Header>}>
                    <SpaceBetween size="m">
                      <Box variant="h4">6 Critical Categories for Production-Ready Infrastructure:</Box>
                      <SpaceBetween size="s">
                        <div>
                          <Box variant="strong">Backup & Recovery</Box>
                          <Box variant="small">AWS Backup, snapshots, Glacier, cross-region replication</Box>
                        </div>
                        <div>
                          <Box variant="strong">Storage Infrastructure</Box>
                          <Box variant="small">S3 tiers, EFS, FSx, Storage Gateway, EBS</Box>
                        </div>
                        <div>
                          <Box variant="strong">DR/HA Configuration</Box>
                          <Box variant="small">Multi-AZ, cross-region, Elastic DR, health checks</Box>
                        </div>
                        <div>
                          <Box variant="strong">Network Services</Box>
                          <Box variant="small">ALB/NLB, CloudFront, Route 53, Transit Gateway, IPv4</Box>
                        </div>
                        <div>
                          <Box variant="strong">Observability & Monitoring</Box>
                          <Box variant="small">CloudWatch, CloudTrail, X-Ray, VPC Flow Logs</Box>
                        </div>
                        <div>
                          <Box variant="strong">Security & Compliance</Box>
                          <Box variant="small">KMS, WAF, GuardDuty, Secrets Manager, Network Firewall</Box>
                        </div>
                      </SpaceBetween>
                    </SpaceBetween>
                  </Container>
                </Grid>
              </ExpandableSection>

              {error && (
                <Alert type="error" dismissible onDismiss={() => setError(null)}>
                  {error}
                </Alert>
              )}

              {loading && (
                <Box textAlign="center" padding="l">
                  <SpaceBetween size="m" alignItems="center">
                    <Spinner size="large" />
                    <Box variant="p" color="text-body-secondary">
                      {loadingStatus}
                    </Box>
                    <ColumnLayout columns={2} variant="text-grid">
                      <div>
                        <StatusIndicator type={calcLoading ? 'loading' : (calcError ? 'error' : 'success')}>
                          Calculator Review {calcLoading ? '(processing...)' : (calcError ? '(failed)' : '(complete)')}
                        </StatusIndicator>
                      </div>
                      <div>
                        <StatusIndicator type={analysisLoading ? 'loading' : (analysisError ? 'error' : (analysis ? 'success' : 'pending'))}>
                          Missing Services Analysis {analysisLoading ? '(processing...)' : (analysisError ? '(failed)' : (analysis ? '(complete)' : '(waiting)'))}
                        </StatusIndicator>
                      </div>
                    </ColumnLayout>
                  </SpaceBetween>
                </Box>
              )}

              <Box textAlign="center">
                <Button
                  variant="primary"
                  onClick={handleAnalyze}
                  disabled={loading || !calculatorUrl.trim()}
                  iconName="search"
                >
                  Analyze
                </Button>
              </Box>
            </SpaceBetween>
          )}
        </SpaceBetween>
      </Container>

      {/* Results with Tabs */}
      {hasResults && (
        <SpaceBetween size="l">
          {/* Calculator URL display */}
          {calculatorUrl && (
            <Container>
              <SpaceBetween direction="horizontal" size="xs">
                <Box variant="awsui-key-label">AWS Pricing Calculator URL:</Box>
                <Box><a href={calculatorUrl} target="_blank" rel="noopener noreferrer">{calculatorUrl}</a></Box>
              </SpaceBetween>
            </Container>
          )}

          {/* Partial error alerts */}
          {calcError && (
            <Alert type="warning" dismissible onDismiss={() => setCalcError(null)}>
              Calculator review failed: {calcError}. The missing services analysis may still be available below.
            </Alert>
          )}
          {analysisError && (
            <Alert type="warning" dismissible onDismiss={() => setAnalysisError(null)}>
              Missing services analysis failed: {analysisError}. The calculator review may still be available below.
            </Alert>
          )}

          <Tabs
            activeTabId={activeResultTab}
            onChange={({ detail }) => setActiveResultTab(detail.activeTabId)}
            tabs={[
              {
                id: 'calculator-review',
                label: 'Calculator Review',
                content: calculatorData ? (
                  <SpaceBetween size="l">
                    {renderDashboardGrid()}
                    {renderModernizationIndex()}
                    {renderServicesTable()}
                  </SpaceBetween>
                ) : (
                  <Alert type="info">Calculator review data is not available.</Alert>
                )
              },
              {
                id: 'missing-services',
                label: 'Missing Services Analysis',
                content: analysis ? (
                  <SpaceBetween size="m">
                    <Alert type="success">
                      <SpaceBetween size="xs">
                        <Box variant="strong">AI-Powered Service Gap Analysis Complete</Box>
                        <Box>
                          Review the comprehensive analysis below to identify missing services and
                          infrastructure gaps across 6 critical categories.
                        </Box>
                      </SpaceBetween>
                    </Alert>

                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {analysis}
                      </ReactMarkdown>
                    </div>

                    <Button
                      onClick={() => downloadMarkdown(analysis, 'missing_services_analysis.md')}
                      iconName="download"
                    >
                      Download Missing Services Report
                    </Button>
                  </SpaceBetween>
                ) : analysisLoading ? (
                  <Box textAlign="center" padding="xxl">
                    <SpaceBetween size="m" alignItems="center">
                      <Spinner size="large" />
                      <Box variant="p" color="text-body-secondary">
                        Running AI-powered missing services analysis... This may take 2-3 minutes.
                      </Box>
                    </SpaceBetween>
                  </Box>
                ) : (
                  <Alert type="info">Missing services analysis is not available.</Alert>
                )
              }
            ]}
          />

          {/* Next Steps */}
          <Alert type="info">
            <SpaceBetween size="xs">
              <Box variant="strong">Next Steps</Box>
              <Box>
                1. Review the calculator dashboard and service gap analysis above<br/>
                2. Schedule a technical review with your customer<br/>
                3. Ask the specific questions provided for each category<br/>
                4. Update the AWS Calculator with recommended services<br/>
                5. Re-run this analysis to validate infrastructure completeness
              </Box>
            </SpaceBetween>
          </Alert>
        </SpaceBetween>
      )}
    </SpaceBetween>
  );
}

export default ServiceCompletenessAnalysis;
