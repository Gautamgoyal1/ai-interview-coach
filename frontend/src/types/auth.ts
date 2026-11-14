export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  target_role?: string | null;
  experience_level?: string | null;
  created_at?: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface AuthCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends AuthCredentials {
  name?: string;
  full_name?: string;
}

export interface UpdateProfileData {
  full_name?: string;
  target_role?: string;
  experience_level?: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}
