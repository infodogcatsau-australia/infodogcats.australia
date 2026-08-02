#!/usr/bin/env node
// One-time migration: copy the 9 objects still referenced from the Supabase
// "cats" storage bucket (a second bucket the original cat-images -> R2
// migration never covered) into R2 at the same key. Read-only against
// Supabase. Each upload is verified with a live HEAD request against the
// new R2 URL before being reported as done — nothing downstream should
// point at an R2 key until it's confirmed serving.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SUPABASE_BUCKET = 'cats';

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
  R2_ACCOUNT_ID,
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_BUCKET_NAME,
  R2_ENDPOINT,
  R2_PUBLIC_URL,
} = process.env;

const KEYS = JSON.parse(
  fs.readFileSync(
    'C:/Users/MEBROU~1/AppData/Local/Temp/claude/c--Users-Mebrouk-Hassan-Desktop-infodigcats-proper-photon/1dca4c43-843b-4732-928b-d0f84bc1cc7b/scratchpad/cats_bucket_keys.json',
    'utf8'
  )
);

const s3 = new S3Client({
  region: 'auto',
  endpoint: R2_ENDPOINT || `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

function encodeStoragePath(key) {
  return key.split('/').map(encodeURIComponent).join('/');
}

async function downloadFromSupabase(key) {
  const url = `${PUBLIC_SUPABASE_URL}/storage/v1/object/public/${SUPABASE_BUCKET}/${encodeStoragePath(key)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download failed with HTTP ${res.status} for ${url}`);
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

async function verifyLiveOnR2(key, expectedLength) {
  const url = `${R2_PUBLIC_URL}/${encodeStoragePath(key)}`;
  const res = await fetch(url, { method: 'HEAD' });
  if (!res.ok) return { ok: false, url, status: res.status };
  const len = Number(res.headers.get('content-length') || -1);
  if (len !== expectedLength) {
    return { ok: false, url, status: res.status, note: `content-length ${len} != uploaded ${expectedLength}` };
  }
  return { ok: true, url, status: res.status, contentType: res.headers.get('content-type') };
}

async function main() {
  console.log(`Migrating ${KEYS.length} object(s) from Supabase bucket "${SUPABASE_BUCKET}" to R2...\n`);

  const results = [];
  for (const key of KEYS) {
    process.stdout.write(`- ${key} ... `);
    try {
      const { buffer, contentType } = await downloadFromSupabase(key);
      await uploadToR2(key, buffer, contentType);
      const verify = await verifyLiveOnR2(key, buffer.length);
      if (!verify.ok) {
        console.log(`UPLOAD OK but VERIFY FAILED (${JSON.stringify(verify)})`);
        results.push({ key, ok: false, reason: 'verify_failed', verify });
      } else {
        console.log(`OK (${buffer.length} bytes, ${verify.contentType}) -> ${verify.url}`);
        results.push({ key, ok: true, url: verify.url, bytes: buffer.length });
      }
    } catch (err) {
      console.log(`FAILED: ${err.message}`);
      results.push({ key, ok: false, reason: 'error', error: err.message });
    }
  }

  const failed = results.filter((r) => !r.ok);
  console.log('\n=== Summary ===');
  console.log(`Total: ${results.length}, OK: ${results.length - failed.length}, Failed: ${failed.length}`);

  fs.writeFileSync(
    'C:/Users/MEBROU~1/AppData/Local/Temp/claude/c--Users-Mebrouk-Hassan-Desktop-infodigcats-proper-photon/1dca4c43-843b-4732-928b-d0f84bc1cc7b/scratchpad/cats_bucket_migration_results.json',
    JSON.stringify(results, null, 2)
  );

  if (failed.length > 0) process.exitCode = 1;
}

main().catch((err) => {
  console.error('Script crashed:', err?.message || err);
  process.exit(1);
});
