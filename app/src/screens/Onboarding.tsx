import { useEffect, useState } from "react";
import { accountApi, api } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";
import { oauthApi } from "../api";

type Mode = "signup" | "code" | "signin" | "reset";

// A password input with the conventional show/hide toggle: hidden characters
// are the reason typos survive, and letting people look is the standard cure
// (alongside typing it twice on the signup form).
function PasswordField(props: {
  label: string; value: string; placeholder?: string;
  onChange: (v: string) => void;
}) {
  const [shown, setShown] = useState(false);
  return (
    <label>{props.label}
      <span className="pw-wrap">
        <input type={shown ? "text" : "password"} value={props.value}
               placeholder={props.placeholder}
               onChange={(e) => props.onChange(e.target.value)} />
        <button type="button" className="pw-toggle" tabIndex={-1}
                aria-label={shown ? "Hide password" : "Show password"}
                onClick={() => setShown(!shown)}>
          {shown ? "Hide" : "Show"}
        </button>
      </span>
    </label>
  );
}

// Stage 1: the account — email verified by a 6-digit code before anything
// can sign in. Stage 2 (below): the profile, created under the account.
function AccountGate() {
  const { setSession } = useSession();
  const [mode, setMode] = useState<Mode>("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [code, setCode] = useState("");
  const [delivery, setDelivery] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [oauthDoors, setOauthDoors] = useState<
    { provider: string; name: string; configured: boolean; setup?: string }[]>([]);
  const [oauthWaiting, setOauthWaiting] = useState(false);

  useEffect(() => {
    oauthApi.providers().then((r) => setOauthDoors(r.providers)).catch(() => {});
  }, []);

  async function signInWith(provider: string) {
    setError(null); setNotice(null); setOauthWaiting(true);
    try {
      const started = await oauthApi.start(provider);
      window.open(started.url, "_blank");
      setNotice("Finish signing in with the browser window that just opened…");
      // Poll the one-time claim until the callback lands or two minutes pass.
      const until = Date.now() + 120000;
      while (Date.now() < until) {
        await new Promise((r) => setTimeout(r, 2000));
        const got = await oauthApi.claim(started.state).catch(() => null);
        if (got === null) { setError("Sign-in was not completed — try again."); break; }
        if (got.ready && got.account_token) {
          finishSession({ account_id: got.account_id!, account_token: got.account_token, email: got.email! });
          return;
        }
      }
    } catch (e) { setError(e); }
    finally { setOauthWaiting(false); }
  }

  function switchMode(m: Mode) {
    setMode(m); setError(null); setNotice(null); setCode("");
    setPassword(""); setConfirm("");
  }

  async function run<T>(fn: () => Promise<T>, then: (r: T) => void) {
    setBusy(true); setError(null); setNotice(null);
    try { then(await fn()); }
    catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const passwordsMatch = password === confirm;
  const finishSession = (a: { account_id: string; account_token: string; email: string }) =>
    setSession({ accountId: a.account_id, accountToken: a.account_token, accountEmail: a.email });

  const isDesktop = Boolean((window as unknown as { qrmeDesktop?: unknown }).qrmeDesktop);
  const whereIsTheCode = delivery === "console"
    ? (isDesktop
        ? <> — this deployment has no mail service configured, so the code was <b>written to the app's backend log</b> (button below opens it)</>
        : <> — this deployment has no mail service configured, so the code was <b>printed in the terminal running the backend</b></>)
    : null;

  // On the code screen, the person may verify by clicking the emailed link
  // in their browser instead of typing the code. The app holds the email and
  // password, so it notices on its own: poll sign-in until the address is
  // proven, then continue without another keystroke.
  useEffect(() => {
    if (mode !== "code" || !password) return;
    const timer = setInterval(async () => {
      try {
        const a = await accountApi.signin({ email: email.trim(), password });
        finishSession(a);
      } catch { /* not verified yet — keep waiting */ }
    }, 3000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, email, password]);

  const signup = async () => {
    setBusy(true); setError(null); setNotice(null);
    try {
      const r = await accountApi.signup({ email: email.trim(), password, display_name: name.trim() || undefined });
      if (r.verification === "local" && r.account_token) {
        // No mail transport on this deployment (the desktop install): the
        // machine owner is trusted, the account is already active.
        finishSession({ account_id: r.account_id, account_token: r.account_token, email: r.email });
        return;
      }
      setDelivery(r.code_delivery || null); setMode("code");
    } catch (e) {
      const msg = (e as Error).message;
      if (msg.includes("already pending")) {
        // A signup that crashed mid-flight leaves a pending account. Never
        // strand the person on the form for that — go to the code screen
        // and issue a fresh code.
        setMode("code");
        try {
          const r = await accountApi.resendCode(email.trim());
          setDelivery(r.code_delivery);
          setNotice("This address already had a signup in progress — we've sent a fresh code.");
        } catch (e2) { setError(e2); }
      } else if (msg.includes("already exists")) {
        setMode("signin");
        setNotice("This address already has an account — sign in (or use Forgot password).");
      } else {
        setError(e);
      }
    } finally { setBusy(false); }
  };

  return (
    <>
      {(mode === "signup" || mode === "signin") && (
        <div className="tabs">
          <button className={mode === "signup" ? "tab active" : "tab"}
                  onClick={() => switchMode("signup")}>Create account</button>
          <button className={mode === "signin" ? "tab active" : "tab"}
                  onClick={() => switchMode("signin")}>Sign in</button>
        </div>
      )}

      {(mode === "signup" || mode === "signin") && oauthDoors.length > 0 && (
        <div className="oauth-doors">
          {oauthDoors.map((d) => (
            <button key={d.provider} disabled={!d.configured || oauthWaiting}
                    title={d.configured ? undefined : d.setup}
                    onClick={() => signInWith(d.provider)}>
              {d.provider === "google" ? "🟢" : ""} Sign in with {d.name}
              {!d.configured && <span className="muted small"> · not configured here</span>}
            </button>
          ))}
          <p className="field-hint">
            A configured provider opens your browser and vouches for your
            email — no code to type. Grey means this deployment hasn't
            registered an OAuth client yet (hover for what to set).
          </p>
        </div>
      )}

      {mode === "signup" && (<>
        <label>Your name<input value={name} placeholder="Your name" onChange={(e) => setName(e.target.value)} /></label>
        <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <PasswordField label="Password" value={password} placeholder="At least 8 characters" onChange={setPassword} />
        <p className="field-hint">At least 8 characters.</p>
        <PasswordField label="Re-enter password" value={confirm} placeholder="Same password again" onChange={setConfirm} />
        {confirm && !passwordsMatch && (
          <div className="error">⚠ The passwords don't match yet.</div>
        )}
      </>)}

      {mode === "code" && (<>
        <p className="muted">
          We emailed a verification link to <b>{email}</b>{whereIsTheCode}.
          <b> Click the link and this screen continues on its own.</b> Prefer
          typing? Enter the 6-digit code from the same email instead.
        </p>
        <label>Verification code
          <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
        </label>
      </>)}

      {mode === "signin" && (<>
        <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <PasswordField label="Password" value={password} onChange={setPassword} />
      </>)}

      {mode === "reset" && (<>
        <p className="muted">Enter your account's email; we'll send a 6-digit reset code{whereIsTheCode}.</p>
        <label>Email<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <div className="actions" style={{ justifyContent: "center" }}>
          <button disabled={busy || !email.trim()}
                  onClick={() => run(() => accountApi.requestReset(email.trim()),
                    (r) => { setDelivery(r.code_delivery); setNotice("If that address has an account, a reset code is on its way."); })}>
            Send reset code
          </button>
        </div>
        <label>Reset code
          <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
        </label>
        <PasswordField label="New password" value={password} placeholder="At least 8 characters" onChange={setPassword} />
        <PasswordField label="Re-enter new password" value={confirm} placeholder="Same password again" onChange={setConfirm} />
        {confirm && !passwordsMatch && (
          <div className="error">⚠ The passwords don't match yet.</div>
        )}
      </>)}

      <Refusal error={error} variant="inline" />
      {notice && <div className="muted small">{notice}</div>}

      {mode === "signup" && (
        <button className="primary"
                disabled={busy || !email.trim() || !password || !passwordsMatch}
                onClick={signup}>
          {busy ? "Creating…" : "Create account"}
        </button>
      )}
      {mode === "code" && (<>
        <button className="primary" disabled={busy || code.trim().length !== 6}
                onClick={() => run(
                  () => accountApi.verifyEmail({ email: email.trim(), code: code.trim() }),
                  finishSession)}>
          {busy ? "Checking…" : "Verify & continue"}
        </button>
        <button className="linkish" disabled={busy}
                onClick={() => run(() => accountApi.resendCode(email.trim()),
                  (r) => { setDelivery(r.code_delivery); setNotice("A new code is on its way — the old one no longer works."); })}>
          Resend code
        </button>
      </>)}
      {mode === "signin" && (<>
        <button className="primary" disabled={busy || !email.trim() || !password}
                onClick={() => run(
                  () => accountApi.signin({ email: email.trim(), password }),
                  finishSession)}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <button className="linkish" onClick={() => switchMode("reset")}>Forgot password?</button>
      </>)}
      {mode === "reset" && (<>
        <button className="primary"
                disabled={busy || !email.trim() || code.trim().length !== 6
                          || !password || !passwordsMatch}
                onClick={() => run(
                  () => accountApi.resetPassword({ email: email.trim(), code: code.trim(), new_password: password }),
                  () => { switchMode("signin"); setNotice("Password changed — sign in with the new one."); })}>
          {busy ? "Resetting…" : "Set new password"}
        </button>
        <button className="linkish" onClick={() => switchMode("signin")}>Back to sign in</button>
      </>)}
    </>
  );
}

// Stage 2: create-profile flow — POST /profiles under the account, then
// register an interactor ("You") and set the owner relationship, so the app
// can chat straight away.
function ProfileCreate() {
  const { session, setSession } = useSession();
  const [name, setName] = useState("");
  const [persona, setPersona] = useState(
    "A warm, curious digital version of me — remembers what matters and speaks plainly.",
  );
  // Empty, not a sample date: this field is age verification, and a
  // pre-filled birthdate is a wrong answer already submitted.
  const [birthdate, setBirthdate] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const profile = await api.createProfile({
        owner_id: session.accountId || "owner-desktop",
        kind: "self",
        display_name: name.trim() || "AI assistant",
        persona: persona.trim(),
        verification: { birthdate },
        purpose: "companion_coach",
      });
      const me = await api.createInteractor({ display_name: "You", birthdate });
      await api.setRelationship(profile.id, me.id, {
        relationship_type: "friend",
        nickname: "me",
        tone: "warm",
      }, profile.owner_token!);
      setSession({
        profileId: profile.id,
        ownerToken: profile.owner_token,
        profile,
        interactorId: me.id,
        interactorToken: me.token,
      });
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <label>
        Profile name
        {/* No pre-filled name. The profile is the user's to name, and a
            default sitting in the box is the one most people never change —
            which is how a sample name becomes the product's mascot. */}
        <input value={name} placeholder="Name your assistant"
               onChange={(e) => setName(e.target.value)} />
      </label>
      <label>
        Persona
        <textarea rows={3} value={persona}
                  onChange={(e) => setPersona(e.target.value)} />
      </label>
      <label>
        Owner birthdate (age verification)
        <input type="date" value={birthdate}
               onChange={(e) => setBirthdate(e.target.value)} />
      </label>

      <Refusal error={error} variant="inline" />

      <button className="primary" disabled={busy || !birthdate} onClick={create}>
        {busy ? "Creating…" : "Create My Profile"}
      </button>
      <p className="hint">
        Signed in as <code>{session.accountEmail}</code> — your profile is
        created under this account.
      </p>
    </>
  );
}

export function Onboarding() {
  const { session } = useSession();
  const accountReady = Boolean(session.accountToken);
  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>Your identity. Your AI.</h1>
        <p className="muted">
          Create a synthetic profile that thinks, remembers, and evolves with you.
          It runs against your local QRME API — your data stays in your vault.
        </p>
        {accountReady ? <ProfileCreate /> : <AccountGate />}
      </div>
    </div>
  );
}
