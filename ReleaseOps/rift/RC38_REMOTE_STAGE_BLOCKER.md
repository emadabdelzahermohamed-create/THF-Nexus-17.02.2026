# Rift RC38 remote staging blocker

The private GCP builder remains reachable through the established WIF path, but the exact cumulative Rift artifact bytes live in ChatGPT Library and are not exposed as an addressable authenticated builder input. ReleaseOps therefore cannot verify canonical RC38 SHA `46ee385c21fb2e437f48a051ab59d90010eb6b0b0b9727f269b37cfa20711c81` before Godot 4.7.2 or Android export. No substitute source is treated as authoritative.

Local/source work continued safely: RC38 focused and clean-extract gates passed, ZIP integrity passed, and deterministic rebuild reproduced the exact artifact SHA. Fresh Godot parser/import/headless and unsigned test-AAB remain pending until exact bytes can be staged.
