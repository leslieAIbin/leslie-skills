# 更新流程

不同来源必须分别更新，避免一个工具覆盖另一个工具管理的文件。

## 个人仓库

开始修改前：

```bash
git -C ~/.agents/skills pull --ff-only
git -C ~/.agents/skills status -sb
```

提交时只暂存本次相关文件，不使用无法审计范围的批量提交：

```bash
git -C ~/.agents/skills add README.md SKILLS.md INSTALL.md UPDATE.md
git -C ~/.agents/skills commit -m "Document skill management"
git -C ~/.agents/skills push
```

新增或改造 Skill 时，同时更新 [SKILLS.md](SKILLS.md)，保留许可证和归属信息，
并在提交前扫描密钥、Token、私钥和本地数据。

## 固定版本的第三方 Skill

适用于 `skill-vetter`、`impeccable`、`design-taste-frontend` 和
`imagegen-frontend-web`：

1. 下载上游到临时审查目录。
2. 使用 `skill-vetter` 审查全部文件、网络访问、命令和权限。
3. 与当前版本比较，不直接覆盖本地定制。
4. 更新 `UPSTREAM.md` 中的版本或 commit。
5. 保留上游 `LICENSE`、`NOTICE` 和归属信息。
6. 验证后再提交个人仓库。

## 飞书 Skill 与 CLI

飞书 Skill 由 CC Switch 直接关联 `larksuite/cli/skills`：

```text
CC Switch → Skills → 刷新 → 更新
```

飞书 CLI 使用官方更新命令：

```bash
lark-cli update --check
lark-cli update
```

不要使用 `lark-cli update --force`，除非明确希望恢复官方全部 Skill；强制更新可能
重新加入已经主动排除的 Skill。更新后回到 CC Switch 核对正式安装清单。

`lark-*` 目录由 `.gitignore` 排除，不提交进个人仓库，也不要改名或直接修改内容。

## 本机专用 Skill

`leslie-wechat-local-vault` 不通过公开 GitHub 分发。更新或迁移时必须单独检查许可证、
隐私边界和本地数据目录；任何微信密钥、数据库、状态、报告或导出文件都不得进入
个人公开仓库。

## CC Switch 更新后的检查

确认以下关系仍成立：

```text
~/.claude/skills/<name>   -> ~/.agents/skills/<name>
~/.codex/skills/<name>    -> ~/.agents/skills/<name>
~/.opencode/skills/<name> -> ~/.agents/skills/<name>
```

发现断链时，优先在 CC Switch 中重新启用对应应用，不要手工复制出第二份源码。
