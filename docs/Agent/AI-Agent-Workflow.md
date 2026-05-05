---
title: AI Agent 工作流总览
category: AI Agent / Claude Code
tags:
  - AI编程
  - ClaudeCode
  - Superpowers
  - gstack
  - Workflow
status: evergreen
updated: 2026-05-04
publish: true
---

# AI Agent 工作流总览

> [!summary] 一句话
> Superpowers 负责工程纪律，gstack 负责真实交付。一个保证代码可信，一个保证产品可用并能上线。

## 快速入口

| 文档 | 适合解决的问题 | 入口 |
| --- | --- | --- |
| Superpowers 项目实战使用指南 | 需求澄清、TDD、调试、审查、验证、分支收尾 | [[Superpowers]] |
| gstack 项目实战使用指南 | 产品诊断、浏览器 QA、安全审计、发布部署、上线监控 | [[gstack]] |

## 分工总览

```mermaid
flowchart LR
    A["需求 / 想法"] --> B["Superpowers<br/>工程纪律"]
    A --> C["gstack<br/>真实交付"]

    B --> B1["brainstorming<br/>需求澄清"]
    B --> B2["writing-plans<br/>实施计划"]
    B --> B3["TDD<br/>先测后写"]
    B --> B4["systematic-debugging<br/>根因调试"]
    B --> B5["code-review<br/>独立审查"]
    B --> B6["verification<br/>完成验证"]

    C --> C1["/office-hours<br/>产品诊断"]
    C --> C2["/autoplan<br/>多视角审查"]
    C --> C3["/qa<br/>真实浏览器 QA"]
    C --> C4["/review / /cso<br/>生产风险和安全"]
    C --> C5["/ship<br/>发布 PR"]
    C --> C6["/canary<br/>上线监控"]
```

## 标准闭环

```mermaid
flowchart TD
    A["需求想法"] --> B["Superpowers<br/>brainstorming"]
    B --> C["gstack<br/>/autoplan"]
    C --> D["Superpowers<br/>writing-plans"]
    D --> E["gstack<br/>/plan-eng-review"]
    E --> F["Superpowers<br/>TDD 编码"]
    F --> G["gstack<br/>/qa"]
    G --> H["Superpowers<br/>verification"]
    H --> I["Superpowers<br/>code review"]
    I --> J["gstack<br/>/review"]
    J --> K["Superpowers<br/>branch finish"]
    K --> L["gstack<br/>/ship"]
    L --> M["gstack<br/>/land-and-deploy"]
    M --> N["gstack<br/>/canary"]
    N --> O["完成"]
```

## 场景速查

| 场景 | 推荐组合 |
| --- | --- |
| 后端 API | `brainstorming` → `writing-plans` → `TDD` → `code review` → `/ship` |
| 前端页面 | `brainstorming` → `/plan-design-review` → `TDD` → `/qa` → `/review` |
| Bug 修复 | `systematic-debugging` → `/investigate` → 回归测试 → `/qa` |
| 快速 MVP | `/office-hours` → `/autoplan` → `/qa` → `/ship` |
| 安全功能 | `brainstorming` → `/cso` → `TDD` → `/cso` → `/ship` |

> [!tip] 使用建议
> 如果你更重视稳定性，以 Superpowers 为主；如果你更重视快速产品验证，以 gstack 为主。两者真正的价值是边界清晰、按阶段接力。
