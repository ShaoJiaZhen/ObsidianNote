---
date: 2026-05-05
topic: obsidian-to-mkdocs-site
status: approved
author: ShaoJiaZhen
brainstormed-with: claude-opus-4-7
publish: false
---

# Obsidian Vault → MkDocs 半公开站点 设计文档

## 1. 目标

把 `ShaoJiaZhen/ObsidianNote` 这个 Obsidian vault 转成一个公开访问的 MkDocs 站点，部署在 GitHub Pages，URL：

```
https://shaojiazhen.github.io/ObsidianNote/
```

读者主要是作者本人，偶尔分享给朋友。

## 2. 核心约束 / 非目标

**核心约束**：
- vault 是单一事实来源，作者完全在 Obsidian 里写作，不接触 build 产物
- 发布是 opt-in 的：默认草稿不公开，只有 `publish: true` 的笔记上站
- 现有 Obsidian 语法（callouts、wikilinks、图片嵌入、mermaid）保留不变，不强制作者改写习惯

**非目标 (v1 不做)**：
- SEO 优化、社交卡片、analytics
- 自定义域名（保留升级空间，v1 用 `*.github.io`）
- 评论 / 留言系统
- RSS / Atom feed
- 自动生成"最近更新"或"按 tag 浏览"等动态首页
- 自动从英文/中文目录名转换为 URL slug

## 3. 关键设计决策

| 决策 | 选项 | 选择 | 理由 |
|---|---|---|---|
| 发布过滤 | A 全部公开 / B opt-in / C opt-out / D 目录白名单 | **B opt-in (`publish: true`)** | 草稿不会被偷看；新笔记默认安全 |
| Obsidian 语法处理 | A 插件 / B 自写预处理 / C 手工迁移 | **A `mkdocs-publisher` 插件** | 同时解决 opt-in + callouts + wikilinks + 嵌图，写作习惯不变 |
| 仓库布局 | A 同 repo gh-pages / B 独立 repo + submodule / C 同 repo + 自定义域名 | **A** | 最少移动件，未来升级到 C 只是加 CNAME |
| 主题 | Material for MkDocs | **Material** | 业界事实标准，CJK / 搜索 / 暗黑模式开箱即用 |
| docs_dir | `docs/` 子目录 / vault 根 | **vault 根** (`docs_dir: .`) | 不破坏 Obsidian 现有目录结构 |

## 4. 架构与数据流

```
作者在 Obsidian 写笔记 (vault = repo 根目录)
    ↓ 给 frontmatter 加 publish: true
git push origin main
    ↓
GitHub Actions 触发 build:
  1. checkout repo (fetch-depth: 0)
  2. pip install mkdocs / material / publisher
  3. mkdocs build --strict
       └── mkdocs-publisher 插件做：
           · 过滤掉 publish ≠ true 的 .md
           · [[wikilink]]               → [text](path/)
           · > [!callout]               → !!! callout
           · ![[image.png]]             → ![](path/image.png)
  4. 输出到 site/
  5. mkdocs gh-deploy → 推到 gh-pages 分支
    ↓
GitHub Pages serve gh-pages 分支
    ↓
读者访问 https://shaojiazhen.github.io/ObsidianNote/
```

**核心特征**：
- vault = source of truth
- build 是无状态、纯派生的：随时可删 `gh-pages` 重 push 重建
- 没有 staging 文件夹、没有同步脚本、没有 submodule

## 5. 仓库新增文件清单

```
ObsidianNote/
├── mkdocs.yml                 ← 主配置
├── requirements.txt           ← 依赖锁定
├── index.md                   ← 站点首页（vault 根目录新建）
├── .github/
│   └── workflows/
│       └── deploy.yml         ← GH Actions
├── overrides/                 ← (空) Material 主题局部覆盖
└── .gitignore                 ← 加 site/ 和 .cache/
```

**不变的东西**：
- 现有 16 篇 .md 的位置和内容
- `.obsidian/` 配置文件夹
- 根目录的 3 张 `Pasted image *.png`
- 现有的 git remote 与 commit 习惯

## 6. mkdocs.yml 关键配置

```yaml
site_name: ShaoJiaZhen's Notes
site_description: 个人知识笔记
site_url: https://shaojiazhen.github.io/ObsidianNote/
repo_url: https://github.com/ShaoJiaZhen/ObsidianNote
repo_name: ShaoJiaZhen/ObsidianNote

docs_dir: .

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

plugins:
  - search:
      lang: [zh, en]
  - publisher:
      publish_default: false      # opt-in 模式
      obsidian:
        wikilinks: true
        callouts: true
        embeds: true

exclude_docs: |
  .obsidian/
  docs/superpowers/
  README.md
  site/
```

> **注**：上面 `plugins.publisher` 的具体 key/value 形式以 `mkdocs-publisher` 实际版本为准；实现阶段对照官方文档校正。

## 7. requirements.txt

```
mkdocs==1.6.*
mkdocs-material==9.5.*
mkdocs-publisher==1.*
```

固定主版本，避免上游 breaking change 把站点弄挂。

## 8. GitHub Actions workflow

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

