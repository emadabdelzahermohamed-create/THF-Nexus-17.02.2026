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

# Exact exercise-specific bilingual steps synchronized with the reviewed runtime catalog.
STEP_OVERRIDES = {
    "Medicine_Ball_Full_Twist": {
        "en": [
            "For this exercise you will need a medicine ball and a partner. Stand back to back with your partner, spaced 2-3 feet apart. This will be your starting position.",
            "Hold the ball in front of the trunk. Open the hips and turn the shoulders at the same time as your partner.",
            "For full rotation, you and your partner should twist in the same direction, i.e. counter-clockwise.",
            "Pass the ball to your partner, and both of you can now twist in the opposite direction to repeat the procedure."
        ],
        "ar": [
            "قف مع شريكك على مسافة مناسبة وامسك الكرة أمام الصدر مع تثبيت القدمين.",
            "أدر الكتفين والجذع معًا في اتجاه واحد، مع إبقاء الركبتين والحوض تحت السيطرة.",
            "مرّر الكرة إلى الشريك عند اكتمال الدوران من دون إجبار أسفل الظهر على مدى مؤلم.",
            "بدّلا اتجاه الدوران بعد التمرير، وتوقفا إذا اختل التوازن أو ظهر ألم."
        ]
    },
    "One-Arm_Medicine_Ball_Slam": {
        "en": [
            "Start in a standing position with a staggered, athletic stance. Hold a medicine ball in one hand, on the same side as your back leg. This will be your starting position.",
            "Begin by winding the arm, raising the medicine ball above your head. As you do so, extend through the hips, knees, and ankles to load up for the slam.",
            "At peak extension, flex the shoulders, spine, and hips to throw the ball hard into the ground directly in front of you.",
            "Catch the ball on the bounce and continue for the desired number of repetitions."
        ],
        "ar": [
            "قف بوقفة متدرجة وامسك الكرة بيد واحدة قرب جانب الرجل الخلفية.",
            "ارفع الكرة فوق الرأس مع مد الورك والركبتين والكاحلين دون تقويس أسفل الظهر.",
            "اسحب الذراع والجذع إلى أسفل ووجّه الكرة بقوة إلى الأرض أمامك مع إبقاء القدمين ثابتتين.",
            "التقط ارتداد الكرة بتحكم وأعد الوقفة قبل التكرار التالي."
        ]
    },
    "Pallof_Press_With_Rotation": {
        "en": [
            "Connect a standard handle to a tower, and position the cable to shoulder height.",
            "With your side to the cable, grab the handle with one hand and step away from the tower. You should be approximately arm's length away from the pulley, with the tension of the weight on the cable. Align outstretched arm with cable.",
            "With your feet positioned hip-width apart, pull the cable into your chest and grab the handle with your other hand. Both hands should be on the handle at this time.",
            "Facing forward, press the cable away from your chest. You core should be tight and engaged.",
            "Keeping your hips straight, twist your torso away from the pulley until you get a full quarter rotation.",
            "Maintain your rigid stance and straight arms. Return to the neutral position in a slow and controlled manner. Your arms should be extended in front of you."
        ],
        "ar": [
            "اضبط الكيبل قرب مستوى الكتف وقف بجانبه والقدمان بعرض الورك.",
            "أمسك المقبض بكلتا اليدين أمام الصدر وابتعد حتى تشعر بشد ثابت في الكيبل.",
            "مد الذراعين أمامك مع إبقاء القدمين والحوض ثابتين.",
            "أدر القفص الصدري ربع دورة بعيدًا عن البكرة دون لف الركبتين أو تحريك الورك.",
            "اثبت لحظة والذراعان ممدودتان مع استمرار التنفس.",
            "ارجع ببطء إلى المنتصف ثم أكمل التكرار وبدّل الجهة حسب المجموعة."
        ]
    },
    "Handstand_Push-Ups": {
        "en": [
            "With your back to the wall bend at the waist and place both hands on the floor at shoulder width.",
            "Kick yourself up against the wall with your arms straight. Your body should be upside down with the arms and legs fully extended. Keep your whole body as straight as possible. If doing this for the first time, have a spotter help you. Also, make sure that you keep facing the wall with your head, rather than looking down.",
            "Slowly lower yourself to the ground as you inhale until your head almost touches the floor. It is of utmost importance that you come down slow in order to avoid head injury.",
            "Push yourself back up slowly as you exhale until your elbows are nearly locked.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "قف مواجهًا للجدار وضع يديك على الأرض بعرض الكتفين، مع مساحة آمنة للرأس ومساعد إذا كانت الحركة جديدة.",
            "ارفع القدمين إلى الجدار ومد الذراعين، وحافظ على الجسم مستقيمًا والرأس بوضع محايد دون النظر للأسفل.",
            "اثنِ المرفقين ببطء حتى يقترب الرأس من وسادة ثابتة، وتوقف قبل الضغط على الرقبة.",
            "ادفع الأرض للعودة مع الزفير حتى يقترب المرفقان من الامتداد دون قفل قاسٍ.",
            "كرر ضمن مدى آمن؛ انزل بمساعدة إذا فقدت الثبات أو ظهر ألم."
        ]
    },
    "Hanging_Leg_Raise": {
        "en": [
            "Hang from a chin-up bar with both arms extended at arms length in top of you using either a wide grip or a medium grip. The legs should be straight down with the pelvis rolled slightly backwards. This will be your starting position.",
            "Raise your legs until the torso makes a 90-degree angle with the legs. Exhale as you perform this movement and hold the contraction for a second or so.",
            "Go back slowly to the starting position as you breathe in.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "تعلّق بالعارضة بذراعين ممدودتين وقبضة ثابتة، واترك الجسم يستقر دون تأرجح.",
            "ارفع الساقين أمامك من الورك حتى زاوية مريحة تقارب 90 درجة دون دفع الجسم للأمام.",
            "ازفر أثناء الرفع وحافظ على الحوض ملتفًا قليلًا للخلف دون شد الرقبة.",
            "أنزل الساقين ببطء إلى وضع البداية قبل بدء التكرار التالي."
        ]
    },
    "Pullups": {
        "en": [
            "Grab the pull-up bar with the palms facing forward using the prescribed grip. Note on grips: For a wide grip, your hands need to be spaced out at a distance wider than your shoulder width. For a medium grip, your hands need to be spaced out at a distance equal to your shoulder width and for a close grip at a distance smaller than your shoulder width.",
            "As you have both arms extended in front of you holding the bar at the chosen grip width, bring your torso back around 30 degrees or so while creating a curvature on your lower back and sticking your chest out. This is your starting position.",
            "Pull your torso up until the bar touches your upper chest by drawing the shoulders and the upper arms down and back. Exhale as you perform this portion of the movement. Concentrate on squeezing the back muscles once you reach the full contracted position. The upper torso should remain stationary as it moves through space and only the arms should move. The forearms should do no other work other than hold the bar.",
            "After a second on the contracted position, start to inhale and slowly lower your torso back to the starting position when your arms are fully extended and the lats are fully stretched.",
            "Repeat this motion for the prescribed amount of repetitions."
        ],
        "ar": [
            "أمسك البار بقبضة أمامية؛ اجعل المسافة أوسع من الكتفين أو مساوية لهما أو أضيق حسب القبضة المختارة.",
            "مد الذراعين، وارجع بالجذع قليلًا مع رفع الصدر والحفاظ على أسفل الظهر تحت السيطرة.",
            "اسحب المرفقين لأسفل والخلف حتى يقترب أعلى الصدر من البار، دون تأرجح.",
            "اخفض الجذع ببطء مع الشهيق حتى تمتد الذراعان بالكامل دون ارتخاء مفاجئ.",
            "كرر مع ثبات الجذع؛ استخدم مساعدة أو مدى أقصر إذا تعذر الأداء النظيف."
        ]
    },
    "Barbell_Bench_Press_-_Medium_Grip": {
        "en": [
            "Lie back on a flat bench. Using a medium width grip (a grip that creates a 90-degree angle in the middle of the movement between the forearms and the upper arms), lift the bar from the rack and hold it straight over you with your arms locked. This will be your starting position.",
            "From the starting position, breathe in and begin coming down slowly until the bar touches your middle chest.",
            "After a brief pause, push the bar back to the starting position as you breathe out. Focus on pushing the bar using your chest muscles. Lock your arms and squeeze your chest in the contracted position at the top of the motion, hold for a second and then start coming down slowly again. Ideally, lowering the weight should take about twice as long as raising it.",
            "Repeat the movement for the prescribed amount of repetitions.",
            "When you are done, place the bar back in the rack."
        ],
        "ar": [
            "استلقِ على مقعد مستوٍ، أمسك البار بقبضة متوسطة وارفعه من الحامل فوق الصدر مع تثبيت القدمين ولوحي الكتف.",
            "خذ شهيقًا واخفض البار ببطء حتى يلامس منتصف الصدر مع بقاء الرسغين فوق المرفقين.",
            "توقف لحظة ثم ادفع البار لأعلى مع الزفير دون ارتداد، وحافظ على مسار ثابت.",
            "كرر النزول المتحكم والصعود؛ اجعل النزول أبطأ من الصعود وتجنب قفل المرفقين بعنف.",
            "بعد آخر عدة أعد البار إلى الحامل باستخدام الحواجز أو مساعد عند الحاجة."
        ]
    },
    "Barbell_Deadlift": {
        "en": [
            "Stand in front of a loaded barbell.",
            "While keeping the back as straight as possible, bend your knees, bend forward and grasp the bar using a medium (shoulder width) overhand grip. This will be the starting position of the exercise. If it is difficult to hold on to the bar with this grip, alternate your grip or use wrist straps.",
            "While holding the bar, start the lift by pushing with your legs while simultaneously getting your torso to the upright position as you breathe out. In the upright position, stick your chest out and contract the back by bringing the shoulder blades back. Think of how the soldiers in the military look when they are in standing in attention.",
            "Go back to the starting position by bending at the knees while simultaneously leaning the torso forward at the waist while keeping the back straight. When the weights on the bar touch the floor you are back at the starting position and ready to perform another repetition.",
            "Perform the amount of repetitions prescribed in the program."
        ],
        "ar": [
            "قف أمام بار محمّل وضعه فوق منتصف القدمين.",
            "اثنِ الورك والركبتين، أمسك البار بقبضة متوسطة وحافظ على الظهر محايدًا.",
            "ادفع الأرض بالقدمين وارفع الجذع مع الزفير حتى الوقوف، دون سحب البار بعيدًا عن الساقين.",
            "ادفع الورك للخلف واثنِ الركبتين لإعادة البار للأرض مع بقاء الظهر محايدًا.",
            "كرر العدات مع نفس المسار؛ توقف إذا فقدت ثبات الظهر أو القبضة."
        ]
    },
    "Barbell_Shoulder_Press": {
        "en": [
            "Sit on a bench with back support in a squat rack. Position a barbell at a height that is just above your head. Grab the barbell with a pronated grip (palms facing forward).",
            "Once you pick up the barbell with the correct grip width, lift the bar up over your head by locking your arms. Hold at about shoulder level and slightly in front of your head. This is your starting position.",
            "Lower the bar down to the shoulders slowly as you inhale.",
            "Lift the bar back up to the starting position as you exhale.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "اجلس مع دعم للظهر وضع البار في الحامل أعلى مستوى الرأس بقليل، وأمسكه بقبضة أمامية.",
            "ارفع البار أمام الرأس إلى مستوى الكتفين مع شد البطن وثبات القدمين.",
            "اخفض البار ببطء إلى الكتفين مع الشهيق.",
            "ادفع البار فوق الرأس مع الزفير دون تقويس أسفل الظهر.",
            "كرر بمدى مريح، وتوقف إذا تحركت الأضلاع للأمام أو ظهر ألم بالكتف."
        ]
    },
    "Pallof_Press": {
        "en": [
            "Connect a standard handle to a tower, and—if possible—position the cable to shoulder height. If not, a low pulley will suffice.",
            "With your side to the cable, grab the handle with both hands and step away from the tower. You should be approximately arm's length away from the pulley, with the tension of the weight on the cable.",
            "With your feet positioned hip-width apart and knees slightly bent, hold the cable to the middle of your chest. This will be your starting position.",
            "Press the cable away from your chest, fully extending both arms. You core should be tight and engaged.",
            "Hold the repetition for several seconds before returning to the starting position.",
            "At the conclusion of the set, repeat facing the other direction."
        ],
        "ar": [
            "اضبط الكيبل قرب مستوى الكتف وقف بجانبه مع القدمين بعرض الورك.",
            "أمسك المقبض بكلتا اليدين أمام منتصف الصدر وابتعد حتى يصبح الكيبل مشدودًا.",
            "اثن الركبتين قليلًا وشد البطن مع إبقاء الحوض مواجهًا للأمام.",
            "ادفع المقبض بعيدًا حتى تمتد الذراعان، ولا تدع شد الكيبل يلف جذعك.",
            "اثبت لثوانٍ مع التنفس الطبيعي ثم أعد المقبض ببطء إلى الصدر.",
            "أكمل المجموعة ثم بدّل اتجاه الوقوف لموازنة مقاومة الدوران."
        ]
    },
    "Romanian_Deadlift": {
        "en": [
            "Put a barbell in front of you on the ground and grab it using a pronated (palms facing down) grip that a little wider than shoulder width. Depending on the weight used, you may need wrist wraps to perform the exercise and also a raised platform in order to allow for better range of motion.",
            "Bend the knees slightly and keep the shins vertical, hips back and back straight. This will be your starting position.",
            "Keeping your back and arms completely straight at all times, use your hips to lift the bar as you exhale. The movement should not be fast but steady and under control.",
            "Once you are standing completely straight up, lower the bar by pushing the hips back, only slightly bending the knees, unlike when squatting. Take a deep breath at the start of the movement and keep your chest up. Hold your breath as you lower and exhale as you complete the movement.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "أمسك البار أمام الفخذين بقبضة أمامية أوسع قليلًا من الكتفين، واستخدم منصة ثابتة عند الحاجة.",
            "اثنِ الركبتين قليلًا، وادفع الورك للخلف مع بقاء الساقين شبه عموديتين والظهر محايدًا.",
            "ارفع الجذع بتحريك الورك للأمام مع الزفير، والذراعان مستقيمتان والبار قريب من الجسم.",
            "ادفع الورك للخلف واخفض البار ببطء مع الشهيق دون تحويل الحركة إلى سكوات.",
            "كرر بتحكم، وتوقف إذا فقدت وضع الظهر أو بدأت الركبتان تنثنيان كثيرًا."
        ]
    },
    "Front_Box_Jump": {
        "en": [
            "Begin with a box of an appropriate height 1-2 feet in front of you. Stand with your feet should width apart. This will be your starting position.",
            "Perform a short squat in preparation for jumping, swinging your arms behind you.",
            "Rebound out of this position, extending through the hips, knees, and ankles to jump as high as possible. Swing your arms forward and up.",
            "Land on the box with the knees bent, absorbing the impact through the legs. You can jump from the box back to the ground, or preferably step down one leg at a time."
        ],
        "ar": [
            "ضع صندوقًا ثابتًا بارتفاع مناسب أمامك، والقدمان بعرض الكتفين.",
            "اثنِ الركبتين قليلًا وارجع الذراعين استعدادًا للقفز.",
            "اقفز بدفع الورك والركبتين والكاحلين، وحرك الذراعين للأمام والأعلى.",
            "اهبط على الصندوق بركبتين مثنيتين لامتصاص الصدمة، ثم انزل خطوة خطوة إذا كان ذلك أأمن."
        ]
    },
    "Mountain_Climbers": {
        "en": [
            "Begin in a pushup position, with your weight supported by your hands and toes. Flexing the knee and hip, bring one leg until the knee is approximately under the hip. This will be your starting position.",
            "Explosively reverse the positions of your legs, extending the bent leg until the leg is straight and supported by the toe, and bringing the other foot up with the hip and knee flexed. Repeat in an alternating fashion for 20-30 seconds."
        ],
        "ar": [
            "ابدأ في وضع البلانك، واليدان تحت الكتفين والجسم من الرأس إلى الكعبين في خط مستقيم.",
            "اسحب ركبة نحو الصدر ثم أعد القدم وبدّل الجهة بإيقاع متحكم فيه مع ثبات الحوض وعدم هبوط أسفل الظهر."
        ]
    },
    "Overhead_Slam": {
        "en": [
            "Hold a medicine ball with both hands and stand with your feet at shoulder width. This will be your starting position.",
            "Initiate the countermovement by raising the ball above your head and fully extending your body.",
            "Reverse the motion, slamming the ball into the ground directly in front of you as hard as you can.",
            "Receive the ball with both hands on the bounce and repeat the movement."
        ],
        "ar": [
            "قف والقدمان بعرض الكتفين وامسك الكرة الطبية بكلتا اليدين أمام الجسم.",
            "ارفع الكرة فوق الرأس مع مد الجسم دون المبالغة في تقويس أسفل الظهر.",
            "ادفع الكرة بقوة إلى الأرض أمامك بثني الورك والركبتين مع بقاء الحركة تحت السيطرة.",
            "التقط الكرة بعد ارتدادها وأعد الوقفة قبل التكرار التالي."
        ]
    },
    "Air_Bike": {
        "en": [
            "Lie flat on the floor with your lower back pressed to the ground. For this exercise, you will need to put your hands beside your head. Be careful however to not strain with the neck as you perform it. Now lift your shoulders into the crunch position.",
            "Bring knees up to where they are perpendicular to the floor, with your lower legs parallel to the floor. This will be your starting position.",
            "Now simultaneously, slowly go through a cycle pedal motion kicking forward with the right leg and bringing in the knee of the left leg. Bring your right elbow close to your left knee by crunching to the side, as you breathe out.",
            "Go back to the initial position as you breathe in.",
            "Crunch to the opposite side as you cycle your legs and bring closer your left elbow to your right knee and exhale.",
            "Continue alternating in this manner until all of the recommended repetitions for each side have been completed."
        ],
        "ar": [
            "استلقِ واضغط أسفل الظهر نحو الأرض وضع اليدين بجانب الرأس دون شد الرقبة.",
            "ارفع الكتفين قليلًا وثن الركبتين حتى تكون الساقان مرفوعتين عن الأرض.",
            "مد الرجل اليمنى وقرّب المرفق الأيمن من الركبة اليسرى مع تدوير الجذع.",
            "عد إلى الوسط مع إبقاء أسفل الظهر ملاصقًا للأرض.",
            "بدّل الجهة؛ مد الرجل اليسرى وقرّب المرفق الأيسر من الركبة اليمنى.",
            "استمر بالتبادل دون سحب الرأس باليدين أو حبس النفس."
        ]
    },
    "Fast_Skipping": {
        "en": [
            "Start in a relaxed position with one leg slightly forward. This will be your starting position.",
            "Skip by executing a step-hop pattern of right-right-step to left-left-step, and so on, alternating back and forth.",
            "Perform fast skips by maintaining close contact with the ground and reduce air time, moving as quickly as possible."
        ],
        "ar": [
            "ابدأ في وضع مريح مع تقديم إحدى القدمين قليلًا.",
            "نفّذ نمط خطوة وقفزة بالتبادل: يمين–يمين–خطوة انتقال، ثم يسار–يسار–خطوة انتقال.",
            "زد سرعة القفز مع إبقاء زمن الطيران قصيرًا والقدمين قريبين من الأرض."
        ]
    },
    "Box_Skip": {
        "en": [
            "You will need several boxes lined up about 8 feet apart.",
            "Begin facing the first box with one leg slightly behind the other.",
            "Drive off the back leg, attempting to gain as much height with the hips as possible.",
            "Immediately upon landing on the box, drive the other leg forward and upward to gain height and distance, leaping from the box. Land between the first two boxes with the same leg that landed on the first box.",
            "Then, step to the next box and repeat."
        ],
        "ar": [
            "رتّب عدة صناديق ثابتة في صف، واترك نحو 2.4 متر بين كل صندوق وآخر.",
            "قف أمام الصندوق الأول مع وضع إحدى القدمين خلف الأخرى قليلًا.",
            "ادفع بالأرض من القدم الخلفية لرفع الورك واكتساب ارتفاع نحو الصندوق.",
            "عند الهبوط على الصندوق، ادفع الرجل الأخرى للأمام والأعلى ثم اقفز نحو الصندوق التالي؛ اهبط بين الصندوقين على القدم نفسها التي هبطت بها على الأول.",
            "انتقل إلى الصندوق التالي وكرر التسلسل، مع التأكد من ثبات الهبوط قبل القفزة التالية."
        ]
    },
    "Front_Cone_Hops_or_hurdle_hops": {
        "en": [
            "Set up a row of cones or other small barriers, placing them a few feet apart.",
            "Stand in front of the first cone with your feet shoulder width apart. This will be your starting position.",
            "Begin by jumping with both feet over the first cone, swinging both arms as you jump.",
            "Absorb the impact of landing by bending the knees, rebounding out of the first leap by jumping over the next cone.",
            "Continue until you have jumped over all of the cones."
        ],
        "ar": [
            "رتّب صفًا من الأقماع أو الحواجز المنخفضة، مع ترك بضعة أقدام بين كل حاجز وآخر.",
            "قف أمام أول حاجز والقدمان بعرض الكتفين.",
            "اقفز بكلتا القدمين معًا فوق الحاجز، وحرّك الذراعين للمساعدة في الدفع.",
            "امتص الهبوط بثني الركبتين ثم ارتدّ للقفز فوق الحاجز التالي.",
            "واصل حتى تتجاوز الصف كاملًا، وتوقف إذا أصبح الهبوط صلبًا أو اختل اتجاه الركبتين."
        ]
    },
    "Lateral_Cone_Hops": {
        "en": [
            "Position a number of cones in a row several feet apart.",
            "Stand next to the end of the cones, facing 90 degrees to the direction of travel. This will be your starting position.",
            "Begin the jump by dipping with the knees to initiate a stretch reflex, and immediately reverse direction to push off the ground, jumping up and sideways over the cone.",
            "Use your legs to absorb impact upon landing, and rebound into the next jump, continuing down the row of cones."
        ],
        "ar": [
            "ضع عدة أقماع في صف يفصل بينها بضعة أقدام.",
            "قف بجانب طرف الصف واجعل جسمك متعامدًا مع اتجاه الانتقال.",
            "اثنِ الركبتين قليلًا ثم ادفع الأرض فورًا للقفز جانبيًا فوق القمع.",
            "امتص الهبوط بالساقين ثم انتقل مباشرة إلى القفزة التالية حتى نهاية الصف."
        ]
    },
    "Side_Hop-Sprint": {
        "en": [
            "Stand to the side of a cone or hurdle.",
            "Begin this drill by hopping sideways over the obstacle, rebounding out of your landing to hop back to where you started.",
            "Hop for a prescribed number or repetitions as quickly as possible, and finish this drill by sprinting a short distance upon landing the last hop."
        ],
        "ar": [
            "قف إلى جانب قمع أو حاجز منخفض.",
            "اقفز جانبيًا فوق الحاجز ثم استخدم الهبوط للارتداد والعودة إلى نقطة البداية.",
            "كرر العدد المحدد بأسرع إيقاع يمكن التحكم فيه، ثم انطلق لمسافة قصيرة بعد آخر هبوط."
        ]
    },
    "Freehand_Jump_Squat": {
        "en": [
            "Cross your arms over your chest.",
            "With your head up and your back straight, position your feet at shoulder width.",
            "Keeping your back straight and chest up, squat down as you inhale until your upper thighs are parallel, or lower, to the floor.",
            "Now pressing mainly with the ball of your feet, jump straight up in the air as high as possible, using the thighs like springs. Exhale during this portion of the movement.",
            "When you touch the floor again, immediately squat down and jump again.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "اعقد الذراعين أمام الصدر.",
            "قف والقدمان بعرض الكتفين، والرأس مرفوع والظهر مستقيم.",
            "اخفض الوركين في سكوات مع الشهيق حتى يصبح الفخذان موازيين للأرض أو أدنى، مع إبقاء الصدر مرفوعًا.",
            "ادفع بمقدمة القدمين واقفز عموديًا بأعلى ارتفاع يمكنك التحكم فيه، مع الزفير.",
            "عند ملامسة الأرض، اثنِ الوركين والركبتين لامتصاص الهبوط والعودة فورًا إلى وضع السكوات.",
            "كرر العدد المطلوب مع الحفاظ على محاذاة الركبتين وهبوط هادئ؛ توقف إذا فقدت السيطرة."
        ]
    },
    "Lateral_Bound": {
        "en": [
            "Assume a half squat position facing 90 degrees from your direction of travel. This will be your starting position.",
            "Allow your lead leg to do a countermovement inward as you shift your weight to the outside leg.",
            "Immediately push off and extend, attempting to bound to the side as far as possible.",
            "Upon landing, immediately push off in the opposite direction, returning to your original start position.",
            "Continue back and forth for several repetitions."
        ],
        "ar": [
            "ابدأ بنصف سكوات، واجعل جسمك متعامدًا مع اتجاه الوثب.",
            "حرّك الساق القائدة قليلًا إلى الداخل وانقل وزنك إلى الساق الخارجية.",
            "ادفع الأرض وامدد الورك والركبة للوثب جانبيًا إلى أبعد مسافة تستطيع التحكم بها.",
            "عند الهبوط، ادفع فورًا بالاتجاه المعاكس للعودة إلى موضع البداية.",
            "واصل الوثب ذهابًا وإيابًا لعدة تكرارات، مع امتصاص الهبوط والحفاظ على اتجاه الركبتين."
        ]
    },
    "Side_to_Side_Box_Shuffle": {
        "en": [
            "Stand beside a stable box with one foot centered on it and the other foot on the floor; keep your knees soft.",
            "Hop laterally across the box and switch which foot lands on the box and which lands on the floor, using your arms for balance.",
            "Continue shuffling from side to side with quiet, controlled landings and a clear path."
        ],
        "ar": [
            "قف بجانب صندوق ثابت، وضع قدمًا في منتصفه والأخرى على الأرض مع ثني الركبتين قليلًا.",
            "اقفز جانبيًا فوق الصندوق وبدّل موضع القدمين؛ استخدم الذراعين للموازنة.",
            "واصل الانتقال من جانب إلى آخر بهبوط هادئ ومتحكم فيه مع إبقاء المسار خاليًا."
        ]
    },
    "Bicycling": {
        "en": [
            "Adjust the saddle so your knee remains slightly bent when the pedal is at its lowest point.",
            "Start with easy resistance and a smooth cadence; keep your shoulders relaxed and hands secure on the bars.",
            "Increase effort gradually, then reduce resistance and slow your cadence before dismounting."
        ],
        "ar": [
            "اضبط ارتفاع المقعد بحيث تبقى الركبة مثنية قليلًا عندما تكون الدواسة في أدنى نقطة.",
            "ابدأ بمقاومة خفيفة ودوران سلس للدواسات، مع إرخاء الكتفين وثبات اليدين على المقود.",
            "زد الجهد تدريجيًا، ثم خفّض المقاومة والإيقاع قبل النزول عن الدراجة."
        ]
    },
    "Bicycling_Stationary": {
        "en": [
            "Adjust the seat so your knee stays slightly bent at the bottom of the pedal stroke, then secure your feet if straps are provided.",
            "Choose a manual setting or suitable program and begin with low resistance; do not treat console calorie estimates as measured results.",
            "Pedal smoothly and raise resistance gradually only while you can keep a steady cadence and relaxed posture."
        ],
        "ar": [
            "اضبط المقعد بحيث تبقى الركبة مثنية قليلًا عند أسفل دورة الدواسة، وثبّت القدمين إذا توفرت أحزمة.",
            "اختر الوضع اليدوي أو برنامجًا مناسبًا وابدأ بمقاومة منخفضة؛ تقدير السعرات على الشاشة ليس قياسًا فعليًا.",
            "بدّل الدواسات بسلاسة وزد المقاومة تدريجيًا فقط مع الحفاظ على إيقاع ثابت ووضع مريح."
        ]
    },
    "Recumbent_Bike": {
        "en": [
            "Move the seat until your knee remains slightly bent when the pedal is farthest away, and sit with your back supported.",
            "Secure your feet and start at low resistance with an even pedal stroke.",
            "Increase effort gradually, then lower resistance and slow down before getting off."
        ],
        "ar": [
            "حرّك المقعد حتى تبقى الركبة مثنية قليلًا عند أبعد نقطة للدواسة، واجلس مع إسناد الظهر.",
            "ثبّت القدمين وابدأ بمقاومة منخفضة ودورة دواسة منتظمة.",
            "زد الجهد تدريجيًا، ثم خفّض المقاومة وأبطئ الإيقاع قبل النزول."
        ]
    },
    "Linear_Acceleration_Wall_Drill": {
        "en": [
            "Lean into a wall at about 45 degrees with your body aligned and glutes engaged.",
            "Drive one knee up quickly, then strike the foot down beneath your hips without letting the trunk collapse.",
            "Switch legs and repeat with the same forward lean and controlled foot placement.",
            "Once the rhythm is stable, alternate the legs rapidly for the prescribed interval; stop if your posture breaks down."
        ],
        "ar": [
            "استند إلى الحائط بزاوية تقارب 45 درجة، مع محاذاة الجسم وشد عضلات الألوية.",
            "ارفع ركبة واحدة بسرعة ثم اضرب الأرض بالقدم أسفل الحوض دون انهيار الجذع.",
            "بدّل الساق وكرر مع الحفاظ على الميل الأمامي وموضع قدم متحكم فيه.",
            "بعد ثبات الإيقاع، بدّل الساقين بسرعة خلال المدة المحددة، وتوقف إذا اختل وضع الجسم."
        ]
    },
    "Single-Cone_Sprint_Drill": {
        "en": [
            "Place one cone on a clear, non-slip surface and stand beside it with your arms in a running position.",
            "Take quick, short steps around the cone while driving your arms and lifting your knees without crossing your feet.",
            "Rest after three controlled circuits, or sooner if you lose footing or coordination."
        ],
        "ar": [
            "ضع قمعًا واحدًا على سطح ثابت غير زلق وخالٍ من العوائق، وقف بجانبه بوضعية الجري.",
            "نفّذ خطوات قصيرة وسريعة حول القمع مع تحريك الذراعين ورفع الركبتين دون تشابك القدمين.",
            "استرح بعد ثلاث دورات متحكم فيها، أو قبل ذلك إذا اختل التوازن أو التناسق."
        ]
    },
    "Elliptical_Trainer": {
        "en": [
            "Step onto the pedals, hold the handles securely, and select an easy program or low resistance before starting.",
            "Move through a smooth stride with an upright torso and relaxed shoulders; use moving handles only if they feel stable.",
            "Increase resistance or incline gradually, then reduce the effort and let the machine slow before stepping off."
        ],
        "ar": [
            "اصعد إلى الدواسات وأمسك المقابض بثبات، واختر برنامجًا سهلًا أو مقاومة منخفضة قبل البدء.",
            "تحرك بخطوة سلسة مع جذع منتصب وكتفين مرتاحين، واستخدم المقابض المتحركة فقط إذا كانت مستقرة.",
            "زد المقاومة أو الميل تدريجيًا، ثم خفّض الجهد واترك الجهاز يبطئ قبل النزول."
        ]
    },
    "Rowing_Stationary": {
        "en": [
            "Secure your feet in the straps, sit tall, and hinge slightly forward from the hips with a neutral back.",
            "Drive through the legs first, then swing the torso slightly back and pull the handle toward the upper abdomen.",
            "Return the arms first, hinge forward, and then bend the knees to slide toward the starting position.",
            "Repeat in that order with a smooth rhythm; stop if you feel back pain or cannot maintain control."
        ],
        "ar": [
            "ثبّت القدمين بالأحزمة، واجلس منتصبًا مع ميل بسيط للأمام من الورك وظهر محايد.",
            "ادفع بالقدمين أولًا، ثم أمل الجذع قليلًا للخلف واسحب المقبض نحو أعلى البطن.",
            "أعد الذراعين أولًا، ثم أمل الجذع للأمام واثنِ الركبتين للعودة إلى وضع البداية.",
            "كرر التسلسل بإيقاع سلس، وتوقف إذا ظهر ألم بالظهر أو تعذر الحفاظ على التحكم."
        ]
    },
    "Bodyweight_Walking_Lunge": {
        "en": [
            "Stand with feet about hip-width apart, torso upright, and hands on your hips or by your sides.",
            "Step forward and lower until the rear knee approaches the floor while the front knee tracks in line with the foot.",
            "Push through the whole front foot to stand without bouncing or letting the knee collapse inward.",
            "Bring the rear foot forward into the next lunge and alternate sides with a controlled stride."
        ],
        "ar": [
            "قف والقدمان بعرض الورك تقريبًا، والجذع منتصب، واليدان على الحوض أو بجانب الجسم.",
            "تقدم خطوة إلى الأمام وانزل حتى تقترب الركبة الخلفية من الأرض مع بقاء الركبة الأمامية في اتجاه القدم.",
            "ادفع بالأرض بكامل القدم الأمامية للوقوف دون ارتداد أو انهيار الركبة إلى الداخل.",
            "قدّم القدم الخلفية إلى الاندفاع التالي وبدّل الجانبين بخطوة متحكم فيها."
        ]
    },
    "Jogging_Treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, choose a low starting speed, and begin only when the belt is moving safely.",
            "Jog with a tall posture, short controlled steps, and relaxed shoulders; avoid holding the rails during normal running.",
            "Reduce the belt to a walk and wait for it to stop before stepping off."
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واختر سرعة بداية منخفضة، ولا تبدأ إلا بعد تحرك الحزام بأمان.",
            "اهرول بجذع منتصب وخطوات قصيرة متحكم فيها وكتفين مرتاحين؛ لا تتمسك بالمقابض أثناء الجري الطبيعي.",
            "اخفض السرعة إلى المشي وانتظر توقف الحزام قبل النزول."
        ]
    },
    "Prowler_Sprint": {
        "en": [
            "Choose a sled load that creates resistance but still allows quick, short steps without losing posture.",
            "Grip the upright or low handles, extend the arms, brace the trunk, and lean forward from the ankles.",
            "Drive through the floor with alternating short steps for a short distance while keeping the sled path clear.",
            "Stop before technique breaks down; reduce the load if your steps slow sharply or your back rounds."
        ],
        "ar": [
            "اختر وزنًا للزلاجة يوفر مقاومة مع السماح بخطوات قصيرة وسريعة دون فقدان الوضع.",
            "أمسك بالمقابض المرتفعة أو المنخفضة، ومد الذراعين، وشد الجذع، ومل للأمام من الكاحلين.",
            "ادفع الأرض بخطوات قصيرة متبادلة لمسافة قصيرة مع إبقاء مسار الزلاجة خاليًا.",
            "توقف قبل انهيار التقنية؛ خفّض الوزن إذا تباطأت الخطوات بشدة أو تقوس الظهر."
        ]
    },
    "Running_Treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, set a conservative speed and incline, and start the belt before stepping on.",
            "Run with controlled strides, eyes forward, and a stable torso; use the rails only for balance or dismounting.",
            "Lower the speed to a walk, wait for the belt to stop, and then step off."
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واضبط سرعة وميلًا مناسبين، ثم شغّل الحزام قبل الصعود إليه.",
            "اجرِ بخطوات متحكم فيها ونظرك للأمام وجذع ثابت؛ استخدم المقابض للتوازن أو عند النزول فقط.",
            "اخفض السرعة إلى المشي، وانتظر توقف الحزام ثم انزل."
        ]
    },
    "Trail_Running_Walking": {
        "en": [
            "Wear shoes with suitable grip, scan the trail ahead, and choose a pace that matches the surface and visibility.",
            "On climbs, shorten your stride and keep effort steady rather than overreaching.",
            "On descents, take shorter steps, bend the knees, and slow down to manage impact and avoid slipping.",
            "Walk technical, loose, or slippery sections and stop if footing becomes unsafe."
        ],
        "ar": [
            "ارتدِ حذاءً مناسبًا للتشبث بالأرض، وراقب المسار أمامك واختر سرعة تناسب السطح ومدى الرؤية.",
            "في الصعود، قصّر الخطوة وحافظ على جهد ثابت بدل المبالغة في مدها.",
            "في النزول، قصّر الخطوات واثنِ الركبتين وأبطئ لتقليل الصدمة وتجنب الانزلاق.",
            "امشِ في المقاطع الوعرة أو المفككة أو الزلقة، وتوقف إذا أصبح تثبيت القدم غير آمن."
        ]
    },
    "Walking_Treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, select a comfortable starting speed, and start the belt before stepping on.",
            "Walk upright with eyes forward and a natural arm swing; avoid leaning on the rails throughout the session.",
            "Reduce the speed to zero and wait for the belt to stop before stepping off."
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واختر سرعة بداية مريحة، ثم شغّل الحزام قبل الصعود إليه.",
            "امشِ بجذع منتصب ونظرك للأمام وحركة ذراعين طبيعية؛ تجنب الاتكاء المستمر على المقابض.",
            "اخفض السرعة إلى الصفر وانتظر توقف الحزام قبل النزول."
        ]
    },
    "Crunches": {
        "en": [
            "Lie on your back with knees bent and feet flat; keep your lower back gently in contact with the floor.",
            "Place fingertips beside your ears with elbows open; do not pull on your head.",
            "Exhale and curl your shoulder blades a few inches off the floor by tightening your abdominal muscles.",
            "Pause briefly at the top without swinging or straining your neck.",
            "Inhale and lower your shoulders slowly to the starting position."
        ],
        "ar": [
            "استلقِ على ظهرك واثنِ الركبتين مع تثبيت القدمين على الأرض، وأبقِ أسفل الظهر ملامسًا للأرض برفق.",
            "ضع أطراف الأصابع بجانب الأذنين واترك المرفقين مفتوحين، ولا تسحب الرأس باليدين.",
            "ازفر وارفع لوحي الكتف بضعة سنتيمترات عن الأرض بشد عضلات البطن.",
            "توقف لحظة في الأعلى دون تأرجح أو إجهاد الرقبة.",
            "خذ شهيقًا وأنزل الكتفين ببطء إلى وضع البداية."
        ]
    },
    "Plank": {
        "en": [
            "Start face down with forearms on the floor and elbows directly beneath your shoulders; tuck your toes under.",
            "Lift your torso and hips into a straight line from head to heels, bracing your abdomen and glutes.",
            "Breathe steadily and keep your hips from sagging or rising; hold only while alignment remains controlled.",
            "Lower your knees and hips carefully to finish, or use a shorter hold or knee plank if alignment breaks."
        ],
        "ar": [
            "ابدأ ووجهك إلى الأرض، وضع الساعدين عليها والمرفقين أسفل الكتفين مباشرة، مع تثبيت أصابع القدمين.",
            "ارفع الجذع والحوض حتى يصنع الجسم خطًا مستقيمًا من الرأس إلى الكعبين، مع شد البطن والألوية.",
            "تنفس بانتظام وامنع هبوط الحوض أو ارتفاعه؛ استمر فقط ما دامت المحاذاة ثابتة.",
            "أنزل الركبتين والحوض بتحكم لإنهاء الثبات، أو استخدم مدة أقصر أو بلانك على الركبتين إذا اختل الوضع."
        ]
    },
    "Russian_Twist": {
        "en": [
            "Sit with knees bent and heels on the floor, then lean back slightly while keeping your spine long.",
            "Hold your hands together in front of your chest and brace your abdomen without rounding your lower back.",
            "Rotate your rib cage to one side within a comfortable range while keeping your hips and knees steady.",
            "Return through the center and rotate to the other side; move under control instead of swinging your arms.",
            "Keep your feet grounded; for an easier version sit more upright and use a smaller rotation, and stop if your lower back hurts."
        ],
        "ar": [
            "اجلس والركبتان مثنيتان والكعبان على الأرض، ثم أمل الجذع قليلًا للخلف مع إطالة العمود الفقري.",
            "ضم اليدين أمام الصدر وشد عضلات البطن دون تدوير أسفل الظهر.",
            "أدر القفص الصدري إلى أحد الجانبين ضمن مدى مريح مع تثبيت الحوض والركبتين.",
            "عد إلى المنتصف ثم أدر الجذع إلى الجهة الأخرى بتحكم بدل تأرجح الذراعين.",
            "أبقِ القدمين على الأرض؛ ولتسهيل الحركة اجلس أكثر انتصابًا وقلل الدوران، وتوقف إذا ظهر ألم أسفل الظهر."
        ]
    },
    "Side_Bridge": {
        "en": [
            "Lie on your side with the elbow directly under the shoulder; keep the legs straight or bend the knees for an easier version.",
            "Brace your abdomen and lift your hips until your shoulder, hip, and ankle form one line.",
            "Breathe steadily, keep the top hip stacked over the lower hip, and avoid rolling your chest toward the floor.",
            "Lower your hips with control and repeat on the other side; stop if the shoulder becomes painful."
        ],
        "ar": [
            "استلقِ على جانبك وضع المرفق أسفل الكتف مباشرة؛ أبقِ الساقين مستقيمتين أو اثنِ الركبتين لتسهيل الحركة.",
            "شد عضلات البطن وارفع الحوض حتى يصطف الكتف والحوض والكاحل في خط واحد.",
            "تنفس بانتظام وأبقِ الورك العلوي فوق السفلي، وتجنب تدوير الصدر نحو الأرض.",
            "أنزل الحوض بتحكم وكرر على الجانب الآخر، وتوقف إذا ظهر ألم في الكتف."
        ]
    },
    "Superman": {
        "en": [
            "Lie face down on a mat with arms extended overhead and legs straight; look down to keep your neck neutral.",
            "Gently brace your abdomen and squeeze your glutes before lifting.",
            "Raise the opposite arm and leg a small distance, or lift both sides only if comfortable; do not force an arch in the lower back.",
            "Pause briefly, lower slowly, and alternate sides or repeat as prescribed; stop if back pain appears."
        ],
        "ar": [
            "استلقِ على بطنك فوق بساط مع مد الذراعين أمام الرأس والساقين للخلف، وانظر إلى الأرض لإبقاء الرقبة محايدة.",
            "شد عضلات البطن برفق واضغط الألوية قبل الرفع.",
            "ارفع الذراع والساق المتعاكستين مسافة صغيرة، أو ارفع الطرفين معًا فقط إذا كان ذلك مريحًا، دون المبالغة في تقويس أسفل الظهر.",
            "توقف لحظة ثم اخفض الطرفين ببطء وبدّل الجهة أو كرر حسب البرنامج؛ توقف إذا ظهر ألم بالظهر."
        ]
    },
    "Flutter_Kicks": {
        "en": [
            "Lie face down on a sturdy flat bench with your hips near the edge, grip the front securely, and let straight legs hover clear of the floor.",
            "Brace your abdomen and glutes while keeping your pelvis steady and lower back neutral.",
            "Alternate small leg lifts, raising one leg slightly as the other lowers without swinging or arching your back.",
            "Continue evenly for the prescribed repetitions or time; stop if your lower back hurts or the bench feels unstable."
        ],
        "ar": [
            "استلقِ على بطنك فوق مقعد مسطح وثابت مع اقتراب الوركين من الحافة، وأمسك مقدمة المقعد بإحكام واترك الساقين مستقيمتين فوق الأرض.",
            "شد عضلات البطن والألوية مع تثبيت الحوض والحفاظ على وضع محايد لأسفل الظهر.",
            "ارفع إحدى الساقين مسافة صغيرة بينما تنخفض الأخرى، بالتبادل دون تأرجح أو تقويس الظهر.",
            "واصل بإيقاع منتظم حسب التكرارات أو المدة المحددة، وتوقف إذا ظهر ألم أسفل الظهر أو لم يكن المقعد ثابتًا."
        ]
    },
    "Downward_Facing_Balance": {
        "en": [
            "Place your abdomen and hips on a stable exercise ball and set both hands on a clear, non-slip floor in front of you.",
            "Walk your hands forward until your torso is supported and aligned, keeping the ball centered under your pelvis and abdomen.",
            "Brace your core and lift both legs only to hip height while keeping the elbows and knees straight; avoid over-arching your back.",
            "Breathe steadily, lower your legs, and walk your hands back; use assistance or skip the move if you cannot balance securely."
        ],
        "ar": [
            "ضع البطن والوركين فوق كرة تمرين ثابتة، وثبّت اليدين على أرضية غير زلقة وخالية من العوائق أمامك.",
            "حرّك اليدين إلى الأمام حتى يستند الجذع وتصبح محاذاته مستقيمة، مع إبقاء الكرة تحت الحوض والبطن.",
            "شد عضلات الجذع وارفع الساقين حتى مستوى الورك فقط، مع إبقاء المرفقين والركبتين مستقيمين وتجنب تقويس الظهر.",
            "تنفس بانتظام ثم اخفض الساقين وأعد اليدين للخلف؛ اطلب المساعدة أو اترك التمرين إذا تعذر الحفاظ على التوازن."
        ]
    },
    "Barbell_Squat": {
        "en": [
            "Set the bar in a rack just below shoulder height and place the safety pins below your controlled squat depth. Position the bar across the upper back, brace, and set feet about shoulder-width apart.",
            "Unrack with both feet stable, step back carefully, and keep the whole foot planted with toes turned slightly outward.",
            "Breathe in and bend at the hips and knees, lowering only as far as you can keep your trunk steady and knees tracking over the toes.",
            "Drive through the whole foot to stand, keeping the bar over mid-foot; exhale without snapping the knees straight.",
            "Regain balance before returning the bar to the rack; use the safety pins and a spotter when appropriate."
        ],
        "ar": [
            "اضبط البار على الحامل أسفل مستوى الكتفين قليلًا، وضع مسامير الأمان أسفل عمق النزول الذي تتحكم فيه. ضع البار على أعلى الظهر، وشد الجذع، واجعل القدمين بعرض الكتفين تقريبًا.",
            "ارفع البار من الحامل بقدمين ثابتتين، وخذ خطوة أو خطوتين للخلف بحذر، مع إبقاء القدم كاملة على الأرض وتوجيه الأصابع للخارج قليلًا.",
            "خذ شهيقًا واثنِ الوركين والركبتين للنزول، ولا تتجاوز العمق الذي يحافظ على ثبات الجذع واتجاه الركبتين مع أصابع القدم.",
            "ادفع الأرض بكامل القدم للوقوف مع بقاء البار فوق منتصف القدم، وازفر دون قفل الركبتين بعنف.",
            "استعد توازنك قبل إعادة البار للحامل، واستخدم مسامير الأمان ومساعدًا عند الحاجة."
        ]
    },
    "Bent_Over_Barbell_Row": {
        "en": [
            "Stand with feet hip-width apart, hold the bar just outside the knees, soften the knees, and hinge until the torso inclines; keep the spine neutral and bar close.",
            "Brace and pull the bar toward the lower ribs by driving the elbows back; keep the torso still rather than jerking.",
            "Pause with the shoulder blades drawn together without shrugging or lifting the chin.",
            "Lower the bar under control to straight arms; stop if you cannot maintain a neutral back."
        ],
        "ar": [
            "قف والقدمان بعرض الحوض، وامسك البار خارج الركبتين قليلًا، واثنِ الركبتين وادفع الوركين للخلف حتى يميل الجذع مع ظهر محايد والبار قريبًا.",
            "شد الجذع واسحب البار نحو الأضلاع السفلية بتحريك المرفقين للخلف، دون هز الجذع أو انتزاع الحمل.",
            "توقف لحظة مع تقريب لوحي الكتف دون رفع الكتفين نحو الأذنين أو رفع الذقن.",
            "أنزل البار بتحكم حتى تمتد الذراعان، وتوقف إذا تعذر الحفاظ على وضع محايد للظهر."
        ]
    },
    "Dumbbell_Bench_Press": {
        "en": [
            "Sit on a flat bench with dumbbells on your thighs, then lie back and guide them to chest height one at a time; get help for heavy loads.",
            "Plant your feet, gently set the shoulder blades, and keep wrists stacked over elbows.",
            "Lower the dumbbells beside the chest with elbows angled about 30–60 degrees from the torso; do not bounce.",
            "Press up over the chest while exhaling, keeping the weights controlled and avoiding a hard elbow snap.",
            "Bring the dumbbells back to the thighs carefully before sitting up."
        ],
        "ar": [
            "اجلس على مقعد مستوٍ والدمبل على الفخذين، ثم استلقِ وارفع كل دمبل إلى مستوى الصدر بالتتابع؛ اطلب المساعدة عند استخدام حمل ثقيل.",
            "ثبّت القدمين ولوحي الكتف برفق، واجعل الرسغين فوق المرفقين.",
            "اخفض الدمبل بجانب الصدر مع إبعاد المرفقين عن الجذع بزاوية مريحة تقارب 30 إلى 60 درجة، دون ارتداد.",
            "ادفع الدمبل فوق الصدر مع الزفير وتحكم في المسار، وتجنب قفل المرفقين بعنف.",
            "أعد الدمبل إلى الفخذين بحذر قبل الجلوس."
        ]
    },
    "Dumbbell_Bicep_Curl": {
        "en": [
            "Stand tall with a dumbbell in each hand, palms forward or facing each other, and elbows close to the sides.",
            "Bend the elbows to curl the weights toward the shoulders while keeping the upper arms still.",
            "Pause briefly at the top without swinging the torso or rolling the shoulders forward.",
            "Lower the dumbbells slowly to the starting position; reduce the load if you need momentum."
        ],
        "ar": [
            "قف باستقامة والدمبل بجانب الجسم، واجعل راحتي اليدين للأمام أو متقابلتين والمرفقين قريبين من الجانبين.",
            "اثنِ المرفقين وارفع الدمبل نحو الكتفين مع إبقاء العضدين ثابتين.",
            "توقف لحظة في الأعلى دون تأرجح الجذع أو تدوير الكتفين للأمام.",
            "اخفض الدمبل ببطء إلى البداية، وقلل الحمل إذا احتجت إلى استخدام زخم الجسم."
        ]
    },
    "Dumbbell_Shoulder_Press": {
        "en": [
            "Sit with back support and bring the dumbbells to shoulder height; keep feet planted, wrists straight, and ribs stacked over the pelvis.",
            "Start with elbows slightly in front of the body and forearms close to vertical.",
            "Press the dumbbells overhead along a comfortable path while exhaling; do not arch the lower back to finish the lift.",
            "Lower the weights slowly to shoulder height without dropping the elbows suddenly.",
            "Use a lighter load or neutral grip if needed, and stop if the shoulder becomes painful."
        ],
        "ar": [
            "اجلس مع مسند ظهر وارفع الدمبل إلى مستوى الكتفين، وثبّت القدمين واجعل الرسغين مستقيمين والقفص الصدري فوق الحوض.",
            "ابدأ والمرفقان أمام الجسم قليلًا والساعدان قريبين من الوضع الرأسي.",
            "ادفع الدمبل فوق الرأس في مسار مريح مع الزفير، دون تقويس أسفل الظهر لإكمال الرفعة.",
            "اخفض الأوزان ببطء إلى مستوى الكتفين دون إسقاط المرفقين فجأة.",
            "استخدم حملًا أخف أو قبضة محايدة عند الحاجة، وتوقف إذا ظهر ألم في الكتف."
        ]
    },
    "Parallel_Bar_Dip": {
        "en": [
            "Grip both parallel bars and support your body with shoulders down; use an assisted machine or foot support if you cannot hold the start steadily.",
            "Bend the elbows to lower your body through a comfortable range, keeping control and avoiding a forced deep shoulder stretch.",
            "Press through the hands to rise until the elbows are nearly straight without shrugging.",
            "Stop if the shoulders hurt or your body swings; shorten the range or choose an assisted variation."
        ],
        "ar": [
            "أمسك العارضتين المتوازيتين وارفع الجسم مع إبقاء الكتفين منخفضين؛ استخدم جهاز المساعدة أو دعم القدمين إذا تعذر الثبات.",
            "اثنِ المرفقين لخفض الجسم ضمن مدى مريح، وتحكم في النزول دون إجبار الكتف على امتداد عميق.",
            "ادفع براحتي اليدين للصعود حتى يقترب المرفقان من الاستقامة دون رفع الكتفين.",
            "توقف إذا ظهر ألم بالكتف أو تأرجح الجسم؛ قلل المدى أو استخدم نسخة بمساعدة."
        ]
    },
    "Barbell_Hip_Thrust": {
        "en": [
            "Sit with your upper back against a stable bench, place a padded bar across the hips, and set feet flat about hip-width apart.",
            "Brace the abdomen, keep the ribs down and chin slightly tucked, then drive through the feet to raise the hips.",
            "Finish when the torso and thighs align; squeeze the glutes without arching the lower back.",
            "Lower the hips under control and stop before the pelvis rolls or the back becomes painful."
        ],
        "ar": [
            "اجلس وأعلى الظهر مستند إلى مقعد ثابت، وضع بارًا مبطنًا فوق الحوض وثبّت القدمين كاملتين بعرض الحوض تقريبًا.",
            "شد البطن وأبقِ الأضلاع منخفضة والذقن للداخل قليلًا، ثم ادفع الأرض بالقدمين لرفع الحوض.",
            "توقف عندما يصطف الجذع والفخذان، واعصر عضلات الألوية دون تقويس أسفل الظهر.",
            "اخفض الحوض بتحكم وتوقف قبل التفافه أو ظهور ألم في الظهر."
        ]
    },
    "Dumbbell_Step_Ups": {
        "en": [
            "Choose a stable, non-slip step low enough to keep balance, hold the dumbbells at your sides, and place the whole working foot on the box.",
            "Drive through the foot on the box to stand tall; use the trailing leg only for balance rather than pushing off hard.",
            "Step down slowly, keeping the working knee aligned with the toes and landing quietly.",
            "Alternate legs as prescribed; reduce the step height or load if balance or knee control is lost."
        ],
        "ar": [
            "اختر صندوقًا ثابتًا غير زلق وارتفاعه يسمح بالتوازن، وأمسك الدمبل بجانب الجسم وضع القدم العاملة كاملة على الصندوق.",
            "ادفع بالقدم المرتكزة على الصندوق حتى تقف باستقامة، واستخدم الساق الخلفية للتوازن لا للدفع بقوة.",
            "انزل ببطء مع توجيه الركبة نحو أصابع القدم والهبوط بهدوء.",
            "بدّل الساقين حسب البرنامج، وقلل ارتفاع الصندوق أو الحمل إذا اختل التوازن أو تحكم الركبة."
        ]
    },
    "Seated_Cable_Rows": {
        "en": [
            "Sit at the cable station with knees slightly bent, feet supported, torso upright, and the handle held with arms extended.",
            "Brace and pull the handle toward the lower ribs by driving the elbows back; avoid rocking the torso.",
            "Pause briefly with shoulder blades moving together without shrugging the shoulders.",
            "Extend the arms slowly and allow the shoulder blades to move naturally while keeping the lower back controlled."
        ],
        "ar": [
            "اجلس أمام جهاز الكيبل مع ثني الركبتين قليلًا وتثبيت القدمين والجذع منتصب، وأمسك المقبض والذراعان ممدودتان.",
            "شد الجذع واسحب المقبض نحو الأضلاع السفلية بتحريك المرفقين للخلف، دون تأرجح الجذع.",
            "توقف لحظة مع تقريب لوحي الكتف دون رفع الكتفين نحو الأذنين.",
            "مد الذراعين ببطء ودع لوحي الكتف يتحركان طبيعيًا مع الحفاظ على ثبات أسفل الظهر."
        ]
    },
    "Leg_Press": {
        "en": [
            "Sit with your back and pelvis supported, place feet about shoulder-width on the platform, and keep the knees aligned with the toes.",
            "Release the safety lever only when ready, then lower the platform slowly until you reach a comfortable depth without the pelvis curling off the backrest.",
            "Press through the whole foot to return the platform, keeping the knees slightly soft rather than snapping them straight.",
            "Do not bounce at the bottom or force the knees inward; reduce the range if the pelvis shifts.",
            "Re-engage the safety locks before exiting the machine, and stop if knee or back pain occurs."
        ],
        "ar": [
            "اجلس مع إسناد الظهر والحوض، وضع القدمين بعرض الكتفين تقريبًا على مسند القدمين واجعل الركبتين في اتجاه الأصابع.",
            "حرر ذراع الأمان بعد الاستعداد فقط، ثم اخفض المنصة ببطء إلى عمق مريح دون التفاف الحوض أو انفصاله عن مسند الظهر.",
            "ادفع المنصة بكامل القدم للعودة، مع إبقاء الركبتين مرتخيتين قليلًا بدل قفلهما بعنف.",
            "لا ترتد من أسفل الحركة ولا تدع الركبتين تنهاران للداخل؛ قلل المدى إذا تحرك الحوض.",
            "أعد أقفال الأمان قبل مغادرة الجهاز، وتوقف إذا ظهر ألم في الركبة أو الظهر."
        ]
    }

    "Dips_-_Triceps_Version": {
        "en": [
            "To get into the starting position, hold your body at arm's length with your arms nearly locked above the bars.",
            "Now, inhale and slowly lower yourself downward. Your torso should remain upright and your elbows should stay close to your body. This helps to better focus on tricep involvement. Lower yourself until there is a 90 degree angle formed between the upper arm and forearm.",
            "Then, exhale and push your torso back up using your triceps to bring your body back to the starting position.",
            "Repeat the movement for the prescribed amount of repetitions."
        ],
        "ar": [
            "ابدأ أعلى العارضتين بذراعين شبه ممدودتين مع تثبيت الكتفين.",
            "خذ شهيقًا وانزل ببطء مع إبقاء الجذع قائمًا والمرفقين قريبين من الجسم.",
            "توقف عند مدى مريح للمرفقين؛ لا تهبط إلى حد ألم الكتف.",
            "ازفر وادفع بالعضلة ثلاثية الرؤوس للعودة دون قفل قاسٍ للمرفقين."
        ]
    },
    "Barbell_Step_Ups": {
        "en": [
            "Stand up straight while holding a barbell placed on the back of your shoulders (slightly below the neck) and stand upright behind an elevated platform (such as the one used for spotting behind a flat bench). This is your starting position.",
            "Place the right foot on the elevated platform. Step on the platform by extending the hip and the knee of your right leg. Use the heel mainly to lift the rest of your body up and place the foot of the left leg on the platform as well. Breathe out as you execute the force required to come up.",
            "Step down with the left leg by flexing the hip and knee of the right leg as you inhale. Return to the original standing position by placing the right foot of to next to the left foot on the initial position.",
            "Repeat with the right leg for the recommended amount of repetitions and then perform with the left leg."
        ],
        "ar": [
            "ضع قدمًا كاملة على صندوق ثابت، وثبّت البار على أعلى الظهر مع شد الجذع.",
            "ادفع بالكعب والقدم المرتكزة واصعد حتى الوقوف دون قفزة من القدم الخلفية.",
            "اصعد بالقدم الأخرى ثم انزل بتحكم خطوة واحدة في كل مرة.",
            "أكمل العدات بساق واحدة ثم بدّل الجهة، وخفّض ارتفاع الصندوق إذا اختل التوازن."
        ]
    },
    "Platform_Hamstring_Slides": {
        "en": [
            "For this movement a wooden floor or similar is needed. Lay on your back with your legs extended. Place a gym towel or a light weight underneath your heel. This will be your starting position.",
            "Begin the movement by flexing the knee, keeping your other leg straight.",
            "Continue bringing the heel closer to you, sliding it on the floor.",
            "At full knee flexion, reverse the movement to return to the starting position."
        ],
        "ar": [
            "استلقِ على الظهر وضع الكعبين على سطح منزلق ثابت مع مد الساقين.",
            "شد عضلات البطن والألوية وارفع الحوض إلى جسر مع إبقاء الضلوع والحوض بمحاذاة.",
            "اسحب الكعبين نحو الجسم بثني الركبتين مع الحفاظ على ارتفاع الحوض.",
            "مد الساقين ببطء دون إسقاط الحوض، وقلّل المدى إذا تشنجت خلفية الفخذ."
        ]
    },
    "Standing_Dumbbell_Calf_Raise": {
        "en": [
            "Stand with your torso upright holding two dumbbells in your hands by your sides. Place the ball of the foot on a sturdy and stable wooden board (that is around 2-3 inches tall) while your heels extend off and touch the floor. This will be your starting position.",
            "With the toes pointing either straight (to hit all parts equally), inwards (for emphasis on the outer head) or outwards (for emphasis on the inner head), raise the heels off the floor as you exhale by contracting the calves. Hold the top contraction for a second.",
            "As you inhale, go back to the starting position by slowly lowering the heels.",
            "Repeat for the recommended amount of times."
        ],
        "ar": [
            "قف طويلًا والدمبلان بجانب الجسم، وضع مقدمة القدمين على حافة ثابتة إن توفر دعم آمن.",
            "اخفض الكعبين قليلًا تحت مستوى مقدمة القدمين دون ارتداد.",
            "ارفع الكعبين بالضغط على عضلتي السمانة وتوقف لحظة في الأعلى.",
            "اخفض الكعبين ببطء مع إبقاء الركبتين والجذع ثابتين."
        ]
    },
    "Cable_Crossover": {
        "en": [
            "To get yourself into the starting position, place the pulleys on a high position (above your head), select the resistance to be used and hold the pulleys in each hand.",
            "Step forward in front of an imaginary straight line between both pulleys while pulling your arms together in front of you. Your torso should have a small forward bend from the waist. This will be your starting position.",
            "With a slight bend on your elbows in order to prevent stress at the biceps tendon, extend your arms to the side (straight out at both sides) in a wide arc until you feel a stretch on your chest. Breathe in as you perform this portion of the movement. Keep in mind that throughout the movement, the arms and torso should remain stationary; the movement should only occur at the shoulder joint.",
            "Return your arms back to the starting position as you breathe out. Make sure to use the same arc of motion used to lower the weights.",
            "Hold for a second at the starting position and repeat the movement for the prescribed amount of repetitions."
        ],
        "ar": [
            "اضبط البكرتين في موضع مرتفع واختر حملًا يمكن التحكم فيه، ثم أمسك المقبضين وتقدم خطوة.",
            "مل قليلًا من الورك مع ثني بسيط للمرفقين وثبات الجذع.",
            "افتح الذراعين بقوس واسع حتى تشعر بتمدد مريح في الصدر دون شد مؤلم للكتف.",
            "قرّب اليدين أمام الصدر بالقوس نفسه مع الزفير دون اصطدام الأوزان.",
            "أعد الذراعين ببطء وكرر مع الحفاظ على زاوية المرفقين."
        ]
    },
    "Close-Grip_Front_Lat_Pulldown": {
        "en": [
            "Sit down on a pull-down machine with a wide bar attached to the top pulley. Make sure that you adjust the knee pad of the machine to fit your height. These pads will prevent your body from being raised by the resistance attached to the bar.",
            "Grab the bar with the palms facing forward using the prescribed grip. Note on grips: For a wide grip, your hands need to be spaced out at a distance wider than your shoulder width. For a medium grip, your hands need to be spaced out at a distance equal to your shoulder width and for a close grip at a distance smaller than your shoulder width.",
            "As you have both arms extended in front of you - while holding the bar at the chosen grip width - bring your torso back around 30 degrees or so while creating a curvature on your lower back and sticking your chest out. This is your starting position.",
            "As you breathe out, bring the bar down until it touches your upper chest by drawing the shoulders and the upper arms down and back. Concentrate on squeezing the back muscles once you reach the full contracted position. The upper torso should remain stationary (only the arms should move). The forearms should do no other work except for holding the bar; therefore do not try to pull the bar down using the forearms.",
            "After a second in the contracted position, while squeezing your shoulder blades together, slowly raise the bar back to the starting position when your arms are fully extended and the lats are fully stretched. Inhale during this portion of the movement.",
            "6. Repeat this motion for the prescribed amount of repetitions."
        ],
        "ar": [
            "اجلس واضبط وسادة الفخذين لمنع ارتفاع الجسم أثناء السحب.",
            "أمسك البار بقبضة أضيق من الكتفين مع مد الذراعين.",
            "ارفع الصدر قليلًا مع ميل بسيط للجذع وثبات الحوض.",
            "ازفر واسحب المرفقين إلى أسفل حتى يقترب البار من أعلى الصدر، لا خلف الرقبة.",
            "توقف لحظة مع إبعاد الكتفين عن الأذنين وتجنب التأرجح.",
            "أعد البار ببطء إلى المد الكامل بتحكم."
        ]
    },
    "Dip_Machine": {
        "en": [
            "Sit securely in a dip machine, select the weight and firmly grasp the handles.",
            "Now keep your elbows in at your sides in order to place emphasis on the triceps. The elbows should be bent at a 90 degree angle.",
            "As you contract the triceps, extend your arms downwards as you exhale. At the bottom of the movement, focus on keeping a little bend in your arms to keep tension on the triceps muscle.",
            "Now slowly let your arms come back up to the starting position as you inhale.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "اضبط المقعد والحمل واجلس مع قبضة ثابتة على مقابض الجهاز.",
            "أبقِ المرفقين قريبين من الجذع والكتفين منخفضين.",
            "ازفر ومد المرفقين لتحريك المقابض إلى أسفل دون قفل قاسٍ للمفاصل.",
            "عد ببطء مع الشهيق حتى زاوية مريحة دون رفع الكتفين.",
            "كرر دون تأرجح، وخفّض الحمل إذا فقدت التحكم."
        ]
    },
    "Face_Pull": {
        "en": [
            "Set the rope or dual handles at face height and choose a light load; stand with a stable staggered stance.",
            "Pull the rope toward your forehead, driving the elbows outward and back while separating your hands.",
            "Pause with the upper arms near shoulder height; keep the ribs stacked and avoid shrugging or leaning back.",
            "Extend your arms forward slowly and return without letting the weight pull your shoulders abruptly."
        ],
        "ar": [
            "اضبط الحبل أو المقبضين عند مستوى الوجه واختر حملًا خفيفًا، ثم قف بوقفة ثابتة.",
            "اسحب الحبل نحو الجبهة وحرّك المرفقين للخارج والخلف مع إبعاد اليدين.",
            "توقف لحظة عندما يقترب العضدان من مستوى الكتفين، مع إبقاء الأضلاع فوق الحوض دون رفع الكتفين.",
            "مد الذراعين إلى الأمام ببطء وعد دون ترك الوزن يجذب الكتفين فجأة."
        ]
    },
    "Front_Barbell_Squat": {
        "en": [
            "This exercise is best performed inside a squat rack for safety purposes. To begin, first set the bar on a rack that best matches your height. Once the correct height is chosen and the bar is loaded, bring your arms up under the bar while keeping the elbows high and the upper arm slightly above parallel to the floor. Rest the bar on top of the deltoids and cross your arms while grasping the bar for total control.",
            "Lift the bar off the rack by first pushing with your legs and at the same time straightening your torso.",
            "Step away from the rack and position your legs using a shoulder width medium stance with the toes slightly pointed out. Keep your head up at all times as looking down will get you off balance and also maintain a straight back. This will be your starting position. (Note: For the purposes of this discussion we will use the medium stance described above which targets overall development; however you can choose any of the three stances described in the foot positioning section).",
            "Begin to slowly lower the bar by bending the knees as you maintain a straight posture with the head up. Continue down until the angle between the upper leg and the calves becomes slightly less than 90-degrees (which is the point in which the upper legs are below parallel to the floor). Inhale as you perform this portion of the movement. If you performed the exercise correctly, the front of the knees should make an imaginary straight line with the toes that is perpendicular to the front. If your knees are past that imaginary line (if they are past your toes) then you are placing undue stress on the knee and the exercise has been performed incorrectly.",
            "Begin to raise the bar as you exhale by pushing the floor mainly with the middle of your foot as you straighten the legs again and go back to the starting position.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "داخل حامل السكوات، اضبط مسامير الأمان أسفل أعمق وضع آمن؛ واستند بالبار على مقدمة الكتفين مع رفع المرفقين.",
            "قف لرفع البار من الحامل، ثم ارجع خطوة أو خطوتين واضبط القدمين بعرض الكتفين تقريبًا.",
            "خذ شهيقًا وشد الجذع، ثم انزل بالورك بين الركبتين مع إبقاء الجذع قائمًا والمرفقين مرتفعين.",
            "اجعل الركبتين في اتجاه أصابع القدم وثبّت القدم كاملة، ولا تنزل أبعد من المدى الذي تتحكم فيه.",
            "ازفر وادفع الأرض للوقوف مع منع الركبتين من الانهيار إلى الداخل.",
            "أعد البار إلى الحامل بأمان بعد آخر عدة، وخفّض الحمل إذا هبط المرفقان أو انطوى الجذع."
        ]
    },
    "Hammer_Curls": {
        "en": [
            "Stand up with your torso upright and a dumbbell on each hand being held at arms length. The elbows should be close to the torso.",
            "The palms of the hands should be facing your torso. This will be your starting position.",
            "Now, while holding your upper arm stationary, exhale and curl the weight forward while contracting the biceps. Continue to raise the weight until the biceps are fully contracted and the dumbbell is at shoulder level. Hold the contracted position for a brief moment as you squeeze the biceps. Focus on keeping the elbow stationary and only moving your forearm.",
            "After the brief pause, inhale and slowly begin the lower the dumbbells back down to the starting position.",
            "Repeat for the recommended amount of repetitions."
        ],
        "ar": [
            "قف مستقيمًا والدمبلان بجانب الجسم والكفان في وضع محايد، مع إبقاء المرفقين قريبين من الجذع.",
            "ثبّت العضدين وازفر أثناء ثني المرفقين لرفع الدمبلين دون تأرجح الجذع.",
            "توقف عندما يقترب الدمبلان من الكتفين مع إبقاء الرسغين مستقيمين ودون رفع الكتفين.",
            "اثبت لحظة دون دفع الوزن أو تحريك المرفقين إلى الأمام.",
            "خذ شهيقًا واخفض الدمبلين ببطء إلى امتداد مريح للذراعين."
        ]
    },
    "Incline_Dumbbell_Press": {
        "en": [
            "Lie back on an incline bench with a dumbbell in each hand atop your thighs. The palms of your hands will be facing each other.",
            "Then, using your thighs to help push the dumbbells up, lift the dumbbells one at a time so that you can hold them at shoulder width.",
            "Once you have the dumbbells raised to shoulder width, rotate your wrists forward so that the palms of your hands are facing away from you. This will be your starting position.",
            "Be sure to keep full control of the dumbbells at all times. Then breathe out and push the dumbbells up with your chest.",
            "Lock your arms at the top, hold for a second, and then start slowly lowering the weight. Tip Ideally, lowering the weights should take about twice as long as raising them.",
            "Repeat the movement for the prescribed amount of repetitions.",
        ],
        "ar": [
            "استلقِ على مقعد مائل وامسك دمبلًا بكل يد فوق الفخذين، والكفان متقابلان.",
            "استخدم الفخذين لمساعدة رفع الدمبلين إلى مستوى الكتفين بالتتابع.",
            "أدر الرسغين حتى تتجه الكفان للأمام، وثبّت القدمين ولوحي الكتف على المقعد.",
            "ازفر وادفع الدمبلين فوق الصدر بمسار متحكم دون تقويس أسفل الظهر.",
            "توقف لحظة في الأعلى دون اصطدام الأوزان، ثم اخفضها ببطء مع جعل النزول أبطأ من الصعود.",
            "كرر بالمدى الذي تتحكم فيه، وخفّض الحمل إذا فقدت ثبات الكتف.",
        ]
    },
    "Lateral_Raise_-_With_Bands": {
        "en": [
            "To begin, stand on an exercise band so that tension begins at arm's length. Grasp the handles using a pronated (palms facing your thighs) grip that is slightly less than shoulder width. The handles should be resting on the sides of your thighs. Your arms should be extended with a slight bend at the elbows and your back should be straight. This will be your starting position.",
            "Use your side shoulders to lift the handles to the sides as you exhale. Continue to lift the handles until they are slightly above parallel. As you lift the handles, slightly tilt the hand as if you were pouring water and keep your arms extended. Also, keep your torso stationary and pause for a second at the top of the movement.",
            "Lower the handles back down slowly to the starting position. Inhale as you perform this portion of the movement.",
            "Repeat for the recommended amount of repetitions.",
        ],
        "ar": [
            "قف على منتصف المطاط والقدمان بعرض الورك، وأمسك المقبضين بجانب الفخذين مع ثني بسيط للمرفقين.",
            "ازفر وارفع الذراعين إلى الجانبين حتى قرب مستوى الكتفين دون ميل الجذع أو رفع الكتفين نحو الأذنين.",
            "توقف لحظة مع بقاء الرسغين محايدين والذراعين تحت السيطرة، ولا ترفع فوق مدى مريح.",
            "اخفض المقبضين ببطء مع الشهيق حتى البداية مع الحفاظ على شد المطاط.",
        ]
    },
    "Leg_Extensions": {
        "en": [
            "For this exercise you will need to use a leg extension machine. First choose your weight and sit on the machine with your legs under the pad (feet pointed forward) and the hands holding the side bars. This will be your starting position. You will need to adjust the pad so that it falls on top of your lower leg (just above your feet). Also, make sure that your legs form a 90-degree angle between the lower and upper leg. If the angle is less than 90-degrees then that means the knee is over the toes which in turn creates undue stress at the knee joint. If the machine is designed that way, either look for another machine or just make sure that when you start executing the exercise you stop going down once you hit the 90-degree angle.",
            "Using your quadriceps, extend your legs to the maximum as you exhale. Ensure that the rest of the body remains stationary on the seat. Pause a second on the contracted position.",
            "Slowly lower the weight back to the original position as you inhale, ensuring that you do not go past the 90-degree angle limit.",
            "Repeat for the recommended amount of times.",
        ],
        "ar": [
            "اجلس واضبط محور الركبة مع محور الجهاز، واجعل الوسادة فوق أسفل الساقين بقليل وثبّت الظهر.",
            "ازفر ومد الركبتين بتحكم حتى قرب الامتداد الكامل دون قفل المفصل بعنف.",
            "توقف لحظة مع إبقاء الحوض والظهر ملاصقين للمقعد ودون تأرجح الجذع.",
            "اخفض الوزن ببطء مع الشهيق إلى مدى مريح، وقلّل الحمل أو المدى إذا ظهر ألم بالركبة.",
        ]
    },
    "Leverage_High_Row": {
        "en": [
            "Load an appropriate weight onto the pins and adjust the seat height so that you can just reach the handles above you. Adjust the knee pad to help keep you down. Grasp the handles with a pronated grip. This will be your starting position.",
            "Pull the handles towards your torso, retracting your shoulder blades as you flex the elbow.",
            "Pause at the bottom of the motion, and then slowly return the handles to the starting position.",
            "For multiple repetitions, avoid completely returning the weight to the stops to keep tension on the muscles being worked.",
        ],
        "ar": [
            "اضبط المقعد ووسادة الركبتين، وثبّت القدمين وامسك المقبضين بقبضة أمامية.",
            "اسحب المقبضين نحو الجذع بتحريك المرفقين للخلف مع تقريب لوحي الكتف دون هز الجذع.",
            "توقف لحظة عند نهاية السحب وأبقِ الرقبة محايدة والكتفين بعيدين عن الأذنين.",
            "أعد المقبضين ببطء إلى الأمام دون ترك الأوزان تصطدم أو فقدان التحكم في الشد.",
        ]
    },
    "Lying_Leg_Curls": {
        "en": [
            "Adjust the machine lever to fit your height and lie face down on the leg curl machine with the pad of the lever on the back of your legs (just a few inches under the calves). Preferably use a leg curl machine that is angled as opposed to flat since an angled position is more favorable for hamstrings recruitment.",
            "Keeping the torso flat on the bench, ensure your legs are fully stretched and grab the side handles of the machine. Position your toes straight (or you can also use any of the other two stances described on the foot positioning section). This will be your starting position.",
            "As you exhale, curl your legs up as far as possible without lifting the upper legs from the pad. Once you hit the fully contracted position, hold it for a second.",
            "As you inhale, bring the legs back to the initial position. Repeat for the recommended amount of repetitions.",
        ],
        "ar": [
            "اضبط الوسادة فوق الكعبين وأسفل الساقين، واستلقِ على البطن مع محاذاة الركبتين لمحور الجهاز.",
            "ثبّت الحوض والجذع على المقعد، ثم ازفر واثنِ الركبتين لجذب الكعبين نحو الجسم دون رفع الفخذين.",
            "توقف لحظة عند الانقباض مع إبقاء أسفل الظهر محايدًا وعدم تقويسه.",
            "أنزل الساقين ببطء مع الشهيق حتى امتداد مريح للركبتين دون إسقاط الوزن.",
        ]
    },
    "Machine_Bench_Press": {
        "en": [
            "Sit down on the Chest Press Machine and select the weight.",
            "Step on the lever provided by the machine since it will help you to bring the handles forward so that you can grab the handles and fully extend the arms.",
            "Grab the handles with a palms-down grip and lift your elbows so that your upper arms are parallel to the floor to the sides of your torso. Your forearms will be pointing forward since you are grabbing the handles. Once you bring the handles forward and extend the arms you will be at the starting position.",
            "Now bring the handles back towards you as you breathe in.",
            "Push the handles away from you as you flex your pecs and you breathe out. Hold the contraction for a second before going back to the starting position.",
            "Repeat for the recommended amount of reps.",
        ],
        "ar": [
            "اضبط المقعد بحيث تصطف المقابض مع منتصف الصدر، ثم اختر حملًا يمكنك التحكم فيه.",
            "استخدم ذراع المساعدة في الجهاز لتقريب المقابض، واجلس مع تثبيت الظهر وإمساكها بإحكام.",
            "ابدأ والمرفقان مثنيان بزاوية مريحة، مع استقرار لوحي الكتف والرسغين بمحاذاة الساعدين.",
            "خذ شهيقًا وأعد المقابض نحو الصدر ببطء دون دفع الكتفين للأمام.",
            "ازفر وادفع المقابض إلى الأمام مع إبقاء الجذع ثابتًا، وتجنب قفل المرفقين بعنف.",
            "أعد المقابض إلى وضع البداية بتحكم دون اصطدام الأوزان، وتوقف إذا ظهر ألم.",
        ]
    },
    "One-Arm_Dumbbell_Row": {
        "en": [
            "Choose a flat bench and place a dumbbell on each side of it.",
            "Place the right leg on top of the end of the bench, bend your torso forward from the waist until your upper body is parallel to the floor, and place your right hand on the other end of the bench for support.",
            "Use the left hand to pick up the dumbbell on the floor and hold the weight while keeping your lower back straight. The palm of the hand should be facing your torso. This will be your starting position.",
            "Pull the resistance straight up to the side of your chest, keeping your upper arm close to your side and keeping the torso stationary. Breathe out as you perform this step. Concentrate on squeezing the back muscles once you reach the full contracted position. Also, make sure that the force is performed with the back muscles and not the arms. Finally, the upper torso should remain stationary and only the arms should move. The forearms should do no other work except for holding the dumbbell; therefore do not try to pull the dumbbell up using the forearms.",
            "Lower the resistance straight down to the starting position. Breathe in as you perform this step.",
            "Repeat the movement for the specified amount of repetitions.",
        ],
        "ar": [
            "ضع دمبلًا بجانب مقعد ثابت، واستند بإحدى اليدين والركبة من الجهة نفسها على المقعد.",
            "مل من الورك حتى يميل الجذع للأمام مع ظهر محايد وثبات الحوض.",
            "أمسك الدمبل باليد الحرة واترك الذراع ممدودة تحت الكتف دون تدوير الجذع.",
            "ازفر واسحب المرفق بمحاذاة الجسم نحو الورك، مع إبقاء الكتف والجذع ثابتين.",
            "اخفض الدمبل ببطء مع الشهيق حتى تمتد الذراع دون إسقاط الوزن أو شد الكتف.",
            "أكمل العدات ثم بدّل الجهة، واستخدم حملًا أخف إذا بدأ الجذع بالدوران.",
        ]
    },
    "Side_Lateral_Raise": {
        "en": [
            "Pick a couple of dumbbells and stand with a straight torso and the dumbbells by your side at arms length with the palms of the hand facing you. This will be your starting position.",
            "While maintaining the torso in a stationary position (no swinging), lift the dumbbells to your side with a slight bend on the elbow and the hands slightly tilted forward as if pouring water in a glass. Continue to go up until you arms are parallel to the floor. Exhale as you execute this movement and pause for a second at the top.",
            "Lower the dumbbells back down slowly to the starting position as you inhale.",
            "Repeat for the recommended amount of repetitions.",
        ],
        "ar": [
            "قف مستقيمًا والدمبلان بجانب الفخذين والكفان للداخل، مع ثني بسيط للمرفقين.",
            "ارفع الدمبلين إلى الجانبين حتى قرب مستوى الكتفين مع ثبات الجذع ودون تأرجح.",
            "توقف لحظة مع إبقاء الرقبة مرتاحة والكتفين منخفضين والرسغين ثابتين.",
            "اخفض الدمبلين ببطء مع الشهيق إلى وضع البداية وكرر بالمدى المتحكم فيه.",
        ]
    },
    "Smith_Machine_Bench_Press": {
        "en": [
            "Place a flat bench underneath the smith machine. Now place the barbell at a height that you can reach when lying down and your arms are almost fully extended. Once the weight you need is selected, lie down on the flat bench. Using a pronated grip that is wider than shoulder width, unlock the bar from the rack and hold it straight over you with your arms locked. This will be your starting position.",
            "As you breathe in, come down slowly until you feel the bar on your middle chest.",
            "After a second pause, bring the bar back to the starting position as you breathe out and push the bar using your chest muscles. Lock your arms in the contracted position, hold for a second and then start coming down slowly again. It should take at least twice as long to go down than to come up.",
            "Repeat the movement for the prescribed amount of repetitions.",
            "When you are done, lock the bar back in the rack.",
        ],
        "ar": [
            "ضع المقعد المستوي تحت جهاز سميث واضبط ارتفاع البار، ثم استلقِ وأمسكه بقبضة أوسع قليلًا من الكتفين.",
            "حرر البار من الخطافات وثبته فوق منتصف الصدر مع محاذاة الرسغين للمرفقين.",
            "خذ شهيقًا واخفض البار ببطء إلى منتصف الصدر مع زاوية مريحة للمرفقين.",
            "ازفر وادفع البار إلى الأعلى دون ارتداد عن الصدر أو قفل المرفقين بعنف.",
            "بعد آخر عدة، أعد البار إلى خطافات الأمان وتأكد من تثبيته قبل النهوض.",
        ]
    },
    "Smith_Machine_Squat": {
        "en": [
            "To begin, first set the bar on the height that best matches your height. Once the correct height is chosen and the bar is loaded, step under the bar and place the back of your shoulders (slightly below the neck) across it.",
            "Hold on to the bar using both arms at each side (palms facing forward), unlock it and lift it off the rack by first pushing with your legs and at the same time straightening your torso.",
            "Position your legs using a shoulder width medium stance with the toes slightly pointed out. Keep your head up at all times and also maintain a straight back. This will be your starting position. (Note: For the purposes of this discussion we will use the medium stance which targets overall development; however you can choose any of the three stances discussed in the foot stances section).",
            "Begin to slowly lower the bar by bending the knees as you maintain a straight posture with the head up. Continue down until the angle between the upper leg and the calves becomes slightly less than 90-degrees (which is the point in which the upper legs are below parallel to the floor). Inhale as you perform this portion of the movement. If you performed the exercise correctly, the front of the knees should make an imaginary straight line with the toes that is perpendicular to the front. If your knees are past that imaginary line (if they are past your toes) then you are placing undue stress on the knee and the exercise has been performed incorrectly.",
            "Begin to raise the bar as you exhale by pushing the floor with the heel of your foot as you straighten the legs again and go back to the starting position.",
            "Repeat for the recommended amount of repetitions.",
        ],
        "ar": [
            "اضبط ارتفاع البار وضعه على أعلى عضلات الظهر لا على الرقبة، وتأكد من ثبات القدمين أسفل البار.",
            "أمسك البار من الجانبين، حرره من الخطافات وقف بثبات ثم اضبط القدمين بعرض الكتفين تقريبًا.",
            "شد الجذع وخذ شهيقًا، ثم اخفض الورك مع ثني الركبتين باتجاه أصابع القدم.",
            "انزل إلى عمق تستطيع التحكم فيه مع بقاء الكعبين على الأرض والجذع ثابتًا.",
            "ازفر وادفع الأرض للوقوف دون انهيار الركبتين إلى الداخل أو فرط تقوس الظهر.",
            "بعد المجموعة أعد البار إلى الخطافات بإحكام، وخفّض الحمل إذا اختل المسار.",
        ]
    },
}

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
    ("Box_Skip", "قفز متتابع بين الصناديق", "football", "agility"),
    ("Front_Cone_Hops_or_hurdle_hops", "قفز أمامي فوق الأقماع", "football", "agility"),
    ("Lateral_Cone_Hops", "قفز جانبي فوق الأقماع", "football", "agility"),
    ("Single-Cone_Sprint_Drill", "تدريب العدو حول قمع واحد", "football", "speed"),
    ("Side_Hop-Sprint", "قفز جانبي ثم انطلاق", "football", "speed"),
    ("Bicycling", "ركوب الدراجة", "cycling", "endurance"),
    ("Bicycling_Stationary", "دراجة ثابتة", "cycling", "endurance"),
    ("Recumbent_Bike", "دراجة ثابتة بمقعد خلفي", "cycling", "endurance"),
    ("Barbell_Step_Ups", "صعود الصندوق بالبار", "gym", "strength"),
    ("Platform_Hamstring_Slides", "انزلاق الكعبين لثني خلفية الفخذ", "gym", "strength"),
    ("Standing_Dumbbell_Calf_Raise", "رفع السمانة واقفًا بالدمبل", "gym", "strength"),
    ("Rowing_Stationary", "تجديف ثابت", "hiit", "endurance"),
    ("Fast_Skipping", "قفز متناوب سريع", "boxing", "conditioning"),
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
    "Leg_Extensions": "isolation",
    "Incline_Dumbbell_Press": "horizontal_push",
    "Side_Bridge": "core",
    "Flutter_Kicks": "core",
    "Downward_Facing_Balance": "core",
    "Superman": "core",
    "Mountain_Climbers": "core",
    "Linear_Acceleration_Wall_Drill": "locomotion",
    "Straight-Arm_Dumbbell_Pullover": "horizontal_pull",
    "One-Arm_Medicine_Ball_Slam": "core",
    "Overhead_Slam": "core",
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

