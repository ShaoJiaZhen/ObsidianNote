"""MkDocs hooks: pre-process Obsidian-style wikilinks before pub-obsidian.

Two issues this fixes:

1. Intra-doc heading wikilinks `[[#7.5 代码审查阶段]]`
   pub-obsidian's slugify is ASCII-only with trailing separator
   (e.g. `#75-`), but the default mkdocs toc generates `id="75"` (CJK
   stripped, trailing separator removed). The mismatch makes every
   intra-doc heading wikilink in CJK-mixed-with-numbers headings 404.

2. File-level wikilinks `[[Filename]]` without path
   pub-obsidian converts these to `[Filename](Filename.md)` — basename
   only, no path resolution. So `[[Superpowers]]` from `docs/index.md`
   resolves to `index.md`'s sibling `Superpowers.md` rather than
   `docs/Agent/Superpowers.md`. Obsidian itself uses
   "shortest-path-when-possible" lookup; we replicate that here.

The hook runs `on_files` to build a basename → docs-relative path map,
then `on_page_markdown` (BEFORE pub-obsidian's same event handler) to
rewrite both wikilink shapes into plain markdown links.
"""

import os
import posixpath
import re

from markdown.extensions.toc import slugify
from mkdocs.plugins import event_priority

# Match an in-doc heading wikilink (must be `[[#...]]`, not `![[...]]`).
# Forms: `[[#anchor]]` and `[[#anchor|display]]`.
HEADING_WIKILINK_RE = re.compile(r"(?<!\!)\[\[#([^\]\|]+?)(?:\|([^\]]+?))?\]\]")

# Match a file-level wikilink: `[[Name]]` or `[[Name|display]]`.
# Excludes embeds (`![[...]]`) and heading-only links (`[[#...]]`).
FILE_WIKILINK_RE = re.compile(r"(?<!\!)\[\[(?!#)([^\]\|#]+?)(?:#([^\]\|]+))?(?:\|([^\]]+?))?\]\]")

# Files keyed by basename (no extension). Built in on_files, used in on_page_markdown.
_FILE_MAP: dict[str, str] = {}


def on_files(files, config, **_):
    """Build basename → docs-relative-path map for file wikilink resolution."""
    _FILE_MAP.clear()
    for f in files:
        if not f.src_path.endswith(".md"):
            continue
        # Use POSIX-style paths regardless of platform so URLs are consistent.
        rel = f.src_path.replace(os.sep, "/")
        stem = posixpath.basename(rel)[: -len(".md")]
        # If duplicate basenames exist, keep first; that's fine for this vault.
        _FILE_MAP.setdefault(stem, rel)
    return files


def _replace_heading(match: re.Match) -> str:
    anchor_text = match.group(1).strip()
    display = (match.group(2) or anchor_text).strip()
    slug = slugify(anchor_text, "-")
    return f"[{display}](#{slug})"


def _replace_file(match: re.Match, current_src_path: str) -> str:
    name = match.group(1).strip()
    section = match.group(2)
    display = (match.group(3) or name).strip()

    target_rel = _FILE_MAP.get(name)
    if target_rel is None:
        # Leave the wikilink alone — pub-obsidian (or strict mode) will surface it.
        return match.group(0)

    # Compute relative path from current page to target page.
    current_dir = posixpath.dirname(current_src_path.replace(os.sep, "/"))
    rel = posixpath.relpath(target_rel, current_dir or ".") if current_dir else target_rel

    anchor = f"#{slugify(section.strip(), '-')}" if section else ""
    return f"[{display}]({rel}{anchor})"


@event_priority(200)  # Run before pub-obsidian's @event_priority(100)
def on_page_markdown(markdown: str, page=None, **_) -> str:
    if page is None or page.file is None:
        return markdown

    src_path = page.file.src_path
    new = HEADING_WIKILINK_RE.sub(_replace_heading, markdown)
    new = FILE_WIKILINK_RE.sub(lambda m: _replace_file(m, src_path), new)
    return new
