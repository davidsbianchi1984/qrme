import React, { createContext, useContext, useEffect, useState } from "react";
import type { Session } from "./api";

interface Ctx {
  session: Session | null;
  setSession: (s: Session | null) => void;
}
const C = createContext<Ctx | null>(null);
const KEY = "suite.session";

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setState] = useState<Session | null>(() => {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch { return null; }
  });
  useEffect(() => {
    if (session) localStorage.setItem(KEY, JSON.stringify(session));
    else localStorage.removeItem(KEY);
  }, [session]);
  return <C.Provider value={{ session, setSession: setState }}>{children}</C.Provider>;
}
export function useSession(): Ctx {
  const ctx = useContext(C);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
