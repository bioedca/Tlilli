// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! Skeleton fuzz target: proves the libFuzzer harness builds and runs against `tlilli-core`.
//! The real targets (Markdown, docx and LaTeX importers, PDF text extraction, DOI sniffing, MCP
//! tool inputs, JSON-RPC framing; `docs/prd/34-testing.md` §1) replace this one, each with a seed
//! corpus under `corpus/<target>/` (`PR-TST-013`).

#![no_main]

use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // Until there is a parser to round-trip, the only public entry point is the version; it must
    // not depend on the input, so any divergence here is a harness bug.
    let version = tlilli_core::version();
    assert_ne!(version, "");
    assert_eq!(
        version,
        tlilli_core::version(),
        "input of {} bytes",
        data.len()
    );
});
