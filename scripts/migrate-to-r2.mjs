#!/usr/bin/env node
// One-time migration: copy every object in the Supabase "cat-images" storage
// bucket into the Cloudflare R2 bucket at the same key. Read-only against
// Supabase — never deletes or modifies anything there. Safe to re-run:
// existing R2 objects are skipped via HeadObjectCommand.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createClient } from '@supabase/supabase-js';
import { S3Client, PutObjectCommand, HeadObjectCommand } from '@aws-sdk/client-s3';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SUPABASE_BUCKET = 'cat-images';
const PROGRESS_INTERVAL = 20;
const RETRIES = 2;
const RETRY_BASE_DELAY_MS = 500;

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

const {
  PUBLIC_SUPABASE_URL,
  SUPABASE_SERVICE_ROLE,
  R2_ACCOUNT_ID,
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_BUCKET_NAME,
  R2_ENDPOINT,
} = process.env;

const required = {
  PUBLIC_SUPABASE_URL,
  SUPABASE_SERVICE_ROLE,
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_BUCKET_NAME,
};
for (const [name, value] of Object.entries(required)) {
  if (!value) {
    console.error(`Missing required env var: ${name} (check .env.local)`);
    process.exit(1);
  }
}
if (!R2_ENDPOINT && !R2_ACCOUNT_ID) {
  console.error('Missing required env var: either R2_ENDPOINT or R2_ACCOUNT_ID must be set (check .env.local)');
  process.exit(1);
}

const supabase = createClient(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE);

const s3 = new S3Client({
  region: 'auto',
  endpoint: R2_ENDPOINT || `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

async function retry(fn, { retries = RETRIES, baseDelay = RETRY_BASE_DELAY_MS } = {}) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, baseDelay * 2 ** attempt));
      }
    }
  }
  throw lastErr;
}

// Supabase Storage .list() is not recursive and paginates at up to 1000
// entries; folders come back as entries with a null id/metadata.
async function listAllFiles(prefix = '') {
  const files = [];
  const limit = 1000;
  let offset = 0;

  while (true) {
    const { data, error } = await supabase.storage.from(SUPABASE_BUCKET).list(prefix, {
      limit,
      offset,
      sortBy: { column: 'name', order: 'asc' },
    });
    if (error) throw new Error(`List failed for prefix "${prefix}": ${error.message}`);
    if (!data || data.length === 0) break;

    for (const entry of data) {
      if (entry.name === '.emptyFolderPlaceholder') continue;
      const fullPath = prefix ? `${prefix}/${entry.name}` : entry.name;
      const isFolder = entry.id === null && entry.metadata === null;
      if (isFolder) {
        files.push(...(await listAllFiles(fullPath)));
      } else {
        files.push(fullPath);
      }
    }

    if (data.length < limit) break;
    offset += limit;
  }

  return files;
}

async function existsInR2(key) {
  try {
    await s3.send(new HeadObjectCommand({ Bucket: R2_BUCKET_NAME, Key: key }));
    return true;
  } catch (err) {
    if (err?.$metadata?.httpStatusCode === 404 || err?.name === 'NotFound') return false;
    throw err;
  }
}

function encodeStoragePath(key) {
  return key.split('/').map(encodeURIComponent).join('/');
}

async function downloadFromSupabase(key) {
  const url = `${PUBLIC_SUPABASE_URL}/storage/v1/object/public/${SUPABASE_BUCKET}/${encodeStoragePath(key)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download failed with HTTP ${res.status}`);
  const contentType = res.headers.get('content-type') || 'application/octet-stream';
  const buffer = Buffer.from(await res.arrayBuffer());
  return { buffer, contentType };
}

async function uploadToR2(key, buffer, contentType) {
  await s3.send(
    new PutObjectCommand({
      Bucket: R2_BUCKET_NAME,
      Key: key,
      Body: buffer,
      ContentType: contentType,
      ContentLength: buffer.length,
    })
  );
}

async function main() {
  console.log(`Listing objects in Supabase bucket "${SUPABASE_BUCKET}"...`);
  const files = await listAllFiles('');
  const total = files.length;
  console.log(`Found ${total} file(s).\n`);

  let uploaded = 0;
  let skipped = 0;
  const failed = [];

  for (let i = 0; i < total; i++) {
    const key = files[i];
    try {
      const already = await retry(() => existsInR2(key));
      if (already) {
        skipped++;
      } else {
        const { buffer, contentType } = await retry(() => downloadFromSupabase(key));
        await retry(() => uploadToR2(key, buffer, contentType));
        uploaded++;
      }
    } catch (err) {
      failed.push({ path: key, error: err?.message || String(err) });
    }

    const done = i + 1;
    if (done % PROGRESS_INTERVAL === 0 || done === total) {
      console.log(`${done}/${total} done`);
    }
  }

  console.log('\n=== Migration Summary ===');
  console.log(`Total files found:  ${total}`);
  console.log(`Uploaded:           ${uploaded}`);
  console.log(`Skipped (existed):  ${skipped}`);
  console.log(`Failed:             ${failed.length}`);
  if (failed.length > 0) {
    console.log('\nFailures:');
    for (const f of failed) {
      console.log(`  - ${f.path}: ${f.error}`);
    }
  }

  if (failed.length > 0) process.exitCode = 1;
}

main().catch((err) => {
  console.error('Migration script crashed:', err?.message || err);
  process.exit(1);
});
