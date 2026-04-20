import { useState, useEffect } from "react";
import AppLayout from "@cloudscape-design/components/app-layout";
import SideNavigation from "@cloudscape-design/components/side-navigation";
import Box from "@cloudscape-design/components/box";
import Header from "@cloudscape-design/components/header";
import Container from "@cloudscape-design/components/container";
import Button from "@cloudscape-design/components/button";
import SpaceBetween from "@cloudscape-design/components/space-between";
import ColumnLayout from "@cloudscape-design/components/column-layout";
import Alert from "@cloudscape-design/components/alert";
import ArchitectureDiagram from "./ArchitectureDiagram";
import MigrationAssessment from "./MigrationAssessment";
import ExecutionPlanning from "./ExecutionPlanning";
import ResourcePlanning from "./ResourcePlanning";
import AwsCost from "./AwsCost";
import Artifacts from "./Artifacts";
import WhatIfScenario from "./WhatIfScenario";

/* ------------------------------------------------------------------ */
/* useSessionState — useState backed by sessionStorage                 */
/* ------------------------------------------------------------------ */
export function useSessionState<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = sessionStorage.getItem(key);
      return stored ? JSON.parse(stored) : initial;
    } catch {
      return initial;
    }
  });
  useEffect(() => {
    if (value === null || value === undefined || value === "") {
      sessionStorage.removeItem(key);
    } else {
      sessionStorage.setItem(key, JSON.stringify(value));
    }
  }, [key, value]);
  return [value, setValue] as const;
}

type Page = "home" | "architecture" | "migration" | "aws-cost" | "execution" | "resource" | "artifacts" | "what-if";

