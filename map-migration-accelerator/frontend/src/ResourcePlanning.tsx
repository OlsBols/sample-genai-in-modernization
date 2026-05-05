import { useState, useCallback, useRef } from "react";
import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import Alert from "@cloudscape-design/components/alert";
import Button from "@cloudscape-design/components/button";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Box from "@cloudscape-design/components/box";
import StatusIndicator from "@cloudscape-design/components/status-indicator";
import Table from "@cloudscape-design/components/table";
import ExpandableSection from "@cloudscape-design/components/expandable-section";
import RadioGroup from "@cloudscape-design/components/radio-group";
import FormField from "@cloudscape-design/components/form-field";
import { useSessionState } from "./App";

/* ------------------------------------------------------------------ */
/* Resource profile data (mirrors resource_profile_template.csv)       */
/* ------------------------------------------------------------------ */
const RESOURCE_PROFILES = [
  { category: "core", role: "Project Manager", level: "senior", charge: 250 },
  { category: "core", role: "Project technical lead", level: "senior", charge: 250 },
  { category: "core", role: "Testing lead", level: "senior", charge: 200 },
  { category: "core", role: "Application architect", level: "senior", charge: 250 },
  { category: "core", role: "DevOps engineer", level: "senior", charge: 300 },
  { category: "core", role: "AWS architect", level: "senior", charge: 400 },
  { category: "core", role: "Operations lead", level: "senior", charge: 250 },
  { category: "support", role: "Portfolio lead", level: "senior", charge: 300 },
  { category: "support", role: "Migration consultant", level: "senior", charge: 350 },
  { category: "specialist", role: "Security", level: "senior", charge: 350 },
  { category: "support", role: "Legal, Commercial and compliance", level: "senior", charge: 100 },
  { category: "support", role: "Finance", level: "senior", charge: 200 },
  { category: "specialist", role: "Network specialist", level: "senior", charge: 250 },
  { category: "specialist", role: "Database specialist", level: "senior", charge: 300 },
  { category: "specialist", role: "Data Engineer", level: "senior", charge: 350 },
  { category: "specialist", role: "AI/ML specialist", level: "senior", charge: 400 },
  { category: "specialist", role: "Data Strategist", level: "senior", charge: 500 },
  { category: "specialist", role: "Data Scientist", level: "senior", charge: 300 },
  { category: "specialist", role: "VMWare specialist", level: "senior", charge: 300 },
  { category: "specialist", role: "SAP specialist", level: "senior", charge: 400 },
];

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
                      cell: (item: string[]) => item[ci] || "—",
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
/* ResourcePlanning component                                          */
/* ------------------------------------------------------------------ */
interface ResourcePlanningProps {
  strategyResult: string;
}

export default function ResourcePlanning({ strategyResult }: ResourcePlanningProps) {
  const [rpResult, setRpResult] = useSessionState<string>("ep-rp-result", "");
  const [rpStreaming, setRpStreaming] = useState(false);
  const [rpEvents, setRpEvents] = useState<StreamEvent[]>([]);
  const [rpError, setRpError] = useState("");

  // Strategy source toggle
  const hasSessionStrategy = !!strategyResult;
  const [strategySource, setStrategySource] = useState<string>(hasSessionStrategy ? "session" : "upload");
  const [uploadedStrategy, setUploadedStrategy] = useState("");
  const [uploadedFileName, setUploadedFileName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // The active strategy text based on selected source
  const activeStrategy = strategySource === "session" ? strategyResult : uploadedStrategy;
  const canGenerate = activeStrategy.trim().length > 0;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      setUploadedStrategy(text);
    };
    reader.readAsText(file);
  };

  const handleGenerate = useCallback(async () => {
    if (rpStreaming || !canGenerate) return;
    setRpResult("");
    setRpEvents([]);
    setRpError("");
    setRpStreaming(true);
    try {
      const res = await fetch("/api/execution/resource-planning", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ strategy: activeStrategy }),
      });
      if (!res.ok) {
        const err = await res.json();
        setRpError(err.error || "Resource planning generation failed");
        setRpStreaming(false);
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
              setRpEvents((prev) => [...prev, { type: "lifecycle", data }]);
            } else if (currentEventType === "done") {
              setRpResult(data);
            } else if (currentEventType === "error") {
              setRpError(data);
            }
            currentEventType = "";
          }
        }
      }
    } catch (err: any) {
      setRpError(err.message);
    }
    setRpStreaming(false);
  }, [rpStreaming, activeStrategy, canGenerate]);

  // Strategy preview text
  const strategyLabel = strategySource === "upload" && uploadedFileName ? `Strategy: ${uploadedFileName}` : "Strategy Summary";

  return (
    <SpaceBetween size="l">
      <Header variant="h1" description="Generate resource plans based on your migration strategy">
        Resource Planning
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

      {/* Strategy preview — expanded to show full content */}
      {activeStrategy ? (
        <ExpandableSection headerText={strategyLabel} variant="container" defaultExpanded>
          <StructuredOutput markdown={activeStrategy} />
        </ExpandableSection>
      ) : (
        <Container header={<Header variant="h2">{strategyLabel}</Header>}>
          <Box variant="p" color="text-body-secondary">
            {strategySource === "session" ? "No session strategy available." : "Upload a strategy file to preview its contents."}
          </Box>
        </Container>
      )}

      {/* Resource profile template — collapsed by default */}
      <ExpandableSection headerText="Resource Profile Template" variant="container">
        <Table
          variant="embedded"
          columnDefinitions={[
            { id: "category", header: "Category", cell: (item) => item.category, width: 100 },
            { id: "role", header: "Role", cell: (item) => item.role },
            { id: "level", header: "Level", cell: (item) => item.level, width: 80 },
            { id: "charge", header: "Daily Rate (£)", cell: (item) => `£${item.charge}`, width: 110 },
          ]}
          items={RESOURCE_PROFILES}
          wrapLines
          stickyHeader
        />
      </ExpandableSection>

      {/* Generate button */}
      <Container>
        <Button variant="primary" onClick={handleGenerate} loading={rpStreaming} disabled={!canGenerate}>
          {rpStreaming ? "Generating..." : "Generate Resource Plan"}
        </Button>
      </Container>

      {rpError && <Alert type="error" dismissible onDismiss={() => setRpError("")}>{rpError}</Alert>}

      {/* Progress */}
      {rpEvents.length > 0 && !rpResult && (
        <Container header={<Header variant="h3">Progress</Header>}>
          <SpaceBetween size="xs">
            {rpEvents.map((e, i) => (
              <StatusIndicator key={i} type="success">{e.data}</StatusIndicator>
            ))}
            {rpStreaming && <StatusIndicator type="loading">Processing...</StatusIndicator>}
          </SpaceBetween>
        </Container>
      )}

      {/* Result */}
      {rpResult && <StructuredOutput markdown={rpResult} />}
    </SpaceBetween>
  );
}
