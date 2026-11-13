
export interface User {
  id: number;
  email: string;
  full_name?: string | null;
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
