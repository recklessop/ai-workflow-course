# tools/

## `build_wiki.py`: render the course into a wiki

The course wiki (the "textbook" view under the **Wiki** tab) is **generated build
output**. The single source of truth is `modules/**/README.md` + `capstone/README.md`.
**Never hand-edit the wiki**; edits there are overwritten on the next sync.

`build_wiki.py` is host-agnostic: it writes Markdown pages into a wiki working
directory (`Home.md`, `_Sidebar.md`, `_Footer.md`, one page per module + capstone),
rewriting `lab/…` and repo-root links to absolute URLs back in the main repo (so the
runnable labs stay in the repo and are linked, never copied into the wiki).

### Run it manually

```bash
# clone the wiki repo (Gitea)
git clone https://git.jpaul.io/justin/ai-workflow-course.wiki.git wiki

# render into it
python3 tools/build_wiki.py --repo-root . --out wiki \
    --web-base https://git.jpaul.io/justin/ai-workflow-course --branch main --host gitea

# publish
cd wiki && git add -A && git commit -m "docs(wiki): sync from modules/" && git push
```

For GitHub, use `--host github` and `--web-base https://github.com/<owner>/<repo>`.

### Automated sync (CI)

- **Gitea:** `.gitea/workflows/sync-wiki.yml` runs on every push to `main` that
  touches `modules/**`, `capstone/**`, `README.md`, or this generator.
- **GitHub:** `.github/workflows/sync-wiki.yml` does the same on the mirror.

Both need, one time:
1. an **Actions runner** attached (Gitea: Settings → Actions → Runners);
2. a repo secret **`WIKI_TOKEN`** with wiki write (a scoped PAT/deploy token, *not*
   a site-admin token; on GitHub the default `GITHUB_TOKEN` can't push the wiki);
3. the wiki **initialized** once (Gitea is already initialized; on GitHub create one
   page in the UI first so `<repo>.wiki.git` exists).
