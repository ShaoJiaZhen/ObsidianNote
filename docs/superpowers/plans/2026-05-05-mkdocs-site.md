# Obsidian Vault → MkDocs Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing `ShaoJiaZhen/ObsidianNote` Obsidian vault into a half-public MkDocs site deployed to GitHub Pages at `https://shaojiazhen.github.io/ObsidianNote/`, with opt-in publishing via `publish: true` frontmatter.

**Architecture:** Single repo. Vault root doubles as MkDocs `docs_dir`. `mkdocs-publisher` plugin filters by `publish:` frontmatter and converts Obsidian-native syntax (callouts, wikilinks, image embeds) to MkDocs equivalents at build time. GitHub Actions builds on push to `main` and deploys to the `gh-pages` branch.

**Tech Stack:** Python 3.12, MkDocs 1.6, mkdocs-material 9.5, mkdocs-publisher 1.x, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-05-05-obsidian-to-mkdocs-site-design.md`

**Working directory for all tasks:** `I:\GitHub\ObsidianNote` (NOT the skills repo).

---

## Pre-flight

Before starting, the executing engineer must:

- [ ] Be in `I:\GitHub\ObsidianNote` (verify with `git remote -v` → should show `ShaoJiaZhen/ObsidianNote`)
- [ ] Have Python 3.12+ installed (`python --version`)
- [ ] Have `git` configured (`git config user.name && git config user.email`)
- [ ] Be on `main` branch (`git status` shows `On branch main`)
- [ ] Working tree clean (`git status` shows nothing to commit)

If any check fails, fix before proceeding.

---

## Task 1: Add `.gitignore`

**Files:**
- Create: `I:\GitHub\ObsidianNote\.gitignore`

- [ ] **Step 1: Create the file with exact content**

```gitignore
# MkDocs build output
site/

# Python
__pycache__/
*.pyc
.venv/
venv/

# mkdocs-publisher cache
.cache/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Verify nothing tracked is now ignored**

Run: `git status --ignored`
Expected: `site/` and `.venv/` (if you create them later) appear under "Ignored files". No previously tracked files (e.g., your existing `.md` files, `.obsidian/`) should be ignored.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "Add .gitignore for MkDocs build output and Python venv"
```

---

## Task 2: Add `requirements.txt` with pinned MkDocs deps

**Files:**
- Create: `I:\GitHub\ObsidianNote\requirements.txt`

- [ ] **Step 1: Create the file with exact content**

```
mkdocs==1.6.*
mkdocs-material==9.5.*
mkdocs-publisher==1.*
```

- [ ] **Step 2: Create local Python venv and install**

```bash
python -m venv .venv
# Windows PowerShell activation:
.venv\Scripts\Activate.ps1
# (or on bash: source .venv/Scripts/activate)
pip install -r requirements.txt
```

Expected: All 3 packages install successfully with no version conflicts.

- [ ] **Step 3: Verify installs**

```bash
mkdocs --version
```
Expected: prints `mkdocs, version 1.6.x`.

```bash
pip show mkdocs-material mkdocs-publisher | findstr "Name Version"
```
Expected: both packages listed with their pinned major versions.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "Pin MkDocs, Material theme, and publisher plugin versions"
```

---

## Task 3: Tracer bullet — minimal `mkdocs.yml` that builds

**Goal of this task:** Get an end-to-end "smallest thing that builds" before adding any complexity. No theme, no plugins, no Obsidian features yet.

**Files:**
- Create: `I:\GitHub\ObsidianNote\mkdocs.yml`

- [ ] **Step 1: Create minimal mkdocs.yml**

```yaml
site_name: ShaoJiaZhen's Notes
docs_dir: .

# v1 tracer bullet: only the homepage. Everything else added in later tasks.
nav:
  - Home: index.md

# Exclude vault internals + ourselves from build (we'll add publisher later for real opt-in)
exclude_docs: |
  .obsidian/
  docs/superpowers/
  README.md
  site/
  Pasted image *.png
```

- [ ] **Step 2: Create a placeholder `index.md` so the build has something to render**

```markdown
# ShaoJiaZhen's Notes

(Tracer bullet placeholder — replaced in Task 7.)
```

Save to: `I:\GitHub\ObsidianNote\index.md`

- [ ] **Step 3: Build locally**

```bash
mkdocs build --strict
```

Expected:
- Exit code 0
- Output dir `site/` created
- `site/index.html` exists
- No warnings about missing files

If `--strict` fails because of CJK directories, that's expected and we'll fix in Task 5. For now, also try `mkdocs build` without `--strict` to confirm the build itself works.

