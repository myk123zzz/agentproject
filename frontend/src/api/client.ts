import DOMPurify from "dompurify";
import { marked } from "marked";

export async function streamChat(
  query: string,
  threadId: string,
  signal: AbortSignal,
  onEvent: (event: { event: string; data: unknown }) => void,
): Promise<void> {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/v1/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query, thread_id: threadId }),
    signal,
  });

  if (!response.ok) {
    const err = await response.text();
    onEvent({ event: "error", data: { message: err } });
    return;
  }

  if (!response.body) return;

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent({ event: currentEvent || "data", data });
        } catch {
          onEvent({ event: currentEvent || "data", data: line.slice(6) });
        }
        currentEvent = "";
      }
    }
  }
}

export function renderSafeMarkdown(source: string): string {
  const html = marked.parse(source) as string;
  return DOMPurify.sanitize(html);
}
