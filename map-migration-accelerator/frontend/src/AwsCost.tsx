import { useState, useCallback, useRef } from "react";
import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import Alert from "@cloudscape-design/components/alert";
import Button from "@cloudscape-design/components/button";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Box from "@cloudscape-design/components/box";
import StatusIndicator from "@cloudscape-design/components/status-indicator";
import Table from "@cloudscape-design/components/table";
import Tabs from "@cloudscape-design/components/tabs";
import ExpandableSection from "@cloudscape-design/components/expandable-section";
import RadioGroup from "@cloudscape-design/components/radio-group";
import FormField from "@cloudscape-design/components/form-field";
import { useSessionState } from "./App";

/* ------------------------------------------------------------------ */
/* Markdown rendering helpers (same as ExecutionPlanning)               */
/* ------------------------------------------------------------------ */
interface StructuredSection {
  title: string;
  blocks: Array<{ type: "text" | "table" | "code"; content: string; headers?: string[]; rows?: string[][]; lang?: string }>;
}

function parseStructuredMarkdown(md: string): StructuredSection[] {
  const sections: StructuredSection[] = [];
  const parts = md.split(/^##\s+/m).filter((p) => p.trim());
  for (const part of parts) {
    const lines = part.split("\n");
    const title = lines[0].trim();
    const body = lines.slice(1).join("\n").trim();
    const blocks: StructuredSection["blocks"] = [];
    const bodyLines = body.split("\n");
    let i = 0;
    let textBuf: string[] = [];
    const flushText = () => {
      const t = textBuf.join("\n").trim();
      if (t) blocks.push({ type: "text", content: t });
      textBuf = [];
    };
    while (i < bodyLines.length) {
      const line = bodyLines[i];
      const codeMatch = line.trim().match(/^```(\w*)/);
      if (codeMatch) {
        flushText();
        const lang = codeMatch[1] || "";
        const codeLines: string[] = [];
        i++;
        while (i < bodyLines.length && !bodyLines[i].trim().startsWith("```")) {
          codeLines.push(bodyLines[i]);
          i++;
        }
        i++;
        blocks.push({ type: "code", content: codeLines.join("\n"), lang });
        continue;
      }
      if (line.trim().startsWith("|") && i + 1 < bodyLines.length && /^\|[\s\-:|]+\|/.test(bodyLines[i + 1].trim())) {
        flushText();
        const tableLines: string[] = [];
        while (i < bodyLines.length && bodyLines[i].trim().startsWith("|")) {
          tableLines.push(bodyLines[i]);
          i++;
        }
        if (tableLines.length >= 2) {
          const parseRow = (r: string) => r.split("|").map((c) => c.trim()).filter((c) => c !== "");
          const headers = parseRow(tableLines[0]);
          const rows = tableLines.slice(2).map(parseRow).filter((r) => r.length > 0);
          blocks.push({ type: "table", content: tableLines.join("\n"), headers, rows });
        }
      } else {
        textBuf.push(line);
        i++;
      }
    }
    flushText();
    if (title && blocks.length > 0) sections.push({ title, blocks });
  }
  return sections;
}

function renderBold(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? <strong key={i}>{p.slice(2, -2)}</strong> : p
  );
}

