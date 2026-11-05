//! The `tlilli` command (`docs/prd/21-architecture-and-tech-stack.md` §2, ADR-0001): `export
//! --canonical`, `import`, `skills install`, `mcp` (proxy to the server), `doctor` and the
//! generators of the reference pages.
//!
//! Phase 0 ships `--version` and the four generators that `PR-DOC-003` names, with skeleton
//! outputs until the surfaces they document exist (bootstrap task 29): `mcp schema --markdown`,
//! `schema dump`, `--help-markdown` and `skills build --docs`. `scripts/gen_reference.sh` runs them
//! into `docs/reference/`. Exit codes
//! follow `FR-01-050`: 0 success, 1 user error (every failure the generators can report so far).

#![forbid(unsafe_code)]

mod reference;

use std::io::Write as _;
use std::path::PathBuf;
use std::process::ExitCode;

use clap::{CommandFactory, Parser, Subcommand};

/// Tlilli command-line tool.
#[derive(Parser)]
#[command(
    name = "tlilli",
    version,
    about,
    arg_required_else_help = true,
    args_conflicts_with_subcommands = true
)]
struct Cli {
    /// Print the command reference as Markdown (docs/reference/cli.md) and exit.
    #[arg(long)]
    help_markdown: bool,

    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// Describe the MCP server's protocol surface.
    #[command(subcommand)]
    Mcp(McpCommand),
    /// Generate the committed JSON Schemas.
    #[command(subcommand)]
    Schema(SchemaCommand),
    /// Build the skill pack from its sources.
    #[command(subcommand)]
    Skills(SkillsCommand),
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

#[derive(Subcommand)]
enum SkillsCommand {
    /// Build the skill reference page; the per-client packages follow in v0.2.
    Build {
        /// File to write the skill reference into (docs/reference/skills.md in the repository).
        #[arg(long, value_name = "FILE")]
        docs: PathBuf,
        /// Directory that holds the skill sources.
        #[arg(long, value_name = "DIR", default_value = "skills")]
        source: PathBuf,
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
        Some(Command::Mcp(McpCommand::Schema { markdown })) => {
            reference::write_mcp_pages(&markdown)
        }
        Some(Command::Schema(SchemaCommand::Dump { dir })) => reference::write_schemas(&dir),
        Some(Command::Skills(SkillsCommand::Build { docs, source })) => {
            reference::write_skills_page(&source, &docs)
        }
        // `args_conflicts_with_subcommands` keeps `--help-markdown` and a command apart.
        None if cli.help_markdown => std::io::stdout()
            .write_all(reference::help_markdown(Cli::command()).as_bytes())
            .map_err(|error| format!("standard output: {error}")),
        // clap refuses an empty command line first (`arg_required_else_help`).
        None => Err("no command given; run `tlilli --help`".to_owned()),
    };
    match result {
        Ok(()) => ExitCode::SUCCESS,
        Err(failure) => {
            eprintln!("tlilli: {failure}");
            ExitCode::from(1)
        }
    }
}
