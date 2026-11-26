# Your AI assistant and datawatch

## Turn it on

**Settings → Devices & services → datawatch → Configure**, then choose an **AI assistant**.
Leave it empty to turn it off.

Your assistant stays yours: its instructions, personality and settings are **not edited**.
While this is on, Home Assistant adds datawatch's tools and a short introduction to what the
assistant already has, and removes them when you turn it off. Nothing needs pasting into its
instructions. If you added a datawatch paragraph for version 0.1, remove just that
paragraph: it says the assistant cannot read datawatch.

## What it needs

- **Device control** turned on in the assistant's own settings. That is how Home Assistant
  gives an assistant these tools, and every assistant with it gets them.
- **Enough context window.** See below.

## What it can do

| You might ask | It uses |
|---|---|
| "How is my datawatch work going?" | status |
| "What datawatch projects do I have?" | projects |
| "Any datawatch questions?" or "What do you think about this one?" | questions |
| "What needs my attention?", "How many plans do we have?", "What's next?", "What's on hold?" | work |
| "Why is the release job blocked?" | automaton |
| "Which sessions are waiting?", "What finished?", "What did that deliver?" | work, automaton |
| "What does 'held' mean in datawatch?" | documentation search and reading |

If you have a project focus, a work report covers that project unless you ask for all
projects.

It is never given what a session said: datawatch returns raw screen text, which can hold
secrets or misleading instructions.

It cannot change datawatch or answer a question. To answer, say "open datawatch", then
"questions". See the [README](../README.md#what-you-can-say).

If it asks you a follow-up question, your next reply goes straight to it without the wake
word, so let it finish before saying "open datawatch" with your wake word.

## Context window

A model can only take in so much text at once. datawatch adds an introduction and seven tool
descriptions to every request, and a tool's reply can be a few thousand characters: a whole
question, or a page of documentation (cut at 6,000 characters). Assistants with many exposed
devices already use much of the window. If it overflows, some models silently drop older
text, which can include your instructions.

For a local model, such as one served by Ollama, check the context window setting in that
assistant's settings, and give it more room if needed. More context uses more memory and can
make replies slower.

## Be careful

Questions are written by programs and could contain text meant to mislead a model. See
[Privacy and safety](../README.md#privacy-and-safety).
