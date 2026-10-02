import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import { db, error, json, requireAuth } from '@appdeploy/sdk';

type AndroidTicket = {
  ticketHash: string;
  userId: string;
  codeChallenge: string;
  redirectUri: string;
  expiresAt: number;
  createdAt: number;
};

type AndroidSession = {
  tokenHash: string;
  userId: string;
  expiresAt: number;
  createdAt: number;
};

type V2Set = {
  exerciseId: string;
  ordinal: number;
  setType: 'warmup' | 'working' | 'drop' | 'failure';
  reps: number;
  loadKg: number;
  restSeconds: number;
  rpe: number | null;
  rir: number | null;
};

type V2Workout = {
  clientRecordId: string;
  clientRecordVersion: number;
  startedAt: string;
  endedAt: string;
  sport: string;
  exerciseSessionType: number;
  source: 'THF_ANDROID';
  provenancePackage: 'com.topherofit.thf.pulse';
  sets: V2Set[];
  volumeKg: number;
  fingerprint: string;
  receivedAt: number;
  updatedAt: number;
};

const ANDROID_REDIRECT = 'topherofit://auth/v2/complete';
const TICKET_TTL_MS = 2 * 60 * 1000;
const SESSION_TTL_MS = 15 * 60 * 1000;
const ticketTable = 'fitness_v2_android_auth_tickets';
const sessionTable = 'fitness_v2_android_auth_sessions';
const workoutTable = (userId: string) => `fitness_v2_workouts_${userId}`;
const competitionTable = 'fitness_v2_competition_submissions';
const b64url = /^[A-Za-z0-9_-]+$/;
const recordId = /^[A-Za-z0-9._:-]{8,120}$/;

const sha256 = (value: string) => createHash('sha256').update(value, 'utf8').digest('hex');
const challengeFor = (verifier: string) => createHash('sha256').update(verifier, 'ascii').digest('base64url');
const randomCredential = () => randomBytes(32).toString('base64url');

function authorizationHeader(event: unknown): string {
  if (!event || typeof event !== 'object' || !('headers' in event)) return '';
  const headers = (event as { headers?: Record<string, string | undefined> }).headers || {};
  const key = Object.keys(headers).find(name => name.toLowerCase() === 'authorization');
  return key ? String(headers[key] || '') : '';
}

async function androidUser(event: unknown): Promise<string | null> {
  const authorization = authorizationHeader(event);
  if (!authorization.startsWith('Bearer ')) return null;
  const token = authorization.slice(7).trim();
  if (!token.startsWith('thf_v2_') || token.length > 256 || !b64url.test(token.slice(7))) return null;
  const tokenHash = sha256(token);
  const page = await db.list<AndroidSession>(sessionTable, { filter: { tokenHash }, limit: 2 });
  const session = page.items.find(item => item.tokenHash === tokenHash);
  if (!session || session.expiresAt <= Date.now()) {
    if (session) await db.delete(sessionTable, [session.id]);
    return null;
  }
  return session.userId;
}

function boundedNumber(value: unknown, min: number, max: number): number {
  const number = Number(value);
  if (!Number.isFinite(number) || number < min || number > max) throw new Error('invalid_numeric_value');
  return number;
}

function optionalEffort(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null;
  return boundedNumber(value, 0, 10);
}