export default function App() {
  const [activePage, setActivePage] = useState<Page>("home");

  // Shared state — persisted in sessionStorage
  const [assessment, setAssessment] = useSessionState<any>("ma-assessment", null);
  const [strategyResult, setStrategyResult] = useSessionState<string>("ma-strategy", "");

  const clearSession = () => {
    // Clear all session keys used by the app
    const keys = ["ma-assessment", "ma-strategy", "ep-lz-design", "ep-lz-iac", "ep-lz-diag", "ep-tb-result", "ep-taiga-result", "ep-wr-result", "ep-rp-result", "ac-cost-result", "ac-milestone-result", "wis-chat-history"];
    keys.forEach((k) => sessionStorage.removeItem(k));
    setAssessment(null);
    setStrategyResult("");
  };

  const hasAssessmentAndStrategy = !!assessment && !!strategyResult;

  return (
    <AppLayout
      navigation={
        <SideNavigation
          header={{ text: "MAP Agentic Accelerator", href: "#" }}
          activeHref={activePage}
          onFollow={(e) => {
            e.preventDefault();
            const page = e.detail.href as Page;
            setActivePage(page);
          }}
          items={[
            { type: "link", text: "Home", href: "home" },
            { type: "link", text: "Dependency Assessment", href: "migration" },
            { type: "link", text: "Modernisation & Cost", href: "aws-cost" },
            {
              type: "link",
              text: "Resource Planning",
              href: "resource",
            },
            {
              type: "link",
              text: "Migration Execution and Planning",
              href: "execution",
              info: !hasAssessmentAndStrategy ? <Box variant="small" color="text-status-inactive">Requires assessment & strategy</Box> : undefined,
            },
            { type: "link", text: "What-If Scenario", href: "what-if" },
            { type: "link", text: "Reports & Artifacts", href: "artifacts" },
            { type: "link", text: "Architecture Generator", href: "architecture" },
          ]}
        />
      }
      content={
        activePage === "home" ? (
          <SpaceBetween size="l">
            <Header
              variant="h1"
              description="AI-powered AWS Migration Acceleration Program (MAP) assessment and execution planning"
            >
              MAP Agentic Accelerator
            </Header>

            {/* Overview */}
            <Container header={<Header variant="h2">Overview</Header>}>
              <SpaceBetween size="s">
                <Box variant="p">
                  This demo illustrates the application of Generative AI (Gen AI) during the AWS Migration Acceleration Program (MAP) assessment phase, after the completion of on-premises discovery. It showcases capabilities that enhance migration planning, cost optimisation, identification of modernisation opportunities, and resource planning — processes which were previously both time-consuming and complex.
                </Box>
                <Box variant="p">
                  This demo can analyse infrastructure data to generate strategic recommendations, predict MAP funding milestones, and create comprehensive migration wave plans with greater efficiency and insight than traditional methods.
                </Box>
                <Box variant="p">
                  AWS partners can leverage these GenAI capabilities across three progressive implementation levels — from direct model usage to fully automated solutions — creating a transformative approach to cloud migration assessment.
                </Box>
              </SpaceBetween>
            </Container>

            {/* Key Features */}
            <Container header={<Header variant="h2">Key Features</Header>}>
              <ColumnLayout columns={3} variant="text-grid">
                <SpaceBetween size="xs">
                  <div className="feature-title">Portfolio Discovery & Assessment</div>
                  <Box variant="p" fontSize="body-s">Upload application and infrastructure CSVs for automated classification, risk signal identification, dependency analysis, and migration readiness scoring.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Migration Strategy</div>
                  <Box variant="p" fontSize="body-s">AI-driven R-type classification (6 Rs), wave planning with five velocity strategies (WP1–WP5), and Gantt chart visualisation for migration timelines.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">AWS Cost Analysis</div>
                  <Box variant="p" fontSize="body-s">Modernisation pathway recommendations across 8 categories (Cloud Native, Containers, Managed Databases, AI, etc.) with monthly and annual cost estimates.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">MAP Milestone Prediction</div>
                  <Box variant="p" fontSize="body-s">Predict when the $50K cumulative spend milestone will be achieved, with acceleration strategies if the timeline exceeds four months.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Landing Zone & IaC</div>
                  <Box variant="p" fontSize="body-s">Multi-agent design producing landing zone architecture, CloudFormation templates, and Draw.io diagrams — all generated in parallel.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Resource Planning</div>
                  <Box variant="p" fontSize="body-s">Team structure evaluation (Hub-and-Spoke vs Wave-Based), role-based resource allocation, and cost modelling using configurable resource profiles.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Task Breakdown & Project Management</div>
                  <Box variant="p" fontSize="body-s">Structured wave → epic → story → task hierarchy with Gantt charts and one-click push to Taiga for project tracking.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Wave Runbooks</div>
                  <Box variant="p" fontSize="body-s">Operational runbooks with pre-migration checklists, cutover steps, rollback plans, communication plans, and timelines.</Box>
                </SpaceBetween>
                <SpaceBetween size="xs">
                  <div className="feature-title">Interactive Chat</div>
                  <Box variant="p" fontSize="body-s">Multi-turn conversational interface over your assessment data — ask questions about your portfolio, dependencies, or strategy at any time.</Box>
                </SpaceBetween>
              </ColumnLayout>
            </Container>

            {/* Disclaimers */}
            <Alert type="warning" header="AI Accuracy Disclaimer">
              While GenAI provides valuable insights, it might occasionally generate inaccurate predictions. Always validate and double-check AI-generated recommendations before implementation.
            </Alert>

            <Alert type="info" header="Proof of Concept">
              This solution is explicitly designed for proof-of-concept purposes only to explore the art of possibility with Generative AI for MAP assessments. Please adhere to your company's enhanced security and compliance policies.
            </Alert>

            {/* Actions */}
            <Container>
              <SpaceBetween size="s" direction="horizontal">
                <Button variant="primary" onClick={() => setActivePage("migration")}>
                  Get Started — Dependency Assessment
                </Button>
                <Button variant="normal" iconName="remove" onClick={clearSession}>
                  Clear Session Data
                </Button>
              </SpaceBetween>
            </Container>
          </SpaceBetween>
        ) : activePage === "architecture" ? (
          <ArchitectureDiagram />
        ) : activePage === "execution" ? (
          hasAssessmentAndStrategy ? (
            <ExecutionPlanning assessment={assessment} strategyResult={strategyResult} />
          ) : (
            <Container header={<Header variant="h1">Migration Execution and Planning</Header>}>
              <Box variant="p" color="text-body-secondary">
                Complete a Migration Assessment and generate a Strategy first, then return here to plan execution.
              </Box>
            </Container>
          )
        ) : activePage === "resource" ? (
          <ResourcePlanning strategyResult={strategyResult} />
        ) : activePage === "aws-cost" ? (
          <AwsCost assessment={assessment} strategyResult={strategyResult} />
        ) : activePage === "artifacts" ? (
          <Artifacts />
        ) : activePage === "what-if" ? (
          <WhatIfScenario />
        ) : (
          <MigrationAssessment
            assessment={assessment}
            setAssessment={setAssessment}
            strategyResult={strategyResult}
            setStrategyResult={setStrategyResult}
          />
        )
      }
      toolsHide
    />
  );
}
