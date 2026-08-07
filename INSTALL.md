# 安装与新机器恢复

## 1. 前置工具

- Git 与 GitHub CLI (`gh`)
- CC Switch
- Node.js / npm
- Bun（仅部分 JavaScript Skill 需要）
- Claude Code、Codex、OpenCode 中实际要使用的客户端

## 2. 恢复个人仓库

只在目标目录尚不存在时执行：

```bash
gh auth login -h github.com -p https -w
mkdir -p ~/.agents
gh repo clone leslieAIbin/leslie-skills ~/.agents/skills
```

不要把仓库克隆进 `~/.claude/skills`、`~/.codex/skills` 或
`~/.opencode/skills`；这些目录只承载 CC Switch 创建的软链接。

## 3. 配置 CC Switch

设置：

```text
Skills 存储位置：~/.agents/skills
Skills 同步方式：软链接
```

然后：

1. 在 Skills 页面选择“导入已有”。
2. 为 Claude Code、Codex、OpenCode 启用个人仓库中的 Skill。
3. 在“仓库管理”中添加飞书官方仓库：

```text
Owner: larksuite
Name: cli
Branch: main
Subdirectory: skills
```

4. 安装 [SKILLS.md](SKILLS.md) 中列出的 17 个正式 `lark-*` Skill。

必须填写 `Subdirectory: skills`，否则 CC Switch 会把仓库测试夹具误识别为 Skill。

## 4. 恢复本地依赖

```bash
for skill in leslie-diagram leslie-markdown-to-html leslie-post-to-wechat leslie-post-to-x; do
  scripts="$HOME/.agents/skills/$skill/scripts"
  if [ -f "$scripts/package.json" ]; then
    (cd "$scripts" && bun install)
  fi
done
```

API Key 只写入本机环境或对应的本机 `.env`，不得提交到仓库。

## 5. 安装和配置飞书 CLI

```bash
npm install -g @larksuite/cli@latest
lark-cli --version
```

首次初始化需要在浏览器登录飞书，并可能需要企业管理员审批：

```bash
lark-cli config init --new --brand feishu --lang zh_cn
```

不要在聊天、命令参数或 Git 仓库中粘贴 App Secret、Access Token 或 Cookie。
完成应用初始化后，按实际使用范围增量申请 user 权限，不使用无必要的全量授权。

## 6. 验证

```bash
find ~/.agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
find -L ~/.claude/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
find -L ~/.codex/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
find -L ~/.opencode/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
lark-cli auth status --json --verify
```

如果自动化环境无法访问 macOS 钥匙串，应优先在正常终端中运行验证；不要为了省事
把钥匙串主密钥降级为普通文件。
