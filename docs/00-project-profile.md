# Project Profile — Rosa Nails & Spa / Website chatbot
Last updated: 2026-11-26 · Version: 2 (DRAFT, waiting for owner approval of the design)

Change from v1: launch moved to **2026-11-27**. Scope cut to the smallest safe version.

## In one paragraph (plain language)
A small chat window on the Rosa Nails & Spa website. It answers questions about
services, prices, opening hours, address and a short FAQ, in English or Dutch.
When a customer wants an appointment, the bot collects service, wished date/time
and name, then shows a "Book via WhatsApp" button with a ready-written message.
Rosa confirms herself. The bot never books, never takes payment, never gives advice
on allergies, skin, pregnancy or medication (fixed reply: ask Rosa on WhatsApp),
and when unsure it sends the customer to WhatsApp instead of guessing.

## Key numbers
| Item | Value | Source |
|---|---|---|
| Chat volume | < 300 conversations/month | ASSUMED |
| Peak concurrent users | < 5 | ASSUMED |
| Monthly run budget | Hard limit €20 for the chatbot | client |
| Launch date | 2026-11-27 (Preview first; no merge to main until the owner says so) | client |
| Acceptable downtime | Hours (phone and WhatsApp still work) | ASSUMED |
| Data stored | None. Conversations are not saved | client |

## Classification
- Product type: AI chatbot (FAQ + hand-off to WhatsApp) on an existing website
- Scale tier: **S** · Budget band: **B1** (< €20/month)
- Risk level: **Low-Medium**. Customers may type health details; the bot must not store them, comment on them, or advise.

## Scope v1 (27/11)
| In | Moves to v1.1 | Out of scope |
|---|---|---|
| Widget, English + Dutch | Aftercare answers | In-chat booking |
| Prices and services read live from Neon with a separate READ-ONLY DB user | Spanish | WhatsApp API, Instagram, Messenger |
| Opening hours, address | Saving conversations | Payments |
| 5–10 FAQ answers, drafted for Rosa's approval tonight (`docs/faq-draft.md`, approved 2026-11-26) | Full ADRs and full threat model (v1 has a one-page version) | |
| "Book via WhatsApp" button (wa.me, prefilled message) | | |
| Allergy / skin / pregnancy / medication → fixed reply pointing to WhatsApp | | |
| Unsure or error → WhatsApp, never a guess | | |
| Privacy line in the widget | | |
| Hard spend limit €20, simple rate limit, kill switch env variable | | |
| 20–30 test conversations: prices 100% correct, health questions 100% to WhatsApp | | |

## Stack
| Layer | Choice | Est. monthly cost |
|---|---|---|
| Widget | React component in `front_end` | €0 |
| API | New `POST /api/chat` in the existing FastAPI on Vercel | €0 |
| Data | `services` table via a read-only Postgres role in Neon; hours/address from backend config | €0 |
| LLM | Small Claude model (Haiku class), via Anthropic API | estimated a few euros, verify with real token usage in testing |
| Storage of chats | none | €0 |

## Standards applied at this tier
ON: HTTPS, secrets only in Vercel env vars, input limits, rate limit, spend cap, kill switch, no message content in logs,
tests on price and health cases, short design + threat model page, privacy line.
DEFERRED (turn on when): full ADRs (v1.1), staging env (chat volume > 1k/month), shared rate-limit store (when abuse seen).

## Risks accepted
- Rate limit on serverless is best-effort (per instance). The real protection against cost is the provider spend limit.
- Changing an env variable on Vercel needs a redeploy to take effect, so the kill switch takes about a minute, not an instant.
- Opening hours and address exist in several places. v1 adds one more copy for the bot, guarded by a test that compares it to the website.

## Open questions
- **DECISION OPEN before merging to main: Vercel plan.** The Hobby plan does not allow commercial use, and this is a business website. Choose Pro (or another host) before the chatbot goes to production. Preview testing is fine meanwhile.
- Who creates the Anthropic API key (with a €20 monthly spend limit) and the Neon read-only role? Steps are in the design.
- Bot tone (ASSUMED: friendly, little emoji).
