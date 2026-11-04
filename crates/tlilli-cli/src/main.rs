//! The `tlilli` command (`docs/prd/21-architecture-and-tech-stack.md` §2): `export --canonical`,
//! `import`, `skills install`, `mcp` (proxy to the server), `doctor` and the schema generators.
//!
//! Phase 0 ships `--version` and the `schema` subcommand group as a placeholder; bootstrap task 29
//! fills the group with `schema dump` and `mcp schema --markdown`.

#![forbid(unsafe_code)]

use clap::{Parser, Subcommand};

/// Tlilli command-line tool.
#[derive(Parser)]
#[command(name = "tlilli", version, about)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Generate the committed schemas and protocol reference (placeholder until task 29).
    #[command(subcommand)]
    Schema(SchemaCommand),
}

#[derive(Subcommand)]
enum SchemaCommand {
    /// Dump the JSON Schemas of the MCP tool inputs (placeholder until task 29).
    Dump,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Command::Schema(SchemaCommand::Dump) => {
            eprintln!(
                "tlilli {}: `schema dump` is a placeholder; the generators arrive with bootstrap task 29",
                env!("CARGO_PKG_VERSION")
            );
        }
    }
}
