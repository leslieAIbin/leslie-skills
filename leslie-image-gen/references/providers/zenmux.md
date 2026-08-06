# ZenMux image routes

This customized Skill uses one credential and two model families:

| Skill provider | ZenMux model | Protocol | Endpoint |
|---|---|---|---|
| `openai` | `openai/gpt-image-2` | OpenAI Images | `https://zenmux.ai/api/v1/images/generations` (and `/edits`) |
| `google` | `google/gemini-3.1-flash-image` | Vertex AI Generate Content | `https://zenmux.ai/api/vertex-ai/v1/publishers/google/models/gemini-3.1-flash-image:generateContent` |

Set only `ZENMUX_API_KEY`. The adapters choose the endpoint and authentication header automatically:

- OpenAI route: `Authorization: Bearer ...`
- Vertex AI route: `Authorization: Bearer ...`

Optional endpoint overrides are `ZENMUX_OPENAI_BASE_URL` and `ZENMUX_GOOGLE_BASE_URL`. Do not put the key in this file, `EXTEND.md`, source control, or generated prompt files.

The Skill pins the two endpoint defaults and model IDs above. It deliberately does not pin ZenMux's internal upstream provider (for example OpenAI versus Azure): leaving routing to ZenMux gives the gateway room to use an available provider. Only add a provider preference if ZenMux documents and you explicitly need that routing behavior.

## Credential and proxy behavior

- A PAYG key beginning with `sk-ai-v1-` is checked locally for the complete 64-character hexadecimal payload before any paid request. The key is never included in an error message.
- When a ZenMux URL is selected, `ZENMUX_API_KEY` always wins over `OPENAI_API_KEY`, `GOOGLE_API_KEY`, and `GEMINI_API_KEY`. This prevents an official-provider key from accidentally being sent to the ZenMux gateway.
- Standard proxy variables (`HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY`, including lowercase forms) are inherited from the current shell. Do not hard-code a proxy URL into the Skill.
- `403 access_denied` is treated as a credential/configuration failure and is not retried. `402` means the account cannot fund the request. Other transient network/server failures may still retry.
- If a request fails and ZenMux returns `X-ZenMux-RequestId`, keep the request ID when contacting support. The Skill includes it in the error without exposing the key.

Recommended setup:

```bash
export ZENMUX_API_KEY="<complete-key-from-the-ZenMux-console>"
```

Then run the normal `--provider openai` or `--provider google` command. Do not pass the key as a command-line flag because it may be retained in shell history.

For Google image generation the request includes both `TEXT` and `IMAGE` response modalities, as required by the Vertex AI-compatible route.
