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
  // Which in-process tandems the gateway wired. False = that joint runs
  // degraded (no care team / no sealing), not that a product is down.
  tandems?: { jim_qrme: boolean; qrme_pdi: boolean };
}
export interface Session {
  identity: string;
  products: {
    qrme?: { profile_id: string; owner_token: string; interactor_id: string; interactor_token: string };
    jim?: { user_id: string; user_token: string };
    pdi?: { tenant_id: string; tenant_token: string };
  };
}

export interface Ecosystem {
  org: { id: string; name: string; departments: { id: string; name: string; role: string }[] };
  care_team: { linked: boolean };
  note: string;
}
export interface OperationEntry {
  key: string; updated_at: string; org: string | null; goal: string | null;
  plan: string | null; departments: (string | null)[];
}

export const api = {
  health: () => req<Health>("/suite/health"),
  session: (display_name: string, birthdate: string) =>
    req<Session>("/suite/session", { method: "POST", body: { display_name, birthdate } }),
  ecosystem: (s: Session) =>
    req<Ecosystem>("/suite/ecosystem", { method: "POST", body: { qrme: s.products.qrme, jim: s.products.jim } }),
  operations: (s: Session) =>
    req<{ entries: OperationEntry[]; note: string }>(
      "/suite/operations", { method: "POST", body: { qrme: s.products.qrme } }),
};
