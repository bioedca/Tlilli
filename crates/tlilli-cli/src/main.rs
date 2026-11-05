//! The `tlilli` command (`docs/prd/21-architecture-and-tech-stack.md` §2, ADR-0001): `export
//! --canonical`, `import`, `skills install`, `mcp` (proxy to the server), `doctor` and the
//! generators of the reference pages.
//!
//! Phase 0 ships `--version` and the generators that `PR-DOC-003` names, with skeleton outputs
//! until the surfaces they document exist (bootstrap task 29): `mcp schema --markdown` and
//! `schema dump` so far. `scripts/gen_reference.sh` runs them into `docs/reference/`. Exit codes
//! follow `FR-01-050`: 0 success, 1 user error (every failure the generators can report so far).

#![forbid(unsafe_code)]

mod reference;

use std::path::PathBuf;
use std::process::ExitCode;

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
    /// Describe the MCP server's protocol surface.
    #[command(subcommand)]
    Mcp(McpCommand),
    /// Generate the committed JSON Schemas.
    #[command(subcommand)]
    Schema(SchemaCommand),
}

#[derive(Subcommand)]
enum McpCommand {
    /// Write the MCP protocol reference: tools.md, resources.md and prompts.md.
    Schema {
        /// Directory to write the pages into (docs/reference/mcp in the repository).
        #[arg(long, value_name = "DIR")]
        markdown: PathBuf,
    },
}

#[derive(Subcommand)]
enum SchemaCommand {
    /// Write the JSON Schemas: canonical JSON and style sheet, tool inputs from v0.2.
    Dump {
        /// Directory to write the schemas into (docs/reference/schemas in the repository).
        #[arg(value_name = "DIR")]
        dir: PathBuf,
    },
}

/// Parses the command line, runs the command and maps the outcome to an exit code.
fn main() -> ExitCode {
    let cli = match Cli::try_parse() {
        Ok(cli) => cli,
        Err(error) => {
            // `--help` and `--version` succeed; every other parse error, including a missing
            // command, is a user error: exit 1, not clap's default 2.
            let _ = error.print();
            return ExitCode::from(u8::from(error.use_stderr()));
        }
    };
    let result = match cli.command {
        Command::Mcp(McpCommand::Schema { markdown }) => reference::write_mcp_pages(&markdown),
        Command::Schema(SchemaCommand::Dump { dir }) => reference::write_schemas(&dir),
    };
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(failure) => {
            eprintln!("tlilli: {failure}");
            ExitCode::from(1)
        }
    }
}
