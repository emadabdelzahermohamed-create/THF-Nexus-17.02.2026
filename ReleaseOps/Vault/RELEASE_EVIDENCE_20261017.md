# THF Vault API 36 candidate

Source provenance: `THF-VAULT-CANONICAL-NATIVE-SOURCE-V2.zip`

- Authoritative source SHA-256: `052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432`
- Package: `com.topherofit.thf.vault`
- Compile/target SDK: 36
- Fix: the runtime now consumes the canonical `THF_BASE_URL` BuildConfig field used by `app/build.gradle`.
- Rollback: revert the single candidate commit; the earlier QA APK remains identified by SHA-256 `7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e`.

No production signing material is stored here. A successful CI build is an exact QA candidate only, not physical-phone or Play acceptance.
