// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! Reads `tauri.conf.json` and `capabilities/`, generates the permission schemas under
//! `gen/schemas/` (not committed) and embeds the Windows resources.

#![forbid(unsafe_code)]

fn main() {
    tauri_build::build();
}
