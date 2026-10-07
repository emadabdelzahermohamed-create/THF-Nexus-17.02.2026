#!/usr/bin/env python3
"""Build the deterministic, bilingual Fitness V2 offline program library."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
EXERCISES_PATH = PULSE / "data" / "exercises.json"
PROGRAMS_PATH = PULSE / "data" / "programs.json"
PROGRAMS_JS_PATH = PULSE / "data" / "programs.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "PROGRAMS_MANIFEST.json"

SOURCE_COMMIT = "f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5"

# Two real programs per first-class Train section. Names and prescriptions are
# original THF editorial composition; referenced exercise data/media retain the
# pinned public-domain source provenance recorded in the exercise catalog.
SPECS = [
    ("gym-foundations", "gym", "Gym Foundations", "أساسيات الجيم", "beginner", "general_fitness", 6, 3, 42),
    ("gym-strength-builder", "gym", "Strength Builder", "بناء القوة", "intermediate", "strength", 8, 4, 55),
    ("home-foundations", "home", "Home Foundations", "أساسيات المنزل", "beginner", "general_fitness", 4, 3, 28),
    ("home-progressive-strength", "home", "Progressive Home Strength", "قوة منزلية متدرجة", "intermediate", "strength", 6, 4, 35),
    ("walk-run-foundation", "running", "Walk to Run", "من المشي إلى الجري", "beginner", "endurance", 6, 3, 32),
    ("run-5k-capacity", "running", "5K Capacity", "الاستعداد لخمسة كيلومترات", "intermediate", "endurance", 8, 4, 42),
    ("cycling-base", "cycling", "Cycling Base", "قاعدة ركوب الدراجات", "beginner", "endurance", 6, 3, 38),
    ("cycling-intervals", "cycling", "Cycling Intervals", "فترات الدراجة", "intermediate", "conditioning", 6, 4, 45),
    ("football-speed", "football", "Football Speed", "سرعة كرة القدم", "beginner", "speed", 6, 3, 36),
    ("football-match-fitness", "football", "Match Fitness", "لياقة المباراة", "intermediate", "conditioning", 8, 4, 45),
    ("swim-dryland", "swimming", "Swim Dryland Foundation", "إعداد السباحة خارج الماء", "beginner", "general_fitness", 6, 3, 35),
    ("swim-strength", "swimming", "Swim Strength", "قوة السباحة", "intermediate", "strength", 8, 3, 44),
    ("yoga-foundations", "yoga", "Yoga Foundations", "أساسيات اليوغا", "beginner", "mobility", 4, 3, 28),
    ("yoga-balance-flow", "yoga", "Balance Flow", "تدفق التوازن", "intermediate", "balance", 6, 4, 34),
    ("calisthenics-foundations", "calisthenics", "Calisthenics Foundations", "أساسيات الكاليستنكس", "beginner", "strength", 6, 3, 38),
    ("calisthenics-skills", "calisthenics", "Strength and Skills", "القوة والمهارات", "intermediate", "skill", 8, 4, 48),
    ("boxing-foundations", "boxing", "Boxing Foundations", "أساسيات الملاكمة", "beginner", "conditioning", 6, 3, 34),
    ("boxing-power-core", "boxing", "Power and Core", "القوة والجذع للملاكمة", "intermediate", "power", 8, 4, 42),
    ("hiit-low-impact", "hiit", "Low-impact HIIT", "تمارين متقطعة منخفضة الأثر", "beginner", "conditioning", 4, 3, 24),
    ("hiit-performance", "hiit", "HIIT Performance", "أداء التمارين المتقطعة", "intermediate", "power", 6, 4, 32),
    ("daily-mobility", "mobility", "Daily Mobility", "حركة يومية", "beginner", "mobility", 4, 5, 18),
    ("performance-mobility", "mobility", "Performance Mobility", "حركة لتحسين الأداء", "intermediate", "mobility", 6, 4, 26),
    ("recovery-reset", "recovery", "Recovery Reset", "إعادة ضبط الاستشفاء", "beginner", "recovery", 4, 4, 20),
    ("recovery-after-training", "recovery", "Post-training Recovery", "استشفاء ما بعد التدريب", "intermediate", "recovery", 6, 5, 24),
    ("team-speed", "team_sports", "Team Sport Speed", "سرعة الرياضات الجماعية", "beginner", "agility", 6, 3, 34),
    ("racket-agility", "team_sports", "Racket Agility", "رشاقة رياضات المضرب", "intermediate", "balance", 6, 4, 38),
]

SUPPORT = {
    "gym": ["mobility", "home"],
    "home": ["mobility", "recovery"],
    "running": ["mobility", "home", "recovery"],
    "cycling": ["mobility", "home", "recovery"],
    "football": ["hiit", "mobility", "home"],
    "swimming": ["gym", "mobility", "recovery"],
    "yoga": ["mobility", "recovery"],
    "calisthenics": ["home", "mobility"],
    "boxing": ["hiit", "home", "mobility"],
    "hiit": ["home", "mobility", "recovery"],
    "mobility": ["yoga", "recovery"],
    "recovery": ["mobility", "yoga"],
    "team_sports": ["football", "hiit", "mobility"],
}

SECTION_SUMMARY = {
    "gym": ("Progressive gym sessions with clear load, RPE and RIR targets.", "جلسات جيم متدرجة بأهداف واضحة للحمل وRPE وRIR."),
    "home": ("Practical sessions built for limited space and simple equipment.", "جلسات عملية لمساحة محدودة ومعدات بسيطة."),
    "running": ("Build durable running capacity without abrupt mileage jumps.", "ابنِ قدرة جري مستدامة دون قفزات مفاجئة في المسافة."),
    "cycling": ("Develop aerobic efficiency, cadence control and repeatable power.", "طوّر الكفاءة الهوائية والتحكم في الإيقاع والقدرة المتكررة."),
    "football": ("Prepare acceleration, agility and repeat-effort fitness for football.", "طوّر التسارع والرشاقة والقدرة على تكرار الجهد لكرة القدم."),
    "swimming": ("Dryland support for body line, pull strength and kick endurance.", "إعداد خارج الماء لوضع الجسم وقوة السحب وتحمل الرجلين."),
    "yoga": ("Practice controlled positions, breathing and balance with clear options.", "تدرّب على الوضعيات والتنفس والتوازن مع بدائل واضحة."),
    "calisthenics": ("Progress bodyweight strength from stable foundations to skills.", "طوّر قوة وزن الجسم من الأساس الثابت إلى المهارات."),
    "boxing": ("Condition footwork, trunk rotation and repeatable striking power.", "طوّر حركة القدمين ودوران الجذع وقوة الضرب المتكررة."),
    "hiit": ("Use bounded work-rest intervals with scalable impact and intensity.", "استخدم فترات عمل وراحة محددة مع أثر وشدة قابلين للتدرج."),
    "mobility": ("Restore useful range of motion through controlled daily practice.", "استعد مدى حركة مفيدًا عبر ممارسة يومية مضبوطة."),
    "recovery": ("Downshift after training with tissue work and calm movement.", "اخفض الشدة بعد التدريب بعمل الأنسجة وحركة هادئة."),
    "team_sports": ("Build transferable speed, landing control and change of direction.", "طوّر السرعة والتحكم في الهبوط وتغيير الاتجاه للرياضات."),
}

SAFETY = {
    "en": "Stop for sharp pain, dizziness, chest pain, or unusual shortness of breath. Keep two good repetitions in reserve until technique is consistent.",
    "ar": "توقف عند الألم الحاد أو الدوار أو ألم الصدر أو ضيق النفس غير المعتاد. اترك عدتين جيدتين في الاحتياط حتى يثبت الأداء الصحيح.",
}

SECTION_SAFETY = {
    "gym": ("Use safeties or a spotter for loaded barbell work.", "استخدم حواجز الأمان أو مساعدًا في تمارين البار المحمّلة."),
    "home": ("Clear the floor and keep furniture outside the movement path.", "أخلِ الأرضية وأبعد الأثاث عن مسار الحركة."),
    "running": ("Build time before speed and stop if pain changes your stride.", "زد زمن التدريب قبل السرعة وتوقف إذا غيّر الألم طريقة خطوتك."),
    "cycling": ("Set the bike securely and keep cadence controlled before adding resistance.", "ثبّت الدراجة جيدًا واضبط الإيقاع قبل زيادة المقاومة."),
    "football": ("Use a non-slip surface and recover fully before maximal direction changes.", "استخدم سطحًا غير زلق واستعد بالكامل قبل تغييرات الاتجاه القصوى."),
    "swimming": ("This is dryland support and does not replace supervised water practice.", "هذا إعداد خارج الماء ولا يستبدل تدريب السباحة تحت إشراف."),
    "yoga": ("Move within a pain-free range; never force a joint into position.", "تحرك داخل مدى خالٍ من الألم ولا تجبر المفصل على وضعية."),
    "calisthenics": ("Use stable bars and earn control before harder leverage or inversion.", "استخدم قضبانًا ثابتة وأتقن التحكم قبل الرافعات أو الأوضاع المقلوبة الأصعب."),
    "boxing": ("This program is conditioning only; contact and sparring require a qualified coach.", "هذا برنامج لياقة فقط؛ الاحتكاك والنزال يحتاجان مدربًا مؤهلًا."),
    "hiit": ("Choose the low-impact option when landing control or breathing deteriorates.", "اختر البديل منخفض الأثر عند تراجع التحكم في الهبوط أو التنفس."),
    "mobility": ("Use gentle tension only and avoid bouncing into end range.", "استخدم شدًا لطيفًا فقط وتجنب الارتداد عند نهاية المدى."),
    "recovery": ("Foam rolling should feel tolerable, never sharp or numbing.", "يجب أن يبقى التدليك بالأسطوانة محتملًا دون ألم حاد أو تنميل."),
    "team_sports": ("Keep landing space clear and reduce speed before adding reaction demands.", "أخلِ مساحة الهبوط وقلّل السرعة قبل إضافة متطلبات الاستجابة."),
}

SESSION_NAMES = [
    {"en": "Technique and base", "ar": "الأساس والتكنيك"},
    {"en": "Capacity and control", "ar": "القدرة والتحكم"},
    {"en": "Progressive effort", "ar": "جهد متدرج"},
    {"en": "Strength and repeatability", "ar": "القوة وتكرار الأداء"},
    {"en": "Quality recovery session", "ar": "جلسة استشفاء بجودة"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def localized_level(level: str) -> dict[str, str]:
    return {
        "id": level,
        "en": {"beginner": "Beginner", "intermediate": "Intermediate", "expert": "Advanced"}[level],
        "ar": {"beginner": "مبتدئ", "intermediate": "متوسط", "expert": "متقدم"}[level],
    }


def localized_goal(goal: str) -> dict[str, str]:
    labels = {
        "general_fitness": ("General fitness", "لياقة عامة"),
        "strength": ("Strength", "القوة"),
        "endurance": ("Endurance", "التحمل"),
        "conditioning": ("Conditioning", "اللياقة البدنية"),
        "speed": ("Speed", "السرعة"),
        "mobility": ("Mobility", "الحركة"),
        "balance": ("Balance", "التوازن"),
        "skill": ("Skill", "المهارة"),
        "power": ("Power", "القدرة الانفجارية"),
        "recovery": ("Recovery", "الاستشفاء"),
        "agility": ("Agility", "الرشاقة"),
    }
    en, ar = labels[goal]
    return {"id": goal, "en": en, "ar": ar}


def progression_for(weeks: int, level: str) -> dict[str, list[str]]:
    build_end = max(2, weeks - 2)
    target_rpe = 7 if level == "beginner" else 8
    return {
        "en": [
            "Week 1: learn technique and finish every working set with 3–4 repetitions in reserve.",
            f"Weeks 2–{build_end}: add one repetition first; add 2–5% load only when form stays stable at RPE {target_rpe} or lower.",
            f"Week {weeks - 1}: keep the same exercises and confirm repeatable technique without grinding repetitions.",
            f"Week {weeks}: reduce working sets by 30–40%, review progress, then repeat or move to the next level.",
        ],
        "ar": [
            "الأسبوع الأول: تعلّم الأداء وأنهِ كل مجموعة عمل مع 3–4 عدات في الاحتياط.",
            f"الأسابيع 2–{build_end}: أضف عدة أولًا، ثم 2–5% للحمل فقط مع ثبات الأداء عند RPE {target_rpe} أو أقل.",
            f"الأسبوع {weeks - 1}: حافظ على نفس التمارين وتأكد من تكرار الأداء الصحيح دون عدات قسرية.",
            f"الأسبوع {weeks}: قلّل مجموعات العمل 30–40%، راجع تقدمك، ثم كرر البرنامج أو انتقل للمستوى التالي.",
        ],
    }


def build() -> list[dict]:
    exercises = json.loads(EXERCISES_PATH.read_text())
    by_id = {item["id"]: item for item in exercises}
    by_section: dict[str, list[dict]] = defaultdict(list)
    for item in exercises:
        by_section[item["section"]["id"]].append(item)
    for items in by_section.values():
        items.sort(key=lambda item: item["id"])

    programs = []
    for program_index, (program_id, section_id, name_en, name_ar, level, goal, weeks, days, minutes) in enumerate(SPECS):
        primary = by_section[section_id]
        support = [item for support_id in SUPPORT[section_id] for item in by_section[support_id]]
        pool = primary + support
        sessions = []
        used = []
        for session_index, session_name in enumerate(SESSION_NAMES[:days]):
            picks = []
            # Guarantee each session contains at least two exercises from its own section.
            for offset in range(min(3, len(primary))):
                picks.append(primary[(program_index + session_index * 2 + offset) % len(primary)])
            cursor = program_index + session_index
            while len(picks) < 5:
                candidate = pool[cursor % len(pool)]
                cursor += 1
                if candidate["id"] not in {item["id"] for item in picks}:
                    picks.append(candidate)
            used.extend(picks)
            prescriptions = []
            for exercise_index, item in enumerate(picks):
                source = item["prescription"]
                prescriptions.append({
                    "exerciseId": item["id"],
                    "role": "warmup" if exercise_index == 0 else "working",
                    "sets": 2 if exercise_index == 0 else max(2, int(source.get("sets") or 3)),
                    "reps": source.get("reps"),
                    "durationSeconds": source.get("durationSeconds"),
                    "restSeconds": min(150, max(30, int(source.get("restSeconds") or 60))),
                    "targetRpe": 5 if exercise_index == 0 else (7 if level == "beginner" else 8),
                    "targetRir": 4 if exercise_index == 0 else (3 if level == "beginner" else 2),
                })
            sessions.append({
                "id": f"{program_id}-session-{session_index + 1}",
                "name": session_name,
                "estimatedMinutes": minutes,
                "exercises": prescriptions,
            })

        section = primary[0]["section"]
        equipment = {}
        for item in used:
            equipment[item["equipment"]["id"]] = item["equipment"]
        summary_en, summary_ar = SECTION_SUMMARY[section_id]
        safety_en, safety_ar = SECTION_SAFETY[section_id]
        programs.append({
            "id": program_id,
            "name": {"en": name_en, "ar": name_ar},
            "summary": {"en": summary_en, "ar": summary_ar},
            "section": section,
            "goal": localized_goal(goal),
            "level": localized_level(level),
            "weeks": weeks,
            "daysPerWeek": days,
            "estimatedSessionMinutes": minutes,
            "equipment": sorted(equipment.values(), key=lambda value: value["id"]),
            "safety": {"en": f"{SAFETY['en']} {safety_en}", "ar": f"{SAFETY['ar']} {safety_ar}"},
            "progression": progression_for(weeks, level),
            "offline": True,
            "sessions": sessions,
            "provenance": {
                "origin": "Top Hero Fit Fitness V2 editorial composition",
                "license": "THF-owned original program metadata",
                "exerciseCatalogRepository": "yuhonas/free-exercise-db",
                "exerciseCatalogCommit": SOURCE_COMMIT,
                "exerciseCatalogLicense": "Unlicense",
            },
        })
    return programs


def write(programs: list[dict]) -> None:
    serialized = json.dumps(programs, ensure_ascii=False, indent=2) + "\n"
    PROGRAMS_PATH.write_text(serialized)
    PROGRAMS_JS_PATH.write_text("window.THF_PROGRAMS = " + serialized.rstrip() + ";\n")
    section_counts = Counter(program["section"]["id"] for program in programs)
    manifest = {
        "schemaVersion": 1,
        "programCount": len(programs),
        "sectionCounts": dict(sorted(section_counts.items())),
        "programsSha256": sha256(PROGRAMS_PATH),
        "source": {
            "programMetadata": "Top Hero Fit Fitness V2 editorial composition",
            "programMetadataLicense": "THF-owned original",
            "exerciseCatalogRepository": "yuhonas/free-exercise-db",
            "exerciseCatalogCommit": SOURCE_COMMIT,
            "exerciseCatalogLicense": "Unlicense",
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    write(build())
