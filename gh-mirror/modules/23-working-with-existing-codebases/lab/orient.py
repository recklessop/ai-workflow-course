#!/usr/bin/env python3
"""orient.py: build a factual orientation pack for a repo you didn't write.

Run it from the root of a cloned repo. It prints a Markdown summary of *ground truth*
about the codebase (size, languages, project signals, the biggest (often most central)
files, the top-level layout, and likely build/test commands) that you can paste in as the
opening context for an AI session before asking it to map or change anything.

The point is NOT to replace the AI's own exploration. It's to anchor that exploration in
facts the model can't hallucinate: real file names, real counts, real entry points. The AI
then verifies and deepens this; you never let it map from vibes alone.

No dependencies. Standard library only. Works on any OS with Python 3.10+ and git.

    python3 orient.py                 # print the pack
    python3 orient.py > ORIENT.md     # save it to hand to the AI (don't commit it)
"""

from __future__ import annotations

import subprocess
import sys
from collections import Counter
from pathlib import Path

# Files whose mere presence tells you how the project is built, tested, shipped, and configured.
# (key file/dir -> what its presence means). Kept tool- and language-agnostic on purpose.
SIGNALS: dict[str, str] = {
    "pyproject.toml": "Python project (PEP 621 / poetry / hatch)",
    "setup.py": "Python project (legacy setuptools)",
    "requirements.txt": "Python dependencies (pip)",
    "package.json": "Node/JS project",
    "pnpm-lock.yaml": "Node project (pnpm)",
    "yarn.lock": "Node project (yarn)",
    "go.mod": "Go module",
    "Cargo.toml": "Rust crate",
    "pom.xml": "Java/Maven project",
    "build.gradle": "Java/Kotlin/Gradle project",
    "Gemfile": "Ruby project",
    "composer.json": "PHP project",
    "Makefile": "Make targets (often the real entry point for build/test)",
    "Dockerfile": "Containerized (Module 16)",
    "docker-compose.yml": "Multi-service local stack (Module 16)",
    "compose.yaml": "Multi-service local stack (Module 16)",
    ".github": "GitHub Actions / project meta",
    ".gitea": "Gitea Actions",
    ".gitlab-ci.yml": "GitLab CI",
    "tox.ini": "Python test matrix",
    "README.md": "Has a README; read it first",
    "CONTRIBUTING.md": "Has contributor guidance; read before changing",
    "ARCHITECTURE.md": "Has an architecture doc; rare and valuable",
    # Committed AI-instruction files. Name the real ones across vendors; singling out one
    # would both miss files and cut against the vendor-neutral point (Module 5).
    "AGENTS.md": "Has a committed AI instructions file (Module 5)",
    "CLAUDE.md": "Has a committed AI instructions file (Module 5)",
    "GEMINI.md": "Has a committed AI instructions file (Module 5)",
    ".cursorrules": "Has a committed AI instructions file (Module 5)",
    ".cursor/rules": "Has a committed AI instructions file (Module 5)",
    ".github/copilot-instructions.md": "Has a committed AI instructions file (Module 5)",
}

# Common test-runner hints keyed off a present signal file.
TEST_HINTS: dict[str, str] = {
    "pyproject.toml": "pytest    (or: python3 -m pytest)",
    "tox.ini": "tox",
    "package.json": "npm test    (check the \"scripts\" block for the real command)",
    "go.mod": "go test ./...",
    "Cargo.toml": "cargo test",
    "Makefile": "make test    (if a 'test' target exists)",
    "pom.xml": "mvn test",
    "Gemfile": "bundle exec rspec    (or rake test)",
}

CODE_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".kt", ".rb",
    ".php", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".swift", ".scala", ".sh",
}


def git(*args: str) -> str:
    """Run a git command, return stdout (stripped), or "" on failure."""
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def tracked_files() -> list[str]:
    listing = git("ls-files")
    return [line for line in listing.splitlines() if line]


def line_count(path: str) -> int:
    try:
        with open(path, "rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def main() -> int:
    if not Path(".git").exists() and not git("rev-parse", "--is-inside-work-tree"):
        print("Not inside a git repository. cd into a cloned repo first.", file=sys.stderr)
        return 1

    files = tracked_files()
    if not files:
        print("No tracked files found (is this an empty or non-git repo?).", file=sys.stderr)
        return 1

    out: list[str] = []
    w = out.append

    # --- identity -----------------------------------------------------------
    remote = git("remote", "get-url", "origin") or "(no origin remote)"
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "(unknown)"
    total_commits = git("rev-list", "--count", "HEAD") or "?"

    w("# Repo orientation pack\n")
    w(f"- **Origin:** {remote}")
    w(f"- **Branch:** {branch}")
    w(f"- **Total commits:** {total_commits}")
    w(f"- **Tracked files:** {len(files)}")

    # --- languages ----------------------------------------------------------
    ext_counts: Counter[str] = Counter()
    for f in files:
        ext = Path(f).suffix.lower() or "(none)"
        ext_counts[ext] += 1
    w("\n## Languages / file types (top 15 by file count)\n")
    for ext, n in ext_counts.most_common(15):
        marker = " <- code" if ext in CODE_EXTS else ""
        w(f"- `{ext}`: {n}{marker}")

    # --- project signals ----------------------------------------------------
    present = {name for name in SIGNALS if Path(name).exists()}
    w("\n## Project signals (what's present at the root)\n")
    if present:
        for name in SIGNALS:
            if name in present:
                w(f"- `{name}`: {SIGNALS[name]}")
    else:
        w("- (none of the usual manifests/CI/docs at the root; look one level down)")

    # --- likely test command ------------------------------------------------
    hints = [TEST_HINTS[name] for name in TEST_HINTS if name in present]
    w("\n## Likely build/test command (verify before trusting)\n")
    if hints:
        for h in hints:
            w(f"- `{h}`")
    else:
        w("- No obvious runner detected. Search the README and CI config for the real command.")

    # --- biggest files (often the spine) ------------------------------------
    sized = sorted(
        ((line_count(f), f) for f in files if Path(f).suffix.lower() in CODE_EXTS),
        reverse=True,
    )[:15]
    w("\n## Largest code files (often where the core logic lives)\n")
    if sized:
        for n, f in sized:
            w(f"- {n:>6} lines  `{f}`")
    else:
        w("- (no recognized source files)")

    # --- top-level layout ---------------------------------------------------
    top_dirs: Counter[str] = Counter()
    for f in files:
        head = f.split("/", 1)[0]
        top_dirs[head] += 1
    w("\n## Top-level layout (entries by tracked-file count)\n")
    for name, n in sorted(top_dirs.items(), key=lambda kv: (-kv[1], kv[0])):
        kind = "dir" if "/" in next(p for p in files if p.split("/", 1)[0] == name) else "file"
        w(f"- `{name}`{'/' if kind == 'dir' else ''}: {n}")

    # --- recent activity ----------------------------------------------------
    recent = git("log", "--oneline", "-10")
    w("\n## Last 10 commits (the project's recent direction)\n")
    w("```")
    w(recent or "(no history)")
    w("```")

    w("\n---")
    w("> Generated by orient.py. These are *facts*, not conclusions. Hand them to the AI as the")
    w("> opening context, then make it verify and map the areas you actually care about before")
    w("> it changes anything.")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