GUIDANCE = {
    "squat": {
        "regression_en": "Reduce load or depth, or squat to a stable box while keeping the whole foot planted.",
        "regression_ar": "خفّض الحمل أو عمق النزول، أو استخدم صندوقًا ثابتًا مع بقاء القدم كاملة على الأرض.",
        "progression_en": "Add depth, repetitions, or a small load only while the feet stay planted and knees track cleanly.",
        "progression_ar": "زد العمق أو العدات أو حملًا بسيطًا فقط مع ثبات القدم وتتبع الركبة لاتجاهها.",
        "safety_en": "Keep knees aligned with the feet and stop for joint pain, heel lift, or loss of balance.",
        "safety_ar": "حافظ على اتجاه الركبتين مع القدمين وتوقف عند ألم المفصل أو ارتفاع الكعب أو فقدان التوازن.",
    },
    "hinge": {
        "regression_en": "Use a shorter range, lighter load, or a dowel guide until the hip hinge stays separate from spinal motion.",
        "regression_ar": "استخدم مدى أقصر أو حملًا أخف أو عصًا إرشادية حتى تثبت حركة الحوض دون تحريك العمود الفقري.",
        "progression_en": "Increase range or load gradually only while the spine stays neutral and the load remains close.",
        "progression_ar": "زد المدى أو الحمل تدريجيًا فقط مع بقاء الظهر محايدًا والحمل قريبًا من الجسم.",
        "safety_en": "Keep the load close and stop for radiating pain, loss of grip, or rounding that cannot be corrected.",
        "safety_ar": "أبقِ الحمل قريبًا وتوقف عند ألم ممتد أو فقدان القبضة أو تقوس لا يمكنك تصحيحه.",
    },
    "horizontal_push": {
        "regression_en": "Use a wall, higher incline, machine, or lighter load to keep the shoulders and wrists controlled.",
        "regression_ar": "استخدم الحائط أو ميلًا أعلى أو جهازًا أو حملًا أخف للحفاظ على تحكم الكتفين والرسغين.",
        "progression_en": "Lower the incline or add a small load only after every repetition keeps the same shoulder and wrist path.",
        "progression_ar": "اخفض الميل أو أضف حملًا بسيطًا بعد ثبات مسار الكتف والرسغ في كل عدة.",
        "safety_en": "Do not force painful shoulder depth; use secure supports and a spotter when a heavy free load could trap you.",
        "safety_ar": "لا تجبر الكتف على مدى مؤلم، واستخدم دعمًا آمنًا ومساعدًا عند حمل حر ثقيل قد يحاصرك.",
    },
    "vertical_push": {
        "regression_en": "Use a lighter load, neutral grip, seated support, or a shorter pain-free overhead range.",
        "regression_ar": "استخدم حملًا أخف أو قبضة محايدة أو دعمًا بالجلوس أو مدى رأسيًا أقصر دون ألم.",
        "progression_en": "Add range or a small load only while ribs stay stacked over the pelvis and both arms move evenly.",
        "progression_ar": "زد المدى أو حملًا بسيطًا فقط مع ثبات القفص الصدري فوق الحوض وتحرك الذراعين بالتساوي.",
        "safety_en": "Stop for shoulder pain, numbness, uneven pressing, or lower-back arching that you cannot control.",
        "safety_ar": "توقف عند ألم الكتف أو التنميل أو الدفع غير المتساوي أو تقوس أسفل الظهر الذي لا يمكنك التحكم فيه.",
    },
    "horizontal_pull": {
        "regression_en": "Use chest support, a lighter band, or less range so the pull does not depend on torso momentum.",
        "regression_ar": "استخدم دعمًا للصدر أو مطاطًا أخف أو مدى أقل حتى لا يعتمد السحب على زخم الجذع.",
        "progression_en": "Add a pause, range, repetitions, or a small load while the neck stays relaxed and torso remains still.",
        "progression_ar": "أضف توقفًا أو مدى أو عدات أو حملًا بسيطًا مع ارتخاء الرقبة وثبات الجذع.",
        "safety_en": "Stop if you must jerk the torso, shrug repeatedly, or feel sharp shoulder, elbow, or back pain.",
        "safety_ar": "توقف إذا اضطررت لهز الجذع أو رفع الكتفين باستمرار أو شعرت بألم حاد في الكتف أو المرفق أو الظهر.",
    },
    "vertical_pull": {
        "regression_en": "Use assisted support, a pulldown machine, or a shorter range that preserves shoulder control.",
        "regression_ar": "استخدم مساعدة أو جهاز سحب أو مدى أقصر يحافظ على التحكم في الكتف.",
        "progression_en": "Reduce assistance or add repetitions before load, keeping a controlled full reach.",
        "progression_ar": "قلّل المساعدة أو زد العدات قبل الحمل مع الحفاظ على مد كامل ومتحكم فيه.",
        "safety_en": "Avoid pulling behind the neck; stop for painful hanging, numbness, or loss of shoulder control.",
        "safety_ar": "تجنب السحب خلف الرقبة وتوقف عند ألم التعليق أو التنميل أو فقدان التحكم في الكتف.",
    },
    "isolation": {
        "regression_en": "Reduce load or range and support the body so only the intended joint performs the movement.",
        "regression_ar": "خفّض الحمل أو المدى وثبّت الجسم حتى ينفذ المفصل المستهدف الحركة وحده.",
        "progression_en": "Add controlled repetitions first, then a small load without recruiting adjacent joints.",
        "progression_ar": "زد العدات المتحكم فيها أولًا ثم حملًا بسيطًا دون إشراك المفاصل المجاورة.",
        "safety_en": "Keep adjacent joints stable and stop for sharp joint pain, tingling, or momentum you cannot control.",
        "safety_ar": "ثبّت المفاصل المجاورة وتوقف عند ألم مفصلي حاد أو وخز أو زخم لا يمكنك التحكم فيه.",
    },
    "core": {
        "regression_en": "Shorten the lever, reduce range, or add stable support while maintaining normal breathing.",
        "regression_ar": "قصّر ذراع المقاومة أو خفّض المدى أو أضف دعمًا ثابتًا مع استمرار التنفس الطبيعي.",
        "progression_en": "Lengthen the lever or add small resistance only while breathing and spinal position remain controlled.",
        "progression_ar": "أطل ذراع المقاومة أو أضف مقاومة بسيطة فقط مع استمرار التنفس وثبات وضع العمود الفقري.",
        "safety_en": "Do not hold your breath; stop for neck strain, lower-back pain, or loss of pelvic control.",
        "safety_ar": "لا تحبس النفس وتوقف عند إجهاد الرقبة أو ألم أسفل الظهر أو فقدان التحكم في الحوض.",
    },
    "locomotion": {
        "regression_en": "Reduce speed, duration, or incline and choose a level route or stable machine you can control.",
        "regression_ar": "اخفض السرعة أو الزمن أو الميل، واختر مسارًا مستويًا أو جهازًا ثابتًا يمكن التحكم فيه.",
        "progression_en": "Increase only one variable—time, speed, or incline—while gait and breathing remain controlled.",
        "progression_ar": "زد متغيرًا واحدًا فقط—الزمن أو السرعة أو الميل—مع بقاء الخطوة والتنفس تحت السيطرة.",
        "safety_en": "Use a clear route or secure machine and stop for chest pain, dizziness, or unusual breathlessness.",
        "safety_ar": "استخدم مسارًا خاليًا أو جهازًا آمنًا وتوقف عند ألم الصدر أو الدوار أو ضيق نفس غير معتاد.",
    },
    "jump": {
        "regression_en": "Reduce height or speed, or practise a step-down and quiet landing before repeated jumps.",
        "regression_ar": "خفّض الارتفاع أو السرعة، أو تدرّب على النزول والهبوط الهادئ قبل القفز المتكرر.",
        "progression_en": "Add height, speed, or direction one at a time only after every landing is quiet and stable.",
        "progression_ar": "زد الارتفاع أو السرعة أو الاتجاه واحدًا تلو الآخر فقط بعد ثبات وهدوء كل هبوط.",
        "safety_en": "Land quietly on a clear, stable surface; stop when landing alignment or balance deteriorates.",
        "safety_ar": "اهبط بهدوء على سطح ثابت وخالٍ، وتوقف عند تدهور محاذاة الهبوط أو التوازن.",
    },
    "mobility": {
        "regression_en": "Use support, a smaller range, or a shorter hold that produces mild tension without pain.",
        "regression_ar": "استخدم دعمًا أو مدى أصغر أو تثبيتًا أقصر يسبب شدًا خفيفًا دون ألم.",
        "progression_en": "Add a little range or hold time only while the stretch stays gentle and breathing remains relaxed.",
        "progression_ar": "زد المدى أو زمن التثبيت قليلًا فقط مع بقاء الإطالة لطيفة والتنفس هادئًا.",
        "safety_en": "Never bounce or force range; stop for sharp pain, numbness, tingling, or joint pinching.",
        "safety_ar": "لا ترتد أو تجبر المدى، وتوقف عند ألم حاد أو تنميل أو وخز أو انحشار بالمفصل.",
    },
    "recovery": {
        "regression_en": "Use less body weight, a softer tool, or a shorter session around the sensitive area.",
        "regression_ar": "استخدم وزن جسم أقل أو أداة ألين أو مدة أقصر حول المنطقة الحساسة.",
        "progression_en": "Progress with slightly more time or controlled pressure, never by rolling directly over a joint or nerve.",
        "progression_ar": "تدرّج بزيادة بسيطة في الزمن أو الضغط المتحكم فيه، وليس بالدحرجة مباشرة فوق مفصل أو عصب.",
        "safety_en": "Avoid bones, joints, and known nerve paths; stop immediately for numbness, bruising, or sharp pain.",
        "safety_ar": "تجنب العظام والمفاصل ومسارات الأعصاب المعروفة، وتوقف فورًا عند تنميل أو كدمة أو ألم حاد.",
    },
}

