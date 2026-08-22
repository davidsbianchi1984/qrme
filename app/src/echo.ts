// Telling a person apart from the voices in the room.
//
// A room's ear now stands open — you walk in and it is listening, and
// four and a half seconds of your silence sends what you said. That is
// the right shape for a place people TALK in, and it puts an open
// microphone in a room where several synthetic profiles speak out loud
// through the same speaker.
//
// The failure that makes this file necessary was already reported once,
// in JIM's coach sphere: "it's listening at the same time, but it seems
// to be picking up its own voice and triggering itself and not letting
// it finish." One voice was enough to do it there. A room can have four.
//
//     asked     did somebody in the room say something
//     mattered  was it a person, or the speaker on the table
//
// Going deaf while the room speaks would be the easy fix and the wrong
// one: interrupting a profile mid-sentence is exactly the thing a voice
// room is for. So the question is not "is anything playing" but "are
// these the room's own words coming back".
//
// Ported from jim-mini's app/src/echo.ts rather than shared through a
// package, because these two consoles have no build relationship — and
// carried with its reasoning rather than just its constants, so the next
// person to touch a threshold can see what it is buying.
//
// No imports on purpose: the guard suite transpiles this one file and
// runs the real function, instead of pinning a regex to a rule it
// cannot execute.

function words(s: string): string[] {
  return s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/).filter(Boolean);
}

/** Fewer words than this is never called an echo, however well it
 *  matches: "yes", "no", "stop", "wait", "hang on" are exactly the
 *  interruptions worth having in a room, and somebody answering "yes"
 *  to a paragraph containing the word yes must not be mistaken for the
 *  speaker. */
export const SHORTEST_ECHO = 3;

/** How much of what was heard has to be made of what the room just
 *  said. Not 1.0: a transcriber mishears an occasional word, and an open
 *  microphone catches the room around the speaker too. */
export const ECHO_SHARE = 0.7;

/** How many recent turns count as "what the room just said".
 *
 *  More than one because a room reads a backlog: several profile turns
 *  can play back to back, and a microphone that only remembers the last
 *  one starts submitting the one before it. Not unbounded, because a
 *  long-running room would eventually own every common word and start
 *  swallowing the person. */
export const RECENT_TURNS = 4;

/** True when `heard` is the room's own voices coming back.
 *
 *  `said` is what the room has recently spoken, joined together — see
 *  RECENT_TURNS.
 *
 *  The cost of a wrong call is small and asymmetric, which is why the
 *  bar sits where it does: a missed echo puts the room's own words in
 *  somebody's mouth and answers them (the defect), while a false echo
 *  drops one short turn and keeps listening — which reads as "it didn't
 *  catch that", and saying it again fixes it. */
export function isEcho(heard: string, said: string): boolean {
  const mine = words(said);
  if (mine.length === 0) return false;
  const got = words(heard);
  if (got.length < SHORTEST_ECHO) return false;
  const bag = new Set(mine);
  const shared = got.filter((w) => bag.has(w)).length;
  return shared / got.length >= ECHO_SHARE;
}
