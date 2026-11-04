//! Tlilli core: the document model, the event log, the ledger, the style sheet, provenance and
//! import/export. Both doors into a workspace, the desktop shell and the MCP server, go through
//! this crate and emit events; no state lives anywhere else (`INV-02`).
//!
//! The module boundaries follow `docs/prd/21-architecture-and-tech-stack.md` §4. The modules are
//! empty until the v0.1 features land; today the crate only reports its version.

#![forbid(unsafe_code)]

pub mod config;
pub mod event;
pub mod export;
pub mod import;
pub mod ledger;
pub mod model;
pub mod provenance;
pub mod segment;
pub mod storage;
pub mod style;

/// The version of `tlilli-core`, taken from the workspace manifest at compile time.
#[must_use]
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    use super::version;

    #[test]
    fn version_is_a_three_part_numeric_semver_core() {
        let parts: Vec<&str> = version().split('.').collect();
        assert_eq!(parts.len(), 3, "version was {}", version());
        assert!(
            parts
                .iter()
                .all(|part| !part.is_empty() && part.bytes().all(|byte| byte.is_ascii_digit())),
            "version was {}",
            version()
        );
    }
}
