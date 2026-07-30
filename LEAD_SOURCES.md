# Lead Sources — Ryan Berner (Alpine Autopilot)

Known sources that create leads in Lofty (the book of record). The hourly lead engine
(Jobs A–D) mirrors, dedupes, and reports these. Keep this list current so sources are
labeled correctly instead of guessed.

## searchflatheadhomes.com — team home-search website  (PRIMARY; documented 2026-07-30)
- **What:** A team-owned IDX / home-search website that captures buyer & seller registrations.
- **Flow:** visitor registers on searchflatheadhomes.com → pushed into Lofty via Zapier →
  Lofty stores the lead with **Source = "searchflatheadhomes.com"**. NOTE: because it enters
  through the Zapier connector, Lofty's "New Buyer Lead Alert" email may show the generic
  upstream label **"Source: Zapier"** — the *real* origin is on the lead's Source field in the
  CRM (searchflatheadhomes.com), not the email.
- **Lead type:** usually tagged **"Registration"** = account sign-up to browse listings. Real
  contact info + active searcher = good speed-to-lead candidate.
- **ACCESS (important):** Ryan does **NOT** have admin access to this site or its Zap — it is
  team/third-party owned. Any change to the site, its forms, or the Zap that feeds Lofty must
  go through the team/site owner. **Alpine cannot modify this source directly** (and should not
  assume it can). Diagnose from the Lofty record + Zap history only.
- **Example:** Rithwik Sankar (2026-07-29) — $1.2M buyer, Kalispell, Canadian (403) mobile.
  Auto-call correctly skipped by Job D (non-US number); manual first-touch email sent by Ryan.

## Other known sources
- **Realtor.com Speed To Lead (Zap):** referenced in the A2P cutover plan; confirm whether it is
  live and separate from the team site. (Was wrongly assumed to be Rithwik's source — it was not.)
- **Direct email inquiries** → Job A (inbox capture + one-time consultative auto-reply).
- **Portal notifications** (Zillow Premier Agent / Follow Up Boss) → Job B mirror, no auto-reply.
- **Anna inbound calls & texts** → Job C (Vapi call/chat processing).

## Rules for the lead engine
- Everything above lands in Lofty; the engine's job is capture-once + alert-once + speed-to-lead.
- **Speed-to-lead outbound (Job D) dials valid US numbers only** — non-US numbers (e.g. Canadian
  403) are skipped by design. Cross-border AI calling falls under different (CRTC) rules.
- When a NEW source appears with a Lofty "Source" value not listed here, add it to this file.
