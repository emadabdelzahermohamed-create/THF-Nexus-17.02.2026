import importlib.util
import pathlib
import tempfile
import zipfile

SCRIPT = pathlib.Path(__file__).parents[1] / 'validators' / 'audit_game_apk_payload_v1.py'
spec = importlib.util.spec_from_file_location('gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def make_apk(tmp, payload: bytes, offline=False):
    p = pathlib.Path(tmp) / 'candidate.apk'
    with zipfile.ZipFile(p, 'w') as z:
        z.writestr('classes.dex', payload)
        if offline:
            z.writestr('assets/offline.html', b'<html>offline</html>')
    return p


def evaluate(apk, profile):
    with zipfile.ZipFile(apk) as z:
        text = gate.printable(z.read('classes.dex')).lower()
        names = z.namelist()
    has=lambda *xs:any(x.lower() in text for x in xs)
    web=has('android/webkit/WebView','android.webkit.WebView','WebViewClient') and has('loadUrl')
    off=any(n.lower().endswith('offline.html') for n in names)
    common=has('Choreographer','doFrame') and has('android/graphics/Canvas','android.graphics.Canvas','onDraw') and has('MotionEvent','onTouchEvent')
    learning=has('score','streak','level','nextQuestion','LearningGame')
    sensors=has('SensorManager') and has('SensorEvent','TYPE_ACCELEROMETER','TYPE_LINEAR_ACCELERATION')
    fitness=has('reps','lastRep','motion','FitnessGame')
    real=common and (learning if profile=='learning' else sensors and fitness)
    return real and not ((web or off) and not real)


def test_rejects_webview_offline_shell():
    with tempfile.TemporaryDirectory() as td:
        apk=make_apk(td,b'android/webkit/WebView WebViewClient loadUrl evaluateJavascript',True)
        assert not evaluate(apk,'learning')


def test_accepts_learning_game_payload():
    with tempfile.TemporaryDirectory() as td:
        apk=make_apk(td,b'Choreographer doFrame android/graphics/Canvas onDraw MotionEvent onTouchEvent score streak level nextQuestion')
        assert evaluate(apk,'learning')


def test_fitness_requires_sensor_runtime():
    with tempfile.TemporaryDirectory() as td:
        apk=make_apk(td,b'Choreographer doFrame android/graphics/Canvas onDraw MotionEvent onTouchEvent reps motion FitnessGame')
        assert not evaluate(apk,'fitness')


def test_accepts_sensor_fitness_payload():
    with tempfile.TemporaryDirectory() as td:
        apk=make_apk(td,b'Choreographer doFrame android/graphics/Canvas onDraw MotionEvent onTouchEvent SensorManager SensorEvent TYPE_ACCELEROMETER reps lastRep motion FitnessGame')
        assert evaluate(apk,'fitness')
