import { env } from "cloudflare:workers";

export const WAVE_SESSION_COOKIE = "wave_session";
// Cloudflare Workers Web Crypto currently caps PBKDF2 iterations at 100,000.
const DEFAULT_ITERATIONS = 100_000;
const SESSION_DAYS = 30;

function normalizeEmail(value: string) {
  return value.trim().toLowerCase();
}

function bytesToBase64(bytes: Uint8Array) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function base64ToBytes(value: string) {
  const binary = atob(value);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function randomBytes(length: number) {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return bytes;
}

async function sha256Hex(value: string) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function derivePassword(password: string, salt: Uint8Array, iterations = DEFAULT_ITERATIONS) {
  const material = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  const saltBuffer = Uint8Array.from(salt).buffer as ArrayBuffer;
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt: saltBuffer, iterations },
    material,
    256,
  );
  return new Uint8Array(bits);
}

function constantTimeEqual(left: Uint8Array, right: Uint8Array) {
  if (left.length !== right.length) return false;
  let diff = 0;
  for (let index = 0; index < left.length; index += 1) diff |= left[index] ^ right[index];
  return diff === 0;
}

export function validEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizeEmail(value));
}

export function validPassword(value: string) {
  return value.length >= 10 && value.length <= 200;
}

export async function registerWaveUser(emailValue: string, displayNameValue: string, password: string) {
  const email = normalizeEmail(emailValue);
  const displayName = displayNameValue.trim().slice(0, 100);
  if (!validEmail(email) || !displayName || !validPassword(password)) throw new Error("invalid_registration");
  const existing = await env.DB.prepare("SELECT email FROM wave_credentials WHERE email = ? LIMIT 1").bind(email).first();
  if (existing) throw new Error("account_exists");
  const salt = randomBytes(16);
  const derived = await derivePassword(password, salt, DEFAULT_ITERATIONS);
  await env.DB.batch([
    env.DB.prepare("INSERT INTO user_accounts (email, display_name, role, status, updated_at) VALUES (?, ?, 'viewer', 'active', CURRENT_TIMESTAMP) ON CONFLICT(email) DO UPDATE SET display_name=excluded.display_name, status='active', deleted_at=NULL, updated_at=CURRENT_TIMESTAMP").bind(email, displayName),
    env.DB.prepare("INSERT INTO wave_credentials (email, password_hash, password_salt, password_iterations, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)").bind(email, bytesToBase64(derived), bytesToBase64(salt), DEFAULT_ITERATIONS),
  ]);
  return { email, displayName };
}

export async function verifyWavePassword(emailValue: string, password: string) {
  const email = normalizeEmail(emailValue);
  const row = await env.DB.prepare("SELECT c.email, c.password_hash AS passwordHash, c.password_salt AS passwordSalt, c.password_iterations AS passwordIterations, u.display_name AS displayName, u.status FROM wave_credentials c JOIN user_accounts u ON u.email=c.email WHERE c.email=? LIMIT 1").bind(email).first<{ email: string; passwordHash: string; passwordSalt: string; passwordIterations: number; displayName: string; status: string }>();
  if (!row || row.status !== "active") return null;
  const expected = base64ToBytes(row.passwordHash);
  const actual = await derivePassword(password, base64ToBytes(row.passwordSalt), Number(row.passwordIterations) || DEFAULT_ITERATIONS);
  return constantTimeEqual(expected, actual) ? { email: row.email, displayName: row.displayName } : null;
}

export async function createWaveSession(emailValue: string) {
  const email = normalizeEmail(emailValue);
  const token = bytesToBase64(randomBytes(32)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  const sessionHash = await sha256Hex(token);
  const expiresAt = new Date(Date.now() + SESSION_DAYS * 24 * 60 * 60 * 1000).toISOString();
  await env.DB.batch([
    env.DB.prepare("DELETE FROM wave_sessions WHERE expires_at <= ?").bind(new Date().toISOString()),
    env.DB.prepare("INSERT INTO wave_sessions (session_hash, email, expires_at, last_seen_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)").bind(sessionHash, email, expiresAt),
  ]);
  return { token, expiresAt };
}

export async function waveUserFromToken(token: string) {
  const sessionHash = await sha256Hex(token);
  const now = new Date().toISOString();
  const row = await env.DB.prepare("SELECT u.email, u.display_name AS displayName, u.status, s.expires_at AS expiresAt FROM wave_sessions s JOIN user_accounts u ON u.email=s.email WHERE s.session_hash=? AND s.expires_at>? LIMIT 1").bind(sessionHash, now).first<{ email: string; displayName: string; status: string; expiresAt: string }>();
  if (!row || row.status !== "active") return null;
  return { email: row.email, displayName: row.displayName, fullName: row.displayName };
}

export async function revokeWaveSession(token: string | undefined) {
  if (!token) return;
  await env.DB.prepare("DELETE FROM wave_sessions WHERE session_hash=?").bind(await sha256Hex(token)).run();
}

export function sessionCookie(token: string, expiresAt: string) {
  return `${WAVE_SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Expires=${new Date(expiresAt).toUTCString()}`;
}

export function clearSessionCookie() {
  return `${WAVE_SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

export function safeReturnPath(value: unknown) {
  if (typeof value !== "string" || !value.startsWith("/") || value.startsWith("//")) return "/";
  try {
    const url = new URL(value, "https://wave.local");
    if (url.origin !== "https://wave.local") return "/";
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return "/";
  }
}
