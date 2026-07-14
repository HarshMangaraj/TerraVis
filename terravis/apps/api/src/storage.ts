import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

// B2 speaks the S3 API, so we point the standard S3Client at B2's endpoint
export const s3 = new S3Client({
  endpoint: process.env.B2_ENDPOINT,
  region: "auto", // B2 doesn't use AWS regions, "auto" satisfies the SDK's requirement
  credentials: {
    accessKeyId: process.env.B2_KEY_ID!,
    secretAccessKey: process.env.B2_APPLICATION_KEY!,
  },
});

export async function uploadFile(key: string, body: Buffer, contentType: string) {
  await s3.send(
    new PutObjectCommand({
      Bucket: process.env.B2_BUCKET,
      Key: key,
      Body: body,
      ContentType: contentType,
    })
  );
  return `${process.env.B2_ENDPOINT}/${process.env.B2_BUCKET}/${key}`;
}