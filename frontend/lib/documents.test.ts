import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { documents, isDocumentKey, readDocument, splitSections, sectionBody } from "./documents.ts";
import { GET } from "../app/source/[document]/route.ts";

test("headings inside fenced code remain content; every section gets a unique anchor", () => {
  const doc = splitSections("# Title\r\nIntro\r\n## Same\r\nBefore\r\n```text\r\n## Not a section\r\n```\r\n## Same\r\nAfter");
  assert.equal(doc.preamble, "Intro");
  assert.equal(doc.sections.length, 2);
  assert.match(doc.sections[0].body, /## Not a section/);
  assert.notEqual(doc.sections[0].id, doc.sections[1].id);
  assert.equal(sectionBody(doc.sections, "same"), doc.sections[0].body);
});

test("unknown keys and inherited properties cannot become source paths", async () => {
  for (const key of ["../.env", "constructor", "__proto__", "README.md", "missing"]) {
    assert.equal(isDocumentKey(key), false);
    const response = await GET(new Request("http://localhost/source/missing"), { params: Promise.resolve({ document: key }) });
    assert.equal(response.status, 404);
  }
});

test("documents are reread after an edit, without restarting the server", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "lfm-docs-"));
  try {
    await writeFile(path.join(root, "README.md"), "# First\n## Purpose\nOriginal");
    assert.equal((await readDocument("overview", root)).sections[0].body, "Original");
    await writeFile(path.join(root, "README.md"), "# First\n## Purpose\nUpdated");
    assert.equal((await readDocument("overview", root)).sections[0].body, "Updated");
    await assert.rejects(() => readDocument("architecture", root), /ENOENT/);
  } finally { await rm(root, {recursive: true, force: true}); }
});

test("all real documents are available and the full hypothesis tree is retained", async () => {
  for (const key of Object.keys(documents) as (keyof typeof documents)[]) {
    const doc = await readDocument(key);
    assert.ok(doc.sections.length > 0);
  }
  const doc = await readDocument("hypothesis");
  assert.ok(doc.sections.some((section) => section.title.startsWith("1. Vehicles")));
  assert.ok(doc.sections.some((section) => section.title.includes("Pricing")));
  assert.ok(sectionBody(doc.sections, "Status tags"));
});
