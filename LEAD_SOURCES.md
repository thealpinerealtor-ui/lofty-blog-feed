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
- **Lead type:** usually tagged **"Registration"** = account sign-up to browse listings.
- **Handling: LONG-TERM NURTURE, not speed-to-lead.** Per Ryan (2026-07-30), registrations from
  this site are typically early-stage browsers, not ready-now buyers — do NOT fire the aggressive
  speed-to-lead first-touch on them. Route to nurture cadence; a warm personal touch is fine, but
  no urgent auto-dial / rapid auto-reply treatment. (Job D already skips them when non-US; this
  rule makes the nurture intent explicit for US registrations too.)
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

## Canadian leads (NW Montana gets real cross-border buyer volume)
Not legal advice — verify with broker compliance / telecom counsel before changing anything.
- **Live human calls by Ryan: OK.** Calling a Canadian buyer who registered/inquired is generally
  covered by CRTC's Existing Business Relationship exemption (6 months from an inquiry) and/or
  express consent, so it's exempt from most DNC restrictions. Observe CRTC calling hours
  (~9:00 AM–9:30 PM weekdays, 10:00 AM–6:00 PM weekends, local time) and honor opt-outs.
- **Automated / AI-voice (Anna) calls to Canada: DO NOT.** Canada treats prerecorded/AI calls as
  ADAD (automatic dialing-announcing devices); telemarketing ADAD calls are PROHIBITED without
  prior EXPRESS consent specifically to receive an automated call. A generic "contact me" opt-in
  does NOT cover it. Keep Job D skipping non-US numbers. Bright-line rule, not a soft gap.
- **Texts/emails to Canadians = CASL** (express or implied consent + working unsubscribe). A site
  registration opt-in typically covers nurture email/text; confirm the language before relying on it.
- **Process to call Canada as a business (if ever expanding beyond exempt follow-up):** register
  with Canada's National DNCL operator + pay annual subscription (area-code based) to scrub numbers,
  maintain a written DNC policy, identify caller on calls; automated calls additionally require
  documented express ADAD consent per contact. For agent follow-up on own registrations, the
  EBR/consent exemption usually makes full DNCL registration unnecessary — live calls only.

## OPEN FOLLOW-UPS
- [ ] Confirm the exact consent language captured by the searchflatheadhomes.com registration form
      (phone / automated-call / text consent?). Site is team-owned — ask the site owner. If it
      captures express phone+automated consent, Canadian auto-dial math may change; until then,
      Canadian = live-call only.
- [ ] Get broker compliance sign-off on the Canadian live-call + no-ADAD policy above before
      treating it as settled.
