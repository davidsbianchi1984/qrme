import { useEffect, useState } from "react";
import { accountApi, api, getSignupKey, setSignupKey,
         type Sibling } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";
import { t as tr, visitorLang } from "../l10n";
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
                aria-label={shown ? tr("onb.hide.password", visitorLang())
                                  : tr("onb.show.password", visitorLang())}
                onClick={() => setShown(!shown)}>
          {shown ? tr("onb.hide.password", visitorLang())
                 : tr("onb.show.password", visitorLang())}
        </button>
      </span>
    </label>
  );
}

// Stage 1: the account — email verified by a 6-digit code before anything
// can sign in. Stage 2 (below): the profile, created under the account.
function AccountGate() {
  const { session, setSession } = useSession();
  const [mode, setMode] = useState<Mode>("signup");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [code, setCode] = useState("");
  const [delivery, setDelivery] = useState<string | null>(null);
  // Whether this deployment requires an invite key to create an account —
  // read from /health, so the field appears only where the gate exists. A
  // laptop install never sees it; the beta host always does.
  const [needsInvite, setNeedsInvite] = useState(false);
  const [inviteKey, setInviteKey] = useState(getSignupKey());
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
  // The account *and* the person. Memory is keyed on (profile, interactor),
  // so a session that carries only the account leaves every conversation
  // attached to whatever id this browser happened to mint — which is how a
  // starter you had talked to for an hour had never met you on your phone.
  const finishSession = (a: { account_id: string; account_token: string;
                              email: string; interactor_id?: string;
                              interactor_token?: string }) =>
    setSession({ accountId: a.account_id, accountToken: a.account_token,
                 accountEmail: a.email,
                 ...(a.interactor_id ? { interactorId: a.interactor_id } : {}),
                 ...(a.interactor_token
                       ? { interactorToken: a.interactor_token } : {}) });

  const isDesktop = Boolean((window as unknown as { qrmeDesktop?: unknown }).qrmeDesktop);
  const whereIsTheCode = delivery === "console"
    ? (isDesktop
        ? <> {tr("onb.nomail", visitorLang())} <b>{tr("onb.nomail.log", visitorLang())}</b> {tr("onb.nomail.open", visitorLang())}</>
        : <> {tr("onb.nomail", visitorLang())} <b>{tr("onb.nomail.terminal", visitorLang())}</b></>)
    : null;

  // On the code screen, the person may verify by clicking the emailed link
  // in their browser instead of typing the code. The app holds the email and
  // password, so it notices on its own: poll sign-in until the address is
  // proven, then continue without another keystroke.
  useEffect(() => {
    if (mode !== "code" || !password) return;
    const timer = setInterval(async () => {
      try {
        const a = await accountApi.signin({ email: email.trim(), password,
                                  ...(session.interactorId
                                        ? { adopt_interactor_id: session.interactorId }
                                        : {}) });
        finishSession(a);
      } catch { /* not verified yet — keep waiting */ }
    }, 3000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, email, password]);

  useEffect(() => {
    api.healthInfo().then((h) => setNeedsInvite(!!h.signup_key)).catch(() => {});
  }, []);

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
                  onClick={() => switchMode("signup")}>{tr("onb.create", visitorLang())}</button>
          <button className={mode === "signin" ? "tab active" : "tab"}
                  onClick={() => switchMode("signin")}>{tr("onb.signin", visitorLang())}</button>
        </div>
      )}

      {(mode === "signup" || mode === "signin") && oauthDoors.length > 0 && (
        <div className="oauth-doors">
          {oauthDoors.map((d) => (
            <button key={d.provider} disabled={!d.configured || oauthWaiting}
                    title={d.configured ? undefined : d.setup}
                    onClick={() => signInWith(d.provider)}>
              {d.provider === "google" ? "🟢" : ""} {tr("onb.signin.with", visitorLang())} {d.name}
              {!d.configured && <span className="muted small"> {tr("onb.oauth.absent", visitorLang())}</span>}
            </button>
          ))}
          <p className="field-hint">
            {tr("onb.oauth.note", visitorLang())}
          </p>
        </div>
      )}

      {mode === "signup" && (<>
        <label>{tr("onb.yourname", visitorLang())}<input value={name} placeholder={tr("onb.yourname", visitorLang())} onChange={(e) => setName(e.target.value)} /></label>
        <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <PasswordField label={tr("onb.password", visitorLang())} value={password} placeholder={tr("onb.password.min", visitorLang())} onChange={setPassword} />
        <p className="field-hint">{tr("onb.password.min", visitorLang())}</p>
        <PasswordField label={tr("onb.password.again", visitorLang())} value={confirm} placeholder={tr("onb.password.same", visitorLang())} onChange={setConfirm} />
        {confirm && !passwordsMatch && (
          <div className="error">{tr("onb.password.mismatch", visitorLang())}</div>
        )}
        {needsInvite && (<>
          <label>{tr("onb.invite", visitorLang())}
            <input value={inviteKey}
                   placeholder={tr("onb.invite", visitorLang())}
                   onChange={(e) => { setInviteKey(e.target.value); setSignupKey(e.target.value); }} />
          </label>
          <p className="field-hint">{tr("onb.invite.hint", visitorLang())}</p>
        </>)}
      </>)}

      {mode === "code" && (<>
        <p className="muted">
          {tr("onb.verify.sent", visitorLang())} <b>{email}</b>{whereIsTheCode}.
          <b> {tr("onb.verify.click", visitorLang())}</b> {tr("onb.verify.type", visitorLang())}
        </p>
        <label>{tr("onb.code", visitorLang())}
          <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
        </label>
      </>)}

      {mode === "signin" && (<>
        <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <PasswordField label="Password" value={password} onChange={setPassword} />
      </>)}

      {mode === "reset" && (<>
        <p className="muted">{tr("onb.reset.hint", visitorLang())}{whereIsTheCode}.</p>
        <label>{tr("onb.email", visitorLang())}<input type="email" value={email} placeholder="you@example.com" onChange={(e) => setEmail(e.target.value)} /></label>
        <div className="actions" style={{ justifyContent: "center" }}>
          <button disabled={busy || !email.trim()}
                  onClick={() => run(() => accountApi.requestReset(email.trim()),
                    (r) => { setDelivery(r.code_delivery); setNotice("If that address has an account, a reset code is on its way."); })}>
            {tr("onb.reset.send", visitorLang())}
          </button>
        </div>
        <label>{tr("onb.reset.code", visitorLang())}
          <input value={code} inputMode="numeric" placeholder="123456" onChange={(e) => setCode(e.target.value)} />
        </label>
        <PasswordField label={tr("onb.password.new", visitorLang())} value={password} placeholder={tr("onb.password.min", visitorLang())} onChange={setPassword} />
        <PasswordField label={tr("onb.password.new.again", visitorLang())} value={confirm} placeholder={tr("onb.password.same", visitorLang())} onChange={setConfirm} />
        {confirm && !passwordsMatch && (
          <div className="error">{tr("onb.password.mismatch", visitorLang())}</div>
        )}
      </>)}

      <Refusal error={error} variant="inline" />
      {notice && <div className="muted small">{notice}</div>}

      {mode === "signup" && (
        <button className="primary"
                disabled={busy || !email.trim() || !password || !passwordsMatch}
                onClick={signup}>
          {busy ? tr("onb.creating", visitorLang()) : tr("onb.create", visitorLang())}
        </button>
      )}
      {mode === "code" && (<>
        <button className="primary" disabled={busy || code.trim().length !== 6}
                onClick={() => run(
                  () => accountApi.verifyEmail({ email: email.trim(), code: code.trim() }),
                  finishSession)}>
          {busy ? tr("onb.checking", visitorLang()) : tr("onb.verify.go", visitorLang())}
        </button>
        <button className="linkish" disabled={busy}
                onClick={() => run(() => accountApi.resendCode(email.trim()),
                  (r) => { setDelivery(r.code_delivery); setNotice("A new code is on its way — the old one no longer works."); })}>
          {tr("onb.code.resend", visitorLang())}
        </button>
      </>)}
      {mode === "signin" && (<>
        <button className="primary" disabled={busy || !email.trim() || !password}
                onClick={() => run(
                  () => accountApi.signin({ email: email.trim(), password,
                                  ...(session.interactorId
                                        ? { adopt_interactor_id: session.interactorId }
                                        : {}) }),
                  finishSession)}>
          {busy ? tr("onb.signingin", visitorLang()) : tr("onb.signin", visitorLang())}
        </button>
        <button className="linkish" onClick={() => switchMode("reset")}>{tr("onb.forgot", visitorLang())}</button>
      </>)}
      {mode === "reset" && (<>
        <button className="primary"
                disabled={busy || !email.trim() || code.trim().length !== 6
                          || !password || !passwordsMatch}
                onClick={() => run(
                  () => accountApi.resetPassword({ email: email.trim(), code: code.trim(), new_password: password }),
                  () => { switchMode("signin"); setNotice("Password changed — sign in with the new one."); })}>
          {busy ? tr("onb.resetting", visitorLang()) : tr("onb.reset.set", visitorLang())}
        </button>
        <button className="linkish" onClick={() => switchMode("signin")}>{tr("onb.back", visitorLang())}</button>
      </>)}
    </>
  );
}

