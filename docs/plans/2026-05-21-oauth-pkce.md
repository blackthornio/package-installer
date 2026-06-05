# OAuth PKCE for the Salesforce user-login flow

**Date:** 2026-05-21
**Branch:** `feature/oauth-pkce`
**PR:** [#19](https://github.com/blackthornio/package-installer/pull/19)
**Status:** Implementation merged-ready, awaiting CI + manual sandbox verification

## Goal

Add Proof Key for Code Exchange (PKCE, RFC 7636) S256 to the Salesforce OAuth flow that users go through when logging in to the package installer.

## Scope

User-login flow only (`sfdo_template_helpers.oauth2.salesforce` via django-allauth). Scratch-org `AuthCode` redemption, the Dev Hub JWT path, and refresh-token grants are out of scope: none of them are browser-mediated authorization-code flows, so PKCE has nothing to protect.

## Where the connected app credentials live

The Salesforce connected app's consumer key/secret and callback URL are read from env vars in `config/settings/base.py:311-334`:

- `SFDX_CLIENT_ID` / `SFDX_CLIENT_SECRET` (legacy aliases `CONNECTED_APP_CLIENT_ID/SECRET`).
- `SFDX_CLIENT_CALLBACK_URL`.

Required at startup (`ImproperlyConfigured` if missing). Wired into `SOCIALACCOUNT_PROVIDERS["salesforce"]["APP"]`, into a CumulusCI `ServiceConfig` in `metadeploy/api/jobs.py`, and into `metadeploy/api/salesforce.py`. Per-env values come from `.env` locally, env vars in `docker-compose.yml` / `Procfile` / `Dockerfile`, `app.json` for Heroku, and GitHub Actions secrets for CI.

No new env vars introduced by this work; PKCE is purely additive on the wire.

## Decision

Upgrade `django-allauth` 0.51.0 → 0.52.0 and flip the per-provider PKCE flag. allauth 0.52 added the full PKCE plumbing:

- `OAuth2Client.get_access_token(code, pkce_code_verifier=None)`.
- `OAuth2LoginView.login` auto-generates the challenge and stashes the verifier in `session["pkce_code_verifier"]`.
- `OAuth2Adapter.get_access_token_data` auto-pops the verifier and forwards it.
- Opt-in via `SOCIALACCOUNT_PROVIDERS["<provider>"]["OAUTH_PKCE_ENABLED"] = True`.

Net cost in this repo: a settings flag, an allauth pin bump, and one unit test. No subclasses, no fork, no monkey-patching.

## Compatibility audit (justifies the 0.51 → 0.52 bump)

- **Django pin** (`django==3.2.14`) is supported by allauth 0.52 (range 2.0–4.1). ✓
- **`sfdo-template-helpers v0.20.0`** does not pin allauth (declares it only as an extras dep, unbounded). ✓
- **`socialaccount_state` session shape** — read directly by `sfdo_template_helpers`' `complete_login` as `session["socialaccount_state"][1]` — is byte-identical between 0.51 and 0.52. The PKCE verifier lives in a different session key (`pkce_code_verifier`), no collision. ✓
- **Transitive deps**: 0.51 → 0.52 `install_requires` is identical. No cascading lockfile churn. ✓
- **0.52 changelog**: PKCE flag (additive), Django 4.1 support, three new providers (irrelevant), `ACCOUNT_PREVENT_ENUMERATION` extension (gated by a setting we don't enable; we have `ACCOUNT_EMAIL_VERIFICATION = "none"`), Google/Pinterest URL fixes (irrelevant). No removals, no deprecations. ✓

## Backward compatibility

Two switches that compose orthogonally:

| | Client sends PKCE | Client doesn't |
|---|---|---|
| **Connected app requires PKCE** | works | rejected by Salesforce |
| **Connected app doesn't require** | works (Salesforce validates if provided) | works (legacy path) |

Enabling `OAUTH_PKCE_ENABLED` while the connected-app toggle is off lands us in the top-left cell — the goal. **No connected-app changes shipped in this PR.**

### Rollout safety

- Login that started before deploy, completes after: `/authorize` had no challenge, session has no verifier, allauth sends no `code_verifier` on `/token`, Salesforce (toggle off) accepts. Login completes. ✓
- Login started after deploy: PKCE on both sides. ✓

No stuck-mid-flow scenario.

## Verification

- [x] New unit test asserting `code_challenge` + `code_challenge_method=S256` on the `/authorize` redirect, and that the verifier lands in `session["pkce_code_verifier"]`.
- [ ] CI green on PR #19 (`yarn test:py` + frontend lint).
- [ ] Manual: log in to a sandbox via the running dev container; confirm a clean end-to-end login.

## Follow-ups (separate tickets)

1. Flip "Require Proof Key for Code Exchange" on the Salesforce connected app once PKCE has been live in prod for a release cycle.
2. Consider whether to drop `client_secret` once PKCE is required. Current decision: keep it (confidential client + PKCE for defense in depth).
