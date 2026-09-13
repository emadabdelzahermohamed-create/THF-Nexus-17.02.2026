#!/usr/bin/env bash
set -Eeuo pipefail

MINT="${THF_TOKEN_MINT:-HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv}"
RPC_URL="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
OUT="${TOKENOPS_OUT:-tokenops-audit}"
mkdir -p "$OUT"

rpc() {
  local method="$1" params="$2" dest="$3"
  local body code attempt
  body="$(jq -cn --arg m "$method" --argjson p "$params" '{jsonrpc:"2.0",id:1,method:$m,params:$p}')"
  for attempt in 1 2 3 4 5; do
    code="$(curl --silent --show-error --connect-timeout 15 --max-time 60 \
      -H 'Content-Type: application/json' --data "$body" \
      --output "$dest.tmp" --write-out '%{http_code}' "$RPC_URL" || true)"
    if [ "$code" = "200" ] && jq -e '.result != null and (.error == null)' "$dest.tmp" >/dev/null 2>&1; then
      mv "$dest.tmp" "$dest"
      return 0
    fi
    sleep $((attempt * 2))
  done
  echo "RPC failure: method=$method http=$code" >&2
  [ -f "$dest.tmp" ] && cat "$dest.tmp" >&2 || true
  return 1
}

rpc_optional() {
  local method="$1" params="$2" dest="$3" fallback="$4"
  if rpc "$method" "$params" "$dest"; then
    jq --arg status ok '. + {tokenops_status:$status}' "$dest" > "$dest.norm" && mv "$dest.norm" "$dest"
  else
    printf '%s\n' "$fallback" | jq --arg status unavailable '. + {tokenops_status:$status}' > "$dest"
  fi
}

# Required authority/supply facts. Failure here invalidates the audit.
rpc getSlot '[{"commitment":"confirmed"}]' "$OUT/rpc-slot.json"
rpc getAccountInfo "[\"$MINT\",{\"encoding\":\"jsonParsed\",\"commitment\":\"confirmed\"}]" "$OUT/mint-account.json"
rpc getTokenSupply "[\"$MINT\",{\"commitment\":\"confirmed\"}]" "$OUT/token-supply.json"

# Optional public-RPC enrichments. Solana public RPC may rate-limit these methods.
rpc_optional getTokenLargestAccounts "[\"$MINT\",{\"commitment\":\"confirmed\"}]" "$OUT/largest-accounts.json" '{"jsonrpc":"2.0","id":1,"result":{"value":[]},"tokenops_note":"public RPC rate-limited optional largest-account query"}'
rpc_optional getSignaturesForAddress "[\"$MINT\",{\"limit\":20,\"commitment\":\"confirmed\"}]" "$OUT/recent-signatures.json" '{"jsonrpc":"2.0","id":1,"result":[],"tokenops_note":"public RPC rate-limited optional signature query"}'

mapfile -t TOKEN_ACCOUNTS < <(jq -r '.result.value[]?.address' "$OUT/largest-accounts.json" | head -20)
if [ "${#TOKEN_ACCOUNTS[@]}" -gt 0 ]; then
  ACCOUNTS_JSON="$(printf '%s\n' "${TOKEN_ACCOUNTS[@]}" | jq -R . | jq -s .)"
  rpc_optional getMultipleAccounts "[$ACCOUNTS_JSON,{\"encoding\":\"jsonParsed\",\"commitment\":\"confirmed\"}]" "$OUT/largest-account-details.json" '{"jsonrpc":"2.0","id":1,"result":{"value":[]},"tokenops_note":"optional token-account owner enrichment unavailable"}'
else
  jq -n '{jsonrpc:"2.0",id:1,result:{value:[]},tokenops_status:"skipped",tokenops_note:"no largest accounts returned by public RPC"}' > "$OUT/largest-account-details.json"
fi

