#!/usr/bin/env python3
import unittest
from simulation_receipt_gate import bind

H="a"*64; MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"

def epoch(): return {"status":"COMMITTED_FOR_SIMULATION","sign":False,"broadcast":False,"financial_execution":False,"reward_epoch_commitment_sha256":H,"epoch_id":"e1"}
def sim(): return {"cluster":"mainnet-beta","mint":MINT,"unsigned":True,"broadcast":False,"err":None,"slot":1,"message_sha256":"b"*64,"reward_epoch_commitment_sha256":H}

class Gate(unittest.TestCase):
 def test_ready(self):
  r=bind(epoch=epoch(),simulation=sim(),expected_mint=MINT); self.assertEqual(r["status"],"SIMULATION_EVIDENCE_READY_FOR_EXTERNAL_SIGNER_REVIEW"); self.assertFalse(r["sign"]); self.assertFalse(r["broadcast"]); self.assertFalse(r["financial_execution"])
 def test_epoch_mismatch_blocks(self):
  s=sim(); s["reward_epoch_commitment_sha256"]="c"*64; self.assertEqual(bind(epoch=epoch(),simulation=s,expected_mint=MINT)["status"],"BLOCKED")
 def test_signed_or_broadcast_blocks(self):
  s=sim(); s["unsigned"]=False; s["broadcast"]=True; r=bind(epoch=epoch(),simulation=s,expected_mint=MINT); self.assertEqual(r["status"],"BLOCKED")
 def test_rpc_error_blocks(self):
  s=sim(); s["err"]={"InstructionError":[0,"Custom"]}; self.assertEqual(bind(epoch=epoch(),simulation=s,expected_mint=MINT)["status"],"BLOCKED")
 def test_wrong_mint_cluster_blocks(self):
  s=sim(); s["mint"]="wrong"; s["cluster"]="devnet"; self.assertEqual(bind(epoch=epoch(),simulation=s,expected_mint=MINT)["status"],"BLOCKED")
if __name__=="__main__": unittest.main()
