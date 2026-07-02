<template>
  <div class="chat-layout">
    <aside class="sidebar">会话列表</aside>
    <main class="chat-main">
      <div class="messages">
        <div v-for="(msg, i) in store.messages" :key="i" :class="msg.role">
          {{ msg.content }}
        </div>
      </div>
      <form @submit.prevent="send" class="input-area">
        <input v-model="query" placeholder="输入您的问题..." />
        <button type="submit">发送</button>
      </form>
    </main>
    <aside class="evidence">证据面板</aside>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useChatStore } from "../stores/chat";

const store = useChatStore();
const query = ref("");

function send() {
  if (!query.value.trim()) return;
  store.addMessage({ role: "user", content: query.value });
  store.addMessage({ role: "assistant", content: "处理中..." });
  query.value = "";
}
</script>

<style scoped>
.chat-layout { display: flex; height: 100vh; }
.sidebar { width: 260px; border-right: 1px solid #eee; padding: 1rem; }
.chat-main { flex: 1; display: flex; flex-direction: column; }
.messages { flex: 1; padding: 1rem; overflow-y: auto; }
.input-area { display: flex; padding: 1rem; border-top: 1px solid #eee; }
.input-area input { flex: 1; padding: 0.5rem; }
.evidence { width: 300px; border-left: 1px solid #eee; padding: 1rem; }
</style>