python3 - "$MINT" "$OUT" <<'PY'
import json, pathlib, sys
mint=sys.argv[1]; out=pathlib.Path(sys.argv[2])
load=lambda n: json.loads((out/n).read_text())
acct=load('mint-account.json')['result']['value']
supply_doc=load('token-supply.json'); supply=supply_doc['result']['value']
slot=load('rpc-slot.json')['result']
largest_doc=load('largest-accounts.json'); largest=largest_doc['result']['value']
details_doc=load('largest-account-details.json'); details=details_doc['result']['value']
sigs_doc=load('recent-signatures.json'); sigs=sigs_doc['result']

parsed=((acct or {}).get('data') or {}).get('parsed') or {}
info=parsed.get('info') or {}
program=(acct or {}).get('owner')
program_name=parsed.get('type')

holders=[]
for i,item in enumerate(largest):
    detail=details[i] if i < len(details) else None
    dparsed=(((detail or {}).get('data') or {}).get('parsed') or {})
    dinfo=dparsed.get('info') or {}
    holders.append({
        'rank': i+1,
        'token_account': item.get('address'),
        'amount_raw': item.get('amount'),
        'ui_amount_string': item.get('uiAmountString'),
        'owner_wallet': dinfo.get('owner'),
        'state': dinfo.get('state'),
    })

audit={
  'network':'solana-mainnet-beta',
  'mint':mint,
  'rpc_slot':slot,
  'account_exists': acct is not None,
  'program_id':program,
  'parsed_account_type':program_name,
  'decimals': info.get('decimals', supply.get('decimals')),
  'supply_raw': supply.get('amount'),
  'supply_ui': supply.get('uiAmountString'),
  'mint_authority': info.get('mintAuthority'),
  'freeze_authority': info.get('freezeAuthority'),
  'is_initialized': info.get('isInitialized'),
  'largest_accounts_status': largest_doc.get('tokenops_status','unknown'),
  'largest_accounts':holders,
  'recent_signatures_status': sigs_doc.get('tokenops_status','unknown'),
  'recent_signature_count':len(sigs),
  'recent_signatures':[{
      'signature':x.get('signature'), 'slot':x.get('slot'), 'block_time':x.get('blockTime'),
      'confirmation_status':x.get('confirmationStatus'), 'err':x.get('err')
  } for x in sigs],
  'safety':{
      'read_only':True,
      'transaction_created':False,
      'transaction_signed':False,
      'transaction_submitted':False,
      'private_key_used':False,
  }
}
(out/'token-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
summary=[
 "THF_TOKEN_READONLY_AUDIT=PASS",
 "NETWORK=solana-mainnet-beta",
 f"MINT={mint}", f"RPC_SLOT={slot}", f"PROGRAM_ID={program}",
 f"DECIMALS={audit['decimals']}", f"SUPPLY_RAW={audit['supply_raw']}", f"SUPPLY_UI={audit['supply_ui']}",
 f"MINT_AUTHORITY={audit['mint_authority']}", f"FREEZE_AUTHORITY={audit['freeze_authority']}",
 f"LARGEST_ACCOUNTS_STATUS={audit['largest_accounts_status']}",
 f"RECENT_SIGNATURES_STATUS={audit['recent_signatures_status']}", f"RECENT_SIGNATURES={len(sigs)}",
 "TRANSACTION_CREATED=FALSE", "TRANSACTION_SIGNED=FALSE", "TRANSACTION_SUBMITTED=FALSE",
 "PRIVATE_KEY_USED=FALSE", "WAVE_UNTOUCHED=TRUE",
]
(out/'SUMMARY.txt').write_text('\n'.join(summary)+'\n')
print('\n'.join(summary))
PY

(cd "$OUT" && sha256sum token-audit.json mint-account.json token-supply.json largest-accounts.json largest-account-details.json recent-signatures.json rpc-slot.json SUMMARY.txt > SHA256SUMS.txt)
echo "TOKENOPS_EVIDENCE_SHA256=PASS"
