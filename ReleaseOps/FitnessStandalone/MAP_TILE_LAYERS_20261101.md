# Top Hero Fit map tile sources and operational constraints

Date: 2026-11-01
Scope: activity map tiles only; no payment method, billing account, or paid map API is used.

## In-app layers

### Street — OpenStreetMap standard raster
- Tile endpoint: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
- Data attribution: © OpenStreetMap contributors.
- Tile-service policy: https://operations.osmfoundation.org/policies/tiles/
- Operational rules: identify the app with a stable User-Agent, honor normal HTTP caching, show visible attribution, do not prefetch or bulk-download, and do not promise an SLA.
- The app sets `TopHeroFit/<versionName>` in the WebView User-Agent and keeps WebView cache mode at `LOAD_DEFAULT`.

### Terrain — OpenTopoMap
- Tile endpoint: `https://{a|b|c}.tile.opentopomap.org/{z}/{x}/{y}.png`
- Attribution: Map data © OpenStreetMap contributors, SRTM; map style © OpenTopoMap.
- License: CC-BY-SA; commercial use is allowed with attribution/share-alike under the provider's published terms.
- Provider information: https://opentopomap.org/about
- Operational rules: volunteer/community service, no SLA, fair use, no bulk tile downloads or prefetch.

### Satellite — EOxCloudless 2016
- Tile endpoint: `https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg`
- This is the 2016 Sentinel-2 cloudless imagery layer, not current imagery. The UI explicitly labels it “Satellite 2016”.
- Current WMTS capabilities: https://tiles.maps.eox.at/wmts/1.0.0/WMTSCapabilities.xml
- Attribution: “EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016)”.
- Current WMTS capabilities identify the layer as CC BY 4.0. Do not copy the older CC BY-SA wording from historical blog posts.

### Hybrid — EOxCloudless 2016 + EOX streets overlay
- Satellite layer above plus transparent streets overlay:
  `https://tiles.maps.eox.at/wmts/1.0.0/streets_3857/default/g/{z}/{y}/{x}.png`
- Attribution: Data © OpenStreetMap contributors; rendering © EOX and MapServer; link back to https://maps.eox.at/.
- The layer's WMTS capabilities contain the current attribution text. Re-check provider terms before materially increasing request volume.

## Google Maps Platform state
- Maps SDK for Android service: ENABLED.
- API Keys API: ENABLED.
- The Google Cloud Console credentials flow for the THF project prompts to select/link a Google Maps Platform billing account. No billing account was linked and no payment method was added.
- The release-builder service account cannot list API keys; no Google Maps API key was created or stored.
- Native Google Maps SDK and Google traffic/transit overlays are therefore not active in the app. The app retains a Google Maps external directions handoff.
- Do not link a billing account or add a payment method without explicit owner approval. The current no-billing map stack is the approved fallback.

## Network and security
- WebView external HTTP(S) resources are allowed only for exact HTTPS tile hosts/paths used above. Other external HTTP(S) subresources are intercepted and blocked.
- Local `file://` and `data:` assets remain available.
- Map tile layers use normal browser caching and conservative viewport loading; no offline tile prefetch or bulk download is performed.
- Four live tile smoke checks returned HTTP 200: OSM, OpenTopoMap, EOX satellite, and EOX streets overlay.
