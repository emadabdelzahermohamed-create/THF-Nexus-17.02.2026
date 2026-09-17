#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path.cwd()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"RC15.5 patch anchor missing in {path}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


def append_unique(path: str, line: str) -> None:
    text = read(path)
    if line not in text.splitlines():
        text = text.rstrip() + "\n" + line + "\n"
        write(path, text)


# ---------------------------------------------------------------------------
# 1) Automatic AI policy: Arabic is the only automatic target.
#    Generated subtitle/dubbing artifacts use immutable per-job paths so the
#    browser/CDN can cache them forever without serving a stale prior source.
# ---------------------------------------------------------------------------
replace_once(
    "media-server/worker/worker.py",
    '            (job_id, title_id, import_id, json.dumps(["subtitles", "highlights"]), json.dumps(AI_TARGET_LANGUAGES[:21])),',
    '            (job_id, title_id, import_id, json.dumps(["subtitles", "dubbing"]), json.dumps(["ar"])),',
)

# Reuse a completed Arabic subtitle+dub job when the exact source hash was
# already processed for this title. This prevents repeat ASR/translation/TTS.
replace_once(
    "media-server/worker/worker.py",
    '''        existing = connection.execute(\n            "SELECT id FROM ai_jobs WHERE media_import_id=%s AND status IN ('queued', 'processing', 'ready') ORDER BY created_at DESC LIMIT 1",\n            (import_id,),\n        ).fetchone()''',
    '''        existing = connection.execute(\n            "SELECT j.id FROM ai_jobs j JOIN media_imports m ON m.id=j.media_import_id "\n            "WHERE j.title_id=%s AND m.source_sha256=(SELECT source_sha256 FROM media_imports WHERE id=%s) "\n            "AND j.status IN ('queued','processing','dubbing','ready') "\n            "AND j.tasks::text LIKE '%dubbing%' AND j.target_languages::text LIKE '%ar%' "\n            "ORDER BY j.created_at DESC LIMIT 1",\n            (title_id, import_id),\n        ).fetchone()''',
)

replace_once(
    "media-server/ai-worker/ai_worker.py",
    "def create_subtitles(title_id: str, source: Path, segments: list[Segment], source_language: str, detection_confidence: float, languages: list[str], work: Path) -> list[dict[str, object]]:",
    "def create_subtitles(title_id: str, source: Path, segments: list[Segment], source_language: str, detection_confidence: float, languages: list[str], asset_version: str, work: Path) -> list[dict[str, object]]:",
)
replace_once(
    "media-server/ai-worker/ai_worker.py",
    '        url = upload_file(target, f"subtitles/{title_id}/{language}.vtt", "text/vtt; charset=utf-8")',
    '        url = upload_file(target, f"subtitles/{title_id}/{asset_version}/{language}.vtt", "text/vtt; charset=utf-8")',
)
replace_once(
    "media-server/ai-worker/ai_worker.py",
    '        subtitles = create_subtitles(title_id, source, segments, source_language, detection_confidence, [str(item) for item in job["languages"]], work) if "subtitles" in tasks else []',
    '        subtitles = create_subtitles(title_id, source, segments, source_language, detection_confidence, ["ar"], job_id, work) if "subtitles" in tasks else []',
)
replace_once(
    "media-server/ai-worker/ai_worker.py",
    '        if "dubbing" in tasks:',
    '        if "dubbing" in tasks and source_language != "ar":',
)
replace_once(
    "media-server/dubbing-worker/dubbing_worker.py",
    '            url=upload(audio,f"dubbing/{title_id}/{language}/{profile_id}.m4a")',
    '            url=upload(audio,f"dubbing/{title_id}/{job_id}/{language}/{profile_id}.m4a")',
)
replace_once(
    "media-server/live-worker/live_worker.py",
    'connection.execute("INSERT INTO ai_jobs (id, title_id, media_import_id, tasks, target_languages, status) VALUES (%s, %s, %s, %s, %s, \'queued\')", (ai_job_id, title_id, media_id, json.dumps(["subtitles", "highlights"]), json.dumps(AI_TARGET_LANGUAGES[:21])))',
    'connection.execute("INSERT INTO ai_jobs (id, title_id, media_import_id, tasks, target_languages, status) VALUES (%s, %s, %s, %s, %s, \'queued\')", (ai_job_id, title_id, media_id, json.dumps(["subtitles", "dubbing"]), json.dumps(["ar"])))',
)

# The API itself only accepts Arabic as an automatic/manual AI target in this
# release, even if an old client still sends all historical locale values.
replace_once(
    "media-server/api/main.py",
    '        "AI_TARGET_LANGUAGES", ",".join(SUPPORTED_LOCALES)',
    '        "AI_TARGET_LANGUAGES", "ar"',
)

# Keep the existing broad multilingual translation model for correctness, but
# use a much smaller Whisper model on this CPU VPS. Model caches are persistent
# Docker volumes, so model weights are not downloaded for every job.
for env_file in ["media-server/.env.example", "media-server/.env.universal.example"]:
    p = ROOT / env_file
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^AI_TARGET_LANGUAGES=.*$", "AI_TARGET_LANGUAGES=ar", text, flags=re.M)
    text = re.sub(r"^WHISPER_MODEL=.*$", "WHISPER_MODEL=small", text, flags=re.M)
    p.write_text(text, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) VPS page capture. yt-dlp is used server-side only for explicitly allowed