- [ ] **Step 4: Preview locally**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/` in a browser. Expected: see "ShaoJiaZhen's Notes" with the placeholder text. Stop the server with Ctrl+C.

- [ ] **Step 5: Commit (do NOT commit `site/` — `.gitignore` should already exclude it)**

```bash
git add mkdocs.yml index.md
git commit -m "Tracer bullet: minimal mkdocs config that builds"
```

---

## Task 4: Add Material theme + verify rendering

**Files:**
- Modify: `I:\GitHub\ObsidianNote\mkdocs.yml`

- [ ] **Step 1: Add theme block to mkdocs.yml**

Append the following to mkdocs.yml (after the `docs_dir: .` line, before the `nav:` block):

```yaml
site_description: 个人知识笔记
site_url: https://shaojiazhen.github.io/ObsidianNote/
repo_url: https://github.com/ShaoJiaZhen/ObsidianNote
repo_name: ShaoJiaZhen/ObsidianNote

theme:
  name: material
  language: zh
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - search.suggest
    - search.highlight
    - content.code.copy
```

- [ ] **Step 2: Rebuild and preview**

```bash
mkdocs serve
```

Expected at `http://127.0.0.1:8000/`:
- Material theme is active (left sidebar with navigation, search bar at top, dark/light toggle in top right)
- Page header reads "ShaoJiaZhen's Notes"
- GitHub icon top-right links to `ShaoJiaZhen/ObsidianNote`
- Toggle dark/light works

Stop the server with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add mkdocs.yml
git commit -m "Apply Material theme with light/dark palette and Chinese language"
```

---

## Task 5: Add markdown extensions (admonitions, mermaid, tabs, tasklist)

**Files:**
- Modify: `I:\GitHub\ObsidianNote\mkdocs.yml`

- [ ] **Step 1: Append `markdown_extensions` block to mkdocs.yml**

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - tables
  - toc:
      permalink: true
```

- [ ] **Step 2: Add a temporary test page to verify Mermaid + admonition rendering**

Create `I:\GitHub\ObsidianNote\_render-test.md` with:

````markdown
# Render test (temporary)

!!! note
    This is a Material admonition (admonition extension working).

!!! tip "提示"
    Chinese title in admonition.

```mermaid
flowchart LR
    A[Source] --> B[Build] --> C[Site]
```

- [x] Tasklist works
- [ ] Tasklist also works
````

Add to `mkdocs.yml` `nav:` block temporarily:

```yaml
nav:
  - Home: index.md
  - Render test: _render-test.md
```

- [ ] **Step 3: Build and verify**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/_render-test/`. Expected:
- Two coloured admonition boxes (note = blue, tip = green)
- Chinese title "提示" renders correctly inside the tip box
- Mermaid diagram renders as 3 connected boxes (Source → Build → Site)
- Two task list checkboxes, one checked one unchecked

If Mermaid shows as raw code, the `pymdownx.superfences` config is wrong — check indentation.

Stop server with Ctrl+C.

- [ ] **Step 4: Remove the test page from `nav:` (keep file, we'll delete in Task 9)**

Revert `nav:` block to:

```yaml
nav:
  - Home: index.md
```

- [ ] **Step 5: Commit**

```bash
git add mkdocs.yml _render-test.md
git commit -m "Enable admonitions, Mermaid, tabs, tasklist via pymdownx extensions"
```

---

## Task 6: Configure mkdocs-publisher plugin (opt-in mode + Obsidian syntax)

**IMPORTANT:** The exact YAML keys for `mkdocs-publisher` may differ from what's shown below — verify against current upstream docs in Step 1 before proceeding. The spec acknowledges this in §15.

**Files:**
- Modify: `I:\GitHub\ObsidianNote\mkdocs.yml`

- [ ] **Step 1: Read the upstream plugin docs to confirm config syntax**

```bash
pip show mkdocs-publisher | findstr "Home-page Summary"
```

The `Home-page` URL printed there is the authoritative source. Open it in a browser. Also useful: search PyPI for `mkdocs-publisher` and click the project's homepage / repo link.

Specifically confirm:
- The plugin name(s) to use under `plugins:` (the package is modular; newer versions may expose multiple plugins like `pub-meta`, `pub-obsidian`, `pub-blog` instead of one monolithic `publisher` plugin)
- Frontmatter key for opt-in publishing (likely `publish:` or `status:`)
- Whether wikilinks / callouts / image embeds are sub-modules or one plugin

Update Steps 2-3 below with the actual key names if they differ.

- [ ] **Step 2: Append plugins block to mkdocs.yml**

Use this as the starting point. Adjust based on Step 1 findings.

```yaml
plugins:
  - search:
      lang: [zh, en]
  - pub-meta:
      publish_default: false
  - pub-obsidian:
      wikilinks:
        enabled: true
      callouts:
        enabled: true
      attachments:
        enabled: true
