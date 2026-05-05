import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Table from "@cloudscape-design/components/table";
import Button from "@cloudscape-design/components/button";
import StatusIndicator from "@cloudscape-design/components/status-indicator";
import Box from "@cloudscape-design/components/box";

/* ------------------------------------------------------------------ */
/* Artifact definitions — maps session keys to display info            */
/* ------------------------------------------------------------------ */
interface ArtifactDef {
  label: string;
  sessionKey: string;
  format: string;
  extension: string;
  mimeType: string;
}

const ARTIFACTS: ArtifactDef[] = [
  { label: "Portfolio Assessment", sessionKey: "ma-assessment", format: "JSON", extension: "json", mimeType: "application/json" },
  { label: "Migration Strategy", sessionKey: "ma-strategy", format: "Markdown", extension: "md", mimeType: "text/markdown" },
  { label: "AWS Cost Estimation", sessionKey: "ac-cost-result", format: "Markdown", extension: "md", mimeType: "text/markdown" },
  { label: "MAP Milestone Prediction", sessionKey: "ac-milestone-result", format: "Markdown", extension: "md", mimeType: "text/markdown" },
  { label: "Landing Zone Design", sessionKey: "ep-lz-design", format: "Markdown", extension: "md", mimeType: "text/markdown" },
  { label: "IaC Templates", sessionKey: "ep-lz-iac", format: "YAML", extension: "yaml", mimeType: "text/yaml" },
  { label: "Architecture Diagram", sessionKey: "ep-lz-diag", format: "XML", extension: "drawio", mimeType: "application/xml" },
  { label: "Task Breakdown", sessionKey: "ep-tb-result", format: "JSON", extension: "json", mimeType: "application/json" },
  { label: "Wave Runbook", sessionKey: "ep-wr-result", format: "Markdown", extension: "md", mimeType: "text/markdown" },
  { label: "Resource Plan", sessionKey: "ep-rp-result", format: "Markdown", extension: "md", mimeType: "text/markdown" },
];

function getSessionData(key: string): string | null {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || (typeof parsed === "string" && !parsed.trim())) return null;
    return typeof parsed === "object" ? JSON.stringify(parsed, null, 2) : parsed;
  } catch {
    return null;
  }
}

function handleDownload(artifact: ArtifactDef) {
  const data = getSessionData(artifact.sessionKey);
  if (!data) return;
  const blob = new Blob([data], { type: artifact.mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${artifact.label.toLowerCase().replace(/\s+/g, "-")}.${artifact.extension}`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ------------------------------------------------------------------ */
/* Artifacts component                                                 */
/* ------------------------------------------------------------------ */
export default function Artifacts() {
  const items = ARTIFACTS.map((a) => ({
    ...a,
    hasData: !!getSessionData(a.sessionKey),
  }));

  const generatedCount = items.filter((i) => i.hasData).length;

  return (
    <SpaceBetween size="l">
      <Header
        variant="h1"
        description={`${generatedCount} of ${items.length} artifacts generated in this session`}
      >
        Reports & Artifacts
      </Header>

      <Container>
        <Table
          columnDefinitions={[
            {
              id: "artifact",
              header: "Artifact",
              cell: (item) => <Box fontWeight="bold">{item.label}</Box>,
              width: 250,
            },
            {
              id: "format",
              header: "Format",
              cell: (item) => item.format,
              width: 100,
            },
            {
              id: "status",
              header: "Status",
              cell: (item) =>
                item.hasData ? (
                  <StatusIndicator type="success">Generated</StatusIndicator>
                ) : (
                  <StatusIndicator type="stopped">Not yet</StatusIndicator>
                ),
              width: 140,
            },
            {
              id: "actions",
              header: "Actions",
              cell: (item) => (
                <Button
                  variant="normal"
                  iconName="download"
                  disabled={!item.hasData}
                  onClick={() => handleDownload(item)}
                >
                  Download .{item.extension}
                </Button>
              ),
              width: 180,
            },
          ]}
          items={items}
          variant="embedded"
          wrapLines
          stickyHeader
        />
      </Container>
    </SpaceBetween>
  );
}