function normalizeWorkout(body: unknown): Omit<V2Workout, 'fingerprint' | 'volumeKg' | 'receivedAt' | 'updatedAt'> {
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new Error('invalid_workout');
  const input = body as Record<string, unknown>;
  const allowed = new Set(['clientRecordId','clientRecordVersion','startedAt','endedAt','sport','exerciseSessionType','source','provenancePackage','sets']);
  if (Object.keys(input).some(key => !allowed.has(key))) throw new Error('unknown_workout_field');
  const clientRecordId = String(input.clientRecordId || '');
  if (!recordId.test(clientRecordId)) throw new Error('invalid_client_record_id');
  const clientRecordVersion = boundedNumber(input.clientRecordVersion, 1, 1_000_000);
  if (!Number.isInteger(clientRecordVersion)) throw new Error('invalid_record_version');
  const startedAt = String(input.startedAt || '');
  const endedAt = String(input.endedAt || '');
  const start = Date.parse(startedAt);
  const end = Date.parse(endedAt);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start || end - start > 48 * 60 * 60 * 1000) throw new Error('invalid_workout_time');
  const sport = String(input.sport || '').slice(0, 80);
  if (!sport) throw new Error('invalid_sport');
  const exerciseSessionType = boundedNumber(input.exerciseSessionType, 0, 10_000);
  if (!Number.isInteger(exerciseSessionType)) throw new Error('invalid_exercise_session_type');
  if (input.source !== 'THF_ANDROID' || input.provenancePackage !== 'com.topherofit.thf.pulse') throw new Error('invalid_provenance');
  if (!Array.isArray(input.sets) || input.sets.length > 1000) throw new Error('invalid_sets');
  const seen = new Set<string>();
  const sets = input.sets.map((raw, index): V2Set => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error('invalid_set');
    const item = raw as Record<string, unknown>;
    const exerciseId = String(item.exerciseId || '').slice(0, 120);
    const ordinal = boundedNumber(item.ordinal, 1, 10_000);
    if (!exerciseId || !Number.isInteger(ordinal)) throw new Error('invalid_set_identity');
    const identity = `${exerciseId}:${ordinal}`;
    if (seen.has(identity)) throw new Error('duplicate_set');
    seen.add(identity);
    const setType = String(item.setType || 'working');
    if (!['warmup','working','drop','failure'].includes(setType)) throw new Error('invalid_set_type');
    return {
      exerciseId,
      ordinal,
      setType: setType as V2Set['setType'],
      reps: boundedNumber(item.reps, 0, 10_000),
      loadKg: boundedNumber(item.loadKg, 0, 100_000),
      restSeconds: boundedNumber(item.restSeconds, 0, 86_400),
      rpe: optionalEffort(item.rpe),
      rir: optionalEffort(item.rir),
    };
  });
  return {
    clientRecordId,
    clientRecordVersion,
    startedAt: new Date(start).toISOString(),
    endedAt: new Date(end).toISOString(),
    sport,
    exerciseSessionType,
    source: 'THF_ANDROID',
    provenancePackage: 'com.topherofit.thf.pulse',
    sets,
  };
}

function safeEqual(left: string, right: string): boolean {
  const a = Buffer.from(left, 'ascii');
  const b = Buffer.from(right, 'ascii');
  return a.length === b.length && timingSafeEqual(a, b);
}

