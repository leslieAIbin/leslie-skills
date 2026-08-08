# ZenMux 生图后端

## 固定路由

本 Skill 不直接请求 OpenAI 或 Google 官方 API，也不调用 Codex 内置 `image_gen`。所有生成都通过本机 `$leslie-image-gen` 适配器进入 ZenMux。

默认配置：

| 项目 | 值 |
|---|---|
| Provider | `openai` |
| Model | `openai/gpt-image-2` |
| Credential | `ZENMUX_API_KEY` |
| Endpoint | `https://zenmux.ai/api/v1` |
| Aspect ratio | `16:9` |
| Quality | `normal` |

`ZENMUX_API_KEY` 从当前环境或 `~/.leslie-skills/.env` 读取。只检查是否存在，不打印、不复制到提示词、不写入日志或生成目录。

即使环境中存在 `OPENAI_API_KEY` 或 `GOOGLE_API_KEY`，也不要使用。调用时显式传入 `--provider openai --model openai/gpt-image-2`，从而让 ZenMux key 和路由具有确定性。

## 脚本位置

先定位 `$leslie-image-gen` 对应目录。常见位置依次是：

```text
$HOME/.agents/skills/leslie-image-gen
$HOME/.codex/skills/leslie-image-gen
```

主入口是 `scripts/main.ts`。优先用 `bun`；不存在时再按 `$leslie-image-gen` 的说明处理。

## 单张调用

```bash
bun "$HOME/.agents/skills/leslie-image-gen/scripts/main.ts" \
  --promptfiles "<prompt-file>" \
  --image "<output.png>" \
  --provider openai \
  --model openai/gpt-image-2 \
  --ar 16:9 \
  --quality normal \
  --json
```

调用前创建并核验具体输出目录。输出路径必须位于当前 workspace 的 `assets/<article-slug>-illustrations/` 内。

## 失败处理

- 缺少 `ZENMUX_API_KEY`：停止并提示只需配置这一个 key。
- HTTP 402：提示检查 ZenMux 余额。
- HTTP 403：提示检查 ZenMux key 或权限；不要重试或切换官方 API。
- 网络或 5xx：遵循 `leslie-image-gen` 的有限重试规则。
- 生成成功但文件不存在：视为失败，不报告完成。
