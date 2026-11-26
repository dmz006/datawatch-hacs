# Changelog

## 0.1.0 (unreleased)

- Project foundation: integration metadata, tests, CI and a pre-publish leak check.
- Voice conversation core (not yet connected to Home Assistant or datawatch): fixed
  phrases, status, project list, focus by number or name, and silence handling.
- Read-only datawatch client with certificate pinning.
- Setup screens: server address, optional token, certificate approval and reconfigure.
- Requires Home Assistant 2026.11 or later.
- Datawatch mode on voice devices: entry phrases, conversation without the wake word,
  shared focus, spoken errors, and a repair warning if the phrase cannot be registered.