GUIDANCE_FAMILY_OVERRIDES = {
    "Leg_Extensions": "isolation",
    "Incline_Dumbbell_Press": "horizontal_push",
    "Side_Bridge": "core",
    "Flutter_Kicks": "core",
    "Downward_Facing_Balance": "core",
    "Superman": "core",
    "Mountain_Climbers": "core",
    "Linear_Acceleration_Wall_Drill": "locomotion",
    "Straight-Arm_Dumbbell_Pullover": "horizontal_pull",
}

STEP_GUIDANCE_IDS = {
    "Barbell_Step_Ups",
    "Dumbbell_Step_Ups",
    "Step-up_with_Knee_Raise",
    "Bodyweight_Walking_Lunge",
}

STEP_GUIDANCE = {
    "regression_en": "Use a lower step, shorter stride, no added load, or stable support until each transfer is controlled.",
    "regression_ar": "استخدم ارتفاعًا أقل أو خطوة أقصر أو دون حمل إضافي أو مع دعم ثابت حتى تتحكم في كل انتقال.",
    "progression_en": "Add height, stride, repetitions, or a small load one at a time while each planted step stays stable.",
    "progression_ar": "زد الارتفاع أو طول الخطوة أو العدات أو حملًا بسيطًا واحدًا تلو الآخر مع ثبات كل خطوة مرتكزة.",
    "safety_en": "Use a clear, non-slip surface, place the whole working foot securely, and stop for knee pain or loss of balance.",
    "safety_ar": "استخدم سطحًا خاليًا وغير زلق، وثبّت القدم العاملة كاملة، وتوقف عند ألم الركبة أو فقدان التوازن.",
}

