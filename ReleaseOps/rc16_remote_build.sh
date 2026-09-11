#!/usr/bin/env bash
set -Eeuo pipefail

# THF Platform RC16 remote build composer.
# Build-only workspace. Never writes back into canonical source archives.
# No production signing, no Play upload, no WAVE paths.

ROOT="${THF_RC16_BUILD_ROOT:-$HOME/thf-builder-rc16-build}"
OPS="$ROOT/ops"
WORK="$ROOT/work"
OUT="$ROOT/out"
CACHE="$ROOT/cache"
INPUTS_DIRECT="${THF_RC16_INPUTS_DIRECT:-$HOME/thf-builder/inputs-direct}"
INTAKE="${THF_RC16_INTAKE:-$OPS/rc16-intake.json}"
SDK="$ROOT/android-sdk"
GRADLE_HOME="$ROOT/gradle-home"
SUMMARY_TSV="$OUT/build-summary.tsv"

mkdir -p "$OPS" "$WORK" "$OUT" "$CACHE" "$GRADLE_HOME"
chmod 700 "$ROOT" "$OPS" "$WORK" "$OUT" "$CACHE" "$GRADLE_HOME"
: > "$SUMMARY_TSV"

fail(){ echo "FAIL: $*" >&2; exit 20; }
need(){ command -v "$1" >/dev/null 2>&1 || fail "missing required host tool: $1"; }
for c in python3 curl unzip zip sha256sum java; do need "$c"; done
[ "$(uname -m)" = "x86_64" ] || fail "x86_64 builder required"
[ -f "$INTAKE" ] || fail "missing intake: $INTAKE"
[ -d "$INPUTS_DIRECT" ] || fail "missing verified direct inputs: $INPUTS_DIRECT"

JAVA_MAJOR="$(java -version 2>&1 | sed -n '1s/.*version "\([0-9][0-9]*\).*/\1/p')"
[ "${JAVA_MAJOR:-0}" -ge 17 ] || fail "JDK 17+ required"
echo "THF_RC16_JAVA_MAJOR=$JAVA_MAJOR"

# Exact RC16 source verification and safe extraction.
rm -rf "$WORK/core" "$WORK/terra" "$WORK/rift"
python3 - "$INTAKE" "$INPUTS_DIRECT" "$WORK" <<'PY'
import hashlib,json,sys,zipfile
from pathlib import Path
cfg=json.load(open(sys.argv[1],encoding='utf-8'))
base=Path(sys.argv[2]); work=Path(sys.argv[3])

def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def safe_extract(zf,dest):
    root=dest.resolve()
    for m in zf.infolist():
        target=(dest/m.filename).resolve()
        if target != root and root not in target.parents:
            raise RuntimeError(f'unsafe zip member: {m.filename}')
    zf.extractall(dest)

for slug,s in cfg['sources'].items():
    artifact=base/s['artifact']
    if not artifact.is_file(): raise SystemExit(f'MISSING {slug} full archive: {artifact}')
    if sha_file(artifact)!=s['sha256']: raise SystemExit(f'FULL_SHA_MISMATCH {slug}')
    parts=s.get('parts') or []
    if parts:
        concat=hashlib.sha256()
        for pmeta in parts:
            p=base/pmeta['name']
            if not p.is_file(): raise SystemExit(f'MISSING_PART {slug} {pmeta["name"]}')
            if p.stat().st_size!=pmeta['size_bytes']: raise SystemExit(f'PART_SIZE_MISMATCH {slug} {p.name}')
            h=hashlib.sha256()
            with p.open('rb') as f:
                for b in iter(lambda:f.read(1024*1024),b''):
                    h.update(b); concat.update(b)
            if h.hexdigest()!=pmeta['sha256']: raise SystemExit(f'PART_SHA_MISMATCH {slug} {p.name}')
        if concat.hexdigest()!=s['sha256']: raise SystemExit(f'REASSEMBLED_SHA_MISMATCH {slug}')
    dest=work/slug; dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(artifact) as z:
        bad=z.testzip()
        if bad: raise SystemExit(f'ZIP_INTEGRITY_FAIL {slug} {bad}')
        safe_extract(z,dest)
    print(f'EXACT_SOURCE_AND_EXTRACT_PASS={slug}')
print('THF_RC16_EXACT_SOURCE_GATE=PASS')
PY