#    source hosts and only after WAVE rights checks. No cookie/DRM bypass is
#    added. Logged-in/session-bound media remains in the Browser capture path.
# ---------------------------------------------------------------------------
append_unique("media-server/worker/requirements.txt", "yt-dlp[default]==2026.8.19")

worker = read("media-server/worker/worker.py")
if "import yt_dlp" not in worker:
    anchor = "from pathlib import Path\n"
    if anchor not in worker:
        raise SystemExit("worker import anchor missing")
    worker = worker.replace(anchor, "from pathlib import Path\n\nimport yt_dlp\n", 1)
    write("media-server/worker/worker.py", worker)

capture_function = r'''
def capture_page(url: str, destination: Path, allowed_hosts: set[str] | None) -> str:
    """Download a public/authorized video page through yt-dlp into one local media file."""
    validate_source_url(url, allowed_hosts)
    template = str(destination.parent / "captured.%(ext)s")
    options = {
        "format": os.getenv("CAPTURE_FORMAT", "bestvideo*+bestaudio/best"),
        "outtmpl": template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "max_filesize": MAX_BYTES,
        "restrictfilenames": True,
        "http_headers": {"User-Agent": "WAVE-MAWJA-MediaCapture/1.0"},
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.extract_info(url, download=True)
    candidates = [p for p in destination.parent.glob("captured*") if p.is_file() and not p.name.endswith((".part", ".ytdl"))]
    if not candidates:
        raise ValueError("yt-dlp did not produce a media file")
    captured = max(candidates, key=lambda item: item.stat().st_size)
    if captured.stat().st_size <= 0 or captured.stat().st_size > MAX_BYTES:
        raise ValueError("captured source is empty or exceeds configured size limit")
    if captured != destination:
        shutil.move(str(captured), str(destination))
    return file_sha256(destination)

'''
worker = read("media-server/worker/worker.py")
if "def capture_page(" not in worker:
    marker = "def download_source(url: str, destination: Path, source_type: str, upload_key: str | None, allowed_hosts: set[str] | None) -> str:\n"
    if marker not in worker:
        raise SystemExit("download_source anchor missing")
    worker = worker.replace(marker, capture_function + marker, 1)
    write("media-server/worker/worker.py", worker)

replace_once(
    "media-server/worker/worker.py",
    '''def download_source(url: str, destination: Path, source_type: str, upload_key: str | None, allowed_hosts: set[str] | None) -> str:\n    if url.startswith("s3://"):\n''',
    '''def download_source(url: str, destination: Path, source_type: str, upload_key: str | None, allowed_hosts: set[str] | None) -> str:\n    if source_type == "application/x-wave-page":\n        return capture_page(url, destination, allowed_hosts)\n    if url.startswith("s3://"):\n''',
)

replace_once(
    "media-server/api/main.py",
    '''class ResolvePublicRequest(BaseModel):\n    page_url: str = Field(min_length=9, max_length=4096)\n    playlist_limit: int = Field(default=100, ge=1, le=250)\n\n\nclass LocalizedText(BaseModel):''',
    '''class ResolvePublicRequest(BaseModel):\n    page_url: str = Field(min_length=9, max_length=4096)\n    playlist_limit: int = Field(default=100, ge=1, le=250)\n\n\nclass CaptureRequest(BaseModel):\n    title_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,79}$")\n    page_url: HttpUrl\n\n\nclass LocalizedText(BaseModel):''',
)

capture_endpoint = r'''
@app.post("/v1/captures", status_code=202, dependencies=[Depends(require_admin)])
async def create_capture(payload: CaptureRequest) -> dict[str, object]:
    catalog_rights = canonical_rights(payload.title_id)
    page_url = str(payload.page_url)
    parsed = urlparse(page_url)
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise HTTPException(status_code=400, detail="capture page host is missing")
    validate_public_dns(host)
    if not host_allowed(host):
        raise HTTPException(status_code=403, detail="capture host is not in IMPORT_ALLOWED_HOSTS")
    capture_id = uuid.uuid4()
    rights_json = catalog_rights.model_dump(mode="json")
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            "INSERT INTO media_imports (id, title_id, source_url, source_type, source_bytes, rights, status, allowed_hosts, operation) "
            "VALUES (%s, %s, %s, 'application/x-wave-page', 0, %s, 'queued', %s, 'capture-page')",
            (capture_id, payload.title_id, page_url, json.dumps(rights_json), json.dumps([host])),
        )
        connection.commit()
    await redis.xadd(MEDIA_IMPORT_STREAM, {"id": str(capture_id)}, maxlen=10000, approximate=True)
    return {"id": str(capture_id), "status": "queued", "title_id": payload.title_id, "operation": "capture-page"}


'''
api = read("media-server/api/main.py")
if '@app.post("/v1/captures"' not in api:
    marker = '@app.post("/v1/accounts/sync", dependencies=[Depends(require_admin)])\n'
    if marker not in api:
        raise SystemExit("accounts sync anchor missing")
    api = api.replace(marker, capture_endpoint + marker, 1)
    write("media-server/api/main.py", api)

