# Leslie Skills

Leslie 的跨 Agent Skill 单一源码仓库。个人与经过改造的 Skill 保存在这里；
官方飞书 Skill 由 CC Switch 直接跟踪上游；私密数据型 Skill 仅保留在本机。

## 架构

```text
leslieAIbin/leslie-skills ─┐
                           ├─ CC Switch ─ ~/.agents/skills
larksuite/cli/skills ──────┘                  ├─ ~/.claude/skills
                                             ├─ ~/.codex/skills
                                             └─ ~/.opencode/skills
```

- 唯一运行主目录：`~/.agents/skills`
- 分发方式：CC Switch 软链接
- 个人仓库：`leslieAIbin/leslie-skills`
- 飞书上游：`larksuite/cli` 的 `skills/` 子目录
- 当前清单和来源：[SKILLS.md](SKILLS.md)
- 新机器安装：[INSTALL.md](INSTALL.md)
- 日常更新：[UPDATE.md](UPDATE.md)

## 仓库边界

本仓库提交以下内容：

- Leslie 自有或经过明确改造的 Skill。
- 经安全审查后固定版本的第三方 Skill，保留许可证和 `UPSTREAM.md`。
- 安装、更新、来源和恢复文档。

本仓库不提交：

- `lark-*`：由 CC Switch 直接从 `larksuite/cli/skills` 安装和更新。
- `leslie-wechat-local-vault`：本机私有、非商业使用，不进入公开仓库。
- API Key、Token、Cookie、App Secret、私钥、`.env`。
- Memory Home、微信数据库、明文导出、缓存、日志和运行状态。

## 快速恢复

```bash
gh auth login -h github.com -p https -w
mkdir -p ~/.agents
gh repo clone leslieAIbin/leslie-skills ~/.agents/skills
```

随后按 [INSTALL.md](INSTALL.md) 配置 CC Switch、恢复依赖并安装飞书官方 Skill。

## 外部上游

- `skill-vetter`：ClawHub `@spclaudehome/skill-vetter`，MIT-0。
- `impeccable`：`pbakaus/impeccable`，Apache-2.0；不自动安装 Hooks。
- `design-taste-frontend`：`Leonxlnx/taste-skill`，MIT。
- `imagegen-frontend-web`：`Leonxlnx/taste-skill`，MIT。
- `leslie-task-contract`：基于 `joeseesun/qiaomu-goal-meta-skill` 独立改造，MIT。

更新第三方 Skill 前必须重新安全审查，并同步更新对应的 `UPSTREAM.md`、
许可证和版本记录。
