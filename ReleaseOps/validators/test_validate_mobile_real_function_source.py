from pathlib import Path
import importlib.util
import tempfile

MODULE_PATH = Path(__file__).with_name('validate_mobile_real_function_source.py')
spec = importlib.util.spec_from_file_location('mobile_source_gate', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


def fixture(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(prefix='thf-mobile-source-gate-'))
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return root


def android_gradle(package='com.topherofit.thf.pulse') -> str:
    return f"""android {{
  namespace '{package}'
  compileSdk 36
  defaultConfig {{ applicationId '{package}'; targetSdk 36; minSdk 26 }}
}}
"""


def test_accepts_api36_external_https_source():
    root = fixture({
        'android/app/build.gradle': android_gradle(),
        'app/config.py': "BASE='https://api.thf.invalid'\n",
    })
    result = mod.audit(root, 'com.topherofit.thf.pulse')
    assert result['source_gate'] == 'PASS'
    assert result['truth_boundary']['physical_device_acceptance_required'] is True


def test_rejects_runtime_loopback():
    root = fixture({
        'android/app/build.gradle': android_gradle(),
        'templates/home.html': '<a href="http://127.0.0.1:8102/u/demo">link</a>',
    })
    result = mod.audit(root, 'com.topherofit.thf.pulse')
    assert result['source_gate'] == 'FAIL'
    assert any(v['code'] == 'RUNTIME_LOOPBACK_URL' for v in result['violations'])


def test_rejects_placeholder_external_destination():
    root = fixture({
        'android/app/build.gradle': android_gradle(),
        'app/main.py': "LANDING='https://example.com'\n",
    })
    result = mod.audit(root, 'com.topherofit.thf.pulse')
    assert result['source_gate'] == 'FAIL'
    assert any(v['code'] == 'PLACEHOLDER_EXTERNAL_URL' for v in result['violations'])


def test_negative_examples_in_tests_do_not_poison_runtime_gate():
    root = fixture({
        'android/app/build.gradle': android_gradle(),
        'tests/test_policy.py': "BAD='http://localhost:1234'\n",
    })
    assert mod.audit(root, 'com.topherofit.thf.pulse')['source_gate'] == 'PASS'


def test_rejects_wrong_package_or_missing_api36():
    root = fixture({'android/app/build.gradle': "android { compileSdk 35; defaultConfig { applicationId 'wrong.id'; targetSdk 35 } }"})
    result = mod.audit(root, 'com.topherofit.thf.pulse')
    codes = {v['code'] for v in result['violations']}
    assert {'PACKAGE_ID_NOT_BOUND', 'TARGET_SDK_36_NOT_PROVEN', 'COMPILE_SDK_36_NOT_PROVEN'} <= codes
