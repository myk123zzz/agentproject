import { defineStore } from "pinia";
import type { ChatState, ChatMessage, Citation, AgentEvent } from "../types";

export const useChatStore = defineStore("chat", {
  state: (): ChatState => ({
    threadId: crypto.randomUUID(),
    messages: [],
    timeline: [],
    citations: [],
    graphPaths: [],
    streaming: false,
  }),

  actions: {
    addMessage(msg: ChatMessage) {
      this.messages.push(msg);
    },
    setStreaming(v: boolean) {
      this.streaming = v;
    },
    clearTimeline() {
      this.timeline = [];
      this.citations = [];
      this.graphPaths = [];
    },
  },
});
