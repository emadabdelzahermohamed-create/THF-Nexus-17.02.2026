#!/usr/bin/env python3
"""Build the audited offline Fitness V2 exercise catalog.

Input is an explicit checkout of yuhonas/free-exercise-db.  The generated
catalog and copied image sequences are deterministic and carry item-level
source/license metadata.  No network request happens at application runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


SOURCE_REPOSITORY = "https://github.com/yuhonas/free-exercise-db"
SOURCE_LICENSE = "Unlicense"
SOURCE_LICENSE_URL = "https://github.com/yuhonas/free-exercise-db/blob/main/LICENSE.md"
IMPORTED_AT = "2026-10-03"

# id, Arabic name, product section, goal override (optional)
SELECTION = [
    ("Barbell_Bench_Press_-_Medium_Grip", "ضغط صدر بالبار", "gym", "muscle_gain"),
    ("Barbell_Squat", "سكوات بالبار", "gym", "strength"),
    ("Barbell_Deadlift", "رفعة ميتة بالبار", "gym", "strength"),
    ("Bent_Over_Barbell_Row", "تجديف بالبار منحنيًا", "gym", "muscle_gain"),
    ("Barbell_Shoulder_Press", "ضغط كتف بالبار", "gym", "muscle_gain"),
    ("Barbell_Hip_Thrust", "دفع الحوض بالبار", "gym", "muscle_gain"),
    ("Romanian_Deadlift", "رفعة رومانية", "gym", "strength"),
    ("Front_Barbell_Squat", "سكوات أمامي بالبار", "gym", "strength"),
    ("Incline_Dumbbell_Press", "ضغط صدر مائل بالدمبل", "gym", "muscle_gain"),
    ("Dumbbell_Bench_Press", "ضغط صدر بالدمبل", "gym", "muscle_gain"),
    ("Goblet_Squat", "سكوات جوبلت", "gym", "general_fitness"),
    ("One-Arm_Dumbbell_Row", "تجديف دمبل بذراع واحدة", "gym", "muscle_gain"),
    ("Dumbbell_Shoulder_Press", "ضغط كتف بالدمبل", "gym", "muscle_gain"),
    ("Dumbbell_Bicep_Curl", "مرجحة بايسبس بالدمبل", "gym", "muscle_gain"),
    ("Hammer_Curls", "مرجحة هامر", "gym", "muscle_gain"),
    ("Side_Lateral_Raise", "رفرفة جانبية بالدمبل", "gym", "muscle_gain"),
    ("Tricep_Dumbbell_Kickback", "رفس ترايسبس بالدمبل", "gym", "muscle_gain"),
    ("Dumbbell_Step_Ups", "صعود الصندوق بالدمبل", "gym", "strength"),
    ("Seated_Cable_Rows", "تجديف كيبل جالس", "gym", "muscle_gain"),
    ("Close-Grip_Front_Lat_Pulldown", "سحب أمامي قبضة ضيقة", "gym", "muscle_gain"),
    ("Face_Pull", "سحب الحبل للوجه", "gym", "posture"),
    ("Cable_Crossover", "تفتيح صدر بالكيبل", "gym", "muscle_gain"),
    ("Triceps_Pushdown_-_Rope_Attachment", "دفع ترايسبس بالحبل", "gym", "muscle_gain"),
    ("Pallof_Press", "ضغط بالوف لمقاومة الدوران", "gym", "core"),
    ("Leg_Press", "ضغط الأرجل", "gym", "muscle_gain"),
    ("Leg_Extensions", "مدّ الركبة على الجهاز", "gym", "muscle_gain"),
    ("Lying_Leg_Curls", "ثني خلفية الفخذ مستلقيًا", "gym", "muscle_gain"),
    ("Standing_Calf_Raises", "رفع السمانة واقفًا", "gym", "muscle_gain"),
    ("Machine_Bench_Press", "ضغط صدر على الجهاز", "gym", "muscle_gain"),
    ("Leverage_High_Row", "تجديف علوي على الجهاز", "gym", "muscle_gain"),
    ("Dip_Machine", "متوازي على الجهاز", "gym", "muscle_gain"),
    ("Smith_Machine_Squat", "سكوات سميث", "gym", "strength"),
    ("Smith_Machine_Bench_Press", "ضغط صدر سميث", "gym", "muscle_gain"),
    ("Kettlebell_One-Legged_Deadlift", "رفعة كيتل بيل بساق واحدة", "gym", "balance"),
    ("One-Arm_Kettlebell_Swings", "مرجحة كيتل بيل بذراع واحدة", "gym", "power"),
    ("Lateral_Raise_-_With_Bands", "رفرفة جانبية بالمطاط", "gym", "muscle_gain"),
    ("Bodyweight_Squat", "سكوات بوزن الجسم", "home", "general_fitness"),
    ("Bodyweight_Walking_Lunge", "اندفاع أمامي متحرك", "home", "general_fitness"),
    ("Pushups", "ضغط أرضي", "home", "general_fitness"),
    ("Plank", "بلانك أمامي", "home", "core"),
    ("Side_Bridge", "بلانك جانبي", "home", "core"),
    ("Single_Leg_Glute_Bridge", "جسر الحوض بساق واحدة", "home", "general_fitness"),
    ("Air_Bike", "دراجة البطن", "home", "core"),
    ("Mountain_Climbers", "متسلق الجبل", "hiit", "conditioning"),
    ("Crunches", "كرنش للبطن", "home", "core"),
    ("Russian_Twist", "لف روسي", "home", "core"),
    ("Superman", "سوبرمان أرضي", "home", "posture"),
    ("Inchworm", "مشي اليدين", "mobility", "mobility"),
    ("Pullups", "عقلة", "calisthenics", "strength"),
    ("Dips_-_Triceps_Version", "متوازي للترايسبس", "calisthenics", "strength"),
    ("Handstand_Push-Ups", "ضغط الوقوف على اليدين", "calisthenics", "skill"),
    ("Hanging_Leg_Raise", "رفع الرجلين معلقًا", "calisthenics", "core"),
    ("Trail_Running_Walking", "جري أو مشي على المسار", "running", "endurance"),
    ("Jogging_Treadmill", "هرولة على جهاز الجري", "running", "endurance"),
    ("Walking_Treadmill", "مشي على جهاز الجري", "running", "general_fitness"),
    ("Running_Treadmill", "جري على جهاز الجري", "running", "endurance"),
    ("Prowler_Sprint", "عدو دفع الزلاجة", "running", "speed"),
    ("Runners_Stretch", "إطالة العدّائين", "running", "mobility"),
    ("Linear_Acceleration_Wall_Drill", "تسارع خطي أمام الحائط", "football", "speed"),
    ("Box_Skip", "خطوات سريعة على الصندوق", "football", "agility"),
    ("Front_Cone_Hops_or_hurdle_hops", "قفز أمامي فوق الأقماع", "football", "agility"),
    ("Lateral_Cone_Hops", "قفز جانبي فوق الأقماع", "football", "agility"),
    ("Single-Cone_Sprint_Drill", "تدريب العدو حول قمع واحد", "football", "speed"),
    ("Side_Hop-Sprint", "قفز جانبي ثم انطلاق", "football", "speed"),
    ("Bicycling", "ركوب الدراجة", "cycling", "endurance"),
    ("Bicycling_Stationary", "دراجة ثابتة", "cycling", "endurance"),
    ("Recumbent_Bike", "دراجة ثابتة بمقعد خلفي", "cycling", "endurance"),
    ("Barbell_Step_Ups", "صعود الصندوق بالبار للدراجات", "cycling", "strength"),
    ("Platform_Hamstring_Slides", "انزلاق خلفية الفخذ للدراجات", "cycling", "strength"),
    ("Standing_Dumbbell_Calf_Raise", "رفع السمانة بالدمبل للدراجات", "cycling", "strength"),
    ("Rowing_Stationary", "تجديف ثابت", "hiit", "endurance"),
    ("Fast_Skipping", "نط حبل سريع", "boxing", "conditioning"),
    ("Medicine_Ball_Full_Twist", "دوران كامل بالكرة الطبية", "boxing", "power"),
    ("Heavy_Bag_Thrust", "دفع الكيس الثقيل", "boxing", "power"),
    ("Side_to_Side_Box_Shuffle", "خطوات جانبية سريعة للملاكمة", "boxing", "agility"),
    ("Pallof_Press_With_Rotation", "ضغط بالوف مع الدوران", "boxing", "core"),
    ("One-Arm_Medicine_Ball_Slam", "رمي الكرة الطبية بذراع واحدة", "boxing", "power"),
    ("Flutter_Kicks", "رفرفة الرجلين للسباحة", "swimming", "conditioning"),
    ("Full_Range-Of-Motion_Lat_Pulldown", "سحب لات بمدى كامل", "swimming", "strength"),
    ("Straight-Arm_Dumbbell_Pullover", "سحب دمبل بذراعين ممدودتين للسباحة", "swimming", "strength"),
    ("External_Rotation_with_Band", "دوران خارجي بالمطاط للسباحة", "swimming", "strength"),
    ("One_Arm_Lat_Pulldown", "سحب لات بذراع واحدة للسباحة", "swimming", "strength"),
    ("Dumbbell_Scaption", "رفع سكابشن بالدمبل للسباحة", "swimming", "strength"),
    ("Childs_Pose", "وضعية الطفل", "yoga", "mobility"),
    ("Cat_Stretch", "تمدد القطة", "yoga", "mobility"),
    ("Pelvic_Tilt_Into_Bridge", "إمالة الحوض إلى الجسر", "yoga", "mobility"),
    ("Downward_Facing_Balance", "توازن الوجه لأسفل", "yoga", "balance"),
    ("Dancers_Stretch", "إطالة الراقص", "yoga", "mobility"),
    ("Spinal_Stretch", "إطالة العمود الفقري", "yoga", "mobility"),
    ("90_90_Hamstring", "تمدد خلفية الفخذ 90/90", "mobility", "mobility"),
    ("Standing_Gastrocnemius_Calf_Stretch", "تمدد السمانة واقفًا", "mobility", "mobility"),
    ("Ankle_Circles", "دوائر الكاحل", "mobility", "mobility"),
    ("Standing_Hip_Circles", "دوائر الحوض واقفًا", "mobility", "mobility"),
    ("Worlds_Greatest_Stretch", "الإطالة الشاملة", "mobility", "mobility"),
    ("Hamstring-SMR", "تحرير خلفية الفخذ بالفوم رول", "recovery", "recovery"),
    ("Calves-SMR", "تحرير السمانة بالفوم رول", "recovery", "recovery"),
    ("Latissimus_Dorsi-SMR", "تحرير عضلات الظهر العريضة بالفوم رول", "recovery", "recovery"),
    ("Quadriceps-SMR", "تحرير أمامية الفخذ بالفوم رول", "recovery", "recovery"),
    ("Piriformis-SMR", "تحرير العضلة الكمثرية بالفوم رول", "recovery", "recovery"),
    ("Iliotibial_Tract-SMR", "تحرير الشريط الحرقفي بالفوم رول", "recovery", "recovery"),
    ("Front_Box_Jump", "قفز أمامي على الصندوق", "hiit", "power"),
    ("Freehand_Jump_Squat", "سكوات قفز", "hiit", "conditioning"),
    ("Elliptical_Trainer", "جهاز إليبتيكال", "hiit", "endurance"),
    ("Medicine_Ball_Chest_Pass", "تمرير الكرة الطبية من الصدر", "team_sports", "power"),
    ("Step-up_with_Knee_Raise", "صعود مع رفع الركبة", "team_sports", "balance"),
    ("Catch_and_Overhead_Throw", "التقاط ورمي الكرة من أعلى", "team_sports", "power"),
    ("Medicine_Ball_Scoop_Throw", "رمي الكرة الطبية من أسفل", "team_sports", "power"),
    ("Lateral_Bound", "وثب جانبي", "team_sports", "agility"),
    ("Single-Leg_Lateral_Hop", "قفز جانبي بساق واحدة", "team_sports", "balance"),
    ("Overhead_Slam", "رمي الكرة الطبية من أعلى", "hiit", "power"),
    ("Scapular_Pull-Up", "عقلة لوح الكتف", "calisthenics", "skill"),
    ("Parallel_Bar_Dip", "متوازي على عارضتين", "calisthenics", "strength"),
]

MUSCLES_AR = {
    "abdominals": "البطن", "abductors": "مبعدات الفخذ", "adductors": "مقربات الفخذ",
    "biceps": "البايسبس", "calves": "السمانة", "chest": "الصدر", "forearms": "الساعد",
    "glutes": "الألوية", "hamstrings": "خلفية الفخذ", "lats": "الظهر العريض",
    "lower back": "أسفل الظهر", "middle back": "منتصف الظهر", "neck": "الرقبة",
    "quadriceps": "أمامية الفخذ", "shoulders": "الكتف", "traps": "الترابيس", "triceps": "الترايسبس",
}

EQUIPMENT_AR = {
    None: "بدون معدات", "": "بدون معدات", "body only": "وزن الجسم", "barbell": "بار وأوزان",
    "dumbbell": "دمبل", "cable": "كيبل", "machine": "جهاز مقاومة", "kettlebells": "كيتل بيل",
    "bands": "مطاط مقاومة", "medicine ball": "كرة طبية", "exercise ball": "كرة تمرين",
    "foam roll": "فوم رول", "e-z curl bar": "بار EZ", "other": "معدات بسيطة",
}

SECTION_LABELS = {
    "gym": ("Gym", "الجيم"), "home": ("Home", "المنزل"),
    "running": ("Running & walking", "الجري والمشي"), "cycling": ("Cycling", "الدراجات"),
    "football": ("Football", "كرة القدم"), "swimming": ("Swimming", "السباحة"),
    "yoga": ("Yoga & Pilates", "اليوجا والبيلاتس"),
    "calisthenics": ("Calisthenics & gymnastics", "الكاليستنكس والجمباز"),
    "boxing": ("Boxing & martial arts", "الملاكمة والفنون القتالية"),
    "hiit": ("HIIT & cardio", "الكارديو والتمارين المتقطعة"),
    "mobility": ("Mobility & stretching", "الحركة والإطالة"),
    "recovery": ("Recovery", "الاستشفاء"),
    "team_sports": ("Racket & team conditioning", "إعداد رياضات المضرب والفرق"),
}

LEVEL_AR = {"beginner": "مبتدئ", "intermediate": "متوسط", "expert": "متقدم"}
GOAL_AR = {
    "muscle_gain": "بناء العضلات", "strength": "القوة", "general_fitness": "لياقة عامة",
    "posture": "تحسين القوام", "core": "ثبات الجذع", "balance": "التوازن", "power": "القوة الانفجارية",
    "conditioning": "التحمل البدني", "skill": "المهارة", "endurance": "التحمل", "speed": "السرعة",
    "agility": "الرشاقة", "mobility": "الحركة", "recovery": "الاستشفاء",
}

PATTERN_AR = {
    "squat": "سكوات/دفع سفلي", "hinge": "مفصل الورك", "horizontal_push": "دفع أفقي",
    "vertical_push": "دفع رأسي", "horizontal_pull": "سحب أفقي", "vertical_pull": "سحب رأسي",
    "isolation": "عزل عضلي", "core": "مقاومة حركة الجذع", "locomotion": "انتقال هوائي",
    "jump": "قفز وهبوط", "mobility": "حركة وإطالة", "recovery": "تحرير عضلي",
}

PATTERN_OVERRIDES = {
    "Prowler_Sprint": "locomotion",
    "Front_Cone_Hops_or_hurdle_hops": "jump",
    "Lateral_Cone_Hops": "jump",
    "Single-Cone_Sprint_Drill": "locomotion",
    "Side_Hop-Sprint": "jump",
    "Platform_Hamstring_Slides": "hinge",
    "Heavy_Bag_Thrust": "horizontal_push",
    "Side_to_Side_Box_Shuffle": "locomotion",
    "Pallof_Press_With_Rotation": "core",
    "One-Arm_Medicine_Ball_Slam": "jump",
    "Straight-Arm_Dumbbell_Pullover": "vertical_pull",
    "Catch_and_Overhead_Throw": "vertical_push",
    "Medicine_Ball_Scoop_Throw": "hinge",
    "Lateral_Bound": "jump",
    "Single-Leg_Lateral_Hop": "jump",
}

FAMILY = {
    "squat": {
        "setup_en": "Set the feet securely, brace the trunk, and align knees with toes before loading the descent.",
        "setup_ar": "ثبّت القدمين، شد الجذع، واجعل الركبتين في اتجاه أصابع القدم قبل النزول.",
        "steps_ar": ["انزل بالحوض بتحكم مع بقاء القدم كاملة على الأرض.", "حافظ على ثبات الجذع وتتبع الركبة لاتجاه القدم.", "ادفع الأرض واصعد من دون قفل الركبتين بعنف."],
        "breathing_en": "Inhale and brace before descending; exhale through the effort.",
        "breathing_ar": "خذ شهيقًا وثبّت الجذع قبل النزول، وازفر أثناء الصعود.",
        "mistakes_en": ["Knees collapsing inward", "Heels lifting", "Losing trunk control"],
        "mistakes_ar": ["انهيار الركبتين للداخل", "ارتفاع الكعبين", "فقدان ثبات الجذع"],
    },
    "hinge": {
        "setup_en": "Brace the trunk, soften the knees, and keep the load close before moving the hips back.",
        "setup_ar": "شد الجذع، اثن الركبتين قليلًا، وأبقِ الحمل قريبًا قبل دفع الحوض للخلف.",
        "steps_ar": ["ادفع الحوض للخلف مع ظهر محايد.", "توقف قبل أن تفقد ثبات الجذع أو موضع الحمل.", "اضغط بالأقدام ومد الحوض للعودة دون فرط تقوس الظهر."],
        "breathing_en": "Brace on the way down and exhale after passing the hardest point.",
        "breathing_ar": "ثبّت النفس أثناء النزول وازفر بعد تجاوز أصعب نقطة.",
        "mistakes_en": ["Rounding the back", "Load drifting away", "Hyperextending at lockout"],
        "mistakes_ar": ["تقويس الظهر", "ابتعاد الحمل عن الجسم", "فرط مد أسفل الظهر في النهاية"],
    },
    "horizontal_push": {
        "setup_en": "Set the shoulder blades, keep wrists stacked, and establish a stable base before pressing.",
        "setup_ar": "ثبّت لوحي الكتف، اجعل الرسغ فوق المرفق، وثبّت قاعدة الجسم قبل الدفع.",
        "steps_ar": ["اخفض الحمل أو الجسم بتحكم حتى مدى مريح.", "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.", "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا."],
        "breathing_en": "Inhale during the controlled descent; exhale as you press.",
        "breathing_ar": "خذ شهيقًا أثناء النزول وازفر مع الدفع.",
        "mistakes_en": ["Elbows flaring excessively", "Bouncing at the bottom", "Losing wrist alignment"],
        "mistakes_ar": ["فتح المرفقين أكثر من اللازم", "الارتداد في الأسفل", "انحراف الرسغ"],
    },
    "vertical_push": {
        "setup_en": "Brace ribs over pelvis and start with forearms vertical and shoulders controlled.",
        "setup_ar": "ثبّت القفص الصدري فوق الحوض وابدأ بساعدين رأسيين وكتفين متحكم فيهما.",
        "steps_ar": ["ادفع الحمل لأعلى في مسار مريح.", "لا ترفع الكتفين نحو الأذنين ولا تقوس أسفل الظهر.", "اخفض الحمل ببطء إلى وضع البداية."],
        "breathing_en": "Exhale while pressing overhead; inhale on the return.",
        "breathing_ar": "ازفر أثناء الدفع لأعلى وخذ شهيقًا عند العودة.",
        "mistakes_en": ["Arching the lower back", "Shrugging", "Pressing unevenly"],
        "mistakes_ar": ["تقويس أسفل الظهر", "رفع الكتفين", "الدفع بشكل غير متساوٍ"],
    },
    "horizontal_pull": {
        "setup_en": "Lengthen the spine, brace the trunk, and begin with the shoulder blades controlled.",
        "setup_ar": "أطل العمود الفقري، شد الجذع، وابدأ بلوحي كتف متحكم فيهما.",
        "steps_ar": ["اسحب المرفقين للخلف دون هز الجذع.", "قرّب لوحي الكتف مع إبقاء الرقبة مرتاحة.", "مد الذراعين بتحكم من دون إسقاط الحمل."],
        "breathing_en": "Exhale as you pull; inhale during the controlled reach.",
        "breathing_ar": "ازفر أثناء السحب وخذ شهيقًا أثناء العودة المتحكم فيها.",
        "mistakes_en": ["Jerking the torso", "Shrugging", "Cutting the range short"],
        "mistakes_ar": ["هز الجذع", "رفع الكتفين", "اختصار مدى الحركة"],
    },
    "vertical_pull": {
        "setup_en": "Take a secure grip, brace the trunk, and depress the shoulders before pulling.",
        "setup_ar": "أمسك بثبات، شد الجذع، وأنزل الكتفين قبل بدء السحب.",
        "steps_ar": ["ابدأ الحركة من لوح الكتف ثم اسحب بالمرفقين.", "تجنب التأرجح وحافظ على الصدر مرفوعًا طبيعيًا.", "عد إلى المد الكامل بتحكم ومن دون ترك المفصل يسقط."],
        "breathing_en": "Exhale while pulling; inhale as the arms return overhead.",
        "breathing_ar": "ازفر أثناء السحب وخذ شهيقًا عند عودة الذراعين لأعلى.",
        "mistakes_en": ["Swinging", "Pulling behind the neck", "Losing shoulder control"],
        "mistakes_ar": ["التأرجح", "السحب خلف الرقبة", "فقدان التحكم في الكتف"],
    },
    "isolation": {
        "setup_en": "Choose a controllable load, stabilize the nearby joints, and align the working joint.",
        "setup_ar": "اختر حملًا يمكن التحكم فيه، ثبّت المفاصل القريبة، واضبط محاذاة المفصل العامل.",
        "steps_ar": ["حرّك المفصل المستهدف فقط قدر الإمكان.", "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.", "عد ببطء وحافظ على شد العضلة."],
        "breathing_en": "Exhale during the lift or extension; inhale on the controlled return.",
        "breathing_ar": "ازفر أثناء الرفع أو المد وخذ شهيقًا أثناء العودة.",
        "mistakes_en": ["Using momentum", "Moving adjacent joints", "Choosing excessive load"],
        "mistakes_ar": ["استخدام الزخم", "تحريك مفاصل غير مستهدفة", "اختيار حمل زائد"],
    },
    "core": {
        "setup_en": "Stack ribs over pelvis, brace gently, and choose a range that preserves spinal control.",
        "setup_ar": "ضع القفص الصدري فوق الحوض، شد البطن برفق، واختر مدى يحافظ على ثبات العمود الفقري.",
        "steps_ar": ["ابدأ من جذع ثابت وتنفس دون حبس طويل.", "نفّذ الحركة ببطء ومن دون شد الرقبة.", "توقف قبل فقدان وضع الحوض أو أسفل الظهر."],
        "breathing_en": "Keep breathing; exhale during the hardest phase without losing the brace.",
        "breathing_ar": "استمر في التنفس وازفر في أصعب مرحلة من دون فقدان ثبات الجذع.",
        "mistakes_en": ["Holding the breath", "Pulling the neck", "Arching the lower back"],
        "mistakes_ar": ["حبس النفس", "شد الرقبة", "تقويس أسفل الظهر"],
    },
    "locomotion": {
        "setup_en": "Start at an easy pace, use stable footwear or equipment, and keep the route clear.",
        "setup_ar": "ابدأ بإيقاع سهل، استخدم حذاءً أو جهازًا ثابتًا، وتأكد من خلو المسار.",
        "steps_ar": ["ارفع الإيقاع تدريجيًا مع وضع جسم مريح.", "حافظ على خطوات أو دورات سلسة ويمكنك التحدث بجمل قصيرة.", "اخفض السرعة تدريجيًا قبل التوقف."],
        "breathing_en": "Use rhythmic breathing and reduce intensity if breathing becomes uncontrolled.",
        "breathing_ar": "تنفس بإيقاع منتظم وخفّض الشدة إذا فقدت التحكم في التنفس.",
        "mistakes_en": ["Starting too fast", "Overstriding", "Stopping abruptly"],
        "mistakes_ar": ["البدء بسرعة كبيرة", "إطالة الخطوة أكثر من اللازم", "التوقف المفاجئ"],
    },
    "jump": {
        "setup_en": "Clear the landing area, align feet and knees, and rehearse a quiet landing first.",
        "setup_ar": "أخلِ منطقة الهبوط، اضبط القدمين والركبتين، وتدرّب أولًا على هبوط هادئ.",
        "steps_ar": ["حمّل الورك والركبتين بسرعة متحكم فيها.", "ادفع الأرض وحافظ على اتجاه الركبتين.", "اهبط بهدوء واثبت قبل التكرار التالي."],
        "breathing_en": "Exhale on takeoff and reset the breath after each stable landing.",
        "breathing_ar": "ازفر عند القفز وأعد ضبط النفس بعد كل هبوط ثابت.",
        "mistakes_en": ["Knees collapsing inward", "Loud rigid landing", "Repeating before balance returns"],
        "mistakes_ar": ["انهيار الركبتين للداخل", "هبوط صلب وصاخب", "التكرار قبل استعادة التوازن"],
    },
    "mobility": {
        "setup_en": "Move into a supported, pain-free position and keep the breath relaxed.",
        "setup_ar": "اتخذ وضعًا مدعومًا وخاليًا من الألم وحافظ على تنفس هادئ.",
        "steps_ar": ["ادخل المدى ببطء حتى شد خفيف لا ألم.", "حافظ على الوضع والتنفس من دون ارتداد.", "اخرج من الوضع تدريجيًا وكرر على الجهة الأخرى عند الحاجة."],
        "breathing_en": "Use slow nasal breathing and relax further on each exhale.",
        "breathing_ar": "استخدم تنفسًا أنفيًا بطيئًا واسترخِ أكثر مع كل زفير.",
        "mistakes_en": ["Bouncing", "Forcing painful range", "Holding the breath"],
        "mistakes_ar": ["الارتداد", "إجبار الجسم على مدى مؤلم", "حبس النفس"],
    },
    "recovery": {
        "setup_en": "Position the roller under the target tissue, supporting body weight with hands or the other leg.",
        "setup_ar": "ضع الفوم رول أسفل النسيج المستهدف وادعم وزن الجسم باليدين أو الساق الأخرى.",
        "steps_ar": ["تحرك ببطء على مساحة صغيرة.", "توقف فوق المنطقة المشدودة وتنفس من دون ضغط حاد.", "خفف الوزن فور ظهور تنميل أو ألم عصبي."],
        "breathing_en": "Breathe slowly and reduce pressure on each uncomfortable point.",
        "breathing_ar": "تنفس ببطء وخفف الضغط عند كل نقطة غير مريحة.",
        "mistakes_en": ["Rolling too fast", "Pressing directly on a joint", "Ignoring numbness"],
        "mistakes_ar": ["الدحرجة بسرعة", "الضغط مباشرة على المفصل", "تجاهل التنميل"],
    },
}

ENGLISH_STEPS = {
    "squat": ["Descend under control with the whole foot planted.", "Keep the trunk braced and knees tracking over the toes.", "Drive the floor away and stand without snapping the knees."],
    "hinge": ["Push the hips back while keeping a neutral spine.", "Stop before trunk control or load position is lost.", "Press through the feet and extend the hips without over-arching."],
    "horizontal_push": ["Lower the load or body through a controlled, pain-free range.", "Keep forearms aligned and shoulders away from the ears.", "Press smoothly while the trunk remains stable."],
    "vertical_push": ["Press overhead through a comfortable path.", "Keep the ribs stacked and shoulders controlled.", "Lower slowly to the starting position."],
    "horizontal_pull": ["Pull the elbows back without jerking the torso.", "Bring the shoulder blades together while the neck stays relaxed.", "Reach forward again under control."],
    "vertical_pull": ["Initiate with the shoulder blades, then drive the elbows down.", "Keep the trunk controlled without swinging.", "Return to a controlled full reach."],
    "isolation": ["Move primarily through the target joint.", "Pause briefly at peak contraction without throwing the load.", "Return slowly while maintaining muscular tension."],
    "core": ["Start with a stable trunk and continue breathing.", "Move slowly without pulling on the neck.", "Stop before losing pelvic or lower-back position."],
    "locomotion": ["Build pace gradually from an easy start.", "Maintain smooth strides or cycles at a controllable effort.", "Reduce pace gradually before stopping."],
    "jump": ["Load the hips and knees under control.", "Drive through the floor while the knees track cleanly.", "Land quietly and regain balance before the next repetition."],
    "mobility": ["Move slowly into mild tension, never pain.", "Hold the position without bouncing while breathing normally.", "Exit gradually and repeat on the other side when relevant."],
    "recovery": ["Roll slowly over a small area.", "Pause on tight tissue without creating sharp pressure.", "Reduce pressure immediately if numbness or nerve pain appears."],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pattern_for(item: dict) -> str:
    if item["id"] in PATTERN_OVERRIDES:
        return PATTERN_OVERRIDES[item["id"]]
    value = f"{item['id']} {item['name']} {item.get('category', '')}".lower()
    if "smr" in value or item.get("equipment") == "foam roll":
        return "recovery"
    if item.get("category") == "stretching" or any(word in value for word in ("stretch", "pose", "inchworm")):
        return "mobility"
    if item.get("category") == "cardio" or any(word in value for word in ("walking", "jogging", "bicycling", "elliptical", "rowing, stationary")):
        return "locomotion"
    if any(word in value for word in ("jump", "skip", "slam", "acceleration", "mountain climber")):
        return "jump"
    if any(word in value for word in ("squat", "lunge", "leg press", "leg extension", "step up", "step-up")):
        return "squat"
    if any(word in value for word in ("deadlift", "hip thrust", "glute bridge", "swing")):
        return "hinge"
    if any(word in value for word in ("crunch", "plank", "pallof", "air bike", "russian twist", "leg raise", "superman", "full twist")):
        return "core"
    if any(word in value for word in ("lat pulldown", "pullup", "pull-up", "scapular")):
        return "vertical_pull"
    if any(word in value for word in ("row", "face pull")):
        return "horizontal_pull"
    if any(word in value for word in ("shoulder press", "handstand", "overhead slam")):
        return "vertical_push"
    if any(word in value for word in ("bench press", "pushup", "push-up", "dip", "chest pass")):
        return "horizontal_push"
    return "isolation"


def prescription(item: dict, pattern: str) -> dict:
    if pattern in {"mobility", "recovery"}:
        return {"sets": 2, "reps": None, "durationSeconds": 30, "restSeconds": 20, "tempo": "slow / بطيء", "setTypes": ["working"]}
    if pattern == "locomotion":
        return {"sets": 1, "reps": None, "durationSeconds": 1200, "restSeconds": 0, "tempo": "RPE 5–7", "setTypes": ["working"]}
    if pattern == "jump":
        return {"sets": 3, "reps": "5–8", "durationSeconds": None, "restSeconds": 90, "tempo": "explosive / انفجاري", "setTypes": ["warmup", "working"]}
    if item.get("level") == "expert":
        return {"sets": 4, "reps": "4–8", "durationSeconds": None, "restSeconds": 150, "tempo": "2-0-1", "setTypes": ["warmup", "working"]}
    return {"sets": 3, "reps": "8–12", "durationSeconds": None, "restSeconds": 90, "tempo": "3-1-1", "setTypes": ["warmup", "working"]}


def clean_instructions(values: list[str]) -> list[str]:
    result = []
    for value in values:
        normalized = " ".join(value.replace("Tip:", "").split())
        if normalized:
            result.append(normalized)
    return result[:6]


def build(source: Path, repo: Path) -> None:
    source_json = source / "dist" / "exercises.json"
    source_license = source / "LICENSE.md"
    if not source_json.is_file() or not source_license.is_file():
        raise SystemExit("source checkout must contain dist/exercises.json and LICENSE.md")
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    records = {item["id"]: item for item in json.loads(source_json.read_text())}

    product = repo / "fitness-v2" / "product"
    data_dir = repo / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data"
    media_dir = repo / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "media" / "free-exercise-db"
    licenses_dir = product / "sources" / "free-exercise-db"
    data_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)
    licenses_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_license, licenses_dir / "LICENSE.md")

    catalog = []
    for source_id, name_ar, section, goal in SELECTION:
        if source_id not in records:
            raise SystemExit(f"missing selected source exercise: {source_id}")
        item = records[source_id]
        images = item.get("images") or []
        if len(images) < 2:
            raise SystemExit(f"{source_id} does not provide the required two-frame demonstration")
        target = media_dir / source_id
        target.mkdir(parents=True, exist_ok=True)
        assets = []
        asset_hashes = []
        for index, relative in enumerate(images[:2]):
            source_image = source / "exercises" / relative
            suffix = source_image.suffix.lower() or ".jpg"
            destination = target / f"{index}{suffix}"
            shutil.copy2(source_image, destination)
            asset_path = f"media/free-exercise-db/{source_id}/{destination.name}"
            assets.append(asset_path)
            asset_hashes.append({"path": asset_path, "sha256": sha256(destination)})

        pattern = pattern_for(item)
        family = FAMILY[pattern]
        primary = item.get("primaryMuscles") or []
        secondary = item.get("secondaryMuscles") or []
        equipment = item.get("equipment")
        level = item.get("level") or "beginner"
        section_en, section_ar = SECTION_LABELS[section]
        slug = source_id.lower().replace("_", "-").replace("/", "-")
        catalog.append({
            "id": slug,
            "sourceItemId": source_id,
            "name": {"en": item["name"], "ar": name_ar},
            "section": {"id": section, "en": section_en, "ar": section_ar},
            "sport": section,
            "category": item.get("category") or "strength",
            "muscles": {
                "primary": {"en": primary, "ar": [MUSCLES_AR.get(value, value) for value in primary]},
                "secondary": {"en": secondary, "ar": [MUSCLES_AR.get(value, value) for value in secondary]},
            },
            "bodyPart": primary[0] if primary else "full body",
            "equipment": {"id": equipment or "body only", "en": equipment or "body only", "ar": EQUIPMENT_AR.get(equipment, equipment or "وزن الجسم")},
            "level": {"id": level, "en": level.title(), "ar": LEVEL_AR.get(level, level)},
            "movement": {"id": pattern, "en": pattern.replace("_", " ").title(), "ar": PATTERN_AR[pattern]},
            "goal": {"id": goal, "en": goal.replace("_", " ").title(), "ar": GOAL_AR[goal]},
            "setup": {"en": family["setup_en"], "ar": family["setup_ar"]},
            "steps": {"en": clean_instructions(item.get("instructions") or []) or ENGLISH_STEPS[pattern], "ar": family["steps_ar"]},
            "breathing": {"en": family["breathing_en"], "ar": family["breathing_ar"]},
            "prescription": prescription(item, pattern),
            "commonMistakes": {"en": family["mistakes_en"], "ar": family["mistakes_ar"]},
            "regression": {
                "en": "Reduce load, range, speed, or use stable support while keeping the same movement pattern.",
                "ar": "خفّض الحمل أو المدى أو السرعة، أو استخدم دعمًا ثابتًا مع الحفاظ على نفس نمط الحركة.",
            },
            "progression": {
                "en": "Progress only after pain-free control: add a small load, repetition, set, or harder variation—not all at once.",
                "ar": "تدرّج بعد إتقان الحركة دون ألم: أضف حملًا بسيطًا أو عدة أو مجموعة أو نسخة أصعب، وليس كلها معًا.",
            },
            "safety": {
                "en": "Stop for sharp pain, dizziness, numbness, or loss of control. Seek qualified guidance for injury or medical limitations.",
                "ar": "توقف عند ألم حاد أو دوار أو تنميل أو فقدان السيطرة. استشر مختصًا عند وجود إصابة أو قيد طبي.",
            },
            "demo": {"type": "two_frame_image_sequence", "assets": assets, "offline": True, "alt": {"en": f"Start and finish positions for {item['name']}", "ar": f"وضعا البداية والنهاية لتمرين {name_ar}"}},
            "tracking": {"load": pattern not in {"mobility", "recovery", "locomotion", "jump"}, "rpe": True, "rir": pattern not in {"mobility", "recovery", "locomotion"}, "volume": pattern not in {"mobility", "recovery", "locomotion"}},
            "provenance": {
                "source": "free-exercise-db", "repository": SOURCE_REPOSITORY, "commit": commit,
                "sourcePath": f"exercises/{source_id}.json", "license": SOURCE_LICENSE,
                "licenseUrl": SOURCE_LICENSE_URL, "importedAt": IMPORTED_AT, "assetHashes": asset_hashes,
            },
        })

    catalog.sort(key=lambda value: (value["section"]["id"], value["name"]["en"]))
    json_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (data_dir / "exercises.json").write_text(json_text)
    (data_dir / "exercises.js").write_text("window.THF_EXERCISES = " + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + ";\n")

    counts: dict[str, int] = {}
    for value in catalog:
        counts[value["section"]["id"]] = counts.get(value["section"]["id"], 0) + 1
    manifest = {
        "schemaVersion": 1,
        "generatedAt": IMPORTED_AT,
        "exerciseCount": len(catalog),
        "sectionCounts": counts,
        "offlineDemoAssets": sum(len(value["demo"]["assets"]) for value in catalog),
        "source": {
            "repository": SOURCE_REPOSITORY, "commit": commit, "license": SOURCE_LICENSE,
            "licenseUrl": SOURCE_LICENSE_URL, "licenseSha256": sha256(source_license),
            "datasetSha256": sha256(source_json),
        },
        "catalogSha256": hashlib.sha256(json_text.encode()).hexdigest(),
    }
    (product / "CATALOG_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    arguments = parser.parse_args()
    build(arguments.source.resolve(), arguments.repo.resolve())
