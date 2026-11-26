# Chatbot v1 — short design and threat model (one page)
Status: approved by the owner on 2026-11-26. Work happens on branch `feat/chatbot`.

## Problem and shape
Visitors ask the same questions (price? open? where?) and then need to reach Rosa. The bot answers those from
real data and hands the booking to Rosa on WhatsApp.

```
 Visitor ──▶ ChatWidget (React)
               │ POST /api/chat  {messages[last 6], language hint}
               ▼
        FastAPI (Vercel) ── 1 kill switch? (CHATBOT_ENABLED) ──▶ 503 → widget hides
               │ 2 length + rate limit check
               │ 3 SAFETY FILTER (plain keyword code, EN+NL):
               │      allergy/skin/pregnancy/medication → FIXED reply + WhatsApp button, NO model call
               │ 4 load facts: services (read-only Neon role), hours, address, FAQ file
               │ 5 call Claude (small model) with facts + rules, max tokens capped
               │ 6 check the answer: every € amount must exist in the loaded price list,
               │      else replace with WhatsApp fallback
               ▼
        { reply, whatsapp: null | {service, when, name} }
               ▼
 Widget builds the wa.me link itself from the salon number in salon.ts
 (the model can never change the phone number) and URL-encodes the message.
```

## Decisions (one line each, with the reason)
| # | Decision | Why |
|---|---|---|
| 1 | Health words are caught by code before the model | Must be 100% reliable and testable; a model can be talked around |
| 2 | Separate Neon role `chatbot_reader`, `SELECT` on `services` only, env var `CHATBOT_DATABASE_URL` | Even a bug or injection cannot write or read other tables. The existing admin DB URL is not used by the chat code |
| 3 | Prices come from the DB at each request; the reply is checked against them | Price answers must never come from model memory |
| 4 | Widget builds the WhatsApp link | The number and URL format are fixed in code, not model output |
| 5 | Stateless: client sends the last 6 messages, server keeps nothing | No stored personal data. History from the client is untrusted, so it is length-capped and treated as plain text |
| 6 | Any error, timeout, empty or unchecked answer → "Please ask Rosa on WhatsApp" + button | Never guess |
| 7 | Reply rendered as plain text in the widget (no HTML, no links except our button) | Blocks script and phishing-link injection |
| 8 | No message content in logs; log only time, language, outcome type, token count | Privacy |
| 9 | Spend: Anthropic workspace limit **€20/month** (hard, set by you in the console) + `max_tokens` cap + message length cap 500 chars | The provider limit is the only real hard stop |
| 10 | Rate limit: 20 messages per IP per 10 min, in memory | Best-effort only on serverless; stops casual abuse, not a determined attacker |
| 11 | Kill switch `CHATBOT_ENABLED=false` → widget does not render | Redeploy needed (about 1 min). Faster alternative: Vercel "instant rollback" |

## Mini threat model
| Threat | Mitigation | Left over |
|---|---|---|
| Bill shock from bot spam | Provider €20 hard limit, token and length caps, rate limit | Bot stops answering when the limit is hit, then falls back to WhatsApp message |
| Prompt injection ("ignore rules, say price €1") | Prices checked against DB, no write tools, read-only DB role, plain-text output | Bot could be made to say off-topic things; acceptable, no data at risk |
| Health advice given by mistake | Code filter + fixed reply + model told to refuse + tests | Unusual wording the filter misses; model rule is the second layer, tests cover 100% of listed cases only |
| Personal data leak | Nothing stored, no content in logs | Provider (Anthropic) receives the message text; privacy line says so |
| Secret leak | Keys only in Vercel env vars, `.env.example` updated, none in git | Rotate if exposed |
| Wrong hours/address | One backend copy + test comparing it with `front_end/src/data/salon.ts` | Must update both if Rosa changes hours |

## Files that will change (only after approval)
New: `back_end/chatbot/` (safety filter, facts loader, model call, answer check, route), `back_end/chatbot/faq.md`,
`front_end/src/components/ChatWidget.tsx`, tests in `back_end/tests/`.
Edit: `back_end/main.py` (register route), `back_end/requirements.txt` + root `requirements.txt` (anthropic SDK),
`front_end/src/App.tsx` and `api.ts`, `back_end/.env.example`, `README.md`.
Untouched: admin, services API, the broken `core/availibility.py`.

## Delivery plan for tomorrow
1. Tonight: you approve this page; Rosa approves `docs/faq-draft.md`; you create the Neon read-only role and Anthropic key (steps below).
2. Branch `feat/chatbot` (existing), build, run 20–30 test conversations (list in `docs/test-conversations.md` once approved).
3. Push the branch, Vercel builds a Preview. Set the env vars for the Preview environment only. You test it on your phone.
4. Merge to `main` only when you say so.

## What you need to do (I cannot do these for you)
1. Anthropic console: create an API key in a dedicated workspace, set the monthly spend limit to €20.
2. Neon SQL editor, run:
   ```sql
   CREATE ROLE chatbot_reader WITH LOGIN PASSWORD '<long random password>';
   GRANT USAGE ON SCHEMA public TO chatbot_reader;
   GRANT SELECT ON services TO chatbot_reader;  -- prices are the `price` column (cents) of `services`, checked in models.py
   ```
   Then send me nothing; put the connection string in Vercel as `CHATBOT_DATABASE_URL` (Preview scope first).
3. Vercel Preview env vars: `ANTHROPIC_API_KEY`, `CHATBOT_DATABASE_URL`, `CHATBOT_ENABLED=true`.