# RC2 pinned Android command-line tools / SDK 36 contract.
CMD_REV="15859902"
CMD_ZIP="commandlinetools-linux-${CMD_REV}_latest.zip"
CMD_SHA="4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583"
CMD_URL="https://dl.google.com/android/repository/$CMD_ZIP"
CMD_CACHE="$CACHE/$CMD_ZIP"
SDKMANAGER="$SDK/cmdline-tools/latest/bin/sdkmanager"

if [ ! -x "$SDKMANAGER" ]; then
  rm -rf "$CACHE/cmdline-unpack" "$SDK/cmdline-tools/latest"
  mkdir -p "$CACHE/cmdline-unpack" "$SDK/cmdline-tools"
  if [ ! -f "$CMD_CACHE" ] || ! echo "$CMD_SHA  $CMD_CACHE" | sha256sum -c - >/dev/null 2>&1; then
    rm -f "$CMD_CACHE"
    curl --fail --location --retry 5 --retry-delay 2 --connect-timeout 30 "$CMD_URL" -o "$CMD_CACHE"
  fi
  echo "$CMD_SHA  $CMD_CACHE" | sha256sum -c -
  unzip -q "$CMD_CACHE" -d "$CACHE/cmdline-unpack"
  mv "$CACHE/cmdline-unpack/cmdline-tools" "$SDK/cmdline-tools/latest"
fi
[ -x "$SDKMANAGER" ] || fail "sdkmanager bootstrap failed"
export ANDROID_SDK_ROOT="$SDK"
export ANDROID_HOME="$SDK"
export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"

# License acceptance is limited to the disposable SDK under ROOT.
yes | "$SDKMANAGER" --sdk_root="$SDK" --licenses >/dev/null 2>&1 || true
"$SDKMANAGER" --sdk_root="$SDK" \
  "platform-tools" "platforms;android-36" "build-tools;36.0.0"
[ -f "$SDK/platforms/android-36/android.jar" ] || fail "Android platform 36 missing after sdkmanager"
[ -x "$SDK/build-tools/36.0.0/aapt2" ] || fail "Build Tools 36.0.0 missing after sdkmanager"
echo "THF_ANDROID_SDK36=PASS"

# Deterministic current-source project map observed from exact RC16 archives.
declare -A PROJECTS AGPS GRADLES DIST_SHAS WRAPPER_SHAS PACKAGES
PROJECTS[core]="$WORK/core/android"
PROJECTS[terra]="$WORK/terra/android"
PROJECTS[rift]="$WORK/rift/THF_Nexus_Arena_Core/android-arena"
AGPS[core]="8.10.1"
AGPS[terra]="8.12.2"
AGPS[rift]="8.12.2"
GRADLES[core]="8.11.1"
GRADLES[terra]="8.13"
GRADLES[rift]="8.13"
DIST_SHAS[core]="f397b287023acdba1e9f6fc5ea72d22dd63669d59ed4a289a29b1a76eee151c6"
DIST_SHAS[terra]="20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78"
DIST_SHAS[rift]="20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78"
WRAPPER_SHAS[core]="2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046"
WRAPPER_SHAS[terra]="81a82aaea5abcc8ff68b3dfcb58b3c3c429378efd98e7433460610fecd7ae45f"
WRAPPER_SHAS[rift]="81a82aaea5abcc8ff68b3dfcb58b3c3c429378efd98e7433460610fecd7ae45f"
PACKAGES[core]="com.topherofit.thf.core"
PACKAGES[terra]="com.topherofit.thf.terra"
PACKAGES[rift]="com.topherofit.thf.rift"

verify_project(){
  local slug="$1" p="${PROJECTS[$1]}" agp="${AGPS[$1]}" pkg="${PACKAGES[$1]}"
  [ -f "$p/settings.gradle" ] || [ -f "$p/settings.gradle.kts" ] || return 30
  local combined
  combined="$(find "$p" -maxdepth 3 -type f \( -name '*.gradle' -o -name '*.gradle.kts' -o -name 'gradle.properties' \) -print0 | xargs -0 cat 2>/dev/null || true)"
  grep -Eq 'compileSdk([[:space:]]*=)?[[:space:]]*36|compileSdkVersion[[:space:]]+36' <<<"$combined" || return 31
  grep -Eq 'targetSdk([[:space:]]*=)?[[:space:]]*36|targetSdkVersion[[:space:]]+36' <<<"$combined" || return 32
  grep -Fq "$agp" <<<"$combined" || return 33
  grep -Fq "$pkg" <<<"$combined" || return 34
  if grep -Eq 'storeFile|storePassword|keyPassword|keyAlias' <<<"$combined"; then return 35; fi
  return 0
}

