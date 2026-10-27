import argparse
import json

PACKAGE = 'com.topherofit.thf.pulse'
LISTINGS = {
    'ar': {
        'title': 'Top Hero Fit: لياقة ونشاط',
        'shortDescription': 'تمارين منزلية وجيم أوفلاين، دليل صوتي، وخطط للمشي والجري والدراجات.',
        'fullDescription': '''Top Hero Fit يجمع التمارين وتتبع النشاط اليومي في تطبيق واحد يعمل بالعربية والإنجليزية.

الميزات الحالية:
• تتبع المشي والجري وركوب الدراجة باستخدام GPS.
• عرض الوقت والمسافة والسرعة والوتيرة والخطوات والسعرات التقديرية بحسب النشاط والبيانات المتاحة.
• استمرار جلسة النشاط في الخلفية مع إشعار دائم للتحكم والمتابعة.
• مكتبة تمارين وبرامج تدريب متاحة دون اتصال بعد تثبيت التطبيق.
• تعليمات للحركة والتنفس والسلامة مع إرشاد صوتي بالعربية والإنجليزية.
• واجهة عربية RTL وإنجليزية LTR وإعداد لتقليل الحركة.

Top Hero Fit مصمم لمساعدتك على بناء عادة تدريب ومتابعة نشاطك بوضوح دون خلط جلسات المشي والجري والدراجة مع برامج التمارين.

ملاحظات مهمة:
السعرات والقيم المشتقة تقديرات لياقة وليست قياسات طبية. جودة GPS تعتمد على الهاتف والموقع والبيئة المحيطة. التطبيق لا يقدم تشخيصًا طبيًا أو بديلًا عن نصيحة المختص.''',
    },
    'en-US': {
        'title': 'Top Hero Fit: Fitness & GPS',
        'shortDescription': 'Offline home workouts, voice guidance, and walking, running & cycling GPS.',
        'fullDescription': '''Top Hero Fit brings workouts and everyday activity tracking together in one Arabic- and English-ready fitness app.

Current features include:
• GPS activity sessions for walking, running and cycling.
• Time, distance, speed, pace, steps and estimated calories when supported by the activity and available data.
• Background activity sessions with an ongoing notification for status and controls.
• An offline-ready exercise library and structured training programs after the app is installed.
• Movement, breathing and safety guidance with Arabic and English voice cues.
• Arabic RTL and English LTR interfaces, plus a reduced-motion preference.

Top Hero Fit is designed to help you build a consistent training habit while keeping real walking, running and cycling sessions separate from workout programs.

Important notes:
Calories and derived fitness metrics are estimates, not medical measurements. GPS quality depends on your device, location and surroundings. Top Hero Fit does not provide medical diagnosis or replace professional medical advice.''',
    },
}

ICON_PATH = 'ReleaseOps/FitnessStandalone/assets/play_icon_512.png'

def validate_listings():
    from pathlib import Path
    from struct import unpack
    icon = Path(ICON_PATH)
    if not icon.is_file() or icon.stat().st_size > 1024 * 1024:
        raise ValueError('Play icon must exist and be no larger than 1 MB')
    with icon.open('rb') as handle:
        header = handle.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or unpack('>II', header[16:24]) != (512, 512):
        raise ValueError('Play icon must be a 512x512 PNG')
    for language, item in LISTINGS.items():
        if len(item['title']) > 30:
            raise ValueError(f'{language} title too long: {len(item["title"])}')
        if len(item['shortDescription']) > 80:
            raise ValueError(f'{language} short description too long: {len(item["shortDescription"])}')
        if len(item['fullDescription']) > 4000:
            raise ValueError(f'{language} full description too long: {len(item["fullDescription"])}')


def compact(items):
    return [
        {
            'language': item.get('language'),
            'title': item.get('title'),
            'shortDescription': item.get('shortDescription'),
            'fullDescription': item.get('fullDescription'),
        }
        for item in items
    ]


def sync(output_path):
    import google.auth
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    validate_listings()
    creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/androidpublisher'])
    api = build('androidpublisher', 'v3', credentials=creds, cache_discovery=False)
    edit = api.edits().insert(packageName=PACKAGE, body={}).execute()['id']
    try:
        before = api.edits().listings().list(packageName=PACKAGE, editId=edit).execute().get('listings', []) or []
        for language, item in LISTINGS.items():
            api.edits().listings().update(packageName=PACKAGE, editId=edit, language=language, body=item).execute()
            api.edits().images().upload(packageName=PACKAGE, editId=edit, language=language, imageType='icon', media_body=MediaFileUpload(ICON_PATH, mimetype='image/png', resumable=True)).execute()
        api.edits().commit(packageName=PACKAGE, editId=edit).execute()
        edit = None
    finally:
        if edit:
            api.edits().delete(packageName=PACKAGE, editId=edit).execute()

    verify = api.edits().insert(packageName=PACKAGE, body={}).execute()['id']
    try:
        after = api.edits().listings().list(packageName=PACKAGE, editId=verify).execute().get('listings', []) or []
    finally:
        api.edits().delete(packageName=PACKAGE, editId=verify).execute()

    expected = {language: (item['title'], item['shortDescription'], item['fullDescription']) for language, item in LISTINGS.items()}
    actual = {item.get('language'): (item.get('title'), item.get('shortDescription'), item.get('fullDescription')) for item in after}
    for language, value in expected.items():
        if actual.get(language) != value:
            raise RuntimeError(f'listing readback mismatch: {language}')

    result = {'package': PACKAGE, 'committed': True, 'before': compact(before), 'after': compact(after)}
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--output', default='evidence/PLAY_LISTING_SYNC.json')
    args = parser.parse_args()
    validate_listings()
    if args.validate_only:
        print(json.dumps({'package': PACKAGE, 'languages': list(LISTINGS), 'valid': True}, ensure_ascii=False))
        return
    sync(args.output)


if __name__ == '__main__':
    main()
