# System Changelog — Lead Engine & Automations

Running log of configuration and behavior changes, kept for the eventual
technical installation sheet rewrite. System-level entries only — no lead
data (this repo is public).

## 2026-07-27

- **Zapier MCP permissions set to "always allow"** in the Claude app, so
  hourly Lead engine runs no longer stall waiting for tool approvals.
- **Deleted redundant scheduled task** "Auto-respond to new leads
  (email + Anna call)" (hourly at :23, created 2026-07-27). It duplicated
  the Lead engine's jobs (Gmail lead scan, auto-reply, Anna calls) without
  using the shared lead-state dedupe ledger. The Lead engine (hourly at :12)
  is now the single system of record. The realtor.com instant-call Zap in
  Zapier is separate and untouched.
- **Lofty connection quirk found:** the Zapier Lofty integration has two
  connections and no default; runs must pass connection_id 65230325
  explicitly or every Lofty action errors.

## Known bugs / open items

- Lofty "Create Lead" returns "Lead already existed" for known contacts and
  does NOT attach the note — outbound call outcomes currently surface only
  in the run report, not in the CRM timeline. Needs Update Lead flow or
  Lofty API note endpoint.
- Lofty "Find Record" only searches by Lead/Transaction ID — no phone or
  email lookup, so leads known only by phone number can't be safely updated
  without risking a duplicate record.
- Vapi outbound calls placed near the 8 PM MT cutoff: outcome processing
  lands in the next hourly run by design; confirm this is acceptable.
