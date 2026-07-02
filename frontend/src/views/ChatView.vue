<template>
  <div class="chat-layout">
    <aside class="sidebar">会话列表</aside>
    <main class="chat-main">
      <div class="messages" ref="msgContainer">
        <div v-for="(msg, i) in store.messages" :key="i" :class="'msg-' + msg.role">
          <div v-html="renderSafeMarkdown(msg.content)"></div>
          <div v-if="msg.citations?.length" class="citations">
            引用: <span v-for="c in msg.citations" :key="c.id">[{{ c.id }}] {{ c.documentName }} p.{{ c.pageNumber }} </span>
          </div>
        </div>
        <div v-if="store.streaming" class="msg-assistant">...</div>
      </div>
      <form @submit.prevent="send" class="input-area">
        <input v-model="query" placeholder="输入您的问题..." :disabled="store.streaming" />
        <button type="submit" :disabled="store.streaming || !query.trim()">发送</button>
      </form>
    </main>
    <aside class="evidence">
      <div v-if="store.citations.length"><strong>引用来源</strong><ul><li v-for="c in store.citations" :key="c.id">[{{ c.id }}] {{ c.documentName }} p.{{ c.pageNumber }}</li></ul></div>
      <div v-if="store.graphPaths.length"><strong>图谱路径</strong><ul><li v-for="(p,i) in store.graphPaths" :key="i">{{ p.nodes.join(' → ') }}</li></ul></div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChatStore } from "../stores/chat";
import { streamChat, renderSafeMarkdown } from "../api/client";

const store = useChatStore();
const query = ref("");
const msgContainer = ref<HTMLElement | null>(null);

async function send() {
  const q = query.value.trim();
  if (!q || store.streaming) return;
  query.value = "";

  store.addMessage({ role: "user", content: q });
  store.setStreaming(true);
  store.clearTimeline();
  const threadId = store.threadId;
  const assistantIdx = store.messages.length;

  const controller = new AbortController();
  let answerText = "";

  try {
    await streamChat(q, threadId, controller.signal, (evt) => {
      switch (evt.event) {
        case "routing":
          store.timeline.push({ event: "routing", data: evt.data as Record<string, unknown> });
          break;
        case "retrieval":
          store.timeline.push({ event: "retrieval", data: evt.data as Record<string, unknown> });
          break;
        case "content": {
          const text = typeof evt.data === "string" ? evt.data : (evt.data as Record<string, unknown>)?.message || "";
          answerText += text;
          // Update or create assistant message
          if (store.messages[assistantIdx]) {
            store.messages[assistantIdx].content = answerText;
          } else {
            store.addMessage({ role: "assistant", content: answerText });
          }
          break;
        }
        case "citation":
          store.citations.push(evt.data as never);
          store.timeline.push({ event: "citation", data: evt.data as Record<string, unknown> });
          break;
        case "graph_path":
          store.graphPaths.push(evt.data as never);
          store.timeline.push({ event: "graph_path", data: evt.data as Record<string, unknown> });
          break;
        case "review_required":
          store.pendingReview = evt.data as never;
          store.timeline.push({ event: "review_required", data: evt.data as Record<string, unknown> });
          break;
        case "error":
          store.timeline.push({ event: "error", data: evt.data as Record<string, unknown> });
          break;
        case "done":
          store.timeline.push({ event: "done", data: {} });
          break;
      }
    });
  } catch (err: unknown) {
    if ((err as Error).name !== "AbortError") {
      store.addMessage({ role: "assistant", content: "请求失败，请重试。" });
    }
  } finally {
    store.setStreaming(false);
  }
}
</script>

<style scoped>
.chat-layout { display: flex; height: 100vh; }
.sidebar { width: 260px; border-right: 1px solid #eee; padding: 1rem; overflow-y: auto; }
.chat-main { flex: 1; display: flex; flex-direction: column; }
.messages { flex: 1; padding: 1rem; overflow-y: auto; }
.msg-user { background: #e8f4fd; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; }
.msg-assistant { background: #f5f5f5; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; }
.input-area { display: flex; padding: 1rem; border-top: 1px solid #eee; }
.input-area input { flex: 1; padding: 0.5rem; font-size: 1rem; }
.input-area button { padding: 0.5rem 1.5rem; background: #409eff; color: white; border: none; cursor: pointer; }
.evidence { width: 300px; border-left: 1px solid #eee; padding: 1rem; overflow-y: auto; font-size: 0.85rem; }
.citations { font-size: 0.8rem; color: #888; margin-top: 0.3rem; }
</style>
