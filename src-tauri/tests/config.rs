// SPDX-FileCopyrightText: 2026 bioedca
// SPDX-License-Identifier: Apache-2.0

//! Contract checks on the gated app configuration, `tauri.conf.json` and `capabilities/`
//! (`docs/prd/32-code-review.md` §3). Each test pins one PRD rule, so an edit that drops it fails
//! here as well as in review.

use std::fs;
use std::path::{Path, PathBuf};

use serde_json::{Value, json};

fn crate_path(relative: &str) -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join(relative)
}

fn read_text(relative: &str) -> String {
    let path = crate_path(relative);
    fs::read_to_string(&path).unwrap_or_else(|error| panic!("{}: {error}", path.display()))
}

fn read_json(relative: &str) -> Value {
    serde_json::from_str(&read_text(relative))
        .unwrap_or_else(|error| panic!("{relative} is not valid JSON: {error}"))
}

/// `PR-REL-002`: one version source. Without `version`, Tauri takes the version of this crate,
/// which is the workspace version that release-plz bumps.
#[test]
fn tauri_conf_has_no_version() {
    let conf = read_json("tauri.conf.json");
    assert!(
        conf.get("version").is_none(),
        "tauri.conf.json must not set `version`"
    );
}

/// `PR-REL-030` and `PR-REL-034`: signed updater artifacts, the stable manifest on the docs site,
/// passive installs on Windows, and the public key recorded in the GitHub settings record.
#[test]
fn updater_uses_the_recorded_key_and_the_docs_site() {
    let conf = read_json("tauri.conf.json");
    assert_eq!(conf["bundle"]["createUpdaterArtifacts"], json!(true));

    let updater = &conf["plugins"]["updater"];
    let site_url = read_text("../mkdocs.yml")
        .lines()
        .find_map(|line| line.strip_prefix("site_url:"))
        .map(|url| url.trim().trim_end_matches('/').to_owned())
        .expect("mkdocs.yml sets site_url");
    assert_eq!(
        updater["endpoints"],
        json!([format!("{site_url}/updates/stable.json")])
    );
    assert_eq!(updater["windows"]["installMode"], json!("passive"));

    let pubkey = updater["pubkey"].as_str().expect("pubkey is a string");
    let record = read_text("../docs/dev/github-settings.md");
    assert!(
        !pubkey.is_empty() && record.lines().any(|line| line.trim() == pubkey),
        "plugins.updater.pubkey must be the key recorded in docs/dev/github-settings.md §6"
    );
}

/// PRD 22 §3: the main window's capability grants the updater and nothing else until a command
/// or plugin needs more.
#[test]
fn main_capability_grants_only_the_updater() {
    let capability = read_json("capabilities/main.json");
    assert_eq!(capability["windows"], json!(["main"]));
    assert_eq!(capability["permissions"], json!(["updater:default"]));
}

/// PRD 22 §3: a CSP is set, loads nothing remote and allows no inline or evaluated code.
#[test]
fn csp_allows_only_local_content() {
    let conf = read_json("tauri.conf.json");
    let csp = conf["app"]["security"]["csp"]
        .as_str()
        .expect("app.security.csp is a string");
    assert!(csp.contains("default-src 'self'"), "csp was {csp}");
    assert!(!csp.contains("'unsafe-"), "csp was {csp}");
    let remote = csp
        .split([' ', ';'])
        .filter(|source| source.starts_with("http") || source.starts_with("ws"))
        .find(|source| *source != "http://ipc.localhost");
    assert_eq!(remote, None, "csp was {csp}");
}
