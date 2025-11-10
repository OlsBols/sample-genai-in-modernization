# AnyTech Cloud Solutions - Internal Pricing Model

## Partner Internal Cost Calculation Framework

**Partner:** AnyTech Cloud Solutions  
**Model Version:** 2024.3  
**Classification:** Internal Use Only  
**Last Updated:** November 2024  

---

## Migration Complexity Assessment Framework

### Application Complexity Scoring Matrix
| Factor | Weight | Score 1 (Low) | Score 2 (Medium) | Score 3 (High) | Score 4 (Critical) |
|--------|--------|---------------|------------------|----------------|-------------------|
| **Technical Complexity** | 25% | Simple web app, COTS | Multi-tier app, some custom | Distributed system, heavy custom | Legacy mainframe, proprietary |
| **Data Volume** | 20% | <100GB | 100GB-1TB | 1TB-10TB | >10TB |
| **Integration Points** | 20% | <5 systems | 5-15 systems | 15-30 systems | >30 systems |
| **Compliance Requirements** | 15% | None/Basic | Industry standard | PCI/HIPAA/SOX | Multiple regulatory |
| **Business Criticality** | 10% | Dev/Test | Internal tools | Business operations | Customer-facing/Revenue |
| **Customization Level** | 10% | COTS/Minimal | Light customization | Heavy customization | Fully custom/Proprietary |

**Complexity Score Calculation:** Σ(Factor Score × Weight)  
**Score Ranges:** 1.0-1.8 (Low), 1.9-2.7 (Medium), 2.8-3.6 (High), 3.7-4.0 (Critical)

---

## Migration Strategy Determination

### Strategy Selection Based on Complexity Score
- **Rehost (Lift & Shift):** Score 1.0-1.8
- **Replatform (Lift-Tinker-Shift):** Score 1.9-2.7  
- **Refactor/Re-architect:** Score 2.8-4.0
- **Replace/Retire:** Any score (business decision)

### Effort Multipliers by Strategy
- **Rehost:** Base effort × 1.0
- **Replatform:** Base effort × 3.5
- **Refactor:** Base effort × 15-20
- **Replace:** Variable (depends on solution)

---

## Resource Estimation Model

### Base Resource Requirements (per application)

#### Rehost Strategy
- **Solution Architect:** 40 hours
- **Migration Engineer:** 80 hours  
- **Database Specialist:** 60 hours (if DB involved)
- **Network Engineer:** 20 hours
- **Security Engineer:** 30 hours
- **Testing Specialist:** 40 hours
- **Project Manager:** 20 hours

#### Replatform Strategy  
- **Solution Architect:** 120 hours
- **Migration Engineer:** 200 hours
- **Application Developer:** 160 hours
- **Database Specialist:** 140 hours
- **DevOps Engineer:** 100 hours
- **Security Engineer:** 80 hours
- **Testing Specialist:** 120 hours
- **Project Manager:** 60 hours

#### Refactor Strategy
- **Solution Architect:** 300 hours
- **Senior Developer:** 600 hours
- **Application Developer:** 800 hours
- **Database Architect:** 200 hours
- **DevOps Engineer:** 240 hours
- **Security Engineer:** 160 hours
- **Testing Specialist:** 300 hours
- **Project Manager:** 150 hours

### Resource Rate Structure (Internal Costing)
| Role | Internal Cost/Hour | Client Rate/Hour | Margin |
|------|-------------------|------------------|--------|
| Solution Architect | $85 | $200 | 135% |
| Senior Developer | $75 | $180 | 140% |
| Migration Engineer | $70 | $165 | 136% |
| Database Specialist | $80 | $190 | 138% |
| DevOps Engineer | $75 | $175 | 133% |
| Security Engineer | $85 | $195 | 129% |
| Network Engineer | $70 | $160 | 129% |
| Testing Specialist | $65 | $150 | 131% |
| Project Manager | $90 | $185 | 106% |

---

## Infrastructure Component Pricing

### Server Migration Costs
- **Physical to EC2:** 8 hours engineer time + $500 tools/licenses
- **Virtual to EC2:** 4 hours engineer time + $200 tools/licenses  
- **Complex Server (>4 services):** Add 50% time multiplier
- **Legacy OS Migration:** Add 100% time multiplier

### Database Migration Costs
| Database Size | Base Hours | Complexity Multiplier | Additional Factors |
|---------------|------------|----------------------|-------------------|
| <100GB | 40 hours | 1.0x | +20 hours if Oracle |
| 100GB-1TB | 80 hours | 1.2x | +40 hours if custom schema |
| 1TB-10TB | 160 hours | 1.5x | +60 hours if high availability |
| >10TB | 320 hours | 2.0x | +100 hours if real-time replication |

### Network Configuration Costs
- **Basic VPC Setup:** 16 hours
- **Multi-tier Architecture:** 32 hours  
- **Hybrid Connectivity:** 48 hours
- **Complex Security Groups:** +25% time
- **Load Balancer Configuration:** 12 hours each

