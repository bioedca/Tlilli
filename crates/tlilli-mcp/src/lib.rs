// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! Tlilli MCP server library: tools, resources, prompts, guardrails, transports and the auth token
//! (`docs/prd/21-architecture-and-tech-stack.md` §4). It is the only door for agents and stands
//! inside the trust boundary of the user's machine; it never calls `tlilli-core`'s storage
//! directly.
//!
//! The server itself arrives with `rmcp` in v0.2 (`docs/prd/11-fr-v0.2-red-ink.md`); today the
//! crate only reports its version.

#![forbid(unsafe_code)]

/// The version of `tlilli-mcp`, taken from the workspace manifest at compile time.
#[must_use]
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    use super::version;

    #[test]
    fn version_is_the_workspace_version() {
        assert_eq!(version(), env!("CARGO_PKG_VERSION"));
        assert_ne!(version(), "");
    }
}
