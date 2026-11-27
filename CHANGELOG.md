# Changelog

## 0.7.0 (2026-11-26)

- **Focus on anything:** a plan, automation, automaton, task or session, not only a project.
  "set two", "set it" or "set plan *name*". "status", "more detail", "why", "tasks",
  "progress", "history" and "automata" then need no number.
- **Questions for an item:** with an item focused, "questions" reads only the ones datawatch
  links to it. "its questions" asks about the one you chose, and "all questions" reads all.
- **"Go back"** undoes your last step: the previous question or list, or out of what you
  went into.
- Plans and automations can now be chosen by number. Automation lines are numbered.
- Fixed: with a focus on a project, "set four" for a line not yet heard could say there was
  no list.
- Fixed: if datawatch left the title out of one record, a whole reply could fail with
  "I can't reach datawatch". Such a record is now called "untitled".

## 0.6.1 (2026-11-26)

- Fixed: asked what a session said, an AI assistant could give the session's name as if it
  were a message. Names are now labelled "session named ...", and the assistant is told it
  does not have anything a session said. This lowers the risk but cannot guarantee what an
  AI model says.

## 0.6.0 (2026-11-26)

- **Your own spoken reports.** On the datawatch page in Home Assistant choose "Add report",
  name it and pick what goes in it. In datawatch mode say its name, or "reports" to hear
  them. Your AI assistant, if turned on, can run them too.
- **Dashboard sensors:** counts of open questions, automata needing attention, sessions,
  stuck automata and held items, and whether new work is paused. Read once a minute.

## 0.5.0 (2026-11-26)

- **Sessions and finished work.** New in datawatch mode: "sessions", "waiting sessions",
  "running sessions", "failed sessions", "what finished" and "results". Your AI assistant,
  if turned on, can give the same facts.
- What a session said is deliberately not read: datawatch returns raw terminal text.

## 0.4.0 (2026-11-26)

- **Why is it stuck?** Say "what's running" or "what's on hold", pick a line by number from
  those or from "attention", or say "tell me about" and part of a title. Then "why", "tasks"
  or "progress". Your AI assistant, if turned on, can do the same.
- Fixed: when your project focus limited an AI assistant's report, it did not have to say
  so. Reports now name the project, and the assistant can ask for all projects.

## 0.3.0 (2026-11-26)

- **What needs you and what is next.** New in datawatch mode: "what needs my attention",
  "how many plans do we have", "overview", "what's next" and "automations", read three at a
  time. With a focus, plans, overview, what's next and automations cover that project.
- Your AI assistant, if turned on, can give the same reports.

## 0.2.0 (2026-11-26)

- **Questions by voice.** In datawatch mode say "questions" to hear datawatch's open questions
  one at a time, the supervisor's first and blocking ones first.
- **Answering.** Choose an option or say your own words. The answer is read back and is sent
  only when you say "confirm answer".
- **Your AI assistant** (off until you choose one in datawatch's options) can read datawatch
  status, projects, open questions and documentation, and in datawatch mode you can talk to
  it normally. Its own instructions are not changed. It cannot send answers.
- The README's overview diagram now displays in Home Assistant.
- Documentation: how to give the Whisper app a hint when it does not recognise "datawatch".

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
