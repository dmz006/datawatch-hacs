# Troubleshooting

## "open datawatch" gets an answer from my usual assistant

- Check that datawatch is added under **Settings → Devices & services**.
- Check **Settings → System → Repairs** for "The datawatch voice phrase is not working".
- **Say your wake word first.** If your AI assistant has just asked you a follow-up
  question, your next reply goes straight to that assistant. Let it finish, then start
  again with the wake word.
- See what speech-to-text actually heard, using the debug view of your assistant under
  **Settings → Voice assistants**. The phrase must be the whole sentence: "open datawatch",
  "use datawatch" or "datawatch" ("data watch" as two words works too).
- Another automation using the same sentence can answer instead.
- If speech-to-text wrote something else in place of "datawatch", see the next section.

## Speech-to-text does not understand "datawatch"

"datawatch" is not an everyday word, so speech-to-text may write something like "did watch"
instead. The phrase then does not match, and your usual assistant gets it.

**Try "open datawatch"** rather than "datawatch" on its own. A longer phrase may be easier to
recognise.

**If you use the Whisper app, give it a hint:**

1. Open the **Whisper** app in Home Assistant and go to its **Configuration** tab.
2. Set **Initial prompt** to `datawatch`. It is an optional setting, so you may have to show
   the unused options first. If it already has text, add `datawatch` to it.
3. Save, then **restart Whisper**. Speech recognition stops while it restarts. Home Assistant
   itself does not need a restart.

Things to know:

- It is a hint, not voice training. It may not fix every mistake.
- It applies to **all** speech that this Whisper app transcribes, not only datawatch.
  Whisper might also write "datawatch" when you said something that sounds like it.
- To undo it, clear the setting and restart Whisper.

Other speech-to-text services have their own settings, or none for this.

## "This voice device can't hold a datawatch conversation."

The device cannot both announce and start a conversation in Home Assistant, which datawatch
mode needs.

## "Datawatch mode works from a voice device."

The phrase was typed, or sent without a voice device. This is intended.

## "I can't reach datawatch."

- Is datawatch running?
- Can **Home Assistant** (not just your computer) reach the address you entered? Check the
  port too.
- The Home Assistant log has the details.

## "The datawatch certificate has changed."

The server now shows a different certificate. Find out why before trusting it. If you
replaced it yourself, check the new fingerprint and approve it with **Reconfigure**.

## "datawatch refused access."

The token is missing or no longer valid. Update it with **Reconfigure**.

## It says "Sorry, I didn't get that."

Commands are fixed phrases. Say "help" to hear them, and see the list in the
[README](../README.md#what-you-can-say). To talk normally,
[turn on your AI assistant](assistant-context.md).

## My answer was not sent

- Only **"confirm answer"** sends it. "Yes" or "send it" do not.
- "That question was already answered or withdrawn" means someone else got there first, or
  datawatch withdrew it.
- "datawatch refused that answer because it looks like it holds a secret": datawatch does not
  store secrets in answers. Do not say passwords or keys.
- "I don't know whether the answer was sent": say "questions", or look in datawatch, before
  answering again.
- "datawatch refused access": if you use a token, it must be allowed to write.

## The counts are smaller than I expect

You may have a **focus** set. Say "where am I", and "unset" to clear it. The focus is shared
by your voice devices and your AI assistant, and stays until you clear it.

## "I couldn't find ... among the automata"

Finding by name searches only automata that need attention, are running, are on hold or
are among the 50 most recently updated completed ones.

## It will not tell me what a session said

This is on purpose. datawatch returns raw terminal text there, which can hold secrets. Open
the session in datawatch.

## The sensors are unavailable

datawatch could not be read: check it is running and reachable from Home Assistant, and see
the Home Assistant log. They never show zero for a failed read. They update once a minute.

## My report is not recognised

Say "reports" to hear the exact names. Speech-to-text has to write the name as you typed it,
so short, ordinary words work best.

## My assistant says it knows nothing about datawatch

- Choose an assistant under **datawatch → Configure**.
- Turn on **device control** in that assistant's own settings.
- If you added a datawatch paragraph for version 0.1 to its instructions, remove just that
  paragraph.

## My assistant forgets its instructions or gets muddled

Its context window may be too small for the added text. See
[Context window](assistant-context.md#context-window).

## "Your assistant didn't answer."

Check that your AI assistant works in normal use. The Home Assistant log has the details.

## It closes while I am still using it

It closes after two silences in a row, or after three phrases in a row that it does not
understand ("I didn't understand three times."). A command it understands starts that count
again. Say "help" to hear the commands.

## It stays open

Speech from a television or other people that happens to match a command counts as a
command. With an AI assistant turned on, other talk goes to the assistant and does not count
towards closing. Say "close datawatch".

## It stops partway or never starts talking

Please [open an issue](https://github.com/dmz006/datawatch-hacs/issues). To get a log, turn
on **debug logging** from the integration's menu, try again, then turn it off and download
the log. **Read the log before sharing it** and remove addresses, names and anything else
private.
