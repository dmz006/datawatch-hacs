# Security

## Reporting a problem

Please do not describe a security problem in a public issue. If this repository's
**Security** tab offers **Report a vulnerability**, use that: it is private. If it does not,
open an issue that only asks for a private way to get in touch, with no details.

In any report, leave out real addresses, tokens and project names.

## Supported versions

Only the newest release, on Home Assistant 2026.11 or later.

## How the integration protects your datawatch

- It only reads: it sends nothing but `GET` requests.
- It accepts only the certificate you approved, and sends nothing before you approve it.
- It does not follow redirects, so a token is not forwarded elsewhere.
- A saved token is never sent to a different address.

## What it does not protect against

- **It does not know who is speaking.** Anyone who can use your voice devices can hear
  datawatch counts and project names.
- The token is stored with Home Assistant's other integration settings. Protect your Home
  Assistant and its backups.
- It cannot tell whether the certificate you approve is the right one. Compare the
  fingerprint with the file on your own server.
