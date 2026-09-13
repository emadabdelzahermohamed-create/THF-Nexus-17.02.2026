#!/usr/bin/env python3
import copy, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('burn_plan', HERE/'burn_plan.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
sample=json.loads((HERE/'examples'/'burn_plan.sample.json').read_text())
p=mod.build(copy.deepcopy(sample))
assert p['planned_burn_raw']=='200000000000000000', p
assert p['projected_supply_raw']=='800000000000000000', p
assert all(s['token_account']!='UnverifiedAccount' for s in p['sources'])
assert p['execution']['transaction_created'] is False
assert p['execution']['transaction_signed'] is False
assert p['execution']['transaction_submitted'] is False
assert p['execution']['burn_executed'] is False
bad=copy.deepcopy(sample); bad['mint']='bad'
try:
    mod.build(bad); raise AssertionError('wrong mint must fail')
except ValueError: pass
print('THF_TOKENOPS_BURN_TESTS=PASS')
print('TRANSACTION_CREATED=FALSE')
print('TRANSACTION_SIGNED=FALSE')
print('TRANSACTION_SUBMITTED=FALSE')
print('BURN_EXECUTED=FALSE')