# ---------------------------------------------------------------------------
# 3) Web control path: page URL -> VPS capture job. The existing Chromium
#    network-capture and yt-dlp resolver remain available side-by-side.
# ---------------------------------------------------------------------------
control_action = r'''
  if (action === "capture-vps-page") {
    if (!canEdit(context)) return Response.json({ error: "forbidden" }, { status: 403 });
    if (!runtime.MEDIA_API_URL || !runtime.MEDIA_API_TOKEN) return Response.json({ error: "media_server_not_connected" }, { status: 503 });
    const entityType = body.entityType === "episode" ? "episode" : "title";
    const entityId = textValue(body.entityId, 80);
    const rightsTitle = await assertMediaEntityAccess(context, entityType, entityId);
    assertRightsActive(rightsTitle.rightsJson);
    const pageUrl = canonicalPublicMediaUrl(body.pageUrl);
    const remote = await callInternalServer("/v1/captures", "POST", { title_id: entityId, page_url: pageUrl }, "media_capture_failed");
    const remoteJobId = textValue(remote.id, 100);
    if (!remoteJobId) return Response.json({ error: "media_capture_failed" }, { status: 502 });
    const jobId = crypto.randomUUID();
    await env.DB.prepare("INSERT INTO media_jobs (id, entity_type, entity_id, operation, source_kind, remote_job_id, status, created_by) VALUES (?, ?, ?, 'capture-page', 'media-vps', ?, 'queued', ?)")
      .bind(jobId, entityType, entityId, remoteJobId, context.email).run();
    await audit(context, "media.capture-vps", entityType, entityId, { jobId, remoteJobId, pageUrl });
    return Response.json({ ok: true, backend: "media-vps", jobId, remoteJobId, status: "queued" });
  }

'''
control = read("app/api/control/route.ts")
if 'action === "capture-vps-page"' not in control:
    marker = '  if (action === "attach-direct-hls") {\n'
    if marker not in control:
        raise SystemExit("control attach HLS anchor missing")
    control = control.replace(marker, control_action + marker, 1)
    write("app/api/control/route.ts", control)

panel = read("components/browser-ingest-panel.tsx")
if "async function captureViaVps()" not in panel:
    marker = "  async function startLogin() {\n"
    function = r'''  async function captureViaVps() {
    const [entityType, entityId] = target.split(":");
    if (!entityType || !entityId) { setStatus("اختر الفيلم أو الحلقة أولاً."); return; }
    setStatus("جارٍ جلب الفيديو على VPS؛ بعد الحفظ سيبدأ HLS ثم الترجمة والدبلجة العربية تلقائياً…");
    try {
      const result = await postJson("/api/control", { action: "capture-vps-page", entityType, entityId, pageUrl });
      setStatus(`تم إنشاء مهمة جلب VPS: ${String(result.remoteJobId || result.jobId || "queued")}.`);
    } catch (error) { setStatus(error instanceof Error ? error.message : "vps_capture_failed"); }
  }

'''
    if marker not in panel:
        raise SystemExit("panel login anchor missing")
    panel = panel.replace(marker, function + marker, 1)

old_buttons = '''    <div className="review-actions"><button type="button" disabled={!browserReady || !pageUrl} onClick={() => void dynamicResolve()}>فحص Chromium تلقائي</button><button type="button" disabled={!browserReady || !pageUrl} onClick={() => void startLogin()}>فتح نافذة تسجيل الدخول</button><button type="button" disabled={!sessionId} onClick={() => void captureLogin(false)}>التقاط بعد تشغيل الفيديو</button>{mediaServerConnected && <button type="button" disabled={!pageUrl} onClick={() => void vpsResolve()}>فحص yt-dlp على VPS</button>}</div>'''
new_buttons = '''    <div className="review-actions"><button type="button" disabled={!browserReady || !pageUrl} onClick={() => void dynamicResolve()}>فحص Chromium تلقائي</button><button type="button" disabled={!browserReady || !pageUrl} onClick={() => void startLogin()}>فتح نافذة تسجيل الدخول</button><button type="button" disabled={!sessionId} onClick={() => void captureLogin(false)}>التقاط بعد تشغيل الفيديو</button>{mediaServerConnected && <button type="button" disabled={!pageUrl} onClick={() => void vpsResolve()}>فحص yt-dlp على VPS</button>}{mediaServerConnected && <button type="button" disabled={!pageUrl || !target} onClick={() => void captureViaVps()}>جلب الفيديو وحفظه عبر VPS</button>}</div>'''
if old_buttons not in panel:
    raise SystemExit("panel buttons anchor missing")
panel = panel.replace(old_buttons, new_buttons, 1)
write("components/browser-ingest-panel.tsx", panel)

print("RC15.5 patch applied: VPS capture + Arabic-only cached subtitles/dubbing")
