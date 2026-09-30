export type Health = 'Healthy' | 'Monitor' | 'Attention' | 'Critical';
export interface Project {
  id: string; name: string; code: string; customer: string; region: string; value: number;
  completion: number; margin: number; variance: number; scheduleDays: number; riskExposure: number; status: Health;
}
export interface Risk { id: string; projectId: string; title: string; category: string; probability: number; impact: number; exposure: number; owner: string; status: string; mitigation: string; reviewOverdue?: boolean }
export interface Insight { title: string; body: string; sources: string[]; confidence: number; type: string }

