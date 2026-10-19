# THF Social Control Plane

Owned, provider-agnostic social/community orchestration for the THF ecosystem.

Principles:
- strengthen the sports/learning -> competition/community -> fair rewards/utility flywheel;
- official APIs and owned infrastructure first;
- free/open-source/existing capacity before paid routes;
- never publish financial-return promises or unverified token claims;
- encrypted secrets only via environment/secret manager; never commit tokens;
- every publish action must produce an audit event and external id.

Current direct adapters: Facebook Pages, Threads, X. Credentials are intentionally absent.
Transitional connectors (Windsor/Metricool) may be used while direct OAuth apps are provisioned.

Run tests:

```bash
python -m unittest discover -s ReleaseOps/SocialControlPlane/tests -v
```
