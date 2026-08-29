import { Component, type ReactNode } from "react";
import { recordProblem } from "./errors";

/**
 * One screen falling over must not take the console with it.
 *
 * ## What happened without this
 *
 * `api.feed` was declared as answering `{ posts }`. The route has only
 * ever answered `{ feed_posts }`, so the Wall put `undefined` into state
 * and rendered `posts.length` — and React, having no boundary anywhere
 * in this tree, unmounted **the entire application**. Pressing *Wall*
 * gave a beta tester a white page: no tab bar to leave by, no error, no
 * way back except reloading the browser.
 *
 *     asked     does the screen work
 *     mattered  what the rest of the app does when it doesn't
 *
 * A crash is going to happen again — that is what a crash is. What is a
 * choice is whether it costs one card or the whole session.
 *
 * So: the failing screen is replaced with a short, plain notice and a
 * button that re-mounts it, the drawer and every other tab keep working,
 * and the failure is posted to the same problem log every other error in
 * this console goes to (`recordProblem`) so it is a report rather than
 * somebody's memory of a white page — the log keeps the operation and the
 * count, and the screen keeps the sentence. The message is shown because a
 * tester who can read *"Cannot read properties of undefined"* can put it
 * in a message, and that sentence is most of the diagnosis.
 *
 * Keyed by tab in `App.tsx`, so moving to another screen builds a fresh
 * boundary instead of carrying one screen's failure onto the next.
 */
type Props = { children: ReactNode; where: string };
type State = { failed: string | null };

export class Boundary extends Component<Props, State> {
  state: State = { failed: null };

  static getDerivedStateFromError(error: unknown): State {
    return { failed: error instanceof Error ? error.message : String(error) };
  }

  componentDidCatch() {
    // Status 0 is this console's word for "never reached a server", which
    // is exactly true of a render that threw — see `req` in api.ts.
    try {
      recordProblem("RENDER", `screen:${this.props.where}`, 0);
    } catch { /* a boundary that throws is not a boundary */ }
  }

  render() {
    if (this.state.failed === null) return this.props.children;
    return (
      <div className="card">
        <h3>This screen stopped</h3>
        <p className="small">
          Everything else still works — the menu, and every other tab. Only
          this one fell over.
        </p>
        <p className="muted small">{this.state.failed}</p>
        <button onClick={() => this.setState({ failed: null })}>
          Try it again
        </button>
      </div>
    );
  }
}
