import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const R2_ACCOUNT_ID = import.meta.env.R2_ACCOUNT_ID;
const R2_ACCESS_KEY_ID = import.meta.env.R2_ACCESS_KEY_ID;
const R2_SECRET_ACCESS_KEY = import.meta.env.R2_SECRET_ACCESS_KEY;
const R2_ENDPOINT = import.meta.env.R2_ENDPOINT;

export const R2_BUCKET_NAME = import.meta.env.R2_BUCKET_NAME;
export const R2_PUBLIC_URL = import.meta.env.R2_PUBLIC_URL;

export const r2Client = new S3Client({
  region: 'auto',
  endpoint: R2_ENDPOINT || `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

// Same key convention as the Supabase "cat-images" bucket this replaces, so
// existing storage_path values (and the ones written going forward) resolve
// unchanged: <R2_PUBLIC_URL>/<path>.
export function getR2PublicUrl(path: string): string {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${R2_PUBLIC_URL}/${path}`;
}

export async function uploadToR2(path: string, body: Buffer, contentType: string): Promise<void> {
  await r2Client.send(
    new PutObjectCommand({
      Bucket: R2_BUCKET_NAME,
      Key: path,
      Body: body,
      ContentType: contentType,
      ContentLength: body.length,
    })
  );
}
