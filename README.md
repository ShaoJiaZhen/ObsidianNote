# ShaoJiaZhen's Notes

我个人的工程与产品笔记。Obsidian vault → MkDocs 站点。

**Live site**: <https://shaojiazhen.github.io/ObsidianNote/>

主要写给自己看，放在公网上方便偶尔分享。

## 发布机制

opt-in：只有 frontmatter 标了 `publish: true` 的笔记才会上站。其他都默认隐藏。

```yaml
---
title: 笔记标题
publish: true
---
```

push 到 `main` → GitHub Actions 自动 build + 部署到 `gh-pages` 分支 → 站点 1-2 分钟内更新。

取消发布：把 `publish: true` 改成 `false` 或删掉，下次 push 该页消失。

## 本地预览

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
mkdocs serve
# → http://127.0.0.1:8000/
```

## 仓库结构

```
docs/                    MkDocs 内容根；vault 笔记按主题分目录
  Agent/                 AI 编程方法论（已发布）
  Github/                GitHub 项目笔记（默认未发布）
  软件开发/              技术栈学习记录（默认未发布）
  工作记录/              工作日志（默认未发布）
  其他/                  杂项（默认未发布）
  superpowers/           本仓的 brainstorm/spec/plan，构建时排除
mkdocs.yml               站点配置（Material + mkdocs-publisher）
_mkdocs_hooks.py         自定义 hook：修 pub-obsidian 的 wikilink 限制
.github/workflows/       CI：push to main → build + gh-deploy
requirements.txt         锁定 mkdocs / material / publisher 主版本
```

## 技术栈

- [MkDocs](https://www.mkdocs.org/) 1.6
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 9.5
- [mkdocs-publisher](https://mkdocs-publisher.github.io/) 1.4（`pub-meta` opt-in + `pub-obsidian` 语法）
- GitHub Actions + GitHub Pages

## License

笔记内容版权所有。代码部分（mkdocs.yml、`_mkdocs_hooks.py`、workflow）你可以自由参考。
