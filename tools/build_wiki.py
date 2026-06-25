#!/usr/bin/env python3
"""Render the course into wiki pages from the single source of truth (modules/).

Host-agnostic: this writes Markdown into a target wiki working directory. A thin
per-host CI wrapper clones the host's `<repo>.wiki.git`, runs this script, then
commits and pushes. The same script feeds both the Gitea and GitHub wikis; only
the `--host` URL flavor and the CI wrapper differ.

The wiki is GENERATED BUILD OUTPUT. Never hand-edit it; edit modules/ and let CI
re-render. Labs are NOT copied into the wiki; lesson pages link to the runnable
files back in the main repo. Each page gets prev/next navigation so the wiki reads
like a textbook.

Usage:
  build_wiki.py --repo-root . --out <wiki-dir> \
      --web-base https://git.jpaul.io/justin/ai-workflow-course \
      --branch main --host gitea
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Unit structure (module numbers), from the syllabus. Drives the textbook nav.
UNITS = [
    ("Unit 1: Get out of the chat window", range(1, 8)),
    ("Unit 2: Make it shareable, reviewable, recoverable", range(8, 13)),
    ("Unit 3: Automate the checking and shipping", range(13, 20)),
    ("Unit 4: Extend the AI into your systems", range(20, 24)),
    ("Unit 5: AI in the Loop", range(24, 28)),
]


def src_url(web_base: str, branch: str, host: str, path: str) -> str:
    """Browser URL to a file in the main repo (host-specific path scheme)."""
    path = path.rstrip("/")
    if host == "github":
        return f"{web_base}/blob/{branch}/{path}"
    return f"{web_base}/src/branch/{branch}/{path}"  # gitea / forgejo


def first_h1(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def short_title(h1: str) -> str:
    """'Module 1: The Copy-Paste Problem' -> 'The Copy-Paste Problem'."""
    m = re.match(r"^Module\s+\d+\s*[—:-]\s*(.+)$", h1)
    return m.group(1).strip() if m else h1


def rewrite_lab_links(body: str, web_base: str, branch: str, host: str, slug: str) -> str:
    """Make ](lab/...) point at the runnable file in the main repo, not the wiki."""
    def repl(m: re.Match) -> str:
        rel = m.group(1)  # e.g. 'lab/Dockerfile' or 'lab/'
        return f"]({src_url(web_base, branch, host, f'modules/{slug}/{rel}')})"
    return re.sub(r"\]\((lab/[^)]*)\)", repl, body)


# Repo root files that may be linked from prose; in the wiki these must point back
# at the main repo, not at a (nonexistent) wiki page of the same name.
ROOT_FILES = ("AGENTS.md", "README.md", "the-workflow-syllabus.md", "handoff.md", "_TEMPLATE.md")


def rewrite_repo_file_links(body: str, web_base: str, branch: str, host: str) -> str:
    pattern = r"\]\((" + "|".join(re.escape(f) for f in ROOT_FILES) + r")\)"
    return re.sub(
        pattern,
        lambda m: f"]({src_url(web_base, branch, host, m.group(1))})",
        body,
    )


def banner(source_path: str, source_url: str) -> str:
    return (
        f"> 📖 _This page is generated from [`{source_path}`]({source_url}). "
        f"**Edit the source, not the wiki**; edits here are overwritten on the next sync. "
        f"Run the hands-on labs from the repo, linked inline._\n"
    )


def discover_modules(repo_root: Path):
    """Return [(number:int, slug:str, path:Path)] sorted by number."""
    mods = []
    for d in sorted((repo_root / "modules").iterdir()):
        if not d.is_dir():
            continue
        m = re.match(r"^(\d+)-", d.name)
        if m and (d / "README.md").exists():
            mods.append((int(m.group(1)), d.name, d))
    return sorted(mods, key=lambda t: t[0])


def home_intro(repo_root: Path) -> str:
    """Pull title/tagline/thesis from the repo README (up to its first '## ')."""
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    out = []
    for line in readme.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out).strip()


def top_nav(prev) -> str:
    """prev is (page, label) or None."""
    if not prev:
        return ""
    return f"⬅ **Previous: [{prev[1]}]({prev[0]})**\n"


def bottom_nav(nxt) -> str:
    if not nxt:
        return ""
    return f"**Continue to: [{nxt[1]}]({nxt[0]})** ➡\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", required=True, help="wiki working directory to write into")
    ap.add_argument("--web-base", required=True, help="main repo web base URL")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--host", choices=["gitea", "github"], default="gitea")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    mods = discover_modules(repo_root)
    if not mods:
        print("no modules found", flush=True)
        return 1

    # --- pass 1: read everything, build the ordered reading sequence ------
    # each entry: {page, label, body, slug|None}
    seq = []
    titles: dict[int, str] = {}
    slugs: dict[int, str] = {}
    for num, slug, path in mods:
        body = (path / "README.md").read_text(encoding="utf-8")
        h1 = first_h1(body, f"Module {num}")
        titles[num] = h1
        slugs[num] = slug
        seq.append({"page": slug, "label": h1, "body": body, "slug": slug})

    cap = repo_root / "capstone" / "README.md"
    cap_title = None
    if cap.exists():
        body = cap.read_text(encoding="utf-8")
        cap_title = first_h1(body, "Capstone: The Full Loop")
        seq.append({"page": "capstone", "label": cap_title, "body": body, "slug": None})

    # --- pass 2: write each page with banner + prev/next nav --------------
    for i, entry in enumerate(seq):
        prev = (seq[i - 1]["page"], seq[i - 1]["label"]) if i > 0 else None
        nxt = (seq[i + 1]["page"], seq[i + 1]["label"]) if i < len(seq) - 1 else None

        if entry["slug"] is not None:
            source_path = f"modules/{entry['slug']}/README.md"
            body = rewrite_lab_links(entry["body"], args.web_base, args.branch, args.host, entry["slug"])
            body = rewrite_repo_file_links(body, args.web_base, args.branch, args.host)
        else:
            source_path = "capstone/README.md"
            body = rewrite_repo_file_links(entry["body"], args.web_base, args.branch, args.host)

        parts = [banner(source_path, src_url(args.web_base, args.branch, args.host, source_path))]
        tn = top_nav(prev)
        if tn:
            parts.append("\n" + tn)
        parts.append("\n" + body)
        bn = bottom_nav(nxt)
        if bn:
            parts.append("\n---\n\n" + bn)
        (out / f"{entry['page']}.md").write_text("\n".join(parts) + "\n", encoding="utf-8")

    # --- _Sidebar.md (textbook nav) --------------------------------------
    sb = ["### [📖 Home](Home)\n"]
    for unit_title, rng in UNITS:
        present = [n for n in rng if n in slugs]
        if not present:
            continue
        sb.append(f"**{unit_title}**\n")
        for n in present:
            sb.append(f"- [{n} · {short_title(titles[n])}]({slugs[n]})")
        sb.append("")
    if cap_title:
        sb.append("**Finale**\n")
        sb.append(f"- [{short_title(cap_title)}](capstone)")
        sb.append("")
    (out / "_Sidebar.md").write_text("\n".join(sb) + "\n", encoding="utf-8")

    # --- Home.md (landing + TOC) -----------------------------------------
    intro = rewrite_repo_file_links(home_intro(repo_root), args.web_base, args.branch, args.host)
    home = [intro, "\n## Contents\n"]
    for unit_title, rng in UNITS:
        present = [n for n in rng if n in slugs]
        if not present:
            continue
        home.append(f"### {unit_title}\n")
        for n in present:
            home.append(f"- **[{titles[n]}]({slugs[n]})**")
        home.append("")
    if cap_title:
        home.append("### Finale\n")
        home.append(f"- **[{cap_title}](capstone)**")
        home.append("")
    home.append(
        "\n---\n> 📖 _This wiki is generated from the "
        f"[course repo]({args.web_base}); edit `modules/` there, not these pages._"
    )
    (out / "Home.md").write_text("\n".join(home) + "\n", encoding="utf-8")

    # --- _Footer.md -------------------------------------------------------
    (out / "_Footer.md").write_text(
        f"_Generated from the [ai-workflow-course repo]({args.web_base}) • "
        "the model is the cheap, swappable part; the workflow is the durable skill._\n",
        encoding="utf-8",
    )

    pages = len(seq) + 3
    print(f"wrote {pages} wiki files to {out} ({len(mods)} modules"
          f"{' + capstone' if cap_title else ''} + Home/_Sidebar/_Footer, with prev/next nav)",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
