import { getAccessToken } from "../utils/storage";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const SERVICE_UNAVAILABLE =
  "PrepMate's server may be starting or temporarily unavailable. Please wait about a minute, then try again. If you submitted an answer, check your interview before resubmitting.";

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

  // Keep each user action to one request: replaying a POST after a cold start
  // or dropped connection could duplicate a saved answer or provider charge.
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch (error) {
    if (options.signal?.aborted || (error instanceof Error && error.name === "AbortError")) {
      throw error;
    }
    throw new ApiError(SERVICE_UNAVAILABLE, 0);
  }

  if (!response.ok) {
    let message = [502, 503, 504].includes(response.status)
      ? SERVICE_UNAVAILABLE
      : `Request failed (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the default error message if the response isn't JSON.
    }

    throw new ApiError(
      typeof message === "string" ? message : JSON.stringify(message),
      response.status,
    );
  }

  try {
    return await response.json() as T;
  } catch (error) {
    if (options.signal?.aborted || (error instanceof Error && error.name === "AbortError")) {
      throw error;
    }
    // A sleeping host can return an HTML loading page with HTTP 200. Never
    // treat that as a successful API result or expose HTML/parser errors.
    throw new ApiError(SERVICE_UNAVAILABLE, 502);
  }
}