prepare_wrapper(){
  local slug="$1" p="${PROJECTS[$1]}" ver="${GRADLES[$1]}" dsha="${DIST_SHAS[$1]}" wsha="${WRAPPER_SHAS[$1]}"
  local z="$CACHE/gradle-${ver}-bin.zip" dir="$CACHE/gradle-dist-${ver}"
  if [ ! -f "$z" ] || ! echo "$dsha  $z" | sha256sum -c - >/dev/null 2>&1; then
    rm -f "$z"
    curl --fail --location --retry 5 --retry-delay 2 --connect-timeout 30 \
      "https://services.gradle.org/distributions/gradle-${ver}-bin.zip" -o "$z"
  fi
  echo "$dsha  $z" | sha256sum -c -
  if [ ! -x "$dir/gradle-${ver}/bin/gradle" ]; then
    rm -rf "$dir"; mkdir -p "$dir"; unzip -q "$z" -d "$dir"
  fi
  (
    cd "$p"
    "$dir/gradle-${ver}/bin/gradle" --no-daemon wrapper --gradle-version "$ver" --distribution-type bin
    chmod +x gradlew
    echo "$wsha  gradle/wrapper/gradle-wrapper.jar" | sha256sum -c -
    python3 - "gradle/wrapper/gradle-wrapper.properties" "$dsha" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); sha=sys.argv[2]
lines=p.read_text().splitlines()
lines=[x for x in lines if not x.startswith('distributionSha256Sum=')]
lines.append('distributionSha256Sum='+sha)
p.write_text('\n'.join(lines)+'\n')
PY
  )
}

build_one(){
  local slug="$1" p="${PROJECTS[$1]}" agp="${AGPS[$1]}" gradle="${GRADLES[$1]}"
  echo "===== BUILD_START $slug project=$p AGP=$agp Gradle=$gradle ====="
  mkdir -p "$OUT/$slug"
  local log="$OUT/$slug/gradle-build.log"
  if ! verify_project "$slug"; then
    rc=$?; printf '%s\tVERIFY_FAILED_%s\t%s\t%s\t%s\n' "$slug" "$rc" "$p" "$agp" "$gradle" >> "$SUMMARY_TSV"
    echo "BUILD_VERIFY_FAILED=$slug rc=$rc" | tee "$log"
    return 0
  fi
  if ! prepare_wrapper "$slug" >"$OUT/$slug/wrapper.log" 2>&1; then
    rc=$?; printf '%s\tWRAPPER_FAILED_%s\t%s\t%s\t%s\n' "$slug" "$rc" "$p" "$agp" "$gradle" >> "$SUMMARY_TSV"
    tail -200 "$OUT/$slug/wrapper.log" || true
    return 0
  fi
  set +e
  (
    cd "$p"
    export GRADLE_USER_HOME="$GRADLE_HOME"
    export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK"
    ./gradlew --no-daemon --stacktrace :app:assembleDebug :app:bundleRelease
  ) >"$log" 2>&1
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    printf '%s\tBUILD_FAILED_%s\t%s\t%s\t%s\n' "$slug" "$rc" "$p" "$agp" "$gradle" >> "$SUMMARY_TSV"
    echo "BUILD_FAILED=$slug rc=$rc"
    tail -200 "$log" || true
    return 0
  fi
  found=0
  while IFS= read -r -d '' f; do
    found=1
    base="$(basename "$f")"
    cp -f "$f" "$OUT/$slug/${slug}-${base}"
  done < <(find "$p/app/build/outputs" -type f \( -name '*.apk' -o -name '*.aab' \) -print0 2>/dev/null)
  if [ "$found" -ne 1 ]; then
    printf '%s\tNO_CANDIDATE_ARTIFACT\t%s\t%s\t%s\n' "$slug" "$p" "$agp" "$gradle" >> "$SUMMARY_TSV"
    return 0
  fi
  printf '%s\tBUILT_UNSIGNED_TEST\t%s\t%s\t%s\n' "$slug" "$p" "$agp" "$gradle" >> "$SUMMARY_TSV"
  echo "BUILD_PASS=$slug"
}

