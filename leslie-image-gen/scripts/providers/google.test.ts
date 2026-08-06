import assert from "node:assert/strict";
import test, { type TestContext } from "node:test";

import type { CliArgs } from "../types.ts";
import {
  addAspectRatioToPrompt,
  buildGoogleUrl,
  buildPromptWithAspect,
  extractInlineImageData,
  extractPredictedImageData,
  generateImage,
  getDefaultModel,
  getGoogleImageSize,
  isGoogleImagen,
  isGoogleMultimodal,
  normalizeGoogleModelId,
} from "./google.ts";

function useEnv(
  t: TestContext,
  values: Record<string, string | null>,
): void {
  const previous = new Map<string, string | undefined>();
  for (const [key, value] of Object.entries(values)) {
    previous.set(key, process.env[key]);
    if (value == null) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }

  t.after(() => {
    for (const [key, value] of previous.entries()) {
      if (value == null) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  });
}

function makeArgs(overrides: Partial<CliArgs> = {}): CliArgs {
  return {
    prompt: null,
    promptFiles: [],
    imagePath: null,
    provider: null,
    model: null,
    aspectRatio: null,
    size: null,
    quality: null,
    imageSize: null,
    imageApiDialect: null,
    referenceImages: [],
    n: 1,
    batchFile: null,
    jobs: null,
    json: false,
    help: false,
    ...overrides,
  };
}

test("Google provider helpers normalize model IDs and select image size defaults", () => {
  assert.equal(
    normalizeGoogleModelId("models/gemini-3.1-flash-image-preview"),
    "gemini-3.1-flash-image-preview",
  );
  assert.equal(isGoogleMultimodal("models/gemini-3-pro-image-preview"), true);
  assert.equal(isGoogleMultimodal("gemini-3-pro-image"), true);
  assert.equal(isGoogleMultimodal("gemini-3.1-flash-image"), true);
  assert.equal(isGoogleMultimodal("models/gemini-3-pro-image"), true);
  assert.equal(isGoogleImagen("imagen-3.0-generate-002"), true);
  assert.equal(getGoogleImageSize(makeArgs({ imageSize: null, quality: "2k" })), "2K");
  assert.equal(getGoogleImageSize(makeArgs({ imageSize: "4K", quality: "normal" })), "4K");
});

test("Google defaults switch cleanly between direct and ZenMux model IDs", (t) => {
  useEnv(t, { ZENMUX_API_KEY: null, GOOGLE_IMAGE_MODEL: null });
  assert.equal(getDefaultModel(), "gemini-3-pro-image");

  process.env.ZENMUX_API_KEY = `sk-ai-v1-${"a".repeat(64)}`;
  assert.equal(getDefaultModel(), "google/gemini-3.1-flash-image");
});

test("Google ZenMux route prefers ZENMUX_API_KEY over Google keys", async (t) => {
  const zenMuxKey = `sk-ai-v1-${"a".repeat(64)}`;
  useEnv(t, {
    ZENMUX_API_KEY: zenMuxKey,
    GOOGLE_API_KEY: "official-google-key",
    GEMINI_API_KEY: "official-gemini-key",
    GOOGLE_BASE_URL: null,
    ZENMUX_GOOGLE_BASE_URL: null,
    HTTPS_PROXY: null,
    HTTP_PROXY: null,
    ALL_PROXY: null,
    https_proxy: null,
    http_proxy: null,
  });

  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });
  globalThis.fetch = async (input, init) => {
    assert.equal(
      String(input),
      "https://zenmux.ai/api/vertex-ai/v1/publishers/google/models/gemini-3.1-flash-image:generateContent",
    );
    assert.equal(
      new Headers(init?.headers).get("authorization"),
      `Bearer ${zenMuxKey}`,
    );
    return Response.json({
      candidates: [
        {
          content: {
            parts: [
              { inlineData: { data: Buffer.from("zenmux-google").toString("base64") } },
            ],
          },
        },
      ],
    });
  };

  const bytes = await generateImage(
    "test",
    "google/gemini-3.1-flash-image",
    makeArgs({ quality: "normal" }),
  );
  assert.equal(Buffer.from(bytes).toString("utf8"), "zenmux-google");
});

test("Google URL builder appends v1beta when the base URL does not already include it", (t) => {
  useEnv(t, { GOOGLE_BASE_URL: "https://generativelanguage.googleapis.com" });
  assert.equal(
    buildGoogleUrl("models/demo:generateContent"),
    "https://generativelanguage.googleapis.com/v1beta/models/demo:generateContent",
  );
});

test("Google URL and prompt helpers preserve existing v1beta paths and aspect hints", (t) => {
  useEnv(t, { GOOGLE_BASE_URL: "https://example.com/custom/v1beta/" });
  assert.equal(
    buildGoogleUrl("/models/demo:predict"),
    "https://example.com/custom/v1beta/models/demo:predict",
  );

  assert.equal(
    addAspectRatioToPrompt("A city skyline", "16:9"),
    "A city skyline Aspect ratio: 16:9.",
  );
  assert.equal(
    buildPromptWithAspect("A city skyline", "16:9", "2k"),
    "A city skyline Aspect ratio: 16:9. High resolution 2048px.",
  );
});

test("Google response extractors find inline and predicted image payloads", () => {
  assert.equal(
    extractInlineImageData({
      candidates: [
        {
          content: {
            parts: [{ inlineData: { data: "inline-base64" } }],
          },
        },
      ],
    }),
    "inline-base64",
  );

  assert.equal(
    extractPredictedImageData({
      predictions: [{ image: { imageBytes: "predicted-base64" } }],
    }),
    "predicted-base64",
  );

  assert.equal(
    extractPredictedImageData({
      generatedImages: [{ bytesBase64Encoded: "generated-base64" }],
    }),
    "generated-base64",
  );
});
