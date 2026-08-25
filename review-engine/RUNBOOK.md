# Review Engine Runbook — Ryan Berner installation

Authoritative operating procedure for the daily review-request engine.
Companion files: `CONFIG.md` (settings), `TEMPLATES.md` (copy), `../review-state/ledger.md` (state).

Last revised 2026-08-21 after an August closing exposed three defects (see FAILURE MODES).

---

## 1. WHAT COUNTS AS A TRIGGER

A closing enters the engine **only** via an email Ryan sends to himself:

- Sender AND recipient are `ryan@westcompanies.com`
- Subject begins with `CLOSED:` (case-insensitive)
- Format: `CLOSED: <Full Name>, <email>` — phone optional, e.g.
  `CLOSED: Jane Smith, jane@example.com, 406-555-0134`

Nothing else is a trigger. Specifically **NOT** triggers:

- Title company mail (Fidelity National Title / `*@fnf.com`), including
  "RECORDED", "Closed Order Updated", "Closing Scheduled", "Settlement Statement"
- Lender mail (`*@zillowhomeloans.com`), including "loan is funded", "Clear to Close"
- E-signature mail (`*@authentisign.com`), MLS/Zillow marketing, CRM digests
- Any review-request email the engine itself previously sent
- Any `REVIEW-STATE-DELTA` email

**Why this is strict.** Third-party closing mail names every party to the transaction,
not just Ryan's client. A Fidelity subject line reads
`Ref 1: <buyer> Ref 2: <seller>, <co-seller>` — parsing a client out of it can address
a review request to the opposing party, who was represented by another agent.
Ryan's own `CLOSED:` email is the only source that unambiguously identifies *his* client.

If a closing is observed in third-party mail with no matching `CLOSED:` trigger,
**do not send**. Surface it in the wrap-up as an unclaimed closing and let Ryan decide.

## 2. ROUTING

Determined once, at day 0, and frozen for the life of the entry.

- If the word `zillow` (case-insensitive) appears in the subject or body **of Ryan's
  `CLOSED:` trigger email**, destination = `zillow`, link = `REVIEW_LINK_ZILLOW`.
- Otherwise destination = `google`, link = `GOOGLE_REVIEW_LINK`. Google is the default.

**Never** scan third-party mail for the `zillow` keyword. Many of Ryan's buyers finance
through Zillow Home Loans; their transaction mail is saturated with the word "zillow"
and will false-positive every one of them into Zillow routing.

Destination is a single value: `google` or `zillow`. Never both. `google+zillow` is not
a legal value. The Day-3 nudge reuses the exact link recorded at day 0.

## 3. LEDGER

`review-state/ledger.md`, one line per client, pipe-separated:

```
<sha256 of lowercased client email> | <day0> | <nudge> | <status> | <destination>
```

- `day0` — ISO date the day-0 email was sent, or `dry` if sent in dry mode
- `nudge` — ISO date the nudge was sent, or `-`
- `status` — `open` | `complete` | `responded`
- `destination` — `google` | `zillow`

**PRIVACY (absolute).** This repo is public. Never write a name, email address, or phone
number into the ledger or into a delta email. Hashes only. Compute with
`printf '%s' "$(echo "$email" | tr 'A-Z' 'a-z')" | sha256sum` — no trailing newline.

A client already present in the ledger is never re-added and never re-sent.

## 4. MERGE (run this before acting)

The repo copy of the ledger can be up to a week stale — rows only reach git on thoth's
Sunday push. Before any decision:

1. Search Gmail for `subject:REVIEW-STATE-DELTA newer_than:14d`
2. Parse the rows out of those bodies
3. Merge over the repo ledger **in memory**, per row, by hash:
   - a real date beats `dry`
   - a set nudge date never reverts to `-`
   - status is monotonic: `open` < `complete` < `responded`
   - destination is frozen at day 0 and never changes
4. Treat the merged result as the ledger for this run

This is what stops a client who closed Tuesday from being emailed again Thursday.

## 5. SEND — DAY 0

For each new closing not already in the merged ledger:

- Template: DAY 0 EMAIL from `TEMPLATES.md`, verbatim
- Substitute `{FIRST_NAME}`, `{SIGNATURE_LINE}`, and `{GOOGLE_REVIEW_LINK}` with the
  single routed link from §2
- Send via Zapier: `execute_zapier_write_action`, `selected_api` `GoogleMailV2CLIAPI`,
  action `message`, `tool_name` `gmail_send_email`, `body_type` `plain`,
  from and reply-to `ryan@westcompanies.com`
- Record the row with today's date, nudge `-`, status `open`, destination as routed

The templates are the ceiling of pushiness. Do not add links, do not add urgency, do not
offer a second destination, do not editorialize. One ask, one link.

## 6. SEND — DAY 3 NUDGE

For each ledger row where day0 is `NUDGE_DAY` or more days ago, nudge is `-`, and status
is `open`:

1. Check whether the client already responded, in this order:
   - a reply from the client's address newer than day0 → status `responded`, skip
   - a Google Business Profile notification (`businessprofile-noreply@google.com`)
     naming the client, newer than day0 → status `responded`, skip
   - a Zillow review notification naming the client → status `responded`, skip
2. Otherwise send the DAY 3 NUDGE template using the **same link recorded at day 0**
3. Record the nudge date; status becomes `complete`

Nudging someone who has already reviewed is the worst failure this engine can produce.
Check all three signals, not just the email reply.

## 7. SMS

Skipped entirely while `SMS_ENABLED: false` in `CONFIG.md` (pending A2P carrier approval).
When enabled: send the SMS template from `TEMPLATES.md` via the Vapi office line at day 0
only, never as the nudge, and only to a phone number parsed from Ryan's `CLOSED:` email.

## 8. DRY MODE

If `DRY_MODE: true` **or** `GOOGLE_REVIEW_LINK` is `PLACEHOLDER_NOT_SET`: send nothing to
clients. Still compute what would have been sent and record rows with day0 = `dry`.
Emit the delta as normal, then stop.

## 9. WRAP-UP — STATE DELTA

**Do not run `git add` / `commit` / `push`.** Cloud pushes to this repo were retired
2026-08-10 and are refused by the proxy. The weekly reconcile on thoth is the only writer.

For every row created or changed this run, send ONE self-addressed email
(from and to `ryan@westcompanies.com`, `body_type` `plain`):

```
Subject: REVIEW-STATE-DELTA <ISO8601 UTC timestamp>
Body: ledger.md <sha256> | <day0> | <nudge> | <status> | <destination>
```

One line per changed row. Hashes only — no names, emails, or phone numbers in the
subject or body. If no rows changed, send nothing (quiet no-op).

Then report: N new requests (google/zillow split), N nudges, N responded, delta emailed
yes/no, dry mode yes/no. Any send or delta failure is reported plainly, led with
`REVIEW ENGINE ISSUE:`.

## 10. FAILURE MODES SEEN IN PRODUCTION

**2026-08-20 — third-party mail treated as a trigger.** The run sent a day-0 request off
title-company "RECORDED" / "Closed Order Updated" mail; no `CLOSED:` trigger existed. It
resolved to the correct client by luck of that transaction's shape. The same path on a
listing-side file would have addressed the request to the opposing party. Fixed by §1.

**2026-08-20 — false-positive Zillow routing.** The same run recorded destination
`google+zillow` and sent a day-0 email containing both links plus an off-template line
("Either one is a gift — whichever is easier for you"). Root cause: the word "zillow"
was matched in transaction mail from Zillow Home Loans, the buyer's lender, rather than
in a `CLOSED:` trigger. Fixed by §2.

**2026-08-21 — review landed but ledger said `open`.** The client left a 5-star Google
review 20 minutes after the day-0 email. The engine's response check looked only for an
email reply, so the row stayed `open` and a nudge was queued for two days later — a
"please review me" to someone who had already reviewed. Caught and corrected manually.
Fixed by §6.

**Standing gap — unclaimed closings.** Because the ledger held only one entry, any closing
that predates the engine, or that Ryan never sent a `CLOSED:` email for, received no
request at all. Surface these in the wrap-up rather than acting on them.