```

> If the modular `pub-*` plugins above don't exist in your installed version, fall back to the legacy single-plugin form:
> ```yaml
>   - publisher:
>       publish_default: false
>       obsidian:
>         wikilinks: true
>         callouts: true
>         embeds: true
> ```

- [ ] **Step 3: Build and verify the plugin loads**

```bash
mkdocs build --strict
```

Expected:
- Exit code 0
- No "Plugin not found" errors
- `site/` regenerates

If you get `Plugin not found: publisher`, the plugin name is wrong — re-check Step 1. If you get a config validation error like `Unknown configuration option`, the keys are wrong — re-check Step 1 and try the alternative form.

- [ ] **Step 4: Verify opt-in filter works (negative test)**

The placeholder `index.md` does NOT have `publish: true` yet, so with opt-in mode the build should currently produce a site with NO pages (or only `_render-test.md` if it has no frontmatter and the plugin treats untagged as "not published").

Run:

```bash
mkdocs build --strict 2>&1 | grep -i "publish\|warning"
```

Document what you see. Then add `publish: true` to `index.md` frontmatter:

```markdown
---
publish: true
---

# ShaoJiaZhen's Notes

(Tracer bullet placeholder — replaced in Task 7.)
```

Rebuild:

```bash
mkdocs build --strict
```

Open `site/index.html` in a browser — should render. The render-test page should NOT appear (no `publish: true`). This proves opt-in works.

- [ ] **Step 5: Commit**

```bash
git add mkdocs.yml index.md
git commit -m "Add mkdocs-publisher plugin with opt-in mode and Obsidian syntax handlers"
```

---

## Task 7: Replace `index.md` placeholder with real homepage

**Files:**
- Overwrite: `I:\GitHub\ObsidianNote\index.md`

- [ ] **Step 1: Replace the entire file with the homepage from spec §11**

```markdown
---
title: ShaoJiaZhen's Notes
publish: true
---

# ShaoJiaZhen's Notes

这里是我个人的工程与产品笔记。主要写给自己看，但放在公网上方便偶尔分享。

> [!info] 关于这些笔记
> 这些笔记是 opt-in 发布的 — 只有标记 `publish: true` 的才会出现在站点上。
> 没出现的不代表不存在，可能只是还没整理完。

## 推荐从这几篇开始

- [[Superpowers]] — Claude Code 工程纪律层 skills 实战指南
- [[gstack]] — AI 编程的产品交付层（QA / 发布 / 监控）
- [[MattPocockSkills]] — 拷问 + 共享语言驱动的 AI 编程方法论
- [[AI-Agent-Workflow]] — 整体 AI agent 工作流总览

## 按主题浏览

侧栏按目录组织：

- **Agent** — AI 编程 agent 相关方法论与工具
- **Github** — GitHub 上看到的有意思的项目笔记
- **软件开发** — 具体技术栈学习记录

## 联系

