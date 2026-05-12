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

const SERVICE_ANALYSIS_PROMPT = `Analyze this AWS Pricing Calculator CSV for a cloud migration. Identify missing services across 6 categories. Be concise — no repetition between sections.

**ANALYSIS RULES**
- Benchmark: 56% compute, 44% non-compute for production-ready infrastructure
- If ANY backup service is present (DynamoDB Backup, Aurora Backup, RDS Backup, etc.), do NOT flag backup as missing
- Only flag services that are genuinely absent — do not flag services that can be inferred from what's present
- Skip categories where nothing is missing

**CRITICAL — READ THE CSV CAREFULLY BEFORE CONCLUDING:**
- "Group hierarchy" column shows environment structure (PRO, QA, DEV, DR, Networking, Security). If a DR group exists with its own compute/storage/services, DR IS present.
- "Description" column describes workload purpose (e.g., "EC2 - TimeScale Hot" = self-managed database). If EC2 instances are running databases, do NOT say "no database" or flag "no multi-AZ RDS" — self-managed DBs on EC2 are a valid choice.
- "Configuration summary" column contains EBS storage amounts, instance counts, and other config details. EBS is configured WITHIN EC2 in the AWS Calculator — if ANY EC2 row shows "EBS Storage amount (X TB)" or "EBS Storage amount (X GB)", EBS IS included. Sum all EBS across EC2 instances and report the total.
- "Region" column shows deployment region. Compare regions between PRO and DR groups to determine if DR is multi-region or single-region.
- "Number of instances: 2+" in Configuration summary for the same workload = multi-AZ deployment. State this as fact, do not ask the customer.

**6 CATEGORIES TO CHECK**

1. **Backup & Recovery** (2-3%): AWS Backup, EBS snapshots, S3 Glacier, cross-region replication
2. **Storage** (25-30%): S3 tiers, EFS, FSx, Storage Gateway, EBS (check EC2 Configuration summary for "EBS Storage amount" — if present, EBS IS included)
3. **DR/HA** (1-2%): Multi-AZ, cross-region replication, Elastic DR, Route 53 health checks, dedicated DR environment groups. If DR group exists in Group hierarchy, state what's in it. If "Number of instances: 2+" on a workload, state it IS multi-AZ. If DR is in a different Region than PRO, state "multi-region DR". If same region, state "single-region DR".
4. **Network** (10-15%): ALB/NLB, CloudFront, Route 53, Transit GW, Direct Connect, VPN, Data Transfer, NAT GW, Public IPv4
5. **Observability** (2-4%): CloudWatch, CloudTrail, X-Ray, VPC Flow Logs, Config, Systems Manager
6. **Security** (2-4%): KMS, WAF, Shield, GuardDuty, Security Hub, Secrets Manager, Network Firewall

**DO NOT flag these as gaps:**
- "No EBS" when EBS is configured within EC2 instances
- "No RDS/Aurora" when databases are self-managed on EC2 (check Description for DB names like TimeScale, PostgreSQL, MySQL, MongoDB, Oracle)
- "No DR" when a DR environment group exists in Group hierarchy
- "No multi-AZ" when instance count >= 2 for a workload

**OUTPUT — 4 sections:**

**1. COST BREAKDOWN**
One compact table: Category | Annual Cost | % of Total
Then one line: Compute/Non-Compute ratio vs 56/44 benchmark. Assessment status (Complete / Incomplete / Needs Review).

**2. SERVICE GAP ANALYSIS BY CATEGORY**
For each category where gaps exist (skip categories that are complete):
- **Status**: Complete / Partial / Missing
- **Services Found**: list what IS in the calculator (include EBS totals from EC2 config, DR environment details, multi-AZ statements)
- **Services Missing**: list what is NOT, with estimated annual cost per missing service
- **Question to Ask Customer**: one key question (only ask what CANNOT be determined from the CSV data)

Keep each category to 4-5 lines max. Do not repeat the same services across categories.

**3. MISSING SERVICES SUMMARY**
Single prioritized table — consolidates all gaps from section 2:
| Priority | Missing Service | Category | Est. Annual Cost | Question to Ask Customer |

**4. RED FLAGS & ESTIMATED GAP**
Bullet list of red flags found (e.g., no backup, no CDN, security <1%, compute >80%). Only list flags that actually apply — do not list flags that don't apply.
Then two lines: Conservative and Realistic additional annual cost estimates.

Do NOT include separate recommendations or next steps sections — the gap analysis and questions already provide actionable guidance.

Analyze the CSV data below.`;

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
    
    // Collect all per-instance optimization details from aggregated services
    const allDetails = [];
    services.forEach(s => {
      // SP/RI optimization details
      if (s.optimization_details && s.optimization_details.length > 0) {
        s.optimization_details.forEach(d => allDetails.push(d));
      } else if (s.ec2_sp_annual_savings > 0) {
        allDetails.push(s);
      }
      // EBS optimization details
      if (s.ebs_savings > 0) {
        allDetails.push({
          service_name: s.service_name + ' (EBS)',
          description: s.ebs_detail || 'EBS storage optimization',
          region: s.region || '-',
          config_summary: '',
          monthly_cost: s.ebs_savings / 12,
          ec2_sp_annual_savings: s.ebs_savings,
          ec2_sp_hourly_rate: 0,
          ec2_sp_plan_type: s.ebs_plan_type || 'EBS gp2 \u2192 gp3 migration',
        });
      }
    });
    
    if (allDetails.length === 0) return;

    const parseCS = (config, field) => {
      if (!config) return '-';
      const match = config.match(new RegExp(field + '\\s*\\(([^)]+)\\)'));
      return match ? match[1] : '-';
    };

    const sym = calculatorData.is_esc ? '\u20ac' : '$';
    const headers = [
      'Service Name', 'Description', 'Region',
      'Instance Type', 'Operating System',
      'Monthly Cost (' + sym + ')', 'Annual Savings (' + sym + ')',
      'Optimized Hourly Rate (' + sym + ')', 'Plan Type'
    ];

    const rows = allDetails.map(s => {
      let instType = parseCS(s.config_summary, 'Advance EC2 instance');
      if (instType === '-') instType = parseCS(s.config_summary, 'Instance [Tt]ype');
      if (instType === '-') instType = parseCS(s.config_summary, 'Node [Tt]ype');
      return [
        s.service_name || '-',
        s.description || '-',
        s.region || '-',
        instType,
        parseCS(s.config_summary, 'Operating system'),
        (s.monthly_cost || 0).toFixed(2),
        (s.ec2_sp_annual_savings || 0).toFixed(2),
        (s.ec2_sp_hourly_rate || 0).toFixed(5),
        s.ec2_sp_plan_type || '-'
      ];
    });

    const totalSavings = allDetails.reduce((sum, s) => sum + (s.ec2_sp_annual_savings || 0), 0);
    rows.push(['TOTAL', '', '', '', '', '', totalSavings.toFixed(2), '', '']);

    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => '"' + String(cell).replace(/"/g, '""') + '"').join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'optimization_report.csv';
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
    const totalEbsSavings = services.reduce((sum, s) => sum + (s.ebs_savings || 0), 0);
    const totalOptSavings = totalSPSavings + totalEbsSavings;
    const totalDeductions = totalExcluded + totalOptSavings;
    const qualifiedARR = annualARRBeforeExclusions - totalDeductions;
    const nonOptimizedPct = totalARR > 0 ? (totalOptSavings / totalARR) * 100 : 0;
    const optimizableCount = services.filter(s => s.ec2_sp_annual_savings > 0 || s.ebs_savings > 0).length;
    const ebsOptCount = services.filter(s => s.ebs_savings > 0).length;

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
                  ({formatCurrency(totalOptSavings)})
                </Box>
                <Box variant="small" color="text-status-inactive">
                  SP/RI + EBS Optimization Opportunity
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
                  {formatCurrency(totalOptSavings)}
                </Box>
              </div>
              {totalSPSavings > 0 && (
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>SP/RI Savings</span>
                </Box>
                <Box color="text-status-error">{formatCurrency(totalSPSavings)}</Box>
              </div>
              )}
              {totalEbsSavings > 0 && (
              <div>
                <Box variant="awsui-key-label">
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>EBS Storage Optimization</span>
                </Box>
                <Box color="text-status-error">{formatCurrency(totalEbsSavings)}</Box>
                <Box variant="small" color="text-status-inactive">{ebsOptCount} service{ebsOptCount !== 1 ? 's' : ''} with old-gen storage</Box>
              </div>
              )}
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
                  <span style={{ fontWeight: 'bold', fontStyle: 'italic', textDecoration: 'underline' }}>Services Optimizable</span>
                </Box>
                <Box color="text-status-info">
                  {optimizableCount} service{optimizableCount !== 1 ? 's' : ''}
                </Box>
              </div>
              {optimizableCount > 0 && (
                <Button iconName="download" variant="normal" onClick={handleDownloadOptimizationReport}>
                  Download Optimization Report
                </Button>
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
            Calculator Review
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

                    {/* Fargate Advisory */}
                    {(() => {
                      const fargateServices = (calculatorData?.services || []).filter(s => s.optimization_note);
                      if (fargateServices.length === 0) return null;
                      return (
                        <Alert type="info" header="Fargate Optimization Note">
                          <Box>
                            {fargateServices[0].optimization_note.split('\n').map((line, i) => (
                              <Box key={i} variant={line.startsWith('  ') ? 'code' : 'p'} padding={line.startsWith('  ') ? {left: 's'} : {}}>
                                {line}
                              </Box>
                            ))}
                          </Box>
                        </Alert>
                      );
                    })()}

                    {/* Graviton Advisory */}
                    {(() => {
                      const gravitonServices = (calculatorData?.services || []).filter(s => s.graviton_note);
                      if (gravitonServices.length === 0) return null;
                      return (
                        <Alert type="info" header="Graviton Migration Opportunities">
                          <SpaceBetween size="xs">
                            <Box>The following services could benefit from Graviton-based instances for better price-performance:</Box>
                            {gravitonServices.map((s, i) => (
                              <Box key={i} variant="small">• {s.service_name}: {s.graviton_note}</Box>
                            ))}
                          </SpaceBetween>
                        </Alert>
                      );
                    })()}

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
