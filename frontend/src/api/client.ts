import axios from "axios";

export const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

export async function streamChat(
  query: string,
  threadId: string,
  signal: AbortSignal,
  onEvent: (event: { event: string; data: unknown }) => void,
): Promise<void> {
  const response = await fetch("/api/v1/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, thread_id: threadId }),
    signal,
  });

  if (!response.body) return;

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        const eventType = line.slice(7).trim();
        onEvent({ event: eventType, data: {} });
      } else if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        onEvent({ event: "data", data });
      }
    }
  }
}

export function renderSafeMarkdown(source: string): string {
  // Placeholder — real implementation uses marked + DOMPurify
  return source;
}
