import { planGate, RequestError } from "./api";
import { t as tr, visitorLang } from "./l10n";

/**
 * A refusal, rendered as what it is.
 *
 * Most failures here are a sentence and belong in the same small red line
 * the screen already used. Some are not: the plan gate answers with an
 * object built for a screen —
 * `{reason, capability, needs, have, price_usd, period, message, billing}` —
 * so that a console can say *which* capability was wanted, *which* plan has
 * it, what it costs, and that the billing is simulated.
 *
 * That object was being flattened into the error message and shown raw. This
 * component is the other half of the fix in `api.ts`: the transport keeps the
 * structure, and this decides how to draw it.
 *
 * `billing` is rendered next to the price rather than tucked underneath,
 * because it is carried on the refusal itself for a reason — a screen that
 * showed "$130/month" without "simulated — no real funds move" would be
 * making a claim the product spent effort avoiding everywhere else.
 *
 * `variant` exists so this can replace the two error styles already in the
 * console without redrawing either. Screens written later use a red card;
 * the older ones use a bare line with a warning sign. An ordinary failure
 * keeps whichever it had. A **gate always gets the card**, because it is an
 * offer rather than a complaint, and a line of red text is not a shape you
 * can put a button in.
 */
export function Refusal({ error, onPlans, variant = "card" }: {
  error: unknown;
  /** Where "see the plans" goes. Omitted where a screen has nowhere to send
   *  them — the button then does not appear, rather than appearing and
   *  doing nothing. */
  onPlans?: () => void;
  variant?: "card" | "inline";
}) {
  if (!error) return null;
  const gate = planGate(error);

  if (!gate) {
    const text = error instanceof Error ? error.message : String(error);
    // A refusal that says "sign in" without a way to is a dead end — the
    // field report read "authentication required" and had nowhere to tap.
    // Branching on the status rather than the sentence, because the
    // sentence arrives in the reader's language.
    const signin = error instanceof RequestError && error.status === 401
      ? (
        <button onClick={() => {
          window.location.hash = "";
          window.location.reload();
        }}>{tr("refusal.signin", visitorLang())}</button>
      ) : null;
    return variant === "inline"
      ? <div className="error">⚠ {text} {signin}</div>
      : <div className="card error"><p className="small">{text}</p>{signin}</div>;
  }

  // The muted line under the message used to repeat, in English, what the
  // message says: the plan you are on, the plan you need, the price, the
  // period, and that billing is simulated. It was written when `message` was
  // English too, so the repetition cost nothing.
  //
  // Now that the server composes that sentence in the reader's language, the
  // repetition is the only English left on this card — a translated paragraph
  // in an English frame, on the one screen that stands between somebody and a
  // decision to pay.
  //
  //     asked     is the refusal translated
  //     mattered  is what surrounds it
  //
  // So the duplicate goes. The price and the simulated-billing disclosure are
  // adjacent inside `message` — which is the invariant this component was
  // built to keep — and they are adjacent there in every language.
  //
  // The heading keeps `needs` and `capability` because both are identifiers
  // the API refuses with, the same string in every language, and the button
  // is console chrome and lives in `l10n.ts` with the rest of it.
  return (
    <div className="card error" data-screen="161">
      <h4>{gate.needs.toUpperCase()} — {gate.capability}</h4>
      <p className="small">{gate.message}</p>
      {onPlans && (
        <button onClick={onPlans}>
          {tr("refusal.see_plans", visitorLang())}
        </button>
      )}
    </div>
  );
}