THROW_GUIDANCE_IDS = {
    "One-Arm_Medicine_Ball_Slam",
    "Overhead_Slam",
    "Medicine_Ball_Chest_Pass",
    "Medicine_Ball_Scoop_Throw",
    "Catch_and_Overhead_Throw",
}

THROW_GUIDANCE = {
    "regression_en": "Use a lighter ball, slower release, shorter range, or a controlled pass without an explosive catch.",
    "regression_ar": "استخدم كرة أخف أو إطلاقًا أبطأ أو مدى أقصر أو تمريرًا متحكمًا دون التقاط انفجاري.",
    "progression_en": "Add speed, range, or a small load one at a time only while release and catch remain controlled.",
    "progression_ar": "زد السرعة أو المدى أو حملًا بسيطًا واحدًا تلو الآخر فقط مع ثبات الإطلاق والالتقاط.",
    "safety_en": "Clear the throwing area, use a secure ball and target, and stop if release, catch, or trunk control deteriorates.",
    "safety_ar": "أخلِ منطقة الرمي، واستخدم كرة وهدفًا آمنين، وتوقف عند تدهور التحكم في الإطلاق أو الالتقاط أو الجذع.",
}

SLIDER_GUIDANCE = {
    "regression_en": "Shorten the slide, use both legs, or place the feet on a surface with more friction.",
    "regression_ar": "قصّر مسافة الانزلاق أو استخدم الساقين معًا أو ضع القدمين على سطح احتكاكه أعلى.",
    "progression_en": "Increase slide length or use one leg only while the hips remain level and the return stays controlled.",
    "progression_ar": "زد طول الانزلاق أو استخدم ساقًا واحدة فقط مع ثبات الحوض والتحكم في العودة.",
    "safety_en": "Test the sliding surface first, keep the path clear, and stop for hamstring cramp, knee pain, or loss of hip control.",
    "safety_ar": "اختبر سطح الانزلاق أولًا وأخلِ المسار، وتوقف عند تشنج خلفية الفخذ أو ألم الركبة أو فقدان ثبات الحوض.",
}

