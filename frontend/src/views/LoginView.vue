<template>
  <div class="login-page">
    <form @submit.prevent="login" class="login-form">
      <h1>PolicyMind</h1>
      <input v-model="tenantSlug" placeholder="租户标识" required />
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required minlength="8" />
      <button type="submit">登录</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const tenantSlug = ref("");
const username = ref("");
const password = ref("");
const error = ref("");

async function login() {
  error.value = "";
  try {
    const resp = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_slug: tenantSlug.value,
        username: username.value,
        password: password.value,
      }),
    });
    if (!resp.ok) {
      error.value = "登录失败，请检查凭据";
      return;
    }
    const data = await resp.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    router.push("/");
  } catch {
    error.value = "网络错误";
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; }
.login-form { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 360px; }
.login-form h1 { text-align: center; margin-bottom: 1.5rem; }
.login-form input { width: 100%; padding: 0.6rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
.login-form button { width: 100%; padding: 0.6rem; background: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; }
.error { color: #f56c6c; margin-top: 0.5rem; }
</style>
