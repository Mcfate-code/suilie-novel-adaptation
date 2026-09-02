#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const [provider, requestedModel] = process.argv.slice(2);
if (!provider || !requestedModel) {
  throw new Error("usage: node run_novel_sample_benchmark.mjs <openai|anthropic> <model>");
}

const workspace = resolve(import.meta.dirname, "..");
const promptFile = resolve(workspace, "模型样章盲测", "01_统一提示词.md");
const promptDocument = readFileSync(promptFile, "utf8");
const separator = "\n---\n";
const separatorIndex = promptDocument.indexOf(separator);
if (separatorIndex === -1) {
  throw new Error("benchmark prompt separator is missing");
}
const prompt = promptDocument.slice(separatorIndex + separator.length).trim();

const system = [
  "你是中文长篇小说作者，正在参加匿名同题试写。",
  "严格遵守用户提供的 canon、视角、情节和禁止事项。",
  "只输出小说正文，不输出思考过程、标题、说明或自评。",
].join("");

async function postJson(url, headers, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  const responseText = await response.text();
  let data;
  try {
    data = JSON.parse(responseText);
  } catch {
    throw new Error(`HTTP ${response.status}: non-JSON response`);
  }
  if (!response.ok) {
    const safeMessage = data?.error?.message || data?.message || `HTTP ${response.status}`;
    throw new Error(`HTTP ${response.status}: ${safeMessage}`);
  }
  return data;
}

let content;
let usage;
let responseModel;

if (provider === "openai") {
  const activeIndex = process.env.OPENCODEGO_ACTIVE_KEY_INDEX;
  const apiKey = process.env[`OPENCODEGO_API_KEY_${activeIndex}`];
  const url = process.env.OPENCODEGO_CHAT_COMPLETIONS_URL;
  if (!apiKey || !url) {
    throw new Error("OpenCodeGo credentials or endpoint are unavailable");
  }

  const body = {
    model: requestedModel,
    messages: [
      { role: "system", content: system },
      { role: "user", content: prompt },
    ],
    stream: false,
  };
  if (requestedModel === "kimi-k3") {
    body.temperature = Number(process.env.OPENCODEGO_KIMI_TEMPERATURE || "1");
    body.max_completion_tokens = 8192;
  } else {
    body.max_tokens = 4096;
  }

  const data = await postJson(
    url,
    { authorization: `Bearer ${apiKey}` },
    body,
  );
  content = data?.choices?.[0]?.message?.content;
  usage = data?.usage;
  responseModel = data?.model || requestedModel;
} else if (provider === "anthropic") {
  const apiKey = process.env.TBTK_API_KEY;
  const baseUrl = process.env.TBTK_BASE_URL;
  if (!apiKey || !baseUrl) {
    throw new Error("TBTK Claude credentials or endpoint are unavailable");
  }

  const data = await postJson(
    `${baseUrl.replace(/\/$/, "")}/messages`,
    {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    {
      model: requestedModel,
      system,
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    },
  );
  content = data?.content
    ?.filter((block) => block?.type === "text")
    .map((block) => block.text)
    .join("\n");
  usage = data?.usage;
  responseModel = data?.model || requestedModel;
} else {
  throw new Error(`unsupported provider: ${provider}`);
}

if (!content || typeof content !== "string") {
  throw new Error("model response did not contain text content");
}

process.stdout.write(JSON.stringify({
  requestedModel,
  responseModel,
  content: content.trim(),
  usage: usage || null,
}, null, 2));
process.stdout.write("\n");

