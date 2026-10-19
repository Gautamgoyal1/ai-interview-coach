
export interface User {
  id: number;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface AuthCredentials {
  email: string;
  password: string;
}
