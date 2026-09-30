export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";
export type SessionUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
};
export const token = () => localStorage.getItem("pl-token");
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token()) headers.set("Authorization", `Bearer ${token()}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail || "Request failed");
  }
  return response.json();
}
export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; user: SessionUser }>("/auth/token", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<SessionUser>("/auth/me"),
  projects: () => request<any[]>("/projects"),
  projectWorkspace: (id: string) => request<any>(`/projects/${id}/workspace`),
  financials: (projectId?: string) =>
    request<any[]>(`/financials${projectId ? `?project_id=${projectId}` : ""}`),
  forecasts: (projectId?: string) =>
    request<any[]>(`/forecasts${projectId ? `?project_id=${projectId}` : ""}`),
  risks: () => request<any[]>("/risks"),
  contracts: () => request<any[]>("/contracts"),
  clauses: (id: string) => request<any[]>(`/contracts/${id}/clauses`),
  contract: (id: string) => request<any>(`/contracts/${id}`),
  contractPdf: (id: string, download = false) => `${API_URL}/contracts/${id}/pdf${download ? "?download=true" : ""}`,
  reindexContract: (id: string) => request<any>(`/contracts/${id}/reindex`, { method: "POST" }),
  documents: (type?: string) =>
    request<any[]>(`/documents${type ? `?document_type=${type}` : ""}`),
  search: (q: string) => request<any[]>(`/search?q=${encodeURIComponent(q)}`),
  query: (question: string, project_id?: string, contract_id?: string) =>
    request<any>("/ai/query", {
      method: "POST",
      body: JSON.stringify({ question, project_id, contract_id }),
    }),
  feedback: (ai_run_id: string, helpful: boolean, comment?: string) =>
    request<any>("/feedback", {
      method: "POST",
      body: JSON.stringify({ ai_run_id, helpful, comment }),
    }),
  useCases: () => request<any[]>("/use-cases"),
  createUseCase: (payload: any) =>
    request<any>("/use-cases", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  reviewUseCase: (id: string, decision: string, comments: string) =>
    request<any>(`/use-cases/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ decision, comments }),
    }),
  changeUseCaseStage: (id: string, status: string, comments: string) =>
    request<any>(`/use-cases/${id}/stage`, {
      method: "POST",
      body: JSON.stringify({ status, comments }),
    }),
  deleteUseCase: (id: string) =>
    request<any>(`/use-cases/${id}`, { method: "DELETE" }),
  reports: () => request<any[]>("/reports"),
  generateReport: (projectId: string) =>
    request<any>(`/reports/project/${projectId}`, { method: "POST" }),
  reviewReport: (id: string, status: string) =>
    request<any>(`/reports/${id}/${status}`, { method: "PATCH" }),
  reportDownload: (id: string, format: "pdf" | "xlsx") => `${API_URL}/reports/${id}/download?format=${format}`,
  runPipeline: () => request<any>("/pipelines/run", { method: "POST" }),
  pipelines: () => request<any[]>("/pipelines"),
  adoption: () => request<any>("/adoption"),
  governance: () => request<any>("/governance"),
  audit: () => request<any[]>("/audit"),
};
export function saveSession(result: {
  access_token: string;
  user: SessionUser;
}) {
  localStorage.setItem("pl-token", result.access_token);
  localStorage.setItem("pl-user", JSON.stringify(result.user));
}
export function clearSession() {
  localStorage.removeItem("pl-token");
  localStorage.removeItem("pl-user");
  localStorage.removeItem("pl-auth");
}
