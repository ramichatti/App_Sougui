export interface Dashboard {
  id: number;
  role: string;
  dashboard_name: string;
  embed_url: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
}

export interface DashboardResponse {
  dashboards: Dashboard[];
  user_role: string;
}
