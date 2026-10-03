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

type StoredV2Workout = V2Workout & {
  historyId: string;
};

type SyncResponse = {
  result: 'inserted' | 'updated' | 'duplicate' | 'stale';
  clientRecordId: string;
  serverRevision: number;
};

type IdempotencyRecord = {
  fingerprint: string;
  response: SyncResponse;
  createdAt: number;
};

type ResourceKind = 'ticket' | 'session' | 'idempotency' | 'workout-index';

type ResourcePointer = {
  tableName: string;
  kind: ResourceKind;
  createdAt: number;
};

type LegacyDeletionState = {
  ticketNextToken?: string;
  sessionNextToken?: string;
  competitionNextToken?: string;
  updatedAt: number;
};

type DeletionCount = {
  deleted: number;
  done: boolean;
};

type ListedRecord<T> = Omit<T, 'id'> & { id: string };

export type FitnessV2DeletionResult = {
  done: boolean;
  workoutHistory: DeletionCount;
  legacyWorkouts: DeletionCount;
  competitions: DeletionCount;
  resources: DeletionCount;
  legacySharedTables: DeletionCount;
};

const ANDROID_REDIRECT = 'topherofit://auth/v2/complete';
const TICKET_TTL_MS = 2 * 60 * 1000;
const SESSION_TTL_MS = 15 * 60 * 1000;
const LEGACY_TICKET_TABLE = 'fitness_v2_android_auth_tickets';
const LEGACY_SESSION_TABLE = 'fitness_v2_android_auth_sessions';
const LEGACY_COMPETITION_TABLE = 'fitness_v2_competition_submissions';
const b64url = /^[A-Za-z0-9_-]+$/;
const recordId = /^[A-Za-z0-9._:-]{8,120}$/;
const idempotencyKey = /^[A-Za-z0-9._:-]{8,120}$/;
const safeResourceTable = /^fitness_v2_(ticket|session|idem|workout)_[a-f0-9]{40,64}$/;

const sha256 = (value: string) => createHash('sha256').update(value, 'utf8').digest('hex');
const challengeFor = (verifier: string) => createHash('sha256').update(verifier, 'ascii').digest('base64url');
const randomCredential = () => randomBytes(32).toString('base64url');
const ticketTable = (ticketHash: string) => `fitness_v2_ticket_${ticketHash.slice(0, 48)}`;
const sessionTable = (tokenHash: string) => `fitness_v2_session_${tokenHash.slice(0, 48)}`;
const userScope = (userId: string) => sha256(userId).slice(0, 40);
const workoutTable = (userId: string) => `fitness_v2_workouts_${userScope(userId)}`;
const legacyWorkoutTable = (userId: string) => `fitness_v2_workouts_${userId}`;
const workoutRecordTable = (userId: string, clientRecordId: string) =>
  `fitness_v2_workout_${sha256(`${userId}:${clientRecordId}`).slice(0, 48)}`;
const idempotencyTable = (userId: string, key: string) =>
  `fitness_v2_idem_${sha256(`${userId}:${key}`).slice(0, 48)}`;
const competitionTable = (userId: string) => `fitness_v2_competitions_${userScope(userId)}`;
const resourceTable = (userId: string) => `fitness_v2_resources_${userScope(userId)}`;
const deletionStateTable = (userId: string) => `fitness_v2_deletion_${userScope(userId)}`;

async function singleRecord<T>(table: string): Promise<ListedRecord<T> | null> {
  const page = await db.list<T>(table, { limit: 1 });
  return page.items[0] || null;
}

async function trackResource(userId: string, tableName: string, kind: ResourceKind): Promise<string | null> {
  if (!safeResourceTable.test(tableName)) return null;
  const [id] = await db.add(resourceTable(userId), [{ tableName, kind, createdAt: Date.now() } satisfies ResourcePointer]);
  return id;
}

function requestHeader(event: unknown, requestedName: string): string {
  if (!event || typeof event !== 'object' || !('headers' in event)) return '';
  const headers = (event as { headers?: Record<string, string | undefined> }).headers || {};
  const key = Object.keys(headers).find(name => name.toLowerCase() === requestedName.toLowerCase());
  return key ? String(headers[key] || '') : '';
}

