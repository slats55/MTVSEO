// API client — reads NEXT_PUBLIC_API_URL from process.env
// Default: http://localhost:8000

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function normalizeUrl(path: string): string {
  // Strip leading slash to avoid double slashes, then prepend base
  const cleanPath = path.replace(/^\//, "");
  return `${BASE_URL.replace(/\/$/, "")}/${cleanPath}`;
}

export interface ApiError {
  message: string;
  status: number;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      message = body.detail ?? message;
    } catch {
      // no JSON body
    }
    const err: ApiError = { message, status: res.status };
    throw err;
  }
  return res.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  const url = normalizeUrl(path);
  const res = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  return handleResponse<T>(res);
}

// Export BASE_URL for use in type-safe route construction
export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const url = normalizeUrl(path);
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

export { BASE_URL };