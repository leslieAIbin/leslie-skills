export const ZENMUX_OPENAI_BASE_URL = "https://zenmux.ai/api/v1";
export const ZENMUX_GOOGLE_BASE_URL = "https://zenmux.ai/api/vertex-ai";
export const ZENMUX_OPENAI_IMAGE_MODEL = "openai/gpt-image-2";
export const ZENMUX_GOOGLE_IMAGE_MODEL = "google/gemini-3.1-flash-image";

const ZENMUX_PAYG_KEY_PATTERN = /^sk-ai-v1-[a-f0-9]{64}$/i;

export function isZenMuxUrl(value: string): boolean {
  try {
    return new URL(value).hostname.toLowerCase() === "zenmux.ai";
  } catch {
    return false;
  }
}

export function validateZenMuxApiKey(value: string): string {
  if (value !== value.trim()) {
    throw new Error(
      "Invalid ZENMUX_API_KEY: leading or trailing whitespace was detected; copy the complete key again (key omitted).",
    );
  }

  if (value.startsWith("sk-ai-v1-") && !ZENMUX_PAYG_KEY_PATTERN.test(value)) {
    throw new Error(
      `Invalid ZENMUX_API_KEY: the PAYG key is incomplete or malformed (received length ${value.length}; key omitted).`,
    );
  }

  return value;
}

export function getZenMuxApiKey(): string | null {
  const value = process.env.ZENMUX_API_KEY;
  return value ? validateZenMuxApiKey(value) : null;
}

export function zenMuxRequestId(response: Response): string | null {
  return (
    response.headers.get("x-zenmux-requestid") ||
    response.headers.get("x-request-id") ||
    null
  );
}

export function requestIdSuffix(response: Response): string {
  const requestId = zenMuxRequestId(response);
  return requestId ? ` [request id: ${requestId}]` : "";
}
