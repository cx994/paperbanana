# 自定义 Google GenAI `base_url`（代理/网关）使用说明

PaperBanana 默认通过 `google-genai` SDK 直连 Gemini 官方服务（使用 `GOOGLE_API_KEY`）。
如果你有 API Gateway / 代理服务器，需要把请求转发到自定义地址，可以通过环境变量启用自定义 `base_url`。

## 配置项（环境变量）

在 `.env` 或进程环境里设置：

- `GOOGLE_GENAI_BASE_URL`：你的网关地址（例如 `https://test-api-gateway-proxy.com`）
- `GOOGLE_GENAI_USE_VERTEXAI`：是否按 Vertex AI 方式调用（可选）
  - `true`：Vertex AI 风格（默认：当设置了 `GOOGLE_GENAI_BASE_URL` 且未显式指定时）
  - `false`：Gemini Developer API 风格（你的网关实现了 `/v1beta/...` 路径时使用）
- 鉴权（二选一，推荐前者）：
  - `GOOGLE_GENAI_AUTHORIZATION`：完整的 Authorization 头值（例如 `Bearer <token>`）
  - `GOOGLE_GENAI_AUTH_TOKEN`：仅 token（程序会自动拼成 `Bearer <token>`）

启用 `GOOGLE_GENAI_BASE_URL` 后：

- 默认情况下，VLM（分析/规划/评测）与图像生成都会走该 `base_url`。
- PaperBanana 会用 `google-genai` SDK 创建 Client，并把 `base_url`/`Authorization` 注入到 `http_options`。
- 当 `GOOGLE_GENAI_USE_VERTEXAI=false` 时，`google-genai` SDK 需要一个 API key 值（可用
  `GOOGLE_API_KEY` 或 VLM/IMAGE 覆盖；若你的网关只看 Authorization，也可填任意非空占位）。

### 分别给 VLM / Image 配不同的 base_url / key

如果你希望 **Flash（VLM）** 和 **Image（Imagen）** 走不同的网关或不同的 key，可以用以下环境变量覆盖（优先级：组件专用 > 全局默认）：

- VLM 专用：
  - `VLM_GOOGLE_API_KEY`
  - `VLM_GOOGLE_GENAI_BASE_URL`
  - `VLM_GOOGLE_GENAI_USE_VERTEXAI`
  - `VLM_GOOGLE_GENAI_AUTHORIZATION` / `VLM_GOOGLE_GENAI_AUTH_TOKEN`
- Image 专用：
  - `IMAGE_GOOGLE_API_KEY`
  - `IMAGE_GOOGLE_GENAI_BASE_URL`
  - `IMAGE_GOOGLE_GENAI_USE_VERTEXAI`
  - `IMAGE_GOOGLE_GENAI_AUTHORIZATION` / `IMAGE_GOOGLE_GENAI_AUTH_TOKEN`

## CLI 用法

1) 复制并编辑：

```bash
cp .env.example .env
```

2) 在 `.env` 中填写：

```bash
GOOGLE_GENAI_BASE_URL=https://test-api-gateway-proxy.com
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_GENAI_AUTHORIZATION=Bearer test_token
```

3) 运行一次最小端到端生成（会同时测试 VLM + 图片接口）：

```bash
paperbanana generate -i examples/sample_inputs/transformer_method.txt -c "smoke test" -n 1
```

## MCP 用法

MCP Server 会读取运行进程的环境变量来构建 `Settings`。建议在 MCP 客户端配置的 `env` 中显式传入：

```json
{
  "GOOGLE_GENAI_BASE_URL": "https://test-api-gateway-proxy.com",
  "GOOGLE_GENAI_USE_VERTEXAI": "true",
  "GOOGLE_GENAI_AUTHORIZATION": "Bearer test_token"
}
```

## 快速连通性测试（仅测 VLM）

如果你想先验证“文本请求能通”（更快、更省配额），可运行：

```bash
python - <<'PY'
import asyncio
from paperbanana.core.config import Settings
from paperbanana.providers.registry import ProviderRegistry

async def main():
    s = Settings(vlm_provider="gemini")
    vlm = ProviderRegistry.create_vlm(s)
    print(await vlm.generate("Reply with OK only.", max_tokens=8, temperature=0))

asyncio.run(main())
PY
```

## 排查建议

- 401/403：检查 `GOOGLE_GENAI_AUTHORIZATION` 是否正确、是否带 `Bearer ` 前缀。
- 404：通常是网关路由未覆盖 `google-genai` 所请求的路径；优先查看网关 access log。
- 证书问题：可设置 `SKIP_SSL_VERIFICATION=true`（仅用于受信任网络/临时排查）。
