//! Event log: one enum of events. Every mutation is an event with an actor (`Author`,
//! `Agent { run_id, identity }` or `System`), a timestamp, a parent hash and a payload; the log
//! is append-only with a hash chain, and snapshots are materialized from it. The validator
//! rejects events whose actor may not create the object (`INV-01`).
//!
//! Empty until v0.1 (`docs/prd/10-fr-v0.1-black-ink.md`).