// Stage 2: create-profile flow — POST /profiles under the account, then
// register an interactor ("You") and set the owner relationship, so the app
// can chat straight away.
/**
 * The way back into a profile you already have.
 *
 * This screen used to offer exactly one thing to a signed-in account: make a
 * profile. That is the right offer once. It was also the only offer to
 * somebody who already had three — because an owner token is minted once, in
 * the create response, and the roster route that lists a person's profiles
 * asks for one before it will list them. Reinstall the app, or make the
 * profile on a phone and open the console, and the product's answer was to
 * make another.
 *
 *     asked     where do I find my owner token
 *     mattered  nowhere, and the screen that should have said so offered a
 *               second profile instead
 *
 * The listing carries no credential. Opening one is a press, and the press is
 * what mints the token — so a screen showing somebody their own profiles is
 * not also a screen handing out control of them.
 */
function HeldProfiles({ onNew }: { onNew: () => void }) {
  const { session, setSession } = useSession();
  const [held, setHeld] = useState<Sibling[] | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  const accountId = session.accountId || "";
  const accountToken = session.accountToken || "";

  useEffect(() => {
    if (!accountId || !accountToken) return;
    accountApi.heldProfiles(accountId, accountToken)
      .then((r: { profiles: Sibling[] }) => setHeld(r.profiles))
      .catch(setError);
  }, [accountId, accountToken]);

  async function open(profileId: string) {
    setBusy(profileId);
    setError(null);
    try {
      const minted = await accountApi.mintOwnerToken(
        accountId, profileId, accountToken);
      const profile = await api.getProfile(profileId);
      setSession({ profileId, ownerToken: minted.owner_token, profile });
    } catch (e) {
      setError(e);
    } finally {
      setBusy(null);
    }
  }

  if (held === null && !error) return null;

  return (
    <div className="held-profiles">
      <h3>{tr("onb.held.title", visitorLang())}</h3>
      <p className="muted small">{tr("onb.held.pitch", visitorLang())}</p>
      {error != null && <Refusal error={error} />}
      {held?.length === 0 && (
        <p className="muted small">{tr("onb.held.none", visitorLang())}</p>
      )}
      {(held ?? []).map((p) => (
        <div key={p.profile_id} className="held-row">
          <div>
            {/* `shown_as` rather than `display_name`: an anonymous profile is
                anonymous on its owner's own screen too, and the roster hands
                back both so this choice is the client's to make. */}
            <b>{p.shown_as}</b>
            <div className="muted small">{p.kind}</div>
          </div>
          <button disabled={busy !== null}
                  onClick={() => open(p.profile_id)}>
            {tr("onb.held.open", visitorLang())}
          </button>
        </div>
      ))}
      <button className="linkish" onClick={onNew}>
        {tr("onb.held.new", visitorLang())}
      </button>
    </div>
  );
}

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
  const [cardText, setCardText] = useState("");
  const [cardPng, setCardPng] = useState<string | null>(null);
  const [withheld, setWithheld] = useState<string | null>(null);

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

  async function importCard() {
    setBusy(true); setError(null); setWithheld(null);
    try {
      let card: Record<string, unknown> | undefined;
      if (cardText.trim()) card = JSON.parse(cardText);
      const profile = await api.importCard({
        owner_id: session.accountId || "owner-desktop",
        verification: { birthdate },
        card, content: cardPng ?? undefined,
      });
      if (profile.withholdings.length > 0) {
        setWithheld(profile.withholdings.map((w) => w.item).join(" · "));
      }
      const me = await api.createInteractor({ display_name: "You", birthdate });
      await api.setRelationship(profile.id, me.id, {
        relationship_type: "friend", nickname: "me", tone: "warm",
      }, profile.owner_token);
      setSession({
        profileId: profile.id, ownerToken: profile.owner_token,
        profile, interactorId: me.id, interactorToken: me.token,
      });
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  function pickCardPng(file: File | null) {
    if (!file) { setCardPng(null); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result || "");
      setCardPng(url.slice(url.indexOf(",") + 1) || null);
    };
    reader.readAsDataURL(file);
  }

  return (
    <>
      <label>
        {tr("onb.profile.name", visitorLang())}
        {/* No pre-filled name. The profile is the user's to name, and a
            default sitting in the box is the one most people never change —
            which is how a sample name becomes the product's mascot. */}
        <input value={name} placeholder={tr("onb.profile.placeholder", visitorLang())}
               onChange={(e) => setName(e.target.value)} />
      </label>
      <label>
        {tr("onb.persona", visitorLang())}
        <textarea rows={3} value={persona}
                  onChange={(e) => setPersona(e.target.value)} />
      </label>
      <label>
        {tr("onb.birthdate", visitorLang())}
        <input type="date" value={birthdate}
               onChange={(e) => setBirthdate(e.target.value)} />
      </label>

      <Refusal error={error} variant="inline" />

      <button className="primary" disabled={busy || !birthdate} onClick={create}>
        {busy ? tr("onb.creating", visitorLang())
              : tr("onb.create.profile", visitorLang())}
      </button>
      <p className="hint">
        {tr("onb.signedin", visitorLang())} <code>{session.accountEmail}</code> {tr("onb.undercount", visitorLang())}
      </p>

      {/* Or carry in a character card — chara_card_v2/v3 as JSON or a PNG
          with one embedded. What the platform refuses to carry (harness
          instructions), it names. */}
      <label>
        {tr("onb.card", visitorLang())}
        <textarea rows={2} value={cardText}
                  placeholder={tr("onb.card.ph", visitorLang())}
                  onChange={(e) => setCardText(e.target.value)} />
      </label>
      <input type="file" accept="image/png"
             onChange={(e) => pickCardPng(e.target.files?.[0] ?? null)} />
      <button disabled={busy || !birthdate || (!cardText.trim() && !cardPng)}
              onClick={importCard}>
        {tr("onb.card.import", visitorLang())}
      </button>
      {withheld && (
        <p className="hint">{tr("onb.card.withheld", visitorLang())} {withheld}</p>
      )}
    </>
  );
}

