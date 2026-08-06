import assert from "node:assert/strict";
import test from "node:test";

import {
  isZenMuxUrl,
  validateZenMuxApiKey,
  ZENMUX_GOOGLE_BASE_URL,
  ZENMUX_GOOGLE_IMAGE_MODEL,
  ZENMUX_OPENAI_BASE_URL,
  ZENMUX_OPENAI_IMAGE_MODEL,
} from "./zenmux.ts";

test("ZenMux constants pin the two supported image routes", () => {
  assert.equal(ZENMUX_OPENAI_BASE_URL, "https://zenmux.ai/api/v1");
  assert.equal(ZENMUX_GOOGLE_BASE_URL, "https://zenmux.ai/api/vertex-ai");
  assert.equal(ZENMUX_OPENAI_IMAGE_MODEL, "openai/gpt-image-2");
  assert.equal(
    ZENMUX_GOOGLE_IMAGE_MODEL,
    "google/gemini-3.1-flash-image",
  );
});

test("ZenMux URL detection only accepts the exact ZenMux host", () => {
  assert.equal(isZenMuxUrl("https://zenmux.ai/api/v1"), true);
  assert.equal(isZenMuxUrl("https://ZENMUX.AI/api/vertex-ai"), true);
  assert.equal(isZenMuxUrl("https://zenmux.ai.example.com/api/v1"), false);
  assert.equal(isZenMuxUrl("not-a-url"), false);
});

test("ZenMux PAYG key validation catches truncation without exposing the key", () => {
  const valid = `sk-ai-v1-${"a".repeat(64)}`;
  assert.equal(validateZenMuxApiKey(valid), valid);

  const truncated = `sk-ai-v1-${"b".repeat(50)}`;
  assert.throws(
    () => validateZenMuxApiKey(truncated),
    (error: unknown) => {
      const message = error instanceof Error ? error.message : String(error);
      assert.match(message, /incomplete or malformed/);
      assert.doesNotMatch(message, new RegExp(truncated));
      return true;
    },
  );

  assert.throws(
    () => validateZenMuxApiKey(`${valid} `),
    /leading or trailing whitespace/,
  );
});
