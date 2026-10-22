
import { getAccessToken } from "../utils/storage";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  const headers = new Headers(options.headers);

  // Set JSON content type only when a body exists and the caller
  // has not already specified a content type.
  if (options.body && !headers.has("Content-Type")) {
    if (!(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
  }

  // Automatically authenticate protected API requests.
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the default error message if the response isn't JSON.
    }

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message),
    );
  }

  return response.json() as Promise<T>;
}