- GitHub: [@ShaoJiaZhen](https://github.com/ShaoJiaZhen)
- Source: [ShaoJiaZhen/ObsidianNote](https://github.com/ShaoJiaZhen/ObsidianNote)
```

- [ ] **Step 2: Verify it renders**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/`. Expected:
- The 4 wikilinks render as `[[xxx]]` LITERAL TEXT (because the target notes don't have `publish: true` yet — that's Task 8)
- `> [!info]` callout still renders as raw blockquote (publisher should handle it, but if it doesn't, we'll spot it now)

Note any deviations. Both will be fixed by Task 8 (wikilinks) — this is expected at this stage.

Stop server with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add index.md
git commit -m "Replace tracer-bullet placeholder with real homepage"
```

---

## Task 8: Tag the 4 Agent notes with `publish: true`

**Files:**
- Modify: `I:\GitHub\ObsidianNote\Agent\Superpowers.md` (frontmatter only)
- Modify: `I:\GitHub\ObsidianNote\Agent\gstack.md` (frontmatter only)
- Modify: `I:\GitHub\ObsidianNote\Agent\MattPocockSkills.md` (frontmatter only)
- Modify: `I:\GitHub\ObsidianNote\Agent\AI-Agent-Workflow.md` (frontmatter only)

> **DO NOT use a script to batch-edit.** Per spec §10, manually open each file in Obsidian (or any editor), confirm the content is publish-safe, then add the line.

- [ ] **Step 1: `Agent/Superpowers.md` — add publish: true**

Locate the frontmatter (lines 1-13). Add `publish: true` as a new line just before the closing `---`. After:

```yaml
---
title: Superpowers 项目实战使用指南
category: AI Agent / Claude Code / Engineering Workflow
tags:
  - AI编程
  - ClaudeCode
  - Superpowers
  - TDD
  - CodeReview
  - AIAgent
status: evergreen
updated: 2026-05-04
publish: true
---
```

- [ ] **Step 2: `Agent/gstack.md` — add publish: true (same pattern)**

Insert `publish: true` before the closing `---` of the frontmatter.

- [ ] **Step 3: `Agent/MattPocockSkills.md` — add publish: true**

Insert `publish: true` before the closing `---` of the frontmatter.

- [ ] **Step 4: `Agent/AI-Agent-Workflow.md` — add publish: true**

Insert `publish: true` before the closing `---` of the frontmatter.

- [ ] **Step 5: Build and verify all 5 pages render**

```bash
mkdocs build --strict
```

Inspect `site/`. Expected files:
- `site/index.html`
- `site/Agent/Superpowers/index.html`
- `site/Agent/gstack/index.html`
- `site/Agent/MattPocockSkills/index.html`
- `site/Agent/AI-Agent-Workflow/index.html`

Then:

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/`. Expected:
- Sidebar shows `Agent/` group with 4 entries
- Click `Superpowers` → page renders with mermaid diagrams visible, callouts coloured
- Wikilinks on the homepage now resolve as actual links (not `[[xxx]]` literal)
- Searching for "工程纪律" returns hits

Stop server.

- [ ] **Step 6: Commit**

```bash
git add Agent/Superpowers.md Agent/gstack.md Agent/MattPocockSkills.md Agent/AI-Agent-Workflow.md
git commit -m "Opt-in 4 mature Agent notes for publishing"
```

---

## Task 9: Local smoke test (full 9-item checklist from spec §13)

**Files:** None modified. This task is verification.

- [ ] **Step 1: Delete the temporary render-test page**

```bash
rm _render-test.md
git add _render-test.md
git commit -m "Remove temporary render-test page"
```

- [ ] **Step 2: Clean rebuild**

```bash
rm -rf site/
mkdocs build --strict
```

Expected: exit code 0, no warnings.

- [ ] **Step 3: Run `mkdocs serve` and walk through the 9-item smoke test**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000/` and verify:

- [ ] Homepage (`/`) opens without error
- [ ] 4 Agent notes appear in left sidebar under `Agent/`
- [ ] At least one mermaid diagram renders (visit `/Agent/Superpowers/` and scroll)
- [ ] Callouts show as coloured blocks (not raw `> [!summary]` text)
- [ ] Wikilinks navigate correctly (click `[[Superpowers]]` on homepage)
- [ ] Notes WITHOUT `publish: true` (e.g. `Github/AutoCut.md`, `工作记录/日报.md`) do NOT appear in sidebar or search
- [ ] Dark/light toggle works (click sun/moon icon top-right)
- [ ] Chinese search works (search "工程纪律" → finds Superpowers; search "superpowers" → also finds it)
- [ ] Images render — if any of the 4 Agent notes embed `Pasted image *.png`, navigate there and verify display

If any item fails, STOP and diagnose before proceeding. Common fixes:
- Callouts not coloured → publisher config wrong, re-check Task 6 Step 1
- Wikilinks broken → target note missing `publish: true`, or wikilink syntax not enabled in publisher
- Sidebar shows unpublished notes → opt-in not enabled, re-check Task 6 plugin config

Stop server when satisfied.

- [ ] **Step 4: No commit needed (verification only).** If you fixed anything in Step 3, commit those fixes with descriptive messages.

---

## Task 10: Add GitHub Actions deploy workflow

**Files:**
- Create: `I:\GitHub\ObsidianNote\.github\workflows\deploy.yml`

- [ ] **Step 1: Create the workflow file with exact content**

```yaml
name: Deploy MkDocs site

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip
      - run: pip install -r requirements.txt
      - run: mkdocs build --strict
      - if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: mkdocs gh-deploy --force --no-history
```

- [ ] **Step 2: Validate YAML syntax locally (optional but recommended)**

If you have Python:

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"
```

Expected: no output (= valid YAML). If syntax error, you'll get a YAMLError.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions workflow: build on PR, build+deploy on push to main"
```

---

## Task 11: Push to GitHub and verify Actions runs

**Files:** None created/modified.

- [ ] **Step 1: Push current branch**

```bash
git push origin main
```

Expected: push succeeds.

- [ ] **Step 2: Watch the Actions run**

Open `https://github.com/ShaoJiaZhen/ObsidianNote/actions` in a browser.

Expected:
- A run named "Deploy MkDocs site" appears, triggered by the latest commit
- Goes through 5 steps: checkout, setup-python, pip install, mkdocs build, mkdocs gh-deploy
- All green ✓

If `mkdocs build --strict` fails in CI but passed locally, the most likely cause is path case-sensitivity (Windows is case-insensitive, Linux is not). Check wikilink targets and image filenames for case mismatches.

If `mkdocs gh-deploy` fails with permission error, check repo Settings → Actions → General → "Workflow permissions" → must be "Read and write permissions".

- [ ] **Step 3: Verify `gh-pages` branch was created**

In the GitHub UI, switch the branch dropdown — there should now be `main` and `gh-pages`. The `gh-pages` branch should contain `index.html`, `Agent/` etc.

- [ ] **Step 4: No commit needed.** If Actions failed, fix the underlying issue, commit the fix, push again, and re-verify.

---

## Task 12: Configure GitHub Pages (manual, in browser)

**Files:** None.

This is a one-time GitHub UI configuration. Cannot be automated.

- [ ] **Step 1: Open repo settings**

Navigate to `https://github.com/ShaoJiaZhen/ObsidianNote/settings/pages`.

- [ ] **Step 2: Configure source**

Under "Build and deployment":
- Source: `Deploy from a branch`
- Branch: `gh-pages` / `(root)`
- Click `Save`

- [ ] **Step 3: Wait for first deploy (1-2 min) and grab the URL**

The page should refresh and show:

```
Your site is live at https://shaojiazhen.github.io/ObsidianNote/
```

If you see "Your site is being built", wait 1-2 min and refresh.

- [ ] **Step 4: No commit (manual config, not in repo).**

---

## Task 13: Production smoke test against live URL

**Files:** None.

Repeat the 9-item smoke test from Task 9, but against the live site.

- [ ] **Step 1: Open `https://shaojiazhen.github.io/ObsidianNote/` in browser**

- [ ] Homepage opens
- [ ] 4 Agent notes in sidebar
- [ ] Mermaid renders on `/Agent/Superpowers/`
- [ ] Callouts coloured (not raw `> [!summary]`)
- [ ] Wikilinks navigate correctly
- [ ] Unpublished notes don't appear in sidebar/search
- [ ] Dark/light toggle works
- [ ] Chinese search works (search "工程纪律")
- [ ] Images render (if any embedded in published notes)

- [ ] **Step 2: Test a fresh-private-window load**

Open the URL in incognito / private mode to confirm CDN serves correctly to anonymous users (no GitHub login required).

- [ ] **Step 3: If everything passes, mark this task done.**

If any item fails, the difference vs Task 9's local smoke test is usually one of:
- A path case mismatch (Linux CI is case-sensitive)
- An asset that worked locally because of relative-path quirks but not on `*.github.io/ObsidianNote/`
- A `mkdocs-publisher` config that depended on local file system layout

Diagnose, fix, commit, push, retest.

---

## Acceptance Criteria (matches spec §14)

When all 13 tasks are complete and checked off:

- [ ] Repo has `mkdocs.yml`, `requirements.txt`, `.github/workflows/deploy.yml`, `index.md`, `.gitignore`
- [ ] 4 Agent notes have `publish: true`
- [ ] GitHub Pages source set to `gh-pages` branch
- [ ] Latest GitHub Actions run is green
- [ ] `https://shaojiazhen.github.io/ObsidianNote/` accessible
- [ ] All 9 smoke test items pass on the live site

---

## Out of Scope (will NOT be done in this plan)

Per spec §2:

- SEO / social cards / analytics
- Custom domain (would add a `CNAME` file + DNS — easy upgrade later)
- Comments
- RSS / Atom feed
- Auto-generated "recent updates" or tag-based browse pages
- Romanizing CJK directory names to ASCII URL slugs
- Auto-generating the homepage's "推荐从这几篇开始" list

Anything above goes in a separate future plan.

---

## Rollback Procedure

If any task breaks the live site:

1. **Build broke**: gh-pages branch was not updated; live site still serves last good build. No action needed except fix locally and re-push.
2. **Bad content shipped**: `git revert <bad-commit> && git push origin main` → CI rebuilds → live site reverts within 1-2 min.
3. **GitHub Pages misconfigured**: Settings → Pages → temporarily change source to "None" to take site offline.
4. **Need to wipe gh-pages and start over**: `git push origin --delete gh-pages` then re-run Actions manually via "Run workflow" button. mkdocs-publisher will rebuild it from main.
