# App source snapshot

The live v1 is deployed on AppDeploy and uses:
- React/Vite Arabic RTL frontend.
- AppDeploy backend routes as a public Solana RPC gateway.
- No authentication secrets, no private keys, no automatic signatures.

Source files in this folder mirror the main custom logic used by the deployed v1. AppDeploy platform template glue is intentionally not vendored here.

Live URL: https://thf-token-manager-yrh1nu.v2.appdeploy.ai/