export function Onboarding({ onPublic }: {
  /** The two doors that open without an account. Passed in rather than
   *  routed here, so the link and the `#object` hash land in one place. */
  onPublic: (door: "object" | "mark" | "access") => void;
}) {
  const { session } = useSession();
  const accountReady = Boolean(session.accountToken);
  // The roster comes first for somebody signing back in, and the create form
  // is behind one press. A person whose profiles already exist is not here to
  // make another, and offering that first is what produced the second one.
  const [creating, setCreating] = useState(false);
  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>{tr("onb.tagline", visitorLang())}</h1>
        <p className="muted">
          {tr("onb.pitch", visitorLang())}
        </p>
        {!accountReady && <AccountGate />}
        {accountReady && !creating && (
          <HeldProfiles onNew={() => setCreating(true)} />
        )}
        {accountReady && creating && <ProfileCreate />}

        {/* Not everybody arriving here wants a profile. Some are here
            *because* of one — somebody who has found a synthetic profile of
            themselves, or who was sent something and wants to know whether a
            person wrote it. Both routes are public on the backend and were
            reachable only after signing up, which is the one thing neither
            person should have to do. */}
        <div className="public-links">
          <p className="muted small">{tr("pub.invite", visitorLang())}</p>
          <button className="linkish" onClick={() => onPublic("object")}>
            {tr("pub.object.title", visitorLang())}
          </button>
          <button className="linkish" onClick={() => onPublic("mark")}>
            {tr("pub.tab.mark", visitorLang())}
          </button>
          {/* The accessibility statement and its report door, upfront —
              before the account, because the person it exists for may be
              the person this signup shut out. */}
          <button className="linkish" onClick={() => onPublic("access")}>
            {tr("acc.title", visitorLang())}
          </button>
          <p className="muted small">
            {tr("pub.invite.none", visitorLang())}
          </p>
        </div>
      </div>
    </div>
  );
}
