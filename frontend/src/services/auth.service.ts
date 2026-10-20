
import { apiRequest } from "./api";
import type {
  AuthCredentials,
  TokenResponse,
  User,
} from "../types/auth";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "../utils/storage";

export async function register(
  credentials: AuthCredentials,
): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
}

export async function login(
  credentials: AuthCredentials,
): Promise<User> {
  const tokenResponse = await apiRequest<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    },
  );

  setAccessToken(tokenResponse.access_token);

  try {
    return await getCurrentUser();
  } catch (error) {
    clearAccessToken();
    throw error;
  }
}

export async function getCurrentUser(): Promise<User> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Please log in to continue.");
  }

  return apiRequest<User>("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function logout(): void {
  clearAccessToken();
}
