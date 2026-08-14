// Pick the character skin your own profile wears — as tiles you click, the
// way the model picker and the voice picker already work.
//
// The shelf has existed backend-side since the avatar deck was written:
// `GET /avatars/market` names eight systems a person may already have a face
// in, each with how to export from it. It had one door, on Identity, as a
// dropdown next to a URL box — which is a form, not a picker. A person who
// wants their Ready Player Me figure standing in their own conversation had
// to know that screen existed and that the box wanted a link.
//
//     asked     can an owner bring a face from somewhere else
//     mattered  can they do it where they are looking at the face
//
// Each mark is drawn here rather than fetched, for the same reasons
// `ProviderTiles` gives: a console that reaches out to eight vendors' CDNs
// for logo files leaks which product you opened and breaks when a URL moves.
// These are original glyphs in each brand's own colour — recognisable at a
// glance, and honest about being our drawing rather than their trademark.
import type { CSSProperties } from "react";

export interface SkinSource {
  key: string;
  name: string;
  /** The provider's own export route, in their words. */
  how: string;
}

const MARKS: Record<string, { color: string; glyph: JSX.Element }> = {
  ready_player_me: {
    color: "#7c5cff",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3.4a4.3 4.3 0 1 1 0 8.6 4.3 4.3 0 0 1 0-8.6Zm0 10.1c4 0 7.2 2 7.2 4.4v2.1H4.8v-2.1c0-2.4 3.2-4.4 7.2-4.4Z"
              fill="currentColor" />
      </svg>
    ),
  },
  bitmoji: {
    color: "#fffc00",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3c3.6 0 5.8 2.4 5.8 5.6 0 1 .5 1.2 1 1.6.5.4.3 1.2-.4 1.5-.9.4-1 .6-1.3 1.5-.6 1.9-2.6 3.6-5.1 3.6s-4.5-1.7-5.1-3.6c-.3-.9-.4-1.1-1.3-1.5-.7-.3-.9-1.1-.4-1.5.5-.4 1-.6 1-1.6C6.2 5.4 8.4 3 12 3Zm-4 15.1c2.6 1.1 5.4 1.1 8 0l1.4 1c-3.2 1.9-7.6 1.9-10.8 0l1.4-1Z"
              fill="currentColor" />
      </svg>
    ),
  },
  meta_avatar: {
    color: "#0081fb",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M4 16.2c0-4.4 2-8.4 4.7-8.4 1.6 0 2.7 1.1 4 3.2l1 1.7c1 1.7 1.6 2.4 2.3 2.4.9 0 1.5-1.3 1.5-3.2 0-2.4-.9-3.9-2.1-3.9-.8 0-1.6.6-2.5 1.9l-1.1-1.6C13.1 6.4 14.4 5.6 16 5.6c2.6 0 4.4 2.6 4.4 6.3 0 3.3-1.5 5.5-3.7 5.5-1.5 0-2.6-.8-3.9-3l-1.2-2c-1-1.7-1.5-2.3-2.2-2.3-1.2 0-2.3 2.1-2.3 5.4 0 .8.1 1.5.2 2L4 16.2Z"
              fill="currentColor" />
      </svg>
    ),
  },
  apple_memoji: {
    color: "#d6d6da",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 4.2c3.7 0 6.4 2.7 6.4 6.4v2.6c0 3.5-2.9 6.3-6.4 6.3s-6.4-2.8-6.4-6.3v-2.6c0-3.7 2.7-6.4 6.4-6.4Zm-2.5 6a1 1 0 1 0 0 2.1 1 1 0 0 0 0-2.1Zm5 0a1 1 0 1 0 0 2.1 1 1 0 0 0 0-2.1Zm-4.7 4.6c.7 1.1 1.8 1.7 3.2 1.7s2.5-.6 3.2-1.7l-1.2-.7c-.5.7-1.2 1-2 1s-1.5-.3-2-1l-1.2.7Z"
              fill="currentColor" />
      </svg>
    ),
  },
  xbox_avatar: {
    color: "#107c10",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 2.6a9.4 9.4 0 0 1 5.3 1.7c-1.5.2-3.3 1.4-5.3 3.3-2-1.9-3.8-3.1-5.3-3.3A9.4 9.4 0 0 1 12 2.6ZM4.6 5.9c1.1.2 3 1.8 5 4.3-2.6 3.3-4.3 6.6-4.6 8.7A9.4 9.4 0 0 1 4.6 5.9Zm14.8 0a9.4 9.4 0 0 1-.4 13c-.3-2.1-2-5.4-4.6-8.7 2-2.5 3.9-4.1 5-4.3ZM12 12.4c2.4 2.8 4.2 5.9 4.6 7.7a9.4 9.4 0 0 1-9.2 0c.4-1.8 2.2-4.9 4.6-7.7Z"
              fill="currentColor" />
      </svg>
    ),
  },
  zepeto: {
    color: "#ff5a5f",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M6 4.6h12v2L9.6 17.4H18v2H6v-2L14.4 6.6H6v-2Z"
              fill="currentColor" />
      </svg>
    ),
  },
  nintendo_mii: {
    color: "#e60012",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3.6c3.4 0 6 2.5 6 5.9v3c0 4-2.7 7.9-6 7.9s-6-3.9-6-7.9v-3c0-3.4 2.6-5.9 6-5.9Zm-2.7 6.8a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2Zm5.4 0a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2ZM12 15.1c-1.1 0-2 .4-2.6 1l1 1c.4-.3.9-.5 1.6-.5s1.2.2 1.6.5l1-1c-.6-.6-1.5-1-2.6-1Z"
              fill="currentColor" />
      </svg>
    ),
  },
  other: {
    color: "#9fd8e8",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3.4 20 8v8l-8 4.6L4 16V8l8-4.6Zm0 2.3L6 9.2v5.6l6 3.5 6-3.5V9.2l-6-3.5Zm-1 3.5h2v2h2v2h-2v2h-2v-2H9v-2h2v-2Z"
              fill="currentColor" />
      </svg>
    ),
  },
};

/** The shelf as tiles. `chosen` is the source key currently selected; the
 *  caller decides what selecting one reveals — this component's whole job is
 *  the choosing. */
export function SkinTiles(props: {
  sources: SkinSource[];
  chosen: string;
  onPick: (key: string) => void;
  busy?: boolean;
}) {
  return (
    <div className="provider-tiles">
      {props.sources.map((s) => {
        const mark = MARKS[s.key] || MARKS.other;
        const active = props.chosen === s.key;
        const style: CSSProperties = { color: mark.color };
        return (
          <button key={s.key} type="button" disabled={props.busy}
                  className={`provider-tile${active ? " active" : ""}`}
                  style={active ? { ...style, borderColor: mark.color } : style}
                  onClick={() => props.onPick(s.key)}>
            <span className="provider-glyph">{mark.glyph}</span>
            <span className="provider-name">{s.name}</span>
            {/* The provider's own export route, which is the part a person
                actually needs and the part a dropdown had nowhere to put. */}
            <span className="provider-note">{s.how}</span>
            {active && <span className="provider-check">✓</span>}
          </button>
        );
      })}
    </div>
  );
}