export const fitnessV2AndroidRoutes = {
  'POST /api/v2/auth/android/tickets': [requireAuth(), async (context: { body: unknown; user?: { userId: string } }) => {
    const body = (context.body || {}) as Record<string, unknown>;
    const codeChallenge = String(body.codeChallenge || '');
    const redirectUri = String(body.redirectUri || '');
    if (codeChallenge.length !== 43 || !b64url.test(codeChallenge) || redirectUri !== ANDROID_REDIRECT) return error('invalid_android_auth_request', 400);
    const ticket = randomCredential();
    const now = Date.now();
    await db.add(ticketTable, [{ ticketHash: sha256(ticket), userId: context.user!.userId, codeChallenge, redirectUri, createdAt: now, expiresAt: now + TICKET_TTL_MS } satisfies AndroidTicket]);
    return json({ ticket, redirectUri, expiresIn: TICKET_TTL_MS / 1000 }, 201);
  }],

  'POST /api/v2/auth/android/sessions': [async (context: { body: unknown }) => {
    const body = (context.body || {}) as Record<string, unknown>;
    const ticket = String(body.ticket || '');
    const codeVerifier = String(body.codeVerifier || '');
    if (ticket.length < 32 || ticket.length > 256 || !b64url.test(ticket) || codeVerifier.length < 43 || codeVerifier.length > 128 || !/^[A-Za-z0-9._~-]+$/.test(codeVerifier)) return error('invalid_android_auth_exchange', 400);
    const ticketHash = sha256(ticket);
    const page = await db.list<AndroidTicket>(ticketTable, { filter: { ticketHash }, limit: 2 });
    const record = page.items.find(item => item.ticketHash === ticketHash);
    if (!record || record.expiresAt <= Date.now() || !safeEqual(record.codeChallenge, challengeFor(codeVerifier))) return error('invalid_or_expired_ticket', 401);
    await db.delete(ticketTable, [record.id]);
    const accessToken = `thf_v2_${randomCredential()}`;
    const now = Date.now();
    await db.add(sessionTable, [{ tokenHash: sha256(accessToken), userId: record.userId, createdAt: now, expiresAt: now + SESSION_TTL_MS } satisfies AndroidSession]);
    return json({ accessToken, tokenType: 'Bearer', expiresIn: SESSION_TTL_MS / 1000 });
  }],

  'POST /api/v2/workouts/sync': [async (context: { body: unknown; event: unknown }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    let normalized: ReturnType<typeof normalizeWorkout>;
    try { normalized = normalizeWorkout(context.body); } catch (cause) { return error(cause instanceof Error ? cause.message : 'invalid_workout', 422); }
    const fingerprint = sha256(JSON.stringify(normalized));
    const target = workoutTable(userId);
    const page = await db.list<V2Workout>(target, { filter: { clientRecordId: normalized.clientRecordId }, limit: 2 });
    const existing = page.items.find(item => item.clientRecordId === normalized.clientRecordId);
    if (existing && existing.clientRecordVersion === normalized.clientRecordVersion) {
      if (existing.fingerprint !== fingerprint) return error('record_version_conflict', 409);
      return json({ result: 'duplicate', clientRecordId: normalized.clientRecordId, serverRevision: existing.clientRecordVersion });
    }
    if (existing && existing.clientRecordVersion > normalized.clientRecordVersion) return json({ result: 'stale', clientRecordId: normalized.clientRecordId, serverRevision: existing.clientRecordVersion });
    const now = Date.now();
    const volumeKg = normalized.sets.reduce((sum, item) => sum + item.reps * item.loadKg, 0);
    const record: V2Workout = { ...normalized, volumeKg, fingerprint, receivedAt: existing?.receivedAt || now, updatedAt: now };
    if (existing) await db.update(target, [{ id: existing.id, record }]); else await db.add(target, [record]);
    return json({ result: existing ? 'updated' : 'inserted', clientRecordId: normalized.clientRecordId, serverRevision: normalized.clientRecordVersion });
  }],

  'GET /api/v2/workouts': [async (context: { event: unknown }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    const page = await db.list<V2Workout>(workoutTable(userId), { limit: 200 });
    const items = page.items.sort((a, b) => Date.parse(b.startedAt) - Date.parse(a.startedAt));
    return json({ items });
  }],

  'GET /api/v2/progress/summary': [async (context: { event: unknown }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    const page = await db.list<V2Workout>(workoutTable(userId), { limit: 200 });
    const personalRecords = new Map<string, number>();
    for (const workout of page.items) for (const set of workout.sets) personalRecords.set(set.exerciseId, Math.max(personalRecords.get(set.exerciseId) || 0, set.loadKg));
    return json({
      workouts: page.items.length,
      volumeKg: page.items.reduce((sum, item) => sum + item.volumeKg, 0),
      personalRecords: [...personalRecords.entries()].map(([exerciseId, maxLoadKg]) => ({ exerciseId, maxLoadKg })),
      source: 'SERVER_RECORDED',
    });
  }],

  'POST /api/v2/competitions/:competitionId/submissions': [async (context: { body: unknown; event: unknown; params: Record<string, string> }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    const body = (context.body || {}) as Record<string, unknown>;
    const workoutClientRecordId = String(body.workoutClientRecordId || '');
    const claimedMetric = Number(body.claimedMetric);
    const page = await db.list<V2Workout>(workoutTable(userId), { filter: { clientRecordId: workoutClientRecordId }, limit: 2 });
    const workout = page.items.find(item => item.clientRecordId === workoutClientRecordId);
    if (!workout || !Number.isFinite(claimedMetric)) return error('recorded_workout_required', 409);
    const accepted = Math.abs(workout.volumeKg - claimedMetric) < 0.000001;
    if (accepted) await db.add(competitionTable, [{ userId, competitionId: context.params.competitionId, workoutClientRecordId, verifiedMetric: workout.volumeKg, submittedAt: Date.now() }]);
    return json({ accepted, verifiedMetric: workout.volumeKg, verificationLevel: 'SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED', reason: accepted ? null : 'CLAIM_MISMATCH' });
  }],
};
