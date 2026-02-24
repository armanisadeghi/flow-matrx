import type { WorkflowEvent } from "@shared/types/events";

export type EventHandler = (event: WorkflowEvent) => void;
export type ConnectionStateHandler = (connected: boolean, attempt: number) => void;

const WS_BASE =
  typeof window !== "undefined"
    ? (import.meta.env.VITE_WS_URL ?? `ws://${window.location.host}`)
    : "";

const MAX_RETRIES = 8;
const BASE_DELAY_MS = 500;
const MAX_DELAY_MS = 30_000;

function backoffDelay(attempt: number): number {
  return Math.min(BASE_DELAY_MS * 2 ** attempt + Math.random() * 200, MAX_DELAY_MS);
}

export interface RunWebSocketHandle {
  close: () => void;
}

/**
 * Opens a managed WebSocket connection to the run event stream.
 * Automatically reconnects with exponential backoff on unexpected close.
 * Calls onConnectionState on connect/disconnect transitions.
 * Calls onEvent for every message received.
 * Returns a handle with close() to permanently tear down the connection.
 */
export function createRunWebSocket(
  runId: string,
  onEvent: EventHandler,
  onConnectionState: ConnectionStateHandler,
): RunWebSocketHandle {
  let ws: WebSocket | null = null;
  let attempt = 0;
  let destroyed = false;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;

  function connect(): void {
    if (destroyed) return;

    ws = new WebSocket(`${WS_BASE}/ws/runs/${runId}`);

    ws.onopen = () => {
      attempt = 0;
      onConnectionState(true, 0);
    };

    ws.onmessage = (msg) => {
      try {
        const event = JSON.parse(msg.data as string) as WorkflowEvent;
        onEvent(event);
      } catch {
        console.warn("[ws] Failed to parse event", msg.data);
      }
    };

    ws.onerror = () => {
      // onerror always fires before onclose; let onclose drive reconnect logic.
    };

    ws.onclose = (ev) => {
      ws = null;
      onConnectionState(false, attempt);

      // 1000 = normal closure (we called close() intentionally)
      if (destroyed || ev.code === 1000) return;

      if (attempt >= MAX_RETRIES) {
        console.error(`[ws] Giving up after ${MAX_RETRIES} reconnect attempts for run ${runId}`);
        return;
      }

      const delay = backoffDelay(attempt);
      attempt += 1;
      console.info(`[ws] Reconnecting in ${Math.round(delay)}ms (attempt ${attempt})`);
      retryTimer = setTimeout(connect, delay);
    };
  }

  connect();

  return {
    close() {
      destroyed = true;
      if (retryTimer !== null) clearTimeout(retryTimer);
      ws?.close(1000, "component unmounted");
    },
  };
}
