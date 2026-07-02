import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "chat",
    component: () => import("../views/ChatView.vue"),
  },
  {
    path: "/documents",
    name: "documents",
    component: () => import("../views/DocumentsView.vue"),
  },
  {
    path: "/graph",
    name: "graph",
    component: () => import("../views/GraphView.vue"),
  },
  {
    path: "/reviews",
    name: "reviews",
    component: () => import("../views/ReviewsView.vue"),
  },
  {
    path: "/evaluation",
    name: "evaluation",
    component: () => import("../views/EvaluationView.vue"),
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
