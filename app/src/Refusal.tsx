import { planGate } from "./api";

/**
 * A refusal, rendered as what it is.
 *
 * Most failures here are a sentence and belong in a red card. Some are not:
 * the plan gate answers with an object built for a screen —
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
 */
export function Refusal({ error, onPlans }: {
  error: unknown;
  /** Where "see the plans" goes, when a screen has somewhere to send them. */
  onPlans?: () => void;
}) {
  if (!error) return null;
  const gate = planGate(error);

  if (!gate) {
    return (
      <div className="card error">
        <p className="small">{(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="card error">
      <h4>{gate.needs.toUpperCase()} — {gate.capability}</h4>
      <p className="small">{gate.message}</p>
      <p className="muted small">
        You are on <strong>{gate.have}</strong>.{" "}
        {gate.needs} is ${gate.price_usd} a {gate.period} — {gate.billing}.
      </p>
      {onPlans && <button onClick={onPlans}>See the plans</button>}
    </div>
  );
}
