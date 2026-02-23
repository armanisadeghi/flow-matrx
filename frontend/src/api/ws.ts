import type { WorkflowEvent } from "@shared/types/events";

type EventHandler = (event: WorkflowEvent) => void;

export function createRunWebSocket(runId: string, onEvent: EventHandler): WebSocket {
  const wsBase = import.meta.env.VITE_WS_URL ?? `ws://${window.location.host}`;
  const ws = new WebSocket(`${wsBase}/ws/runs/${runId}`);

  ws.onmessage = (msg) => {
    try {
      const event = JSON.parse(msg.data) as WorkflowEvent;
      onEvent(event);
    } catch {
      console.warn("Failed to parse WebSocket event", msg.data);
    }
  };

  ws.onerror = (err) => {
    console.error("WebSocket error", err);
  };

  return ws;
}
