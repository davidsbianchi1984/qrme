import { planGate } from "./api";

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
/** Plan names arrive as the identifiers the gate refuses with — `free`, `pro`
 *  — and read as typos in the middle of a sentence. */
const title = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

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
    return variant === "inline"
      ? <div className="error">⚠ {text}</div>
      : <div className="card error"><p className="small">{text}</p></div>;
  }

  return (
    <div className="card error">
      <h4>{gate.needs.toUpperCase()} — {gate.capability}</h4>
      <p className="small">{gate.message}</p>
      <p className="muted small">
        You are on <strong>{title(gate.have)}</strong>.{" "}
        {title(gate.needs)} is ${gate.price_usd} a {gate.period} —{" "}
        {gate.billing}.
      </p>
      {onPlans && <button onClick={onPlans}>See the plans</button>}
    </div>
  );
}