---

## Service Category Cost Models

### Application Modernization Services
| Service Type | Base Hours | Skill Level | Complexity Factors |
|--------------|------------|-------------|-------------------|
| Code Assessment | 60 | Senior Dev | +50% for legacy languages |
| Containerization | 80 | DevOps | +100% for monoliths |
| Microservices Design | 200 | Architect | +25% per additional service |
| API Development | 120 | Developer | +50% for complex integrations |
| Performance Optimization | 100 | Senior Dev | +75% for real-time requirements |

### Data & Analytics Services  
| Service Type | Base Hours | Skill Level | Scaling Factors |
|--------------|------------|-------------|-----------------|
| Data Lake Setup | 240 | Data Architect | +20% per data source |
| ETL Pipeline | 160 | Data Engineer | +50% for real-time |
| Streaming Implementation | 200 | Senior Engineer | +25% per stream |
| Analytics Dashboard | 120 | Developer | +30% per dashboard |
| ML Model Development | 400 | Data Scientist | +100% for custom models |

### Security & Compliance Services
| Service Type | Base Hours | Skill Level | Compliance Multipliers |
|--------------|------------|-------------|----------------------|
| Security Assessment | 80 | Security Engineer | +50% for PCI/SOX |
| IAM Implementation | 120 | Security Architect | +25% per account |
| Encryption Setup | 60 | Security Engineer | +100% for custom keys |
| Compliance Framework | 300 | Compliance Specialist | +50% per standard |
| Security Monitoring | 160 | Security Engineer | +25% per application |

---

## Risk and Complexity Adjustments

### Risk Multipliers
- **Low Risk (Proven technology, simple architecture):** 0.9x
- **Medium Risk (Standard complexity):** 1.0x  
- **High Risk (Complex integrations, tight timeline):** 1.3x
- **Critical Risk (Mission critical, regulatory):** 1.6x

### Timeline Pressure Multipliers
- **Standard Timeline:** 1.0x
- **Accelerated (20% faster):** 1.25x
- **Rush (40% faster):** 1.6x  
- **Emergency (60% faster):** 2.0x

### Volume Discounts (Internal Cost Reduction)
- **1-10 applications:** No discount
- **11-25 applications:** 5% resource efficiency
- **26-50 applications:** 10% resource efficiency  
- **51-100 applications:** 15% resource efficiency
- **100+ applications:** 20% resource efficiency

---

## Professional Services Estimation

### Program Management Overhead
- **Small Program (<20 apps):** 15% of total effort
- **Medium Program (20-50 apps):** 12% of total effort
- **Large Program (50+ apps):** 10% of total effort

### Knowledge Transfer and Training
- **Basic Training:** 2 hours per internal resource
- **Advanced Training:** 8 hours per internal resource  
- **Certification Prep:** 40 hours per certification
- **Documentation:** 5% of total project effort

### Support and Warranty
- **Hypercare Period:** 30 days post go-live
- **Hypercare Staffing:** 25% of migration team
- **Extended Support:** 10% of migration team for 90 days
- **Warranty Period:** 12 months with 4-hour response SLA

---

## Cost Calculation Methodology

### Step 1: Application Assessment
1. Score each application using complexity matrix
2. Determine migration strategy based on score
3. Apply base resource requirements for strategy
4. Calculate base cost using internal rates

### Step 2: Infrastructure Assessment  
1. Count servers, databases, network components
2. Apply base hours for each component type
3. Add complexity multipliers based on technology
4. Calculate infrastructure migration cost

### Step 3: Service Requirements
1. Identify required modernization services
2. Apply base hours and skill requirements
3. Add scaling factors based on scope
4. Calculate service delivery cost

### Step 4: Risk and Timeline Adjustments
1. Assess overall program risk level
2. Apply risk multipliers to base costs
3. Adjust for timeline requirements
4. Apply volume discounts if applicable

### Step 5: Professional Services
1. Calculate program management overhead
2. Add training and knowledge transfer costs
3. Include support and warranty costs
4. Apply margin to reach client pricing

---

## Quality Gates and Validation

### Estimation Validation Checkpoints
- **Complexity scoring reviewed by senior architect**
- **Resource estimates validated against historical projects**
- **Risk assessments approved by practice lead**
- **Final pricing reviewed by partner leadership**

### Historical Project Benchmarks
- **Average Rehost Cost:** $35,000-$45,000 per application
- **Average Replatform Cost:** $120,000-$180,000 per application  
- **Average Refactor Cost:** $500,000-$800,000 per application
- **Typical Overrun Rate:** 15-25% for complex projects

### Success Metrics Tracking
- **Estimation Accuracy:** Target ±10% of actual costs
- **Resource Utilization:** Target 85% billable utilization
- **Client Satisfaction:** Target >4.5/5.0 rating
- **Project Margin:** Target 25-35% gross margin

---

**Document Classification:** Internal Use Only  
**Prepared By:** Practice Leadership Team  
**Approved By:** Partner Director  
**Next Review:** March 2025