function authorizationHeader(event: unknown): string {
  return requestHeader(event, 'authorization');
}

async function androidUser(event: unknown): Promise<string | null> {
  const authorization = authorizationHeader(event);
  if (!authorization.startsWith('Bearer ')) return null;
  const token = authorization.slice(7).trim();
  if (!token.startsWith('thf_v2_') || token.length > 256 || !b64url.test(token.slice(7))) return null;
  const tokenHash = sha256(token);
  const table = sessionTable(tokenHash);
  const session = await singleRecord<AndroidSession>(table);
  if (!session || session.expiresAt <= Date.now()) {
    if (session) await db.delete(table, [session.id]);
    return null;
  }
  return session.userId;
}

function boundedNumber(value: unknown, min: number, max: number): number {
  if (typeof value !== 'number') throw new Error('invalid_numeric_value');
  if (!Number.isFinite(value) || value < min || value > max) throw new Error('invalid_numeric_value');
  return value;
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
  const sport = String(input.sport || '');
  if (!sport || sport.length > 80) throw new Error('invalid_sport');
  const exerciseSessionType = boundedNumber(input.exerciseSessionType, 0, 10_000);
  if (!Number.isInteger(exerciseSessionType)) throw new Error('invalid_exercise_session_type');
  if (input.source !== 'THF_ANDROID' || input.provenancePackage !== 'com.topherofit.thf.pulse') throw new Error('invalid_provenance');
  if (!Array.isArray(input.sets) || input.sets.length > 1000) throw new Error('invalid_sets');
  const seen = new Set<string>();
  const sets = input.sets.map((raw): V2Set => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error('invalid_set');
    const item = raw as Record<string, unknown>;
    const allowedSetFields = new Set(['exerciseId','ordinal','setType','reps','loadKg','restSeconds','rpe','rir']);
    if (Object.keys(item).some(key => !allowedSetFields.has(key))) throw new Error('unknown_set_field');
    const exerciseId = String(item.exerciseId || '');
    const ordinal = boundedNumber(item.ordinal, 1, 10_000);
    if (!exerciseId || exerciseId.length > 120 || !Number.isInteger(ordinal)) throw new Error('invalid_set_identity');
    const identity = `${exerciseId}:${ordinal}`;
    if (seen.has(identity)) throw new Error('duplicate_set');
    seen.add(identity);
    const setType = String(item.setType || 'working');
    if (!['warmup','working','drop','failure'].includes(setType)) throw new Error('invalid_set_type');
    const reps = boundedNumber(item.reps, 0, 10_000);
    const restSeconds = boundedNumber(item.restSeconds, 0, 86_400);
    if (!Number.isInteger(reps) || !Number.isInteger(restSeconds)) throw new Error('invalid_set_integer');
    return {
      exerciseId,
      ordinal,
      setType: setType as V2Set['setType'],
      reps,
      loadKg: boundedNumber(item.loadKg, 0, 100_000),
      restSeconds,
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

function historyWorkout(item: V2Workout & { id?: string; historyId?: string }): V2Workout {
  const { id: _id, historyId: _historyId, ...stored } = item;
  return stored;
}

function publicWorkout(item: V2Workout & { id?: string; historyId?: string }) {
  const { fingerprint: _fingerprint, ...visible } = historyWorkout(item);
  return visible;
}

async function rememberIdempotency(userId: string, table: string, fingerprint: string, response: SyncResponse): Promise<boolean> {
  const [id] = await db.add(table, [{ fingerprint, response, createdAt: Date.now() } satisfies IdempotencyRecord]);
  if (!id) return false;
  if (!await trackResource(userId, table, 'idempotency')) {
    await db.delete(table, [id]);
    return false;
  }
  return true;
}

async function deleteSimpleTable(tableName: string, limit: number): Promise<DeletionCount> {
  const page = await db.list(tableName, { limit });
  if (!page.items.length) return { deleted: 0, done: !page.nextToken };
  const outcomes = await db.delete(tableName, page.items.map(item => item.id));
  return { deleted: outcomes.filter(Boolean).length, done: !page.nextToken && outcomes.every(Boolean) };
}

async function deleteWorkoutHistory(userId: string): Promise<DeletionCount> {
  const historyTable = workoutTable(userId);
  const page = await db.list<V2Workout>(historyTable, { limit: 25 });
  let deleted = 0;
  let done = !page.nextToken;
  for (const workout of page.items) {
    const indexDeletion = await deleteSimpleTable(workoutRecordTable(userId, workout.clientRecordId), 10);
    if (!indexDeletion.done) {
      done = false;
      continue;
    }
    const [removed] = await db.delete(historyTable, [workout.id]);
    if (removed) deleted += 1;
    else done = false;
  }
  return { deleted, done };
}

async function deleteTrackedResources(userId: string): Promise<DeletionCount> {
  const registry = resourceTable(userId);
  const page = await db.list<ResourcePointer>(registry, { limit: 25 });
  let deleted = 0;
  let done = !page.nextToken;
  for (const pointer of page.items) {
    if (!safeResourceTable.test(pointer.tableName)) {
      const [removed] = await db.delete(registry, [pointer.id]);
      if (removed) deleted += 1;
      else done = false;
      continue;
    }
    const resourceDeletion = await deleteSimpleTable(pointer.tableName, 100);
    if (!resourceDeletion.done) {
      done = false;
      continue;
    }
    const [removed] = await db.delete(registry, [pointer.id]);
    if (removed) deleted += resourceDeletion.deleted + 1;
    else done = false;
  }
  return { deleted, done };
}

type LegacySweep = DeletionCount & { nextToken?: string };

async function sweepLegacySharedTable<T extends { userId: string }>(
  tableName: string,
  userId: string,
  nextToken?: string,
): Promise<LegacySweep> {
  const page = await db.list<T>(tableName, { filter: { userId }, nextToken, limit: 100 });
  const ids = page.items.filter(item => item.userId === userId).map(item => item.id);
  const outcomes = ids.length ? await db.delete(tableName, ids) : [];
  const allDeleted = outcomes.every(Boolean);
  return {
    deleted: outcomes.filter(Boolean).length,
    done: allDeleted && !page.nextToken,
    nextToken: allDeleted ? page.nextToken : nextToken,
  };
}

async function deleteLegacySharedData(userId: string): Promise<DeletionCount> {
  const stateTable = deletionStateTable(userId);
  const state = await singleRecord<LegacyDeletionState>(stateTable);
  const tickets = await sweepLegacySharedTable<AndroidTicket>(LEGACY_TICKET_TABLE, userId, state?.ticketNextToken);
  const sessions = await sweepLegacySharedTable<AndroidSession>(LEGACY_SESSION_TABLE, userId, state?.sessionNextToken);
  const competitions = await sweepLegacySharedTable<{ userId: string }>(LEGACY_COMPETITION_TABLE, userId, state?.competitionNextToken);
  const done = tickets.done && sessions.done && competitions.done;
  if (done) {
    if (state) await db.delete(stateTable, [state.id]);
  } else {
    const next: LegacyDeletionState = {
      ticketNextToken: tickets.nextToken,
      sessionNextToken: sessions.nextToken,
      competitionNextToken: competitions.nextToken,
      updatedAt: Date.now(),
    };
    if (state) await db.update(stateTable, [{ id: state.id, record: next }]);
    else await db.add(stateTable, [next]);
  }
  return { deleted: tickets.deleted + sessions.deleted + competitions.deleted, done };
}

export async function deleteFitnessV2UserData(userId: string): Promise<FitnessV2DeletionResult> {
  const workoutHistory = await deleteWorkoutHistory(userId);
  const legacyWorkouts = await deleteSimpleTable(legacyWorkoutTable(userId), 50);
  const competitions = await deleteSimpleTable(competitionTable(userId), 50);
  const resources = await deleteTrackedResources(userId);
  const legacySharedTables = await deleteLegacySharedData(userId);
  return {
    done: workoutHistory.done && legacyWorkouts.done && competitions.done && resources.done && legacySharedTables.done,
    workoutHistory,
    legacyWorkouts,
    competitions,
    resources,
    legacySharedTables,
  };
}

export const fitnessV2AndroidRoutes = {
  'POST /api/v2/auth/android/tickets': [requireAuth(), async (context: { body: unknown; user?: { userId: string } }) => {
    const body = (context.body || {}) as Record<string, unknown>;
    const codeChallenge = String(body.codeChallenge || '');
    const redirectUri = String(body.redirectUri || '');
    if (codeChallenge.length !== 43 || !b64url.test(codeChallenge) || redirectUri !== ANDROID_REDIRECT) return error('invalid_android_auth_request', 400);
    const ticket = randomCredential();
    const ticketHash = sha256(ticket);
    const target = ticketTable(ticketHash);
    const now = Date.now();
    const [id] = await db.add(target, [{ ticketHash, userId: context.user!.userId, codeChallenge, redirectUri, createdAt: now, expiresAt: now + TICKET_TTL_MS } satisfies AndroidTicket]);
    if (!id) return error('android_auth_ticket_unavailable', 503);
    if (!await trackResource(context.user!.userId, target, 'ticket')) {
      await db.delete(target, [id]);
      return error('android_auth_ticket_tracking_failed', 503);
    }
    return json({ ticket, redirectUri, expiresIn: TICKET_TTL_MS / 1000 }, 201);
  }],

  'POST /api/v2/auth/android/sessions': [async (context: { body: unknown }) => {
    const body = (context.body || {}) as Record<string, unknown>;
    const ticket = String(body.ticket || '');
    const codeVerifier = String(body.codeVerifier || '');
    if (ticket.length < 32 || ticket.length > 256 || !b64url.test(ticket) || codeVerifier.length < 43 || codeVerifier.length > 128 || !/^[A-Za-z0-9._~-]+$/.test(codeVerifier)) return error('invalid_android_auth_exchange', 400);
    const ticketHash = sha256(ticket);
    const table = ticketTable(ticketHash);
    const record = await singleRecord<AndroidTicket>(table);
    if (!record || record.expiresAt <= Date.now() || !safeEqual(record.codeChallenge, challengeFor(codeVerifier))) {
      if (record) await db.delete(table, [record.id]);
      return error('invalid_or_expired_ticket', 401);
    }
    const [deleted] = await db.delete(table, [record.id]);
    if (!deleted) return error('android_auth_ticket_replay_guard_failed', 503);
    const accessToken = `thf_v2_${randomCredential()}`;
    const tokenHash = sha256(accessToken);
    const target = sessionTable(tokenHash);
    const now = Date.now();
    const [sessionId] = await db.add(target, [{ tokenHash, userId: record.userId, createdAt: now, expiresAt: now + SESSION_TTL_MS } satisfies AndroidSession]);
    if (!sessionId) return error('android_session_unavailable', 503);
    if (!await trackResource(record.userId, target, 'session')) {
      await db.delete(target, [sessionId]);
      return error('android_session_tracking_failed', 503);
    }
    return json({ accessToken, tokenType: 'Bearer', expiresIn: SESSION_TTL_MS / 1000 });
  }],

  'POST /api/v2/workouts/sync': [async (context: { body: unknown; event: unknown }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    const requestKey = requestHeader(context.event, 'idempotency-key');
    if (!idempotencyKey.test(requestKey)) return error('invalid_idempotency_key', 400);
    let normalized: ReturnType<typeof normalizeWorkout>;
    try { normalized = normalizeWorkout(context.body); } catch (cause) { return error(cause instanceof Error ? cause.message : 'invalid_workout', 422); }
    const fingerprint = sha256(JSON.stringify(normalized));
    const idemTable = idempotencyTable(userId, requestKey);
    const remembered = await singleRecord<IdempotencyRecord>(idemTable);
    if (remembered) {
      if (!safeEqual(remembered.fingerprint, fingerprint)) return error('idempotency_conflict', 409);
      if (!await trackResource(userId, idemTable, 'idempotency')) return error('idempotency_tracking_failed', 503);
      return json(remembered.response);
    }
    const target = workoutRecordTable(userId, normalized.clientRecordId);
    const existing = await singleRecord<StoredV2Workout>(target);
    if (existing && !await trackResource(userId, target, 'workout-index')) return error('workout_index_tracking_failed', 503);
    let response: SyncResponse;
    if (existing && existing.clientRecordVersion === normalized.clientRecordVersion) {
      if (existing.fingerprint !== fingerprint) return error('record_version_conflict', 409);
      const repaired = await db.update(workoutTable(userId), [{ id: existing.historyId, record: historyWorkout(existing) }]);
      if (!repaired[0]) return error('workout_history_repair_failed', 503);
      response = { result: 'duplicate', clientRecordId: normalized.clientRecordId, serverRevision: existing.clientRecordVersion };
      if (!await rememberIdempotency(userId, idemTable, fingerprint, response)) return error('idempotency_store_failed', 503);
      return json(response);
    }
    if (existing && existing.clientRecordVersion > normalized.clientRecordVersion) {
      response = { result: 'stale', clientRecordId: normalized.clientRecordId, serverRevision: existing.clientRecordVersion };
      if (!await rememberIdempotency(userId, idemTable, fingerprint, response)) return error('idempotency_store_failed', 503);
      return json(response);
    }
    const now = Date.now();
    const volumeKg = normalized.sets.reduce((sum, item) => sum + item.reps * item.loadKg, 0);
    const record: V2Workout = { ...normalized, volumeKg, fingerprint, receivedAt: existing?.receivedAt || now, updatedAt: now };
    if (existing) {
      const stored: StoredV2Workout = { ...record, historyId: existing.historyId };
      const [indexed] = await db.update(target, [{ id: existing.id, record: stored }]);
      if (!indexed) return error('workout_index_update_failed', 503);
      const [listed] = await db.update(workoutTable(userId), [{ id: existing.historyId, record }]);
      if (!listed) return error('workout_history_update_failed', 503);
      response = { result: 'updated', clientRecordId: normalized.clientRecordId, serverRevision: normalized.clientRecordVersion };
    } else {
      const [historyId] = await db.add(workoutTable(userId), [record]);
      if (!historyId) return error('workout_history_insert_failed', 503);
      const [indexId] = await db.add(target, [{ ...record, historyId } satisfies StoredV2Workout]);
      if (!indexId) {
        await db.delete(workoutTable(userId), [historyId]);
        return error('workout_index_insert_failed', 503);
      }
      if (!await trackResource(userId, target, 'workout-index')) {
        await db.delete(target, [indexId]);
        await db.delete(workoutTable(userId), [historyId]);
        return error('workout_index_tracking_failed', 503);
      }
      response = { result: 'inserted', clientRecordId: normalized.clientRecordId, serverRevision: normalized.clientRecordVersion };
    }
    if (!await rememberIdempotency(userId, idemTable, fingerprint, response)) return error('idempotency_store_failed', 503);
    return json(response);
  }],

  'GET /api/v2/workouts': [async (context: { event: unknown }) => {
    const userId = await androidUser(context.event);
    if (!userId) return error('unauthorized', 401);
    const page = await db.list<V2Workout>(workoutTable(userId), { limit: 200 });
    const items = page.items.sort((a, b) => Date.parse(b.startedAt) - Date.parse(a.startedAt)).map(publicWorkout);
    return json({ items, truncated: Boolean(page.nextToken) });
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
    const claimedMetric = body.claimedMetric;
    if (!recordId.test(workoutClientRecordId)) return error('invalid_workout_record_id', 422);
    const workout = await singleRecord<StoredV2Workout>(workoutRecordTable(userId, workoutClientRecordId));
    if (!workout || typeof claimedMetric !== 'number' || !Number.isFinite(claimedMetric)) return error('recorded_workout_required', 409);
    const accepted = Math.abs(workout.volumeKg - claimedMetric) < 0.000001;
    if (accepted) {
      const [id] = await db.add(competitionTable(userId), [{ competitionId: context.params.competitionId, workoutClientRecordId, verifiedMetric: workout.volumeKg, submittedAt: Date.now() }]);
      if (!id) return error('competition_submission_unavailable', 503);
    }
    return json({ accepted, verifiedMetric: workout.volumeKg, verificationLevel: 'SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED', reason: accepted ? null : 'CLAIM_MISMATCH' });
  }],
};