for slug in core terra rift; do build_one "$slug"; done

python3 - "$INTAKE" "$OUT" "$SUMMARY_TSV" "$JAVA_MAJOR" "$CMD_REV" <<'PY'
import hashlib,json,sys,zipfile,subprocess
from pathlib import Path
intake=json.load(open(sys.argv[1],encoding='utf-8'))
out=Path(sys.argv[2]); tsv=Path(sys.argv[3]); java=sys.argv[4]; cmdrev=sys.argv[5]
rows=[]
for line in tsv.read_text().splitlines():
    if not line.strip(): continue
    slug,status,project,agp,gradle=line.split('\t',4)
    rows.append({'slug':slug,'status':status,'project':project,'agp':agp,'gradle':gradle})
summary={'checkpoint':'PLATFORM-RC16-2026-09-11','builds':rows,'toolchain':{'java_major':java,'android_command_line_tools_revision':cmdrev,'android_platform':36,'build_tools':'36.0.0'},'truth':{'production_signing_performed':False,'play_upload_performed':False,'canonical_source_mutated':False,'wave_mutated':False}}
(out/'BUILD_SUMMARY_RC16.json').write_text(json.dumps(summary,indent=2))
arts=[]
for p in sorted(out.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in {'.apk','.aab'}: continue
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    e={'path':str(p.relative_to(out)),'sha256':h.hexdigest(),'size_bytes':p.stat().st_size,'kind':p.suffix.lower()[1:]}
    try:
        with zipfile.ZipFile(p) as z:
            e['zip_integrity']=z.testzip() is None
            names=set(z.namelist())
            e['manifest_present']=('AndroidManifest.xml' in names or 'base/manifest/AndroidManifest.xml' in names)
    except Exception as ex:
        e['zip_integrity']=False; e['error']=str(ex)
    arts.append(e)
evidence={'checkpoint':'PLATFORM-RC16-2026-09-11','source_intake':{k:{'checkpoint':v['checkpoint'],'sha256':v['sha256'],'package_id':v['package_id']} for k,v in intake['sources'].items()},'artifacts':arts,'truth':summary['truth']}
(out/'PACKAGE_EVIDENCE_RC16.json').write_text(json.dumps(evidence,indent=2))
print(json.dumps(summary,indent=2))
print(json.dumps(evidence,indent=2))
PY

sha256sum "$OUT/BUILD_SUMMARY_RC16.json" "$OUT/PACKAGE_EVIDENCE_RC16.json" > "$OUT/SHA256SUMS_RC16_BUILD_EVIDENCE.txt"
find "$OUT" -type f \( -name '*.apk' -o -name '*.aab' \) -print0 | sort -z | xargs -0 -r sha256sum >> "$OUT/SHA256SUMS_RC16_BUILD_EVIDENCE.txt"

cat "$OUT/SHA256SUMS_RC16_BUILD_EVIDENCE.txt"
cat "$OUT/BUILD_SUMMARY_RC16.json"
cat "$OUT/PACKAGE_EVIDENCE_RC16.json"

python3 - "$OUT/BUILD_SUMMARY_RC16.json" "$OUT/PACKAGE_EVIDENCE_RC16.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1])); e=json.load(open(sys.argv[2]))
bad=[x for x in s['builds'] if x['status']!='BUILT_UNSIGNED_TEST']
by={x['slug'] for x in s['builds'] if x['status']=='BUILT_UNSIGNED_TEST'}
art_slugs={a['path'].split('/',1)[0] for a in e['artifacts']}
if bad or by!={'core','terra','rift'} or not {'core','terra','rift'} <= art_slugs:
    print('THF_RC16_UNSIGNED_BUILD=FAIL')
    raise SystemExit(40)
if not all(a.get('zip_integrity') and a.get('manifest_present') for a in e['artifacts']):
    print('THF_RC16_PACKAGE_INSPECTION=FAIL')
    raise SystemExit(41)
print('THF_RC16_UNSIGNED_BUILD=PASS')
print('THF_RC16_PACKAGE_INSPECTION=PASS')
print('PRODUCTION_SIGNING_PERFORMED=FALSE')
print('PLAY_UPLOAD_PERFORMED=FALSE')
print('WAVE_UNTOUCHED=TRUE')
PY