EXPECTED_GUIDANCE_FAMILIES = frozenset({
    "squat", "hinge", "horizontal_push", "vertical_push",
    "horizontal_pull", "vertical_pull", "isolation", "core",
    "locomotion", "jump", "mobility", "recovery",
})


def validate_guidance_diversity(guidance: dict[str, dict[str, str]]) -> None:
    if set(guidance) != EXPECTED_GUIDANCE_FAMILIES:
        raise ValueError("guidance must cover exactly the 12 movement families")

    for language, label in (("ar", "Arabic"), ("en", "English")):
        family_guidance = []
        for family in sorted(EXPECTED_GUIDANCE_FAMILIES):
            values = []
            for field in ("regression", "progression", "safety"):
                key = f"{field}_{language}"
                if key not in guidance[family]:
                    raise ValueError(f"missing {key} for {family}")
                value = guidance[family][key]
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{key} for {family} must be non-blank text")
                values.append(value)
            family_guidance.append(tuple(values))
        if len(set(family_guidance)) != len(EXPECTED_GUIDANCE_FAMILIES):
            raise ValueError(f"{label} guidance must contain 12 distinct families")


def guidance_for(source_id: str, pattern: str) -> dict:
    if source_id in STEP_GUIDANCE_IDS:
        return STEP_GUIDANCE
    if source_id in THROW_GUIDANCE_IDS:
        return THROW_GUIDANCE
    if source_id == "Platform_Hamstring_Slides":
        return SLIDER_GUIDANCE
    return GUIDANCE[GUIDANCE_FAMILY_OVERRIDES.get(source_id, pattern)]


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
    source_id = item["id"]
    if source_id in THROW_GUIDANCE_IDS:
        return {"sets": 3, "reps": "5–8", "durationSeconds": None, "restSeconds": 90, "tempo": "explosive / انفجاري", "setTypes": ["warmup", "working"]}
    if source_id in {"Side_Bridge", "Downward_Facing_Balance"}:
        return {"sets": 3, "reps": None, "durationSeconds": 30, "restSeconds": 45, "tempo": "static / ثابت", "setTypes": ["working"]}
    if source_id in {"Flutter_Kicks", "Mountain_Climbers"}:
        return {"sets": 3, "reps": None, "durationSeconds": 30, "restSeconds": 60, "tempo": "controlled / متحكم", "setTypes": ["working"]}
    if source_id == "Linear_Acceleration_Wall_Drill":
        return {"sets": 3, "reps": None, "durationSeconds": 20, "restSeconds": 60, "tempo": "fast controlled / سريع متحكم", "setTypes": ["warmup", "working"]}
    if pattern in {"mobility", "recovery"}:
        return {"sets": 2, "reps": None, "durationSeconds": 30, "restSeconds": 20, "tempo": "slow / بطيء", "setTypes": ["working"]}
    if pattern == "locomotion":
        return {"sets": 1, "reps": None, "durationSeconds": 1200, "restSeconds": 0, "tempo": "RPE 5–7", "setTypes": ["working"]}
    if pattern == "jump":
        return {"sets": 3, "reps": "5–8", "durationSeconds": None, "restSeconds": 90, "tempo": "explosive / انفجاري", "setTypes": ["warmup", "working"]}
    if item.get("level") == "expert":
        return {"sets": 4, "reps": "4–8", "durationSeconds": None, "restSeconds": 150, "tempo": "2-0-1", "setTypes": ["warmup", "working"]}
    return {"sets": 3, "reps": "8–12", "durationSeconds": None, "restSeconds": 90, "tempo": "3-1-1", "setTypes": ["warmup", "working"]}


