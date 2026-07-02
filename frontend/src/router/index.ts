import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
  },
  {
    path: "/",
    name: "chat",
    component: () => import("../views/ChatView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/documents",
    name: "documents",
    component: () => import("../views/DocumentsView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/graph",
    name: "graph",
    component: () => import("../views/GraphView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/reviews",
    name: "reviews",
    component: () => import("../views/ReviewsView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/evaluation",
    name: "evaluation",
    component: () => import("../views/EvaluationView.vue"),
    meta: { requiresAuth: true },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("access_token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if (to.path === "/login" && token) {
    next("/");
  } else {
    next();
  }
});
