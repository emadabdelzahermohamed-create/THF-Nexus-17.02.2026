import { createWaveSession, registerWaveUser, safeReturnPath, sessionCookie } from "../../../../lib/wave-auth";

function sameOrigin(request: Request) {
  const origin = request.headers.get("origin");
  return !origin || origin === new URL(request.url).origin;
}

export async function POST(request: Request) {
  if (!sameOrigin(request)) return Response.json({ error: "invalid_origin" }, { status: 403 });
  const body = await request.json().catch(() => null) as { email?: unknown; displayName?: unknown; password?: unknown; returnTo?: unknown } | null;
  if (!body || typeof body.email !== "string" || typeof body.displayName !== "string" || typeof body.password !== "string") {
    return Response.json({ error: "invalid_request" }, { status: 400 });
  }
  try {
    const user = await registerWaveUser(body.email, body.displayName, body.password);
    const session = await createWaveSession(user.email);
    return Response.json({ ok: true, redirectTo: safeReturnPath(body.returnTo), user }, { headers: { "set-cookie": sessionCookie(session.token, session.expiresAt), "cache-control": "no-store" } });
  } catch (error) {
    const code = error instanceof Error ? error.message : "registration_failed";
    const status = code === "account_exists" ? 409 : 400;
    return Response.json({ error: code }, { status });
  }
}
