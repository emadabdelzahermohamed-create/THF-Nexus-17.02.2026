# OTC RPC boundary checkpoint — 2026-10-24

Outcome: added deterministic HTTP-boundary tests for the read-only finalized Solana RPC transport used by the THF OTC validation path.

Coverage added: HTTPS-only endpoint rejection; finalized getSlot request shape; finalized/jsonParsed/minContextSlot getAccountInfo request shape; fail-closed RPC error handling; invalid finalized slot rejection; invalid token-account inputs rejected before network access.

Safety: no keys, signatures, sendTransaction, mainnet transfer, sale, deposit, or paid endpoint introduced. Tests mock the HTTP boundary and do not settle anything.

Next executable step: run these tests in an executable checkout/CI, then wire the transport into the existing fail-closed account parser. Only after that gate passes: build an unsigned synthetic standard-program transaction and use simulateTransaction with sigVerify=false. Do not sign or broadcast.

Commercial state: no qualified buyer with final address/quantity/price is recorded here; no funds raised and no THF sold by this checkpoint.
