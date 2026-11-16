interface B2Authorization {
  downloadUrl: string;
  authorizationToken: string;
}

let cachedAuthorization: B2Authorization | null = null;
let cachedAt = 0;
const AUTH_CACHE_MS = 20 * 60 * 1000;

function getConfig() {
  const keyId = process.env.B2_KEY_ID;
  const applicationKey = process.env.B2_APPLICATION_KEY;
  const bucketName = process.env.B2_BUCKET_NAME;
  if (!keyId || !applicationKey || !bucketName) return null;
  return { keyId, applicationKey, bucketName };
}

async function authorize(): Promise<B2Authorization | null> {
  const config = getConfig();
  if (!config) return null;
  if (cachedAuthorization && Date.now() - cachedAt < AUTH_CACHE_MS) return cachedAuthorization;

  const encoded = Buffer.from(`${config.keyId}:${config.applicationKey}`).toString("base64");
  const response = await fetch("https://api.backblazeb2.com/b2api/v2/b2_authorize_account", {
    headers: { Authorization: `Basic ${encoded}` },
    cache: "no-store",
  });
  if (!response.ok) {
    console.error("B2 authorization failed:", response.status);
    return null;
  }
  cachedAuthorization = await response.json() as B2Authorization;
  cachedAt = Date.now();
  return cachedAuthorization;
}

export async function fetchB2ObjectText(uri: string): Promise<string | null> {
  const object = await fetchB2Object(uri);
  return object ? new TextDecoder().decode(object.body) : null;
}

export async function fetchB2Object(uri: string): Promise<{ body: Uint8Array; contentType: string } | null> {
  if (!uri.startsWith("b2://")) return null;
  const config = getConfig();
  const separator = uri.slice(5).indexOf("/");
  if (!config || separator < 0) return null;

  const value = uri.slice(5);
  const bucket = value.slice(0, separator);
  if (bucket !== config.bucketName) return null;
  const fileName = value.slice(separator + 1);
  const authorization = await authorize();
  if (!authorization) return null;

  const encodedFileName = fileName.split("/").map(encodeURIComponent).join("/");
  const url = `${authorization.downloadUrl}/file/${encodeURIComponent(config.bucketName)}/${encodedFileName}`;
  const response = await fetch(url, {
    headers: { Authorization: authorization.authorizationToken },
    next: { revalidate: 30 * 24 * 60 * 60 },
  });
  if (!response.ok) {
    console.error("B2 object download failed:", response.status, fileName);
    return null;
  }
  return {
    body: new Uint8Array(await response.arrayBuffer()),
    contentType: response.headers.get("content-type") || "application/octet-stream",
  };
}
