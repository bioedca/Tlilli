// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! Storage: the `SQLite` schema, forward-only numbered migrations with a pre-migration backup,
//! full-text search and the workspace file layout. The only module that touches the filesystem;
//! no other module reaches into its tables.
//!
//! Empty until v0.1 (`docs/prd/10-fr-v0.1-black-ink.md`).
