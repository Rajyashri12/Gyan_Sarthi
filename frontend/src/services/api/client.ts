const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

type RequestOptions = RequestInit & {
  token?: string;
};

export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, headers, ...rest } = options;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
      ...(headers || {}),
    },
  });

  const contentType = response.headers.get("content-type");

  const data = contentType?.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "object" && data !== null && "detail" in data
        ? String(data.detail)
        : `API request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}

export function getToken(): string | null {
  return localStorage.getItem("gyan_sarthi_token");
}

export function setToken(token: string): void {
  localStorage.setItem("gyan_sarthi_token", token);
}

export function removeToken(): void {
  localStorage.removeItem("gyan_sarthi_token");
}