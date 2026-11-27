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

## My automaton or bug was not added

- Set a **project** first: "list projects", or "set project *name*".
- Only the matching words send it: "confirm automation" or "confirm bug".
- "datawatch's bug intake is turned off": turn it on for that project in datawatch.
- "datawatch gives no folder for project": add the folder to the project in datawatch.
- "datawatch did not accept it": datawatch refused the request. Check its log.
- "I don't know whether it was sent": **look in datawatch before saying it again.**
- "datawatch refused access": if you use a token, it must be allowed to write.

## "Sending to a session is not turned on yet."

This is on purpose. It is waiting for datawatch's access controls.

## A new automaton shows as "untitled"

You were told it was added but could not be named. Name it in datawatch. Do not add it
again.

## The counts are smaller than I expect

You may have a **focus** set. Say "where am I", and "unset" to clear it. The focus is shared
by your voice devices and your AI assistant, and stays until you clear it.

## Some questions are missing

With a plan, automation, automaton, task or session focused, "questions" reads only the
ones datawatch links to it. A question that names no automaton does not show under a plan,
an automation or an automaton. Say "all questions", or "unset".

## Something is called "untitled"

datawatch gave no title for it. In a long list from a plan, only the first 20 missing titles
are looked up.

## "I couldn't find ... among the automata"

Finding by name searches only automata that need attention, are running, are on hold or
are among the 50 most recently updated completed ones.

## It will not tell me what a session said

This is on purpose. datawatch returns raw terminal text there, which can hold secrets. Open
the session in datawatch.

## The sensors are unavailable

datawatch could not be read: check it is running and reachable from Home Assistant, and see
the Home Assistant log. They never show zero for a failed read. The counts update once a
minute, and the dashboard data every 5 minutes.

## A dashboard data sensor is missing, unknown or has no history

- **Missing:** they start disabled. See
  [Data for your own cards](../README.md#data-for-your-own-cards-optional).
- **Unknown:** datawatch does not give that number now, or only as old: stale usage, a
  forecast more than a day old, or a lane it reports nothing for. This is on purpose.
- **No history:** history starts when you enable the sensor. The `data` attribute is never
  saved in history.

## The datawatch Gantt card is missing, empty or old

- **Not in "Add card":** reload the browser page (close and reopen the mobile app) after
  installing or updating, and after restarting Home Assistant. Home Assistant's **Safe
  mode** does not load it.
- **"... was not found":** enable the sensor **Dashboard data: live work**.
- **No task bars:** no task of running, blocked or planning work ran in the last 6 hours.
  A paused datawatch shows this.
- **"datawatch cannot be read right now.":** check datawatch is running, and the Home
  Assistant log.
- **The time looks old:** the card shows the time its data goes up to. It updates every 5
  minutes.

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
