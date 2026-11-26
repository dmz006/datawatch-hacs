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
[README](../README.md#what-you-can-say).

## It closes while I am still using it

It closes after two silences in a row, or after three phrases in a row that it does not
understand ("I didn't understand three times."). A command it understands starts that count
again. Say "help" to hear the commands.

## It stays open

Speech from a television or other people that happens to match a command counts as a
command. Say "close datawatch".

## It stops partway or never starts talking

Please [open an issue](https://github.com/dmz006/datawatch-hacs/issues). To get a log, turn
on **debug logging** from the integration's menu, try again, then turn it off and download
the log. **Read the log before sharing it** and remove addresses, names and anything else
private.