function StructuredOutput({ markdown }: { markdown: string }) {
  const sections = parseStructuredMarkdown(markdown);
  if (sections.length === 0) return <Box>{markdown}</Box>;
  return (
    <SpaceBetween size="l">
      {sections.map((section, si) => (
        <Container key={si} header={<Header variant="h2">{section.title}</Header>}>
          <SpaceBetween size="s">
            {section.blocks.map((block, bi) => {
              if (block.type === "table" && block.headers && block.rows) {
                return (
                  <Table
                    key={bi}
                    variant="embedded"
                    columnDefinitions={block.headers.map((h, ci) => ({
                      id: `col-${ci}`,
                      header: h,
                      cell: (item: string[]) => renderBold(item[ci] || "—"),
                    }))}
                    items={block.rows}
                    wrapLines
                    stickyHeader
                  />
                );
              }
              if (block.type === "code") {
                return (
                  <pre key={bi} style={{ background: "rgba(0,0,0,0.06)", padding: 12, borderRadius: 4, overflowX: "auto", fontSize: 13 }}>
                    <code>{block.content}</code>
                  </pre>
                );
              }
              return (
                <Box key={bi} variant="p">
                  {block.content.split("\n").map((line, li) => {
                    const trimmed = line.trim();
                    if (!trimmed) return null;
                    if (trimmed.startsWith("### ") || trimmed.startsWith("#### ")) {
                      const text = trimmed.replace(/^#{3,4}\s+/, "");
                      return <div key={li} style={{ fontWeight: 700, fontSize: 14, marginTop: 8 }}>{renderBold(text)}</div>;
                    }
                    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
                    if (numMatch) return <div key={li} style={{ paddingLeft: 16 }}>{numMatch[1]}. {renderBold(numMatch[2])}</div>;
                    if (trimmed.startsWith("- ") || trimmed.startsWith("• ") || trimmed.startsWith("* "))
                      return <div key={li} style={{ paddingLeft: 16 }}>• {renderBold(trimmed.replace(/^[-•*]\s+/, ""))}</div>;
                    if (line.startsWith("  - ") || line.startsWith("  • ") || line.startsWith("  * "))
                      return <div key={li} style={{ paddingLeft: 32 }}>◦ {renderBold(trimmed.replace(/^[-•*]\s+/, ""))}</div>;
                    return <div key={li}>{renderBold(trimmed)}</div>;
                  })}
                </Box>
              );
            })}
          </SpaceBetween>
        </Container>
      ))}
    </SpaceBetween>
  );
}

/* ------------------------------------------------------------------ */
/* SSE event type                                                      */
/* ------------------------------------------------------------------ */
interface StreamEvent {
  type: string;
  data: string;
}

/* ------------------------------------------------------------------ */
/* AwsCost component                                                   */
/* ------------------------------------------------------------------ */
interface AwsCostProps {
  assessment: any;
  strategyResult: string;
}

export default function AwsCost({ assessment, strategyResult }: AwsCostProps) {
  const [costResult, setCostResult] = useSessionState<string>("ac-cost-result", "");
  const [milestoneResult, setMilestoneResult] = useSessionState<string>("ac-milestone-result", "");
  const [streaming, setStreaming] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("cost");

  // Strategy source toggle
  const hasSessionStrategy = !!strategyResult;
  const hasSessionAssessment = !!assessment;
  const [strategySource, setStrategySource] = useState<string>(hasSessionStrategy ? "session" : "upload");
  const [uploadedStrategy, setUploadedStrategy] = useState("");
  const [uploadedFileName, setUploadedFileName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeStrategy = strategySource === "session" ? strategyResult : uploadedStrategy;
  const canGenerate = activeStrategy.trim().length > 0 && hasSessionAssessment;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (evt) => {
      setUploadedStrategy(evt.target?.result as string);
    };
    reader.readAsText(file);
  };

  const handleGenerate = useCallback(async () => {
    if (streaming || !canGenerate) return;
    setCostResult("");
    setMilestoneResult("");
    setEvents([]);
    setError("");
    setStreaming(true);
    try {
      const res = await fetch("/api/cost/aws-cost", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assessment, strategy: activeStrategy }),
      });
      if (!res.ok) {
        const err = await res.json();
        setError(err.error || "AWS cost analysis failed");
        setStreaming(false);
        return;
      }
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        let currentEventType = "";
        for (const line of lines) {
          if (line.startsWith("event: ")) currentEventType = line.slice(7).trim();
          else if (line.startsWith("data: ") && currentEventType) {
            const data = JSON.parse(line.slice(6));
            if (currentEventType === "lifecycle") {
              setEvents((prev) => [...prev, { type: "lifecycle", data }]);
            } else if (currentEventType === "cost_done") {
              setCostResult(data);
              setActiveTab("cost");
            } else if (currentEventType === "milestone_done") {
              setMilestoneResult(data);
            } else if (currentEventType === "error") {
              setError(data);
            }
            currentEventType = "";
          }
        }
      }
    } catch (err: any) {
      setError(err.message);
    }
    setStreaming(false);
  }, [streaming, activeStrategy, assessment, canGenerate]);

  const strategyLabel = strategySource === "upload" && uploadedFileName ? `Strategy: ${uploadedFileName}` : "Strategy Summary";

  return (
    <SpaceBetween size="l">
      <Header variant="h1" description="Analyse modernisation pathways, estimate AWS costs, and predict spend milestones">
        Modernisation & Cost
      </Header>

      {/* Strategy source selection */}
      <Container header={<Header variant="h2">Strategy Input</Header>}>
        <SpaceBetween size="m">
          <FormField label="Strategy source">
            <RadioGroup
              value={strategySource}
              onChange={({ detail }) => setStrategySource(detail.value)}
              items={[
                { value: "session", label: "Use session strategy", disabled: !hasSessionStrategy, description: hasSessionStrategy ? "Strategy from your assessment session" : "No strategy available — complete an assessment first" },
                { value: "upload", label: "Upload strategy file", description: "Upload a .md file with your migration strategy" },
              ]}
            />
          </FormField>

          {strategySource === "upload" && (
            <FormField label="Strategy file (.md)">
              <SpaceBetween size="xs">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".md,.txt"
                  onChange={handleFileUpload}
                  style={{ fontSize: 14 }}
                />
                {uploadedFileName && (
                  <StatusIndicator type="success">
                    Loaded: {uploadedFileName} ({Math.round(uploadedStrategy.length / 1024)}KB)
                  </StatusIndicator>
                )}
              </SpaceBetween>
            </FormField>
          )}
        </SpaceBetween>
      </Container>

      {/* Strategy preview */}
      {activeStrategy ? (
        <ExpandableSection headerText={strategyLabel} variant="container">
          <StructuredOutput markdown={activeStrategy} />
        </ExpandableSection>
      ) : (
        <Container header={<Header variant="h2">{strategyLabel}</Header>}>
          <Box variant="p" color="text-body-secondary">
            {strategySource === "session" ? "No session strategy available." : "Upload a strategy file to preview its contents."}
          </Box>
        </Container>
      )}

      {/* Assessment status */}
      {!hasSessionAssessment && (
        <Alert type="info">Complete a Dependency Assessment first to provide application and infrastructure data for cost analysis.</Alert>
      )}

      {/* Generate button */}
      <Container>
        <Button variant="primary" onClick={handleGenerate} loading={streaming} disabled={!canGenerate}>
          {streaming ? "Generating..." : "Generate AWS Cost Analysis"}
        </Button>
      </Container>

      {error && <Alert type="error" dismissible onDismiss={() => setError("")}>{error}</Alert>}

      {/* Progress */}
      {events.length > 0 && streaming && (
        <Container header={<Header variant="h3">Progress</Header>}>
          <SpaceBetween size="xs">
            {events.map((e, i) => (
              <StatusIndicator key={i} type="success">{e.data}</StatusIndicator>
            ))}
            <StatusIndicator type="loading">Processing...</StatusIndicator>
          </SpaceBetween>
        </Container>
      )}

      {/* Results — two tabs */}
      {(costResult || milestoneResult) && (
        <Tabs
          activeTabId={activeTab}
          onChange={({ detail }) => setActiveTab(detail.activeTabId)}
          tabs={[
            {
              id: "cost",
              label: "AWS Cost Estimation",
              disabled: !costResult,
              content: costResult ? <StructuredOutput markdown={costResult} /> : <Box color="text-body-secondary">Waiting for cost analysis...</Box>,
            },
            {
              id: "milestone",
              label: "MAP Milestone Prediction",
              disabled: !milestoneResult,
              content: milestoneResult ? <StructuredOutput markdown={milestoneResult} /> : <Box color="text-body-secondary">Waiting for milestone prediction...</Box>,
            },
          ]}
        />
      )}
    </SpaceBetween>
  );
}
