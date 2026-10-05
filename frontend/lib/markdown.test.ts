import { test } from "node:test";
import assert from "node:assert/strict";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { Markdown } from "../components/markdown.tsx";

test("GFM tables and code trees render without executing raw HTML", () => {
  const content = "| Fuel | Value |\n| --- | --- |\n| Diesel | 1 |\n\n```text\nDemand ? supply\n```\n\n<script>alert(1)</script>";
  const html = renderToStaticMarkup(createElement(Markdown, { children: content }));
  assert.ok(html.includes("<table>"));
  assert.ok(html.includes("Demand ? supply"));
  assert.ok(!html.includes("<script>"));
});
