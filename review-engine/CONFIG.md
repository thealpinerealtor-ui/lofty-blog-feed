# Review Engine Config — Ryan Berner installation

GOOGLE_REVIEW_LINK: https://g.page/r/CQP9LqVF1Q7BEAE/review
# ^ Ryan's Google Business Profile "write a review" short link. LIVE — engine is out of DRY MODE.

REVIEW_LINK_ZILLOW: https://www.zillow.com/reviews/write?s=X1-ZUrpeex33ntrt5_6wmna
# ^ CONFIRMED live — verified landing on Ryan's "Write a Review" form (his photo, "recommend Ryan?").
#   Routed only when the CLOSED email for a client carries the "zillow" tag. Google is default for everyone else.

DRY_MODE: false
# ^ GOOGLE_REVIEW_LINK is set, so the engine now sends for real. Set to true to pause all sending.

ROUTING:
#   - If the CLOSED trigger email contains the word "zillow" (case-insensitive) anywhere in the body,
#     send that client to REVIEW_LINK_ZILLOW.
#   - Otherwise send to GOOGLE_REVIEW_LINK (default / primary).
#   - One request + one Day-3 nudge per client, ever. Hashed-ledger idempotency still applies.

SENDER: ryan@westcompanies.com
SIGNATURE_NAME: Ryan Berner
SIGNATURE_LINE: West and Company | Brokered by eXp Realty · Kalispell & Whitefish, MT
NUDGE_DAY: 3
SMS_ENABLED: false
# ^ Flip to true at A2P approval. SMS template in TEMPLATES.md.
