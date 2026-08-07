# Skill 清单与来源

本文记录可恢复的 Skill、外部来源和本机专用能力。数量是 2026-08-07 的快照。

## 个人仓库：18 个

这些目录随 `leslieAIbin/leslie-skills` 克隆和更新。

| Skill | 用途 | 来源 |
|---|---|---|
| `find-skills` | 发现可安装 Skill | 个人仓库固定版本 |
| `skill-creator` | 创建、优化和评测 Skill | 个人仓库固定版本 |
| `skill-vetter` | 第三方 Skill 安全审查 | ClawHub `@spclaudehome/skill-vetter` |
| `leslie-task-contract` | 跨 Agent 任务契约 | 改造自 `joeseesun/qiaomu-goal-meta-skill` |
| `leslie-agent-memory` | 跨 Agent 长期记忆 | Leslie 定制 |
| `leslie-web-research` | 可追溯的联网调研证据包 | Leslie 定制 |
| `leslie-tech-writer` | Leslie 风格技术文章 | Leslie 定制 |
| `leslie-image-gen` | ZenMux 图片生成 | Leslie 定制 |
| `leslie-cover-image` | 文章封面图 | Leslie 定制 |
| `leslie-article-illustrator` | 文章配图规划与生成 | Leslie 定制 |
| `leslie-infographic` | 信息图 | Leslie 定制 |
| `leslie-diagram` | SVG 技术图 | Leslie 定制 |
| `leslie-markdown-to-html` | 微信兼容 HTML | Leslie 定制 |
| `leslie-post-to-wechat` | 微信公众号草稿 | Leslie 定制，禁止直接发布 |
| `leslie-post-to-x` | X/Twitter 草稿 | Leslie 定制，禁止直接发布 |
| `impeccable` | 全面前端设计和审查 | `pbakaus/impeccable` |
| `design-taste-frontend` | 落地页、作品集和改版设计 | `Leonxlnx/taste-skill` |
| `imagegen-frontend-web` | 按网页区块生成视觉参考图 | `Leonxlnx/taste-skill` |

第三方固定版本的具体来源、许可证和差异记录在各目录的 `UPSTREAM.md`、
`ATTRIBUTION.md`、`LICENSE` 或 `NOTICE.md` 中。

## 飞书官方：17 个

这些 Skill 不提交到个人仓库。CC Switch 直接从以下来源安装：

```text
Owner: larksuite
Name: cli
Branch: main
Subdirectory: skills
```

安装清单：

```text
lark-shared
lark-contact
lark-im
lark-calendar
lark-task
lark-doc
lark-drive
lark-wiki
lark-mail
lark-sheets
lark-base
lark-slides
lark-approval
lark-vc
lark-workflow-standup-report
lark-workflow-meeting-summary
lark-okr
```

`lark-shared` 是认证与安全规则依赖。两个 workflow 分别依赖
`calendar + task` 和 `vc`。禁止安装仓库测试目录里的 `good-skill`、
`bad-skill`、`lark-demo` 或 `cli-e2e-testcase-writer`。

## 本机专用：1 个

| Skill | 原因 |
|---|---|
| `leslie-wechat-local-vault` | 只处理本人有权访问的微信 Mac 本地数据；许可证、隐私和数据边界要求其不得进入公开仓库。 |

## 不属于本仓库的能力

Codex 自带的系统 Skill 和插件 Skill 由 Codex 自己安装和升级，不计入本清单，
也不要复制到 `~/.agents/skills`。
