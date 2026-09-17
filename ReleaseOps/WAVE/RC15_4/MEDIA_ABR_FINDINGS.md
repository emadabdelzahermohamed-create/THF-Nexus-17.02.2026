# WAVE RC15.4 — Media ABR Findings

Date: 2026-09-17
Scope: WAVE_MAWJA only

## Verified transcoding implementation

The reconstructed RC15.3 source already contains a real FFmpeg adaptive-bitrate pipeline for VOD and live sources.

### VOD / uploaded or imported files

`media-server/worker/abr.py` probes the real input with ffprobe and builds only renditions at or below the source height. The configured ladder is 144p, 240p, 360p, 480p, 720p, 1080p, 1440p and 2160p. Non-standard source heights keep a native top rendition. The source is decoded once, split once, and all selected renditions are encoded in one FFmpeg process. Output is an HLS master playlist (`master.m3u8`), per-rendition playlists, HLS segments, and optional per-quality MP4 downloads. Encoder selection is automatic: NVIDIA `h264_nvenc` when available, otherwise `libx264`.

`media-server/worker/worker.py` sends imported files through this transcoder and publishes the resulting HLS master URL as the playback URL.

### Live

`media-server/live-worker/live_worker.py` probes the live source and creates an HLS adaptive ladder using the same resolution family without upscaling. Current live HLS segments are 2 seconds. Live input can be pull-based or push-based through MediaMTX; the stack has RTMP, SRT and HLS support. The live API exposes a generated `master.m3u8` playback URL.

`/v1/encoder/capabilities` reports VOD automatic transcoding with no-upscale and single-decode, and live automatic transcoding with no-upscale and the same 144p–2160p ladder.

## Production connection gap

The deployed Cloudflare Worker currently has `DB` and `BROWSER` bindings, but it does not have `MEDIA_API_URL` or `MEDIA_API_TOKEN` bindings. It also does not have Cloudflare Stream runtime token bindings. Therefore the production web Worker is not currently connected to either the self-hosted FFmpeg media API or Cloudflare Stream.

The existing GitHub `CLOUDFLARE_API_TOKEN` can manage the deployed Worker/D1 path used by RC15.3, but read-only probes to Cloudflare Stream video and live-input endpoints returned HTTP 403 / authentication error. A separate token with Stream permission would be required to use Cloudflare Stream as the transcoding backend.

## Current routing behavior that must change for universal ABR

For a normal file URL such as MP4, `auto-import-url` already prefers the self-hosted media API and then can fall back to Cloudflare Stream when configured. Once the self-hosted media API is connected, MP4 imports can automatically become multi-rendition HLS.

For an already-HLS source, current control routing attaches the HLS URL directly and does not transcode it. RC15.4 should change this policy so a single-rendition HLS source is normalized through the media engine and gets lower adaptive renditions. A source that already has a valid multi-variant master can be retained directly or normalized according to operator policy.

The platform must remain truthful: it may generate lower resolutions from a high-resolution source, but must not present an upscaled rendition as genuine higher source quality. Example: a real 720p source may become 144/240/360/480/720, but not genuine 1080p.

## Available initial media host

The existing GCP VM `thf-wave-builder` is RUNNING as `e2-standard-4`, with 4 vCPU, about 15 GiB RAM, about 126 GiB free on the root filesystem at inspection time, Docker 29.1.3 and FFmpeg 6.1.1 installed. No NVIDIA encoder was observed in the read-only host inspection.

This is sufficient for an initial CPU-based VOD queue and limited live testing, but it should not be treated as a high-concurrency production transcoding cluster. The code already supports automatic NVENC use when GPU capacity is added later.

## RC15.4 target policy

1. File sources (MP4/MOV/MKV/WebM/etc.) -> media worker -> FFmpeg ABR -> generated HLS master.
2. Single-rendition HLS -> media/live worker -> generated lower renditions -> WAVE-owned HLS master.
3. Live RTMP/SRT/HTTP/HLS -> live worker -> real-time FFmpeg ABR -> WAVE-owned HLS master.
4. Existing valid multi-variant HLS -> direct or normalize depending on policy and rights.
5. Player primary source -> HLS master; direct MP4 is fallback/download rather than the normal adaptive playback path.
6. Data Saver -> cap the selected HLS level to a low rung and keep adaptive switching within the cap.
