#!/usr/bin/env node
// One-time data fix: rewrite leftover Supabase Storage URLs baked into
// posts.content / posts.featured_image_path (from the Jun 8 WordPress
// import) to point at R2 instead. The Jul 5 R2 migration moved the storage
// objects and fixed the code paths, but never touched these pre-existing
// absolute URLs sitting in the database — they were still serving images
// straight from Supabase Storage on every pageview. Safe to re-run: only
// rows that still contain the old prefix are updated.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SUPABASE_BUCKET = process.argv[2] || 'cat-images';
const OLD_PREFIX = `https://sitmziehzhvqeftydtdr.supabase.co/storage/v1/object/public/${SUPABASE_BUCKET}/`;

function loadEnvLocal() {
  const envPath = path.join(__dirname, '..', '.env.local');
  const content = fs.readFileSync(envPath, 'utf8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

loadEnvLocal();

const { PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE, R2_PUBLIC_URL } = process.env;
for (const [name, value] of Object.entries({ PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE, R2_PUBLIC_URL })) {
  if (!value) {
    console.error(`Missing required env var: ${name} (check .env.local)`);
    process.exit(1);
  }
}

const NEW_PREFIX = `${R2_PUBLIC_URL}/`;

async function fetchAffectedRows() {
  const url =
    `${PUBLIC_SUPABASE_URL}/rest/v1/posts` +
    `?select=id,slug,content,featured_image_path` +
    `&or=(content.ilike.*supabase.co%2Fstorage*,featured_image_path.ilike.*supabase.co*)`;
  const res = await fetch(url, {
    headers: {
      apikey: SUPABASE_SERVICE_ROLE,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE}`,
    },
  });
  if (!res.ok) throw new Error(`Fetch failed: HTTP ${res.status} ${await res.text()}`);
  return res.json();
}

async function patchRow(id, body) {
  const res = await fetch(`${PUBLIC_SUPABASE_URL}/rest/v1/posts?id=eq.${id}`, {
    method: 'PATCH',
    headers: {
      apikey: SUPABASE_SERVICE_ROLE,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`PATCH ${id} failed: HTTP ${res.status} ${await res.text()}`);
}

function replaceAll(str) {
  return str.split(OLD_PREFIX).join(NEW_PREFIX);
}

async function main() {
  const rows = await fetchAffectedRows();
  console.log(`Found ${rows.length} row(s) with a legacy Supabase Storage URL.\n`);

  let updated = 0;
  let contentChanged = 0;
  let featuredChanged = 0;
  const failed = [];

  for (const row of rows) {
    const body = {};
    if (row.content && row.content.includes(OLD_PREFIX)) {
      body.content = replaceAll(row.content);
      contentChanged++;
    }
    if (row.featured_image_path && row.featured_image_path.includes(OLD_PREFIX)) {
      body.featured_image_path = replaceAll(row.featured_image_path);
      featuredChanged++;
    }
    if (Object.keys(body).length === 0) continue;

    try {
      await patchRow(row.id, body);
      updated++;
      console.log(`updated: ${row.slug}`);
    } catch (err) {
      failed.push({ id: row.id, slug: row.slug, error: err.message });
    }
  }

  console.log('\n=== Summary ===');
  console.log(`Rows updated:       ${updated}`);
  console.log(`content rewritten:  ${contentChanged}`);
  console.log(`featured rewritten: ${featuredChanged}`);
  console.log(`Failed:             ${failed.length}`);
  if (failed.length > 0) {
    console.log('\nFailures:');
    for (const f of failed) console.log(`  - ${f.slug} (${f.id}): ${f.error}`);
    process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error('Script crashed:', err?.message || err);
  process.exit(1);
});
