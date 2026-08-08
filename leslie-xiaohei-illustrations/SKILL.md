---
name: leslie-xiaohei-illustrations
description: 为 Leslie 的中文技术文章、公众号长文、帖子、博客、方法论、AI 工作流和工程复盘设计并生成 16:9 白底手绘正文配图。用户提到“文章配图”“小黑”“怪诞手绘”“正文插图”“shot list”“流程隐喻”“生成几张图”或希望把抽象观点画出来时应使用。默认通过本机 leslie-image-gen 适配器调用 ZenMux，只读取 ZENMUX_API_KEY，不要求 OPENAI_API_KEY 或 GOOGLE_API_KEY。
compatibility: "Requires leslie-image-gen, Bun, and ZENMUX_API_KEY; writes PNG and prompt files inside the active workspace."
---

# Leslie 小黑正文配图

## 定位

把 Leslie 中文文章里的关键判断、流程、系统状态和工程隐喻，变成 16:9 横版正文配图。画面应该像一张聪明、克制、略带荒诞感的产品草图，而不是商业插画、PPT 信息图或儿童卡通。

固定角色是“小黑”：黑色实心、白点眼、细腿、空表情，认真参与一个略显荒诞但逻辑成立的动作。小黑必须承担核心动作，不能只是角落里的装饰。

本 Skill 基于 Ian Xiaohei Illustrations 的 MIT 授权版本改造，保留 Ian 的来源署名；Leslie 版本的主要变化是面向技术写作、固定 ZenMux 生图链路、保存可复用提示词，以及默认 normal 质量快速出图。详见 `NOTICE.md`。

## 按需读取

- `references/style-dna.md`：视觉风格、颜色和禁忌。
- `references/xiaohei-ip.md`：小黑角色与 Leslie 版识别细节。
- `references/composition-patterns.md`：构图与原创隐喻方法。
- `references/prompt-template.md`：单张提示词模板。
- `references/backend-zenmux.md`：ZenMux 调用规则；真正生图前必须读取。
- `references/qa-checklist.md`：生成后的检查标准。
- `assets/examples/`：Leslie 自己生成的低频校准图；不要默认复刻。

## 工作流

### 1. 消化内容

先读取用户提供的正文、Markdown、截图或主题，提炼：

- 文章的核心判断
- 承担认知转折的段落
- 值得视觉化的流程、边界、状态或因果关系
- 不需要配图、保留文字更好的部分

不要平均配图。优先选择能让读者停一下并理解文章的“认知锚点”。

### 2. 规划 shot list

如果用户只要求分析配图位置，先输出 shot list，不调用生图。每张图写清楚：

- 放置位置
- 图的主题与核心意思
- 结构类型
- 小黑承担的动作
- 主要物件
- 3–5 个建议中文短标注

短文通常 1–3 张，正常长文 4–6 张，除非内容确有必要，不超过 8 张。

### 3. 生成提示词

用户明确要求生成图片时，按 `references/prompt-template.md` 为每张图单独写提示词。每张图只讲一个核心意思，并为当前文章重新发明物理隐喻。

把提示词保存到：

```text
assets/<article-slug>-illustrations/prompts/NN-topic.md
```

提示词文件不得包含 API Key、Cookie、Token 或未脱敏的公司机密。

### 4. 通过 ZenMux 生图

读取 `references/backend-zenmux.md` 和 `$leslie-image-gen` 的完整说明，然后使用本机 `leslie-image-gen` 适配器。默认参数：

- provider：`openai`
- model：`openai/gpt-image-2`
- credential：只用 `ZENMUX_API_KEY`
- aspect ratio：`16:9`
- quality：`normal`
- output：PNG

不要改用 Codex 内置 `image_gen`，也不要读取或要求 `OPENAI_API_KEY`、`GOOGLE_API_KEY`。如果 ZenMux 不可用，应明确报告原因并停止，不能悄悄切换供应商。

每张输出保存为：

```text
assets/<article-slug>-illustrations/NN-topic.png
```

保留提示词和最终图片。不要覆盖已有文件，除非用户明确要求替换。

### 5. 视觉检查

生成后必须实际打开图片，并按照 `references/qa-checklist.md` 检查。优先修复：

- 小黑只是装饰
- 中文错字或文字过多
- 画面太满、太像 PPT
- 背景不是纯白
- 左上角出现类型标题
- 与旧案例构图过于相似

如果只是少量错字或多余标题，可用相同 ZenMux 后端做参考图编辑；结构性问题应重生成。

## 交付

简洁报告：

- 生成数量
- 每张图对应的正文用途
- 使用的 ZenMux provider/model/quality
- PNG 与提示词保存路径
- 哪些图最稳，哪些建议重做

不要输出或复述任何 API Key。
