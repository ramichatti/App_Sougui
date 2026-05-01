export interface Privilege {
  id: number;
  name: string;
  description?: string;
  dashboard_id: number | null;
  dashboard_name?: string | null;
  dashboard_is_active?: boolean | null;
  created_at?: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  is_admin: boolean;
  is_system: boolean;
  is_active: boolean;
  privilege_count?: number;
  user_count?: number;
  privileges?: Privilege[];
  created_at?: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string | null;
  role_id: number | null;
  is_admin: boolean;
  is_active: boolean;
  has_image?: boolean;
  profile_image?: string;
  privileges?: Privilege[];
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  user: User;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface VerifyCodeRequest {
  email: string;
  code: string;
}

export interface ResetPasswordRequest {
  email: string;
  code: string;
  new_password: string;
}
