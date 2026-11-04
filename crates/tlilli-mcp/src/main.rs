//! The `tlilli-mcp` binary: a thin command-line front over the library. `.mcp.json` runs
//! `tlilli-mcp stdio` so a coding agent can dogfood the server from a session.

#![forbid(unsafe_code)]

use clap::{Parser, Subcommand};

/// Tlilli MCP server: the only door for agents.
#[derive(Parser)]
#[command(name = "tlilli-mcp", version, about)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Serve MCP over standard input and output.
    Stdio,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Command::Stdio => {
            // Placeholder until the rmcp server lands in v0.2: say so on stderr (stdout belongs to
            // the protocol) and exit cleanly so clients see a closed connection, not a crash.
            eprintln!(
                "tlilli-mcp {}: the MCP server is not implemented yet (v0.2, rmcp); stdio placeholder exiting",
                tlilli_mcp::version()
            );
        }
    }
}
