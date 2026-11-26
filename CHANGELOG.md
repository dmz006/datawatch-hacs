# Changelog

## 0.1.1 (2026-11-26)

- Opening datawatch mode now says "Datawatch activated."
- Datawatch mode closes after three phrases in a row that it does not understand, so a
  television or other talk cannot hold it open.

## 0.1.0 (2026-11-26)

The first release: ask datawatch how your work is going, by voice. It only reads.

- Say "open datawatch", "use datawatch" or "datawatch" to a voice device, then give short
  commands without the wake word.
- Commands for status, more detail, listing projects, setting and clearing a focus, where
  you are, repeat, help and closing.
- One focus shared by all voice devices, kept until you clear it.
- Asks "Still there?" once, then closes, if it hears nothing. Faults are said out loud.
- Setup screens for the server address, an optional token, and approving the server's
  certificate. Reconfigure to change them.
- A repair warning if the entry phrase cannot be registered.
- Requires Home Assistant 2026.11 or later.

Not yet tried with a real microphone and speaker. Questions, items on hold, and failed or
blocked automata are reported across all projects even with a focus.
