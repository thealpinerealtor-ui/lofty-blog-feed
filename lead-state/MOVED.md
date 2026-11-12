# MOVED — do not recreate

The lead engine's dedup and DNC state moved to a private repository on 2026-11-11 and is now
keyed with HMAC-SHA256. Any job that used to read lead-state/ here must STOP and must NOT
recreate these files empty: an empty dnc.txt would drop do-not-call suppression.
