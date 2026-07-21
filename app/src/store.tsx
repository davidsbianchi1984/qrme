import React, { createContext, useContext, useEffect, useState } from "react";
import type { Profile } from "./api";

export interface Session {
  profileId?: string;
  ownerToken?: string;
  interactorId?: string;
  interactorToken?: string;
  profile?: Profile;
}

interface Ctx {
  session: Session;
  setSession: (s: Session) => void;
  signOut: () => void;
}

const SessionContext = createContext<Ctx | null>(null);
const KEY = "qrme.session";

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSessionState] = useState<Session>(() => {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch {
      return {};
    }
  });

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify(session));
  }, [session]);

  const setSession = (s: Session) => setSessionState((prev) => ({ ...prev, ...s }));
  const signOut = () => {
    setSessionState({});
    localStorage.removeItem(KEY);
  };

  return (
    <SessionContext.Provider value={{ session, setSession, signOut }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): Ctx {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