LOADLESS_EXERCISE_IDS = {
    "Side_Bridge", "Flutter_Kicks", "Downward_Facing_Balance",
    "Superman", "Mountain_Climbers", "Linear_Acceleration_Wall_Drill",
}


def tracking_for(item: dict, pattern: str) -> dict[str, bool]:
    source_id = item["id"]
    timed_hold = source_id in {"Side_Bridge", "Downward_Facing_Balance"}
    return {
        "load": source_id not in LOADLESS_EXERCISE_IDS and pattern not in {"mobility", "recovery", "locomotion", "jump"},
        "rpe": True,
        "rir": not timed_hold and pattern not in {"mobility", "recovery", "locomotion"},
        "volume": not timed_hold and pattern not in {"mobility", "recovery", "locomotion"},
    }


def clean_instructions(values: list[str]) -> list[str]:
    result = []
    for value in values:
        normalized = " ".join(value.replace("Tip:", "").split())
        if normalized:
            result.append(normalized)
    return result[:6]


def build(source: Path, repo: Path) -> None:
    validate_guidance_diversity(GUIDANCE)
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
        guidance = guidance_for(source_id, pattern)
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
            "steps": {
                "en": STEP_OVERRIDES.get(source_id, {}).get("en") or clean_instructions(item.get("instructions") or []) or ENGLISH_STEPS[pattern],
                "ar": STEP_OVERRIDES.get(source_id, {}).get("ar") or family["steps_ar"],
            },
            "breathing": {"en": family["breathing_en"], "ar": family["breathing_ar"]},
            "prescription": prescription(item, pattern),
            "commonMistakes": {"en": family["mistakes_en"], "ar": family["mistakes_ar"]},
            "regression": {"en": guidance["regression_en"], "ar": guidance["regression_ar"]},
            "progression": {"en": guidance["progression_en"], "ar": guidance["progression_ar"]},
            "safety": {"en": guidance["safety_en"], "ar": guidance["safety_ar"]},
            "demo": {"type": "two_frame_image_sequence", "assets": assets, "offline": True, "alt": {"en": f"Start and finish positions for {item['name']}", "ar": f"وضعا البداية والنهاية لتمرين {name_ar}"}},
            "tracking": tracking_for(item, pattern),
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