**行为**：
- push to main → build → 部署
- PR → build 验证 → 不部署
- 手动触发 → 强制重 build 并部署
- build 失败 → gh-pages 不动，邮件通知

## 9. 发布工作流（作者日常）

写新笔记 → 上站，3 步：

```
1. 在 Obsidian 里正常写
2. 写完，frontmatter 加 publish: true
3. git commit && git push
   → 1-2 分钟后站点自动更新
```

frontmatter 示例（基于现有 `Agent/MattPocockSkills.md`）：

```yaml
---
title: Matt Pocock Skills 项目实战使用指南
category: AI Agent / Claude Code / Engineering Workflow
tags:
  - AI编程
status: evergreen
updated: 2026-05-05
publish: true          ← 新增
---
```

**取消发布**：把 `publish: true` 改成 `publish: false` 或删掉 → 下次 push 该页消失。

## 10. 首期上站候选 (4 篇)

第一次部署后，手动给以下成熟笔记加 `publish: true`：

- `Agent/Superpowers.md`
- `Agent/gstack.md`
- `Agent/MattPocockSkills.md`
- `Agent/AI-Agent-Workflow.md`

> **不脚本批量加**：避免误发；作者一篇一篇过一遍内容确认可公开。

## 11. 站点首页 (`index.md`)

vault 根目录新建 `index.md`，内容草稿：

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

## 12. 边缘情况与处理

| 场景 | 行为 | 处理 |
|---|---|---|
| wikilink 指向未发布或不存在的笔记 | `--strict` 让 build 红 | (a) 给目标加 `publish: true` (b) 改成普通文字 (c) 用 publisher 注释语法忽略该行 |
| 图片名带空格 (`Pasted image YYYY...png`) | publisher 自动 URL-encode 能渲染 | 不动；建议改 Obsidian 默认让新图片无空格 |
| CJK 目录进 URL | 渲染为 `%E8%BD%AF...`，能用但丑 | v1 不处理；以后单页用 `slug:` frontmatter 覆盖 |
| Mermaid 渲染 | mkdocs-material + `pymdownx.superfences` 启用即可 | 已在 mkdocs.yml 里配 |
| 空 callout 类型 (`[!check]` `[!quote]`) | Material 默认列表外，落到 `note` 样式 | v1 接受默认；后期可加 `extra.css` 自定义 |
| 私密笔记误标 `publish: true` | 一旦 push 即公开，CDN 缓存有滞后 | 私密笔记显式标 `publish: false` 锁定，避免误改 |

## 13. 测试与验证

文档站点不写自动化测试，验证靠以下手段：

**本地预览**：
```bash
mkdocs serve
# → http://127.0.0.1:8000
```

**PR 验证**：每个 PR 跑一次 `mkdocs build --strict`，红就改。

**首次部署 smoke test 清单**：
- [ ] 首页 (`/`) 正常打开
- [ ] 4 篇 Agent 笔记侧栏可见
- [ ] mermaid 图正确渲染
- [ ] callouts 显示为彩色块（不是裸引用）
- [ ] wikilinks 跳转正确，不出现 `[[xxx]]` 字面值
- [ ] 没标 `publish: true` 的笔记**不出现**在搜索结果与侧栏
- [ ] 暗黑模式切换正常
- [ ] 中文搜索能匹配（搜"superpowers"和"工程纪律"都应有结果）
- [ ] 图片正常显示，包括含空格的文件名

**回滚**：
- build 失败 → gh-pages 自动保持上一次成功版本
- 内容回滚 → `git revert <commit> && git push`

## 14. 实现验收标准

实现完成的判定：

- [ ] 仓库新增 `mkdocs.yml`、`requirements.txt`、`.github/workflows/deploy.yml`、`index.md`、`.gitignore`
- [ ] 4 篇 Agent 笔记加上 `publish: true`
- [ ] GitHub Pages Settings → Source 配置完成
- [ ] 第一次 push 后 Actions 绿，gh-pages 分支自动建出
- [ ] `https://shaojiazhen.github.io/ObsidianNote/` 可访问
- [ ] §13 smoke test 9 项全部通过

## 15. 未解决问题 / 后期可能改动

- **`mkdocs-publisher` 配置语法的具体 key/value** — 实现时对照官方 README 校正，不影响整体架构
- **`exclude_docs` 是否能精确排除 `docs/superpowers/`** — 部分 mkdocs 版本要用 glob，实现时验证
- **CJK 目录 slug 化** — 看上线后实际 URL 长什么样再决定要不要做
- **首页"推荐阅读"列表自动生成** — v1 手写，未来如果笔记多到手维护不动，再用 publisher 的列表生成或自定义 macro

## 16. 决策日志（brainstorming 过程）

| 问 | 选 |
|---|---|
| 受众 | B 半公开（GitHub Pages 公开，主要给自己） |
| 发布策略 | B opt-in (`publish: true`) |
| 语法处理 | A `mkdocs-publisher` 插件 |
| 仓库布局 | A 同 repo + gh-pages 分支 |
| 站点标题 | `ShaoJiaZhen's Notes` |
| 首页 | 由 Claude 起草，作者批准 |
