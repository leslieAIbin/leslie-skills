# Leslie Skills

Leslie 的跨 Agent Skill 单一源码仓库。

## 本地结构

- 主目录：`~/.agents/skills`
- Claude Code：由 CC Switch 软链接到 `~/.claude/skills`
- Codex：由 CC Switch 软链接到 `~/.codex/skills`
- OpenCode：由 CC Switch 软链接到 `~/.opencode/skills`

## 新机器恢复

```bash
gh auth login -h github.com -p https -w
mkdir -p ~/.agents
gh repo clone leslieAIbin/leslie-skills ~/.agents/skills
```

恢复 JavaScript Skill 的本地依赖：

```bash
for skill in leslie-diagram leslie-markdown-to-html leslie-post-to-wechat leslie-post-to-x; do
  (cd "$HOME/.agents/skills/$skill/scripts" && bun install)
done
```

然后在 CC Switch 中：

1. 将 Skills 存储位置设为 `~/.agents/skills`。
2. 选择“导入已有”。
3. 为 Claude、Codex、OpenCode 启用需要的 Skill。
4. Skills 同步方式选择“软链接”。

## 日常更新

```bash
git -C ~/.agents/skills pull --ff-only
git -C ~/.agents/skills status
git -C ~/.agents/skills add .
git -C ~/.agents/skills commit -m "Update skills"
git -C ~/.agents/skills push
```

## 安全边界

- 不提交 API Key、Token、Cookie、私钥或 `.env`。
- `leslie-agent-memory` 的 Memory Home 是独立数据目录，不属于本仓库。
- `node_modules`、缓存、运行状态和导出结果不进入版本库。
- JavaScript 依赖通过各 Skill 自带的 `package.json` 与 lockfile 恢复。
