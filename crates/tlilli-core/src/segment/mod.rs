//! Segmentation and diff anchoring: rule-based sentence segmentation seeded by the style sheet's
//! abbreviation list, and span identity kept stable across edits by diff anchoring. Pure
//! functions, property-tested (`concat(spans) == paragraph`).
//!
//! Empty until v0.1 (`docs/prd/10-fr-v0.1-black-ink.md`).
