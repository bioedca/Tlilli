// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! The Tlilli desktop app (`tlilli-app`): the Tauri 2 shell around the web UI in `ui/`
//! (`docs/prd/21-architecture-and-tech-stack.md` §1). It owns the window, the menus, the file
//! dialogs and the updater; the document lives in `tlilli-core`, and the UI reaches it only
//! through commands that return events (`INV-02`).
//!
//! Phase 0 opens one window and registers the updater plugin, nothing else. Checking for updates
//! is the author's choice: nothing here checks on launch (`PR-REL-031`).
//!
//! `unsafe` is forbidden like in every other crate. `PR-ARCH-005` would allow it here behind a
//! `// SAFETY:` comment; a change that needs it relaxes this attribute in the same pull request.

// Release builds on Windows start without a console window; debug builds keep it for logs.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
#![forbid(unsafe_code)]

fn main() -> tauri::Result<()> {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .run(tauri::generate_context!())
}
