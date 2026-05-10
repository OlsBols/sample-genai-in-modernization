import { useState, useRef, useEffect } from "react";
import SpaceBetween from "@cloudscape-design/components/space-between";
import ExpandableSection from "@cloudscape-design/components/expandable-section";
import StatusIndicator from "@cloudscape-design/components/status-indicator";
import Box from "@cloudscape-design/components/box";

export interface StreamEvent {
  type: "lifecycle" | "thinking" | "tool" | "text" | "error" | "done";
  data: string;
}

interface AgentStreamProps {
  url: string;
  body: Record<string, unknown>;
  active: boolean;
  onDone: (result: string) => void;
  onError: (message: string) => void;
}

export default function AgentStream({ url, body, active, onDone, onError }: AgentStreamProps) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [text, setText] = useState("");
  const [thinking, setThinking] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active) return;
    setEvents([]);
    setText("");
    setThinking("");

    const controller = new AbortController();

    (async () => {
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
        if (!res.ok) {
          const err = await res.json();
          onError(err.error || "Stream failed");
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
            if (line.startsWith("event: ")) {
              currentEventType = line.slice(7).trim();
            } else if (line.startsWith("data: ") && currentEventType) {
              const data = JSON.parse(line.slice(6));
              const evt: StreamEvent = { type: currentEventType as StreamEvent["type"], data };

              if (evt.type === "done") {
                onDone(data);
              } else if (evt.type === "error") {
                onError(data);
              } else {
                setEvents((prev) => [...prev, evt]);
                if (evt.type === "text") setText((prev) => prev + data);
                if (evt.type === "thinking") setThinking((prev) => prev + data);
              }
              currentEventType = "";
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") onError(err.message);
      }
    })();

    return () => controller.abort();
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  if (!active && events.length === 0) return null;

  const lifecycleEvents = events.filter((e) => e.type === "lifecycle" || e.type === "tool");

  return (
    <SpaceBetween size="s">
      {lifecycleEvents.length > 0 && (
        <ExpandableSection headerText="Agent activity" defaultExpanded>
          <SpaceBetween size="xxs">
            {lifecycleEvents.map((e, i) => (
              <Box key={i} variant="small" color="text-body-secondary">
                {e.type === "tool" ? (
                  <StatusIndicator type="in-progress">{e.data}</StatusIndicator>
                ) : (
                  <StatusIndicator type="info">{e.data}</StatusIndicator>
                )}
              </Box>
            ))}
          </SpaceBetween>
        </ExpandableSection>
      )}

      {thinking && (
        <ExpandableSection headerText="Agent thinking">
          <Box variant="pre" fontSize="body-s">{thinking}</Box>
        </ExpandableSection>
      )}

      {text && (
        <ExpandableSection headerText="Agent output" defaultExpanded>
          <Box variant="pre" fontSize="body-s">{text}</Box>
        </ExpandableSection>
      )}

      <div ref={bottomRef} />
    </SpaceBetween>
  );
}
