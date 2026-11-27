# Security

## Reporting a problem

Please report security problems privately through
[GitHub's private vulnerability reporting](https://github.com/dmz006/datawatch-hacs/security/advisories/new),
not in a public issue. Leave out real addresses, tokens and project names.

## Supported versions

Only the newest release, on Home Assistant 2026.11 or later.

## How the integration protects your datawatch

- It reads with `GET` requests. It can make these changes, each only after reading it back
  and hearing that kind's own confirming words: answer a question, add a draft automaton
  (then set its title), and report a bug. It never retries a change or asks to replace an
  answer.
- Sending input to a session is in the code but switched off, and is checked in two places.
- AI assistants get tools that only read. None can make a change.
- The dashboard cards are a script this integration serves to your Home Assistant pages. It
  loads nothing from elsewhere, and puts names and titles on the page only as plain text. The
  script's address needs no sign-in, like other Home Assistant card files; it contains no
  data.
- The cards ask for their data over Home Assistant's signed-in connection, with two
  read-only commands. **Any signed-in Home Assistant user can use them**, whether or not a
  card is on their dashboard, and so see project, automation, automaton and lane names.
  datawatch sends more than that (for example decisions and task records); only names,
  titles, states and times are passed on.
- Optional dashboard sensors, off by default, put datawatch's dashboard data (numbers,
  titles, lane and repository names, links) into an entity attribute that is not saved in
  history. datawatch's one free-text release note is removed. Anyone who can see the entity
  can read it. No tool of this integration gives it to an AI model.
- Session terminal output, last responses and prompts are never requested, so they are
  neither spoken nor given to an AI model. Session names, questions, reasons and titles are.
  datawatch sends the text of alerts together with their list; it can be terminal text, so
  it is dropped as the reply is read. Only alert titles are spoken or given to an AI model.
- It accepts only the certificate you approved, and sends nothing before you approve it.
- It does not follow redirects, so a token is not forwarded elsewhere.
- A saved token is never sent to a different address.
- The count sensors, which are on from the start, hold counts only, no titles or question
  text.

## What it does not protect against

- **It does not know who is speaking.** Anyone who can use your voice devices can hear
  datawatch questions, counts and project names, and can **answer questions, add draft
  automata and report bugs**. Confirming words guard against mistakes and mishearing, not
  against another person. Words you dictate are sent to datawatch as speech-to-text wrote
  them.
- **Misleading text and AI.** With an AI assistant on, questions and documentation reach
  your model. It is told to treat them as information only, which cannot be guaranteed. The
  assistant keeps whatever control of your home you gave it.
- The token is stored with Home Assistant's other integration settings. Protect your Home
  Assistant and its backups.
- It cannot tell whether the certificate you approve is the right one. Compare the
  fingerprint with the file on your own server.
