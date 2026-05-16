"""
update_manifests.py

Reads all plugin folders, fetches their GitHub Release history via the API,
and updates:
  - manifest.json       (repo root) — one entry per plugin, latest version info
  - <plugin>/plugin.json            — full release history for that plugin
"""

import os
import re
import ast
import json
import sys
import requests
from pathlib import Path
from datetime import datetime, timezone

GITHUB_TOKEN     = os.environ["GITHUB_TOKEN"]
GITHUB_REPO      = os.environ["GITHUB_REPOSITORY"]
CHANGED_PLUGINS  = json.loads(os.environ.get("CHANGED_PLUGINS", "[]"))

API_BASE  = "https://api.github.com"
HEADERS   = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_plugin_meta(plugin_dir: Path) -> dict | None:
    init = plugin_dir / "__init__.py"
    if not init.exists():
        return None

    content = init.read_text()

    def extract(var):
        m = re.search(rf'^{var}\s*=\s*(.+)', content, re.MULTILINE)
        if not m:
            raise ValueError(f"{var} not found in {init}")
        return ast.literal_eval(m.group(1).strip())

    try:
        return {
            "plugin_name": extract("plugin_name"),
            "plugin_version": extract("plugin_version"),
            "creators": extract("creators"),
            "description": extract("description"),
        }
    except Exception as e:
        print(f"  WARNING: Could not read meta from {init}: {e}")
        return None


def get_releases_for_plugin(plugin_name: str) -> list[dict]:
    """Fetch all GitHub Releases whose tag starts with plugin_name@"""
    url = f"{API_BASE}/repos/{GITHUB_REPO}/releases"
    releases = []
    page = 1

    while True:
        resp = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        if resp.status_code != 200:
            print(f"  WARNING: Could not fetch releases (HTTP {resp.status_code})")
            break
        data = resp.json()
        if not data:
            break
        for r in data:
            tag = r.get("tag_name", "")
            if tag.startswith(f"{plugin_name}@"):
                version = tag.split("@", 1)[1]
                assets = [
                    {
                        "name": a["name"],
                        "download_url": a["browser_download_url"],
                        "size": a["size"],
                    }
                    for a in r.get("assets", [])
                    if a["name"].endswith(".deck")
                ]
                releases.append({
                    "version": version,
                    "tag": tag,
                    "release_url": r["html_url"],
                    "published_at": r["published_at"],
                    "assets": assets,
                })
        page += 1

    # Sort newest first
    releases.sort(key=lambda x: x["published_at"], reverse=True)
    return releases


def asset_download_url(plugin_name: str, version: str) -> str | None:
    """Return the .deck download URL for a specific plugin@version release."""
    releases = get_releases_for_plugin(plugin_name)
    for r in releases:
        if r["version"] == version:
            if r["assets"]:
                return r["assets"][0]["download_url"]
    return None


def get_icon_url(plugin_dir: Path, folder_name: str) -> str | None:
    """Return the raw GitHub content URL for the plugin's icon, if it exists."""
    icon_path = plugin_dir / "assets" / "icon.jpg"
    if not icon_path.exists():
        return None
    return (
        f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"
        f"{folder_name}/assets/icon.jpg"
    )


# ---------------------------------------------------------------------------
# Discover all plugins
# ---------------------------------------------------------------------------

def discover_plugins() -> list[Path]:
    skip = {".github", "scripts", ".git", "__pycache__"}
    plugins = []
    for p in sorted(REPO_ROOT.iterdir()):
        if p.is_dir() and p.name not in skip and not p.name.startswith("."):
            if (p / "__init__.py").exists():
                plugins.append(p)
    return plugins


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    plugins = discover_plugins()

    if not plugins:
        print("No plugin directories found.")
        sys.exit(0)

    print(f"Found {len(plugins)} plugin(s): {[p.name for p in plugins]}")

    manifest = {}
    manifest_path = REPO_ROOT / "manifest.json"

    # Load existing manifest so we preserve plugins we're not touching
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            manifest = {}

    for plugin_dir in plugins:
        name = plugin_dir.name
        print(f"\nProcessing: {name}")

        meta = read_plugin_meta(plugin_dir)
        if not meta:
            print(f"  Skipping — no valid __init__.py metadata")
            continue

        plugin_name    = meta["plugin_name"]
        plugin_version = meta["plugin_version"]

        print(f"  Name: {plugin_name}  Version: {plugin_version}")

        # Fetch release history from GitHub
        releases = get_releases_for_plugin(plugin_name)
        print(f"  Found {len(releases)} release(s) on GitHub")

        icon_url = get_icon_url(plugin_dir, name)
        if icon_url:
            print(f"  Icon: {icon_url}")
        else:
            print(f"  Icon: not found (assets/icon.jpg missing)")

        # --- Update plugin.json ---
        plugin_json_path = plugin_dir / "plugin.json"

        plugin_json = {
            "plugin_name": plugin_name,
            "description": meta["description"],
            "creators": meta["creators"],
            "min_app_version" : meta.get("min_app_version",""),
            "latest_version": plugin_version,
            "icon_url": icon_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "releases": releases,
        }

        plugin_json_path.write_text(json.dumps(plugin_json, indent=2))
        print(f"  Written: {plugin_json_path.relative_to(REPO_ROOT)}")

        # --- Update global manifest entry ---
        latest_download = None
        if releases:
            latest_download = releases[0]["assets"][0]["download_url"] if releases[0]["assets"] else None

        manifest[plugin_name] = {
            "plugin_name": plugin_name,
            "description": meta["description"],
            "creators": meta["creators"],
            "latest_version": plugin_version,
            "icon_url": icon_url,
            "download_url": latest_download,
            "plugin_json_url": (
                f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/"
                f"{name}/plugin.json"
            ),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    # --- Write global manifest ---
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWritten: manifest.json ({len(manifest)} plugin(s))")


if __name__ == "__main__":
    main()
