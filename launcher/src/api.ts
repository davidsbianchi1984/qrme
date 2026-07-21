// Client for the suite gateway (one origin fronting all three products).
const DEFAULT_BASE = "http://127.0.0.1:8000";
export function getBase(): string { return localStorage.getItem("suite.base") || DEFAULT_BASE; }
export function setBase(url: string) { localStorage.setItem("suite.base", url.replace(/\/+$/, "")); }

async function req<T>(path: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  const res = await fetch(getBase() + path, {
    method: opts.method || "GET",
    headers: { "content-type": "application/json" },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const d = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(typeof d === "string" ? d : JSON.stringify(d));
  }
  return data as T;
}

export interface Health {
  origin: string;
  products: Record<string, { mounted: boolean; live: boolean; base: string }>;
}
export interface Session {
  identity: string;
  products: {
    qrme?: { profile_id: string; owner_token: string; interactor_id: string; interactor_token: string };
    jim?: { user_id: string; user_token: string };
    pdi?: { tenant_id: string; tenant_token: string };
  };
}

export const api = {
  health: () => req<Health>("/suite/health"),
  session: (display_name: string, birthdate: string) =>
    req<Session>("/suite/session", { method: "POST", body: { display_name, birthdate } }),
};
