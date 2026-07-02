export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  trace?: AgentEvent[];
}

export interface Citation {
  id: string;
  documentName: string;
  documentVersion: string;
  pageNumber: number;
  quote: string;
  channel: string;
}

export interface AgentEvent {
  event: string;
  data: Record<string, unknown>;
}

export interface ReviewRequest {
  reviewId: number;
  reason: string;
  tool: string;
  arguments: Record<string, unknown>;
}

export interface ChatState {
  threadId: string;
  messages: ChatMessage[];
  timeline: AgentEvent[];
  citations: Citation[];
  graphPaths: GraphPath[];
  pendingReview?: ReviewRequest;
  streaming: boolean;
}

export interface GraphPath {
  nodes: string[];
  edges: string[];
  confidence: number;
}
