import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  getMe: () => api.get("/auth/me"),
  logout: () => api.post("/auth/logout"),
  unlockAccount: (userId) => api.post("/auth/unlock", { user_id: userId }),
};

export const dashboardAPI = {
  getSummary: () => api.get("/dashboard/summary"),
  getActivities: (page = 1) => api.get(`/dashboard/activities?page=${page}`),
  getRiskHistory: () => api.get("/dashboard/risk-history"),
};

export const alertAPI = {
  getAlerts: (unread = false) => api.get(`/alerts?unread=${unread}`),
  markRead: (id) => api.put(`/alerts/${id}/read`),
  markAllRead: () => api.put("/alerts/mark-all-read"),
  getLiveFeed: (limit = 20) => api.get(`/alerts/live-feed?limit=${limit}`),
  createDemoScenario: (scenario) => api.post("/alerts/demo-scenario", { scenario }),
  takeAction: (id, action) => api.post(`/alerts/${id}/action`, { action }),
  getSecurityScore: () => api.get("/alerts/security-score"),
};

export const adminAPI = {
  getStats: () => api.get("/admin/stats"),
  getUsers: () => api.get("/admin/users"),
  getAlerts: () => api.get("/admin/alerts"),
  resolveAlert: (id, action) => api.post(`/admin/resolve-alert/${id}`, { action_taken: action }),
  getModelPerformance: () => api.get("/admin/model-performance"),
};

export const analysisAPI = {
  getSocialInsights: () => api.get("/analysis/social-insights"),
};

export default api;
