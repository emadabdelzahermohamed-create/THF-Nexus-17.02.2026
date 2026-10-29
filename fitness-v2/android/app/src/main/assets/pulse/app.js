(() => {
  'use strict';
  const N = window.PulseNative || null;
  const EXERCISES = Array.isArray(window.THF_EXERCISES) ? window.THF_EXERCISES : [];
  const PROGRAMS = Array.isArray(window.THF_PROGRAMS) ? window.THF_PROGRAMS : [];
  const motionManifest = window.THF_MOTION_MANIFEST || {};
  const failedMotionExerciseIds = new Set();
  let activeMotionErrorHandler = null;
  const $ = id => document.getElementById(id);
  const store = (() => {
    try { localStorage.setItem('__thf_probe', '1'); localStorage.removeItem('__thf_probe'); return localStorage; }
    catch { const memory = new Map(); return {getItem:key=>memory.get(key)||null,setItem:(key,value)=>memory.set(key,String(value)),removeItem:key=>memory.delete(key)}; }
  })();
  const voiceGuidance = window.THFVoiceGuidance.createVoiceGuidance({
    storage: store,
    speakNative: N && typeof N.speak === 'function' ? (text, language, append) => N.speak(text, language, Boolean(append)) : null,
    speakWeb: 'speechSynthesis' in window ? (text, language, append) => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language;
      if (!append) window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    } : null,
  });
  const restTimer = window.THFRestTimer.createRestTimer();
  const parse = (value, fallback) => { try { return value ? JSON.parse(value) : fallback; } catch { return fallback; } };
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[match]));
  const locale = () => state.lang === 'ar' ? 'ar-EG' : 'en-US';
  const local = value => value?.[state.lang] ?? value?.en ?? '';

  const COPY = {
    ar: {
      skip:'انتقل إلى المحتوى',brandTag:'تدريب واضح. تقدم حقيقي.',offlineBanner:'مكتبة التمارين والدليل المصور متاحان دون إنترنت.',todayEyebrow:'خطتك اليوم',todayTitle:'خطوة واحدة واضحة',startWorkout:'ابدأ التمرين',readiness:'جاهزية',sessions:'جلسات',today:'اليوم',minutes:'دقائق',volume:'الحجم',streak:'الاستمرار',days:'أيام',weeklyGoal:'هدف الأسبوع',consistency:'الاستمرارية قبل الشدة',weeklyHint:'أكمل جلسات مناسبة لمستواك ثم تدرّج بهدوء.',trainEyebrow:`26 برنامجًا · ${EXERCISES.length} تمرينًا موثقًا`,trainTitle:'اختر خطتك وتدرّب بوضوح',searchLabel:'ابحث في التمارين',searchPlaceholder:'اسم التمرين أو العضلة أو المعدة',gymLibrary:'مكتبة الجيم',gymTitle:'ابنِ جلستك حسب جسمك ومعداتك',gymHint:'فلترة حقيقية للعضلة والمعدة ونمط الحركة والمستوى والهدف.',exercises:'تمرين',filters:'الفلاتر',bodyPart:'جزء الجسم',muscle:'العضلة',equipment:'المعدة',movement:'نمط الحركة',level:'المستوى',goal:'الهدف',resetFilters:'إعادة ضبط الفلاتر',noResults:'لا توجد نتائج مطابقة',noResultsHint:'جرّب مسح البحث أو تقليل عدد الفلاتر.',backToLibrary:'العودة للمكتبة',toggleFrame:'بدّل الوضع',technique:'طريقة الأداء',sessionLog:'سجل الجلسة',set:'المجموعة',load:'الحمل',reps:'العدات',addSet:'+ إضافة مجموعة',rest:'راحة',skipRest:'تخطّي',safety:'السلامة أولًا',finishWorkout:'إنهاء التمرين وحفظه',progressEyebrow:'افهم تقدمك',progressTitle:'قوة وحجم واستمرارية',totalWorkouts:'كل الجلسات',totalVolume:'إجمالي الحجم',personalRecords:'أرقام شخصية',activeMinutes:'دقائق نشطة',volumeTrend:'حجم آخر 7 جلسات',localData:'محلي',recentHistory:'السجل الأخير',clearHistory:'مسح السجل',healthTitle:'نشاطك في مكان واحد',beforeConnect:'قبل الاتصال',yourChoice:'بياناتك واختيارك',healthRationale:'نقرأ الخطوات وجلسات التمرين والمسافة والسعرات النشطة لعرض ملخصك، ونكتب فقط جلسات THF المكتملة. لا نطلب نبض القلب أو النوم أو الوزن.',healthBullet1:'يمكن رفض أي إذن أو سحبه لاحقًا.',healthBullet2:'يبقى تسجيل التمرين المحلي عاملًا دون اتصال.',healthBullet3:'معرّف ثابت يمنع تكرار الجلسة عند إعادة المحاولة.',reviewPermissions:'راجع الأذونات واتصل',steps7:'خطوات / 7 أيام',distance:'المسافة',activeCalories:'سعرات نشطة',healthEmpty:'اتصل ثم اضغط مزامنة لقراءة البيانات.',neverSynced:'آخر مزامنة: لم تتم',healthSyncing:'جاري المزامنة…',healthSyncWait:'Health Connect مشغول مؤقتًا. انتظر قليلًا ثم أعد المحاولة.',healthSyncFailed:'تعذرت المزامنة. حاول مرة أخرى بعد قليل.',syncNow:'مزامنة الآن',managePermissions:'إدارة الأذونات',samsungPath:'المسار المعتمد: Samsung Health ← Health Connect ← Top Hero Fit. لا نعتبر الربط ناجحًا قبل ظهور بيانات Samsung فعلية.',profileEyebrow:'خطتك تتكيف معك',profileTitle:'ملف التدريب',goalFitness:'لياقة عامة',goalMuscle:'بناء العضلات',goalStrength:'القوة',goalEndurance:'التحمل',goalMobility:'الحركة والاستشفاء',beginner:'مبتدئ',intermediate:'متوسط',advanced:'متقدم',daysPerWeek:'أيام التدريب أسبوعيًا',availableEquipment:'المعدات المتاحة',savePlan:'احفظ وحدّث خطة اليوم',profileSaved:'تم حفظ ملفك وتحديث اقتراح اليوم.',privacyOffline:'الخصوصية والوضع المحلي',refreshStatus:'تحديث الحالة',voiceGuidance:'الدليل الصوتي',reduceMotion:'تقليل الحركة',navToday:'اليوم',navTrain:'تدريب',navProgress:'التقدم',navHealth:'الصحة',navProfile:'ملفي',startThisExercise:'ابدأ هذا التمرين',sourceLicense:'المصدر والترخيص',all:'الكل',offline:'أوفلاين',start:'البداية',finish:'النهاية',setup:'الاستعداد',breathing:'التنفس',defaults:'الجرعة المقترحة',mistakes:'أخطاء شائعة',regression:'نسخة أسهل',progression:'التدرج',working:'أساسية',warmup:'إحماء',completed:'مكتملة',saved:'تم حفظ التمرين محليًا.',emptyHistory:'ابدأ أول تمرين ليظهر تقدمك هنا.',noCatalog:'تعذر تحميل مكتبة التمارين الأوفلاين.',browserHealth:'Health Connect متاح داخل تطبيق Android فقط.',statusOffline:'وضع أوفلاين جاهز',statusOnline:'متصل وجاهز للمزامنة',clearConfirm:'اضغط مرة أخرى خلال 3 ثوانٍ لمسح السجل.',profilePlan:'جلسة مناسبة لهدفك',oneExercise:'حركة واحدة واضحة',min:'د',setsLabel:'مجموعات',sourceText:'free-exercise-db · Unlicense · نسخة أوفلاين موثقة',setProgress:'{done} من {total} مكتملة',dateLabel:'التاريخ',volumeLabel:'الحجم',rpeHelp:'RPE من 1 إلى 10',rirHelp:'RIR عدد العدات المتبقية',programs:'البرامج',exerciseLibrary:'مكتبة التمارين',programLibrary:'برامج أوفلاين منظمة',programTitle:'ابدأ بمسار واضح وتدرّج آمن',programHint:'كل برنامج يحدد الأسابيع والجلسات والتمارين وRPE وRIR ومعيار التدرج.',noPrograms:'لا توجد برامج في هذا القسم',weeks:'أسابيع',daysWeekly:'أيام أسبوعيًا',useProgram:'استخدم هذا البرنامج',programSelected:'تم اختيار البرنامج وتحديث اليوم.',programSessions:'جلسات البرنامج',session:'جلسة',exerciseCount:'تمارين',programSource:'تكوين تحريري أصلي من THF · بيانات وصور التمارين: free-exercise-db / Unlicense'
    },
    en: {
      skip:'Skip to content',brandTag:'Clear training. Real progress.',offlineBanner:'The exercise library and visual demos work fully offline.',todayEyebrow:"Today's plan",todayTitle:'One clear next action',startWorkout:'Start workout',readiness:'Readiness',sessions:'Sessions',today:'Today',minutes:'Minutes',volume:'Volume',streak:'Streak',days:'days',weeklyGoal:'Weekly goal',consistency:'Consistency before intensity',weeklyHint:'Complete sessions that fit your level, then progress gradually.',trainEyebrow:`26 programs · ${EXERCISES.length} documented exercises`,trainTitle:'Choose your plan and train clearly',searchLabel:'Search exercises',searchPlaceholder:'Exercise, muscle, or equipment',gymLibrary:'Gym library',gymTitle:'Build around your body and equipment',gymHint:'Real filters for muscle, equipment, movement, level, and goal.',exercises:'exercises',filters:'Filters',bodyPart:'Body part',muscle:'Muscle',equipment:'Equipment',movement:'Movement',level:'Level',goal:'Goal',resetFilters:'Reset filters',noResults:'No matching exercises',noResultsHint:'Clear the search or remove some filters.',backToLibrary:'Back to library',toggleFrame:'Change position',technique:'Technique',sessionLog:'Session log',set:'Set',load:'Load',reps:'Reps',addSet:'+ Add set',rest:'Rest',skipRest:'Skip',safety:'Safety first',finishWorkout:'Finish and save workout',progressEyebrow:'Understand your progress',progressTitle:'Strength, volume, consistency',totalWorkouts:'All sessions',totalVolume:'Total volume',personalRecords:'Personal records',activeMinutes:'Active minutes',volumeTrend:'Last 7 session volume',localData:'Local',recentHistory:'Recent history',clearHistory:'Clear history',healthTitle:'Your activity in one place',beforeConnect:'Before connecting',yourChoice:'Your data, your choice',healthRationale:'We read steps, exercise sessions, distance, and active calories for your summary, and write only completed THF sessions. We do not request heart rate, sleep, or weight.',healthBullet1:'You may deny or revoke any permission later.',healthBullet2:'Local workout logging remains available offline.',healthBullet3:'A stable identifier prevents duplicate writes on retry.',reviewPermissions:'Review permissions and connect',steps7:'Steps / 7 days',distance:'Distance',activeCalories:'Active calories',healthEmpty:'Connect, then sync to read activity.',neverSynced:'Last sync: never',healthSyncing:'Syncing…',healthSyncWait:'Health Connect is temporarily busy. Wait briefly, then try again.',healthSyncFailed:'Sync failed. Please try again shortly.',syncNow:'Sync now',managePermissions:'Manage permissions',samsungPath:'Supported path: Samsung Health ← Health Connect ← Top Hero Fit. We do not call it connected until real Samsung data appears.',profileEyebrow:'Your plan adapts to you',profileTitle:'Training profile',goalFitness:'General fitness',goalMuscle:'Build muscle',goalStrength:'Strength',goalEndurance:'Endurance',goalMobility:'Mobility & recovery',beginner:'Beginner',intermediate:'Intermediate',advanced:'Advanced',daysPerWeek:'Training days per week',availableEquipment:'Available equipment',savePlan:'Save and update Today',profileSaved:'Profile saved and Today updated.',privacyOffline:'Privacy and offline mode',refreshStatus:'Refresh status',voiceGuidance:'Voice guidance',reduceMotion:'Reduce motion',navToday:'Today',navTrain:'Train',navProgress:'Progress',navHealth:'Health',navProfile:'Profile',startThisExercise:'Start this exercise',sourceLicense:'Source and license',all:'All',offline:'Offline',start:'Start',finish:'Finish',setup:'Setup',breathing:'Breathing',defaults:'Suggested prescription',mistakes:'Common mistakes',regression:'Regression',progression:'Progression',working:'Working',warmup:'Warm-up',completed:'Complete',saved:'Workout saved locally.',emptyHistory:'Start your first workout to see progress here.',noCatalog:'The offline exercise library could not be loaded.',browserHealth:'Health Connect is available in the Android app only.',statusOffline:'Offline mode ready',statusOnline:'Online and ready to sync',clearConfirm:'Press again within 3 seconds to clear history.',profilePlan:'A session aligned to your goal',oneExercise:'one clear movement',min:'min',setsLabel:'sets',sourceText:'free-exercise-db · Unlicense · audited offline copy',setProgress:'{done} of {total} complete',dateLabel:'Date',volumeLabel:'Volume',rpeHelp:'RPE from 1 to 10',rirHelp:'RIR is reps left in reserve',programs:'Programs',exerciseLibrary:'Exercise library',programLibrary:'Structured offline programs',programTitle:'Start with a clear path and safe progression',programHint:'Every program defines its weeks, sessions, exercises, RPE, RIR and progression rule.',noPrograms:'No programs in this section',weeks:'weeks',daysWeekly:'days weekly',useProgram:'Use this program',programSelected:'Program selected and Today updated.',programSessions:'Program sessions',session:'Session',exerciseCount:'exercises',programSource:'Original THF editorial composition · exercise data and images: free-exercise-db / Unlicense'
    }
  };
  Object.assign(COPY.ar, {startSession:'ابدأ الجلسة',saveNext:'احفظ وانتقل للتمرين التالي',finishSession:'أنهِ الجلسة واحفظها',exerciseOf:'تمرين {current} من {total}',nextExercise:'تم حفظ التمرين. التالي: {name}',sessionComplete:'اكتملت الجلسة وحُفظت.',signInSync:'سجّل للدخول والمزامنة',syncConnected:'المزامنة متصلة',syncConnecting:'جارٍ ربط الحساب',offlineReady:'أوفلاين جاهز',syncUnavailable:'المزامنة غير مهيأة',foundingHeroEyebrow:'حزمة تجميلية لمرة واحدة',foundingHeroTitle:'البطل المؤسس',foundingHeroBadge:'البطل المؤسس',foundingHeroBody:'شراء رقمي لمرة واحدة يضيف شارة البطل المؤسس ولمسة ذهبية لملفك.',foundingHeroScope:'شارة تجميلية فقط؛ لا تحجب التمارين أو الصحة، ولا تمنح أفضلية تنافسية أو توكنات أو عائدًا ماليًا.',foundingHeroLoading:'جارٍ التحقق من Google Play…',foundingHeroBuy:'احصل على الحزمة',foundingHeroRestore:'استعادة الشراء',foundingHeroOwned:'حزمة البطل المؤسس مفعلة على هذا الحساب.',foundingHeroPending:'عملية الشراء معلقة؛ ستتفعل الشارة بعد تأكيد Google Play.',foundingHeroUnavailable:'المنتج غير متاح في هذه النسخة بعد. لم يتم تحصيل أي مبلغ.',foundingHeroConfigure:'يلزم ربط مفتاح الترخيص العام ومنتج Play قبل إتاحة الشراء.',foundingHeroAndroidOnly:'متاح داخل نسخة Android المثبتة من Google Play.',foundingHeroCanceled:'تم إلغاء نافذة الشراء ولم يتم تحصيل مبلغ.'});
  Object.assign(COPY.en, {startSession:'Start session',saveNext:'Save and continue',finishSession:'Finish and save session',exerciseOf:'Exercise {current} of {total}',nextExercise:'Exercise saved. Next: {name}',sessionComplete:'Session complete and saved.',signInSync:'Sign in to sync',syncConnected:'Sync connected',syncConnecting:'Connecting account',offlineReady:'Offline ready',syncUnavailable:'Sync not configured',foundingHeroEyebrow:'One-time cosmetic pack',foundingHeroTitle:'Founding Hero',foundingHeroBadge:'Founding Hero',foundingHeroBody:'A one-time digital purchase that adds the Founding Hero badge and a gold profile accent.',foundingHeroScope:'Cosmetic badge only; workouts and Health remain free, with no competitive advantage, tokens, or financial return.',foundingHeroLoading:'Checking Google Play…',foundingHeroBuy:'Get the pack',foundingHeroRestore:'Restore purchase',foundingHeroOwned:'The Founding Hero pack is active for this account.',foundingHeroPending:'Purchase pending; the badge activates after Google Play confirms payment.',foundingHeroUnavailable:'This product is not available in this build yet. No charge was made.',foundingHeroConfigure:'Connect the public Play license key and Play product before enabling purchases.',foundingHeroAndroidOnly:'Available in the Android app installed through Google Play.',foundingHeroCanceled:'The purchase sheet was canceled and no charge was made.'});
  Object.assign(COPY.ar, {onboardingBrand:'خطتك تبدأ منك',onboardingStep:'إعداد سريع · يعمل أوفلاين',onboardingTitle:'ابنِ خطتك الأولى',onboardingIntro:'اختر هدفك وخبرتك وما يتوفر لديك. سنضع جلسة واضحة في «اليوم» ويمكنك تعديل كل شيء لاحقًا.',onboardingBenefitOffline:'دليل مصور أوفلاين',onboardingBenefitSafe:'تدرج وتعليمات سلامة',onboardingBenefitFlexible:'تعديل الخطة في أي وقت',onboardingPrivacy:'يُحفظ هذا الاختيار على جهازك أولًا. لا يلزم حساب للبدء.',createMyPlan:'أنشئ خطتي وابدأ',planReady:'خطتك جاهزة. ابدأ من جلسة اليوم.'});
  Object.assign(COPY.en, {onboardingBrand:'Your plan starts with you',onboardingStep:'Quick setup · works offline',onboardingTitle:'Build your first plan',onboardingIntro:'Choose your goal, experience and available equipment. We will put one clear session in Today, and you can change everything later.',onboardingBenefitOffline:'Offline visual guidance',onboardingBenefitSafe:'Safe progression and cues',onboardingBenefitFlexible:'Change your plan anytime',onboardingPrivacy:'Your choices are saved on this device first. No account is required to begin.',createMyPlan:'Create my plan and start',planReady:'Your plan is ready. Start with Today.'});
  Object.assign(COPY.ar, {accountPrivacyHint:'تستطيع مراجعة السياسة وبدء حذف بيانات حساب THF Fitness من المتصفح الآمن.',privacyPolicy:'سياسة الخصوصية',accountDeletion:'حذف بيانات الحساب',accountResourceAndroidOnly:'هذا الرابط متاح داخل تطبيق Android.'});
  Object.assign(COPY.en, {accountPrivacyHint:'Review the policy or start deleting your THF Fitness account data in the secure browser.',privacyPolicy:'Privacy policy',accountDeletion:'Delete account data',accountResourceAndroidOnly:'This link is available in the Android app.'});
  Object.assign(COPY.ar, {readinessToday:'جاهزية اليوم',todaySummary:'ملخص اليوم',trainContentType:'نوع محتوى التدريب',programSections:'أقسام البرامج',clearSearch:'مسح البحث',trainingSections:'أقسام التدريب',volumeChartLabel:'مخطط حجم التدريب',onboardingBenefitsLabel:'مزايا الخطة',close:'إغلاق'});
  Object.assign(COPY.en, {readinessToday:"Today's readiness",todaySummary:"Today's summary",trainContentType:'Training content type',programSections:'Program sections',clearSearch:'Clear search',trainingSections:'Training sections',volumeChartLabel:'Training volume chart',onboardingBenefitsLabel:'Plan benefits',close:'Close'});
  Object.assign(COPY.ar, {sensorEvidence:'قياس الحركة',sensorVerified:'حساسات الهاتف',sensorWaiting:'بانتظار بيانات الحركة',stepsLive:'الخطوات',detectorEvents:'نبضات الخطوة',confidence:'الثقة',sensorSamples:'عينات الحركة',manualUnverified:'يدوي / غير موثق'});
  Object.assign(COPY.en, {sensorEvidence:'Motion evidence',sensorVerified:'Phone sensors',sensorWaiting:'Waiting for motion data',stepsLive:'Steps',detectorEvents:'Step events',confidence:'Confidence',sensorSamples:'Motion samples',manualUnverified:'Manual / unverified'});
  Object.assign(COPY.ar, {activityEyebrow:'نشاط فعلي بالخارج',activityQuickTitle:'ابدأ نشاطًا بـ GPS',activityQuickHint:'المشي والجري وركوب الدراجة جلسات مستقلة عن برامج التمارين، وتستمر في الخلفية بإشعار دائم.',activityTitle:'المشي والجري والدراجة',backgroundReady:'يستمر بالخلفية',walk:'مشي',run:'جري',cycle:'دراجة',gpsSteps:'GPS + خطوات',gpsSpeed:'GPS + سرعة',selectActivity:'اختر نشاطًا للبدء',gpsWaiting:'جارٍ تثبيت موقع عالي الدقة',gpsWeak:'تم تحديد الموقع — الدقة ضعيفة',gpsStale:'إشارة الموقع متوقفة',gpsOff:'الموقع مغلق',gpsRouteHint:'سيظهر مسارك الحقيقي هنا بعد أول نقاط GPS.',pace:'الوتيرة',speed:'السرعة',gpsAccuracy:'دقة GPS',live:'مباشر',activityBackgroundHint:'يمكنك قفل الشاشة أو فتح تطبيق آخر؛ الإشعار الدائم يؤكد أن الجلسة ما زالت تعمل.',stopAndSaveActivity:'إيقاف وحفظ النشاط',recentActivities:'آخر الأنشطة',backToday:'العودة لليوم',weightKg:'الوزن لحساب السعرات',activitySaved:'تم حفظ النشاط.',pauseActivity:'إيقاف مؤقت',resumeActivity:'استئناف',activityAutoPauseLeave:'إيقاف الجلسة مؤقتًا عند مغادرة شاشة النشاط',activityPermissionNeeded:'اسمح بالموقع وقياس النشاط لبدء التتبع.',activityRunning:'النشاط مستمر بالخلفية',impactPeak:'قمة التسارع',rotationPeak:'قمة الدوران',stability:'الثبات',motionSamplesShort:'عينات الحركة',stepEventsShort:'نبضات الخطوة'});
  Object.assign(COPY.en, {activityEyebrow:'Outdoor activity',activityQuickTitle:'Start a GPS activity',activityQuickHint:'Walking, running and cycling are independent activity sessions, separate from workout programs, and continue in the background with an ongoing notification.',activityTitle:'Walk, run and cycle',backgroundReady:'Background ready',walk:'Walk',run:'Run',cycle:'Cycle',gpsSteps:'GPS + steps',gpsSpeed:'GPS + speed',selectActivity:'Choose an activity to start',gpsWaiting:'Acquiring high-accuracy location',gpsWeak:'Location found — weak accuracy',gpsStale:'Location signal stalled',gpsOff:'Location is off',gpsRouteHint:'Your real GPS route will appear here after the first fixes.',pace:'Pace',speed:'Speed',gpsAccuracy:'GPS accuracy',live:'live',activityBackgroundHint:'You can lock the screen or open another app; the ongoing notification confirms tracking is still active.',stopAndSaveActivity:'Stop and save activity',recentActivities:'Recent activities',backToday:'Back to Today',weightKg:'Weight for calorie estimate',activitySaved:'Activity saved.',pauseActivity:'Pause',resumeActivity:'Resume',activityAutoPauseLeave:'Pause the session when leaving the activity screen',activityPermissionNeeded:'Allow location and activity access to start tracking.',activityRunning:'Activity continues in background',impactPeak:'Acceleration peak',rotationPeak:'Rotation peak',stability:'Stability',motionSamplesShort:'Motion samples',stepEventsShort:'Step events'});

  Object.assign(COPY.ar, {wellnessEyebrow:'العافية اليومية',wellnessTitle:'الماء والتغذية والعادات',wellnessLocal:'محلي على الجهاز',waterTitle:'الترطيب اليومي',waterGoalLabel:'هدف الماء (مل)',waterDisclaimer:'الاحتياج يختلف حسب النشاط والطقس والحالة الصحية؛ هذا سجل شخصي وليس وصفة طبية.',foodBalanceTitle:'توازن الطعام اليوم',vegetableServings:'حصص الخضروات',sweetServings:'حصص الحلويات',foodDisclaimer:'سجل اختياراتك للتوعية دون لوم أو حرمان أو تعويض الطعام بالتمرين.',cycleTrackerTitle:'متابعة الدورة الشهرية',lastPeriodStart:'أول يوم من آخر دورة',cycleLengthLabel:'طول الدورة المعتاد (21–45 يومًا)',nextPeriodEstimate:'موعد تقديري للدورة التالية',cycleDisclaimer:'تقدير تقريبي لا يؤكد التبويض أو يمنع الحمل ولا يشخّص حالة صحية.',habitTrackerTitle:'تغيير العادات بخطوات صغيرة',habitChoose:'اختر عادة للمتابعة',habitSleep:'النوم المنتظم',habitSmoking:'تقليل التدخين / الإقلاع',habitSugary:'تقليل المشروبات السكرية',habitSedentary:'تقليل الجلوس الطويل',habitLogToday:'سجل نجاح اليوم',wellnessPrivacy:'بيانات العافية والدورة محفوظة محليًا على هذا الجهاز في هذا السجل، ولا تُرسل إلى الحساب أو الخادم من هذه الشاشة.'});
  Object.assign(COPY.en, {wellnessEyebrow:'Daily wellness',wellnessTitle:'Hydration, food and habits',wellnessLocal:'Saved on device',waterTitle:'Daily hydration',waterGoalLabel:'Water goal (ml)',waterDisclaimer:'Needs vary with activity, weather and health status; this is a personal log, not medical advice.',foodBalanceTitle:'Today’s food balance',vegetableServings:'Vegetable servings',sweetServings:'Sweet servings',foodDisclaimer:'Log choices for awareness without guilt, restriction, or compensating for food with exercise.',cycleTrackerTitle:'Menstrual cycle tracker',lastPeriodStart:'First day of last period',cycleLengthLabel:'Usual cycle length (21–45 days)',nextPeriodEstimate:'Estimated next period',cycleDisclaimer:'A rough estimate; it does not confirm ovulation, prevent pregnancy or diagnose a health condition.',habitTrackerTitle:'Build habits in small steps',habitChoose:'Choose a habit to track',habitSleep:'Consistent sleep',habitSmoking:'Reduce / quit smoking',habitSugary:'Reduce sugary drinks',habitSedentary:'Break up long sitting',habitLogToday:'Log today as successful',wellnessPrivacy:'Wellness and cycle data in this tracker are saved locally on this device and are not sent to the account or server from this screen.'});

  const SECTION_ORDER = ['gym','home','running','cycling','football','swimming','yoga','calisthenics','boxing','hiit','mobility','recovery','team_sports'];
  const state = {
    lang: store.getItem('pulse.v2.lang') === 'en' ? 'en' : 'ar',
    trainMode: store.getItem('pulse.v2.trainMode') === 'exercises' ? 'exercises' : 'programs',
    programSection: 'all',
    section: 'gym',
    filters: {body:'',muscle:'',equipment:'',movement:'',level:'',goal:''},
    selected: null,
    selectedProgram: null,
    active: parse(store.getItem('pulse.v2.active'), null),
    restTick: null,
    demoFrame: 0,
    clearArmedUntil: 0,
    onboardingDraft: null,
    motionPoll: null,
    motionEvidence: null,
    activityPoll: null,
    activitySnapshot: null
  };
  const t = key => COPY[state.lang][key] || COPY.en[key] || key;

  function toast(message) {
    const node = $('toast'); node.textContent = message; node.classList.remove('hidden');
    clearTimeout(toast.timer); toast.timer = setTimeout(() => node.classList.add('hidden'), 2600);
  }

  function showScreen(id, updateNav = true) {
    document.querySelectorAll('.screen').forEach(node => node.classList.toggle('active', node.id === id));
    if (updateNav) document.querySelectorAll('#primaryNav button').forEach(button => {
      const active = button.dataset.screen === id; button.classList.toggle('active', active);
      if (active) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
    });
    $('primaryNav').classList.toggle('hidden', id === 'activeWorkoutScreen' || id === 'activityScreen');
    document.body.classList.toggle('workout-active', id === 'activeWorkoutScreen');
    const demoVideo = $('activeDemoVideo');
    if (id === 'activeWorkoutScreen' && !demoVideo.classList.contains('hidden')) demoVideo.play().catch(() => {});
    else demoVideo.pause();
    window.scrollTo({top: 0, behavior: 'smooth'});
    if (id === 'progressScreen') renderProgress();
    if (id === 'healthScreen') renderHealthStatus();
    if (id === 'activityScreen') { renderActivity(readActivitySnapshot()); startActivityPolling(); }
  }

  function applyLanguage() {
    document.documentElement.lang = state.lang; document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
    $('languageToggle').textContent = state.lang === 'ar' ? 'EN' : 'ع';
    $('languageToggle').setAttribute('aria-label', state.lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية');
    $('onboardingLanguageToggle').textContent = state.lang === 'ar' ? 'EN' : 'ع';
    $('onboardingLanguageToggle').setAttribute('aria-label', state.lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية');
    document.querySelectorAll('[data-i18n]').forEach(node => { node.textContent = t(node.dataset.i18n); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(node => { node.placeholder = t(node.dataset.i18nPlaceholder); });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(node => { node.setAttribute('aria-label', t(node.dataset.i18nAriaLabel)); });
    $('primaryNav').setAttribute('aria-label', state.lang === 'ar' ? 'التنقل الرئيسي' : 'Primary navigation');
    renderTrainMode(); renderSections(); renderProgramSections(); populateFilters(); renderExercises(); renderPrograms(); renderToday(); renderProgress(); renderProfile(); renderOnboarding(); renderNativeStatus(); renderFoundingHero(); if (typeof renderWellness === 'function') renderWellness();
    if (state.selected) renderDetail(state.selected);
    if (state.selectedProgram) renderProgramDetail(state.selectedProgram);
    if (state.active) renderActiveWorkout();
  }

  function sectionSummary(id) {
    const items = EXERCISES.filter(item => item.section.id === id);
    return {id, items, label: items.length ? local(items[0].section) : id};
  }

  function renderSections() {
    $('sectionRail').innerHTML = SECTION_ORDER.map(id => {
      const section = sectionSummary(id); const selected = id === state.section;
      return `<button type="button" role="tab" data-section="${escapeHtml(id)}" aria-selected="${selected}">${escapeHtml(section.label)} <small>${section.items.length}</small></button>`;
    }).join('');
    $('sectionRail').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      state.section = button.dataset.section; resetFilters(false); renderSections(); populateFilters(); renderExercises();
    }));
    const section = sectionSummary(state.section);
    $('resultsTitle').textContent = section.label;
    $('gymIntro').classList.toggle('hidden', state.section !== 'gym');
  }

  function renderTrainMode() {
    const programsActive = state.trainMode === 'programs';
    $('programsPane').classList.toggle('hidden', !programsActive);
    $('exerciseLibraryPane').classList.toggle('hidden', programsActive);
    $('programsPane').setAttribute('aria-hidden', String(!programsActive));
    $('exerciseLibraryPane').setAttribute('aria-hidden', String(programsActive));
    document.querySelectorAll('#trainModeTabs button').forEach(button => {
      const active = button.dataset.mode === state.trainMode;
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
    });
  }

  function renderProgramSections() {
    const sections = [{id:'all', label:t('all'), count:PROGRAMS.length}].concat(SECTION_ORDER.map(id => {
      const summary = sectionSummary(id);
      return {id, label:summary.label, count:PROGRAMS.filter(program => program.section.id === id).length};
    }));
    $('programSectionRail').innerHTML = sections.map(section => `<button type="button" role="tab" data-section="${escapeHtml(section.id)}" aria-selected="${section.id === state.programSection}">${escapeHtml(section.label)} <small>${section.count}</small></button>`).join('');
    $('programSectionRail').querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      state.programSection = button.dataset.section; renderProgramSections(); renderPrograms();
    }));
  }

  function exerciseFor(reference) { return EXERCISES.find(item => item.id === reference.exerciseId); }

  function renderPrograms() {
    const results = PROGRAMS.filter(program => state.programSection === 'all' || program.section.id === state.programSection);
    $('programCount').textContent = String(PROGRAMS.length);
    $('emptyPrograms').classList.toggle('hidden', results.length > 0);
    $('programGrid').innerHTML = results.map(program => {
      const firstExercise = exerciseFor(program.sessions[0].exercises[0]);
      const image = firstExercise?.demo?.assets?.[0] || '';
      return `<button class="program-card" type="button" data-program="${escapeHtml(program.id)}"><span class="program-cover">${image?`<img src="./${escapeHtml(image)}" alt="">`:''}<span class="program-duration">${program.weeks} ${escapeHtml(t('weeks'))}</span></span><span class="program-copy"><span class="pill gold">${escapeHtml(local(program.section))}</span><h3>${escapeHtml(local(program.name))}</h3><p>${escapeHtml(local(program.summary))}</p><span class="program-meta"><b>${program.daysPerWeek}</b> ${escapeHtml(t('daysWeekly'))} · <b>${program.estimatedSessionMinutes}</b> ${escapeHtml(t('min'))}</span><span class="tag-row"><span class="tag">${escapeHtml(local(program.level))}</span><span class="tag">${escapeHtml(local(program.goal))}</span><span class="tag">✓ ${escapeHtml(t('offline'))}</span></span></span></button>`;
    }).join('');
    $('programGrid').querySelectorAll('.program-card').forEach(card => card.addEventListener('click', () => openProgramDetail(card.dataset.program)));
  }

  function openProgramDetail(id) {
    state.selectedProgram = PROGRAMS.find(program => program.id === id); if (!state.selectedProgram) return;
    renderProgramDetail(state.selectedProgram); $('programDetail').classList.remove('hidden'); document.body.style.overflow = 'hidden'; $('programDetailCloseButton').focus();
  }

  function closeProgramDetail() { $('programDetail').classList.add('hidden'); document.body.style.overflow = ''; }

  function prescriptionText(reference) {
    const dose = reference.durationSeconds ? `${reference.sets} × ${reference.durationSeconds}s` : `${reference.sets} × ${reference.reps || '—'}`;
    return `${dose} · ${reference.restSeconds}s ${t('rest')} · RPE ${reference.targetRpe} · RIR ${reference.targetRir}`;
  }

  function renderProgramDetail(program) {
    $('programDetailSection').textContent = local(program.section); $('programDetailName').textContent = local(program.name); $('programDetailSummary').textContent = local(program.summary);
    $('programDetailMeta').innerHTML = `<span class="tag">${program.weeks} ${escapeHtml(t('weeks'))}</span><span class="tag">${program.daysPerWeek} ${escapeHtml(t('daysWeekly'))}</span><span class="tag">${program.estimatedSessionMinutes} ${escapeHtml(t('min'))}</span><span class="tag">${escapeHtml(local(program.level))}</span><span class="tag">✓ ${escapeHtml(t('offline'))}</span>`;
    $('programSessions').innerHTML = `<div class="results-heading"><h2>${escapeHtml(t('programSessions'))}</h2><span class="count-badge">${program.sessions.length}</span></div>` + program.sessions.map((session,index) => `<article class="program-session"><div class="card-heading"><div><p class="eyebrow">${escapeHtml(t('session'))} ${index+1}</p><h3>${escapeHtml(local(session.name))}</h3></div><div class="program-session-actions"><span class="count-badge">${session.exercises.length} ${escapeHtml(t('exerciseCount'))}</span><button class="button secondary compact" type="button" data-start-program="${escapeHtml(program.id)}" data-start-session="${escapeHtml(session.id)}">${escapeHtml(t('startSession'))}</button></div></div><div class="session-exercises">${session.exercises.map(reference => { const exercise=exerciseFor(reference); return exercise?`<button type="button" data-exercise="${escapeHtml(exercise.id)}"><span><b>${escapeHtml(local(exercise.name))}</b><small>${escapeHtml(prescriptionText(reference))}</small></span><span aria-hidden="true">›</span></button>`:''; }).join('')}</div></article>`).join('');
    $('programSessions').querySelectorAll('[data-exercise]').forEach(button => button.addEventListener('click', () => { const id=button.dataset.exercise; closeProgramDetail(); openDetail(id); }));
    $('programSessions').querySelectorAll('[data-start-program]').forEach(button => button.addEventListener('click', () => startProgramSession(button.dataset.startProgram, button.dataset.startSession)));
    $('programProgression').innerHTML = program.progression[state.lang].map(step => `<li>${escapeHtml(step)}</li>`).join('');
    $('programSafety').textContent = local(program.safety); $('programSource').textContent = t('programSource'); $('useProgramBtn').dataset.program = program.id;
  }

  function useProgram(id) {
    const program = PROGRAMS.find(item => item.id === id); if (!program) return;
    store.setItem('pulse.v2.program', JSON.stringify({programId:id, sessionIndex:0, selectedAt:new Date().toISOString()}));
    closeProgramDetail(); renderToday(); showScreen('todayScreen'); toast(t('programSelected'));
  }

  function uniqueOptions(items, getter, labeler) {
    const map = new Map();
    items.forEach(item => { const value = getter(item); if (value) map.set(value, labeler(item, value)); });
    return [...map.entries()].sort((a,b) => a[1].localeCompare(b[1], locale()));
  }

  function setOptions(node, options, current) {
    node.innerHTML = `<option value="">${escapeHtml(t('all'))}</option>` + options.map(([value,label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join('');
    node.value = current;
  }

  function populateFilters() {
    const items = EXERCISES.filter(item => item.section.id === state.section);
    setOptions($('bodyFilter'), uniqueOptions(items, item=>item.bodyPart, (item,value)=>item.muscles.primary.en.indexOf(value)>=0 ? item.muscles.primary[state.lang][item.muscles.primary.en.indexOf(value)] : value), state.filters.body);
    const muscleMap = new Map(); items.forEach(item => item.muscles.primary.en.concat(item.muscles.secondary.en).forEach((value,index) => { const allEn=item.muscles.primary.en.concat(item.muscles.secondary.en), allLocal=item.muscles.primary[state.lang].concat(item.muscles.secondary[state.lang]); muscleMap.set(value, allLocal[allEn.indexOf(value)] || value); }));
    setOptions($('muscleFilter'), [...muscleMap.entries()].sort((a,b)=>a[1].localeCompare(b[1],locale())), state.filters.muscle);
    setOptions($('equipmentFilter'), uniqueOptions(items,item=>item.equipment.id,item=>local(item.equipment)), state.filters.equipment);
    setOptions($('movementFilter'), uniqueOptions(items,item=>item.movement.id,item=>local(item.movement)), state.filters.movement);
    setOptions($('levelFilter'), uniqueOptions(items,item=>item.level.id,item=>local(item.level)), state.filters.level);
    setOptions($('goalFilter'), uniqueOptions(items,item=>item.goal.id,item=>local(item.goal)), state.filters.goal);
  }

  function matches(item) {
    const query = $('exerciseSearch').value.trim().toLocaleLowerCase(locale());
    const haystack = [item.name.en,item.name.ar,item.equipment.en,item.equipment.ar,...item.muscles.primary.en,...item.muscles.primary.ar,...item.muscles.secondary.en,...item.muscles.secondary.ar].join(' ').toLocaleLowerCase(locale());
    return item.section.id === state.section && (!query || haystack.includes(query)) &&
      (!state.filters.body || item.bodyPart === state.filters.body) &&
      (!state.filters.muscle || item.muscles.primary.en.includes(state.filters.muscle) || item.muscles.secondary.en.includes(state.filters.muscle)) &&
      (!state.filters.equipment || item.equipment.id === state.filters.equipment) &&
      (!state.filters.movement || item.movement.id === state.filters.movement) &&
      (!state.filters.level || item.level.id === state.filters.level) &&
      (!state.filters.goal || item.goal.id === state.filters.goal);
  }

  function motionAsset(item) {
    const entry = motionManifest[item?.id];
    const supported = entry && (entry.kind === 'offline_video' || entry.kind === 'verified_frame_sequence');
    return supported && typeof entry.asset === 'string' && /^media\/motion\/[a-z0-9-]+\.(?:mp4|webm)$/i.test(entry.asset) ? entry : null;
  }
  function referenceCoverageLabel(item, compact = false) {
    if (state.lang === 'ar') return compact ? 'صور مرجعية متحركة' : 'صور مرجعية متحركة تلقائيًا · الفيديو قريبًا';
    return compact ? 'Animated refs' : 'Auto-animated reference frames · video coming soon';
  }
  function motionCoverageLabel(item, compact = false) {
    const entry = motionAsset(item);
    if (entry?.kind === 'offline_video') return state.lang === 'ar' ? 'فيديو أوفلاين' : 'Offline video';
    if (entry?.kind === 'verified_frame_sequence') return state.lang === 'ar' ? 'مقطع إطارات موثّق' : 'Verified frame-sequence clip';
    return referenceCoverageLabel(item, compact);
  }
  function referenceMotionPlayer(item, context = 'detail') {
    const assets = Array.isArray(item?.demo?.assets) ? item.demo.assets.slice(0, 2) : [];
    const safeAssets = assets.length === 2 && assets.every(asset => typeof asset === 'string' && /^media\/free-exercise-db\/[A-Za-z0-9_/-]+\.jpg$/i.test(asset));
    if (!safeAssets) return `<div class="motion-placeholder" role="img" aria-label="${escapeHtml(state.lang === 'ar' ? 'العرض المصوّر غير متاح' : 'Exercise demonstration unavailable')}"><strong>${escapeHtml(state.lang === 'ar' ? 'العرض غير متاح' : 'Demonstration unavailable')}</strong></div>`;
    const alt = escapeHtml(local(item.demo?.alt) || local(item.name));
    const className = context === 'card' ? 'exercise-reference-motion-card' : 'exercise-reference-motion-detail';
    return `<div class="exercise-reference-motion ${className}" role="img" aria-label="${alt}"><img src="./${escapeHtml(assets[0])}" alt="" aria-hidden="true"><img src="./${escapeHtml(assets[1])}" alt="" aria-hidden="true"></div>`;
  }
  function motionPlayer(item, context = 'detail') {
    const entry = motionAsset(item);
    if (!entry) return referenceMotionPlayer(item, context);
    const asset = `./${escapeHtml(entry.asset)}`;
    const poster = item.demo?.assets?.[0] ? ` poster="./${escapeHtml(item.demo.assets[0])}"` : '';
    const label = escapeHtml(local(item.demo?.alt) || local(item.name));
    const reduced = document.documentElement.classList.contains('motion-reduced');
    const controls = context === 'detail' ? 'controls' : '';
    const autoplay = reduced ? '' : 'autoplay';
    const preload = context === 'card' ? 'none' : 'metadata';
    const type = entry.asset.toLowerCase().endsWith('.webm') ? 'video/webm' : 'video/mp4';
    return `<video class="exercise-motion ${context === 'card' ? 'exercise-motion-card' : 'exercise-motion-detail'}" data-exercise-id="${escapeHtml(item.id)}" data-context="${context}" data-clip-limit="6" ${controls} ${autoplay} muted playsinline loop preload="${preload}"${poster} aria-label="${label}"><source src="${asset}" type="${type}"></video>`;
  }
  function motionCredit(item) {
    const entry = motionAsset(item);
    if (!entry || entry.kind !== 'offline_video' || !entry.sourceUrl || !entry.licenseUrl) return '';
    const sourceLabel = state.lang === 'ar' ? 'المصدر' : 'source';
    const licenseLabel = state.lang === 'ar' ? 'ترخيص CC BY-SA 4.0' : 'CC BY-SA 4.0 license';
    return `<p id="detailMotionCredit" class="motion-credit small muted">${state.lang === 'ar' ? 'مصدر الفيديو:' : 'Video source:'} ${escapeHtml(entry.author || '')} · <a href="${escapeHtml(entry.sourceUrl)}" target="_blank" rel="noopener noreferrer">${sourceLabel}</a> · <a href="${escapeHtml(entry.licenseUrl)}" target="_blank" rel="noopener noreferrer">${licenseLabel}</a></p>`;
  }
  function bindDemoClipLimits(root) {
    root.querySelectorAll('video[data-clip-limit]').forEach(video => {
      if (video.dataset.clipLimitBound === '1') return;
      video.dataset.clipLimitBound = '1';
      video.addEventListener('error', () => {
        const item = EXERCISES.find(candidate => candidate.id === video.dataset.exerciseId);
        if (!item) return;
        const context = video.dataset.context === 'card' ? 'card' : 'detail';
        const mediaContainer = video.closest('.media');
        const cardBadge = mediaContainer?.querySelector('.offline-badge');
        const detailBadge = context === 'detail' ? $('detailBadges')?.querySelector('.demo-coverage-badge') : null;
        const template = document.createElement('template');
        template.innerHTML = referenceMotionPlayer(item, context);
        const fallback = template.content.firstElementChild;
        if (fallback) video.replaceWith(fallback);
        if (cardBadge) cardBadge.textContent = motionCoverageLabel(item, true);
        if (detailBadge) detailBadge.textContent = motionCoverageLabel(item);
        if (context === 'detail') $('detailMotionCredit')?.classList.add('hidden');
      }, {once:true});
      video.addEventListener('timeupdate', () => {
        const limit = Number(video.dataset.clipLimit) || 6;
        if (Number.isFinite(video.duration) && video.duration > limit && video.currentTime >= limit) {
          video.currentTime = 0;
          if (!video.paused && !document.documentElement.classList.contains('motion-reduced')) video.play().catch(() => {});
        }
      });
    });
  }
  function renderExercises() {
    if (!EXERCISES.length) { $('exerciseGrid').innerHTML = `<p class="error-message">${escapeHtml(t('noCatalog'))}</p>`; return; }
    const results = EXERCISES.filter(matches);
    $('resultsCount').textContent = String(results.length);
    $('emptyResults').classList.toggle('hidden', results.length > 0);
    $('activeFilterCount').textContent = String(Object.values(state.filters).filter(Boolean).length);
    $('exerciseGrid').innerHTML = results.map(item => `<button class="exercise-card" type="button" data-id="${escapeHtml(item.id)}"><span class="media">${motionPlayer(item, 'card')}<span class="offline-badge">${escapeHtml(motionCoverageLabel(item, true))}</span></span><span class="copy"><span class="pill">${escapeHtml(local(item.section))}</span><h3>${escapeHtml(local(item.name))}</h3><span class="meta">${escapeHtml(local(item.muscles.primary))} · ${escapeHtml(local(item.equipment))}</span><span class="tag-row"><span class="tag">${escapeHtml(local(item.level))}</span><span class="tag">${escapeHtml(local(item.movement))}</span></span></span></button>`).join('');
    bindDemoClipLimits($('exerciseGrid'));
    $('exerciseGrid').querySelectorAll('.exercise-card').forEach(card => card.addEventListener('click', () => openDetail(card.dataset.id)));
  }

  function resetFilters(render = true) {
    state.filters = {body:'',muscle:'',equipment:'',movement:'',level:'',goal:''}; $('exerciseSearch').value = '';
    if (render) { populateFilters(); renderExercises(); }
  }

  function openDetail(id) {
    state.selected = EXERCISES.find(item => item.id === id); if (!state.selected) return;
    renderDetail(state.selected); $('exerciseDetail').classList.remove('hidden'); document.body.style.overflow = 'hidden'; $('detailCloseButton').focus();
  }
  function closeDetail() { $('exerciseDetail').classList.add('hidden'); document.body.style.overflow = ''; }
  function list(items, ordered = false) { const tag = ordered ? 'ol' : 'ul'; return `<${tag}>${items.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</${tag}>`; }
  function renderDetail(item) {
    $('detailDemo').innerHTML = motionPlayer(item, 'detail') + motionCredit(item);
    bindDemoClipLimits($('detailDemo'));
    $('detailBadges').innerHTML = `<span class="pill gold">${escapeHtml(local(item.section))}</span><span class="pill">✓ ${escapeHtml(t('offline'))}</span><span class="pill demo-coverage-badge">${escapeHtml(motionCoverageLabel(item))}</span><span class="pill">${escapeHtml(local(item.level))}</span>`;
    $('detailName').textContent = local(item.name); $('detailMeta').textContent = `${local(item.equipment)} · ${local(item.movement)} · ${local(item.goal)}`;
    $('detailMuscles').innerHTML = item.muscles.primary[state.lang].concat(item.muscles.secondary[state.lang]).map(value => `<span class="tag">${escapeHtml(value)}</span>`).join('');
    const prescription = item.prescription; const dose = prescription.durationSeconds ? `${prescription.sets} × ${prescription.durationSeconds} sec` : `${prescription.sets} × ${prescription.reps} · ${prescription.restSeconds} sec`;
    $('detailContent').innerHTML = `<section class="detail-section"><h3>${escapeHtml(t('setup'))}</h3><p>${escapeHtml(local(item.setup))}</p></section><section class="detail-section"><h3>${escapeHtml(t('technique'))}</h3>${list(item.steps[state.lang],true)}</section><section class="detail-section"><h3>${escapeHtml(t('breathing'))}</h3><p>${escapeHtml(local(item.breathing))}</p></section><section class="detail-section"><h3>${escapeHtml(t('defaults'))}</h3><p>${escapeHtml(dose)} · ${escapeHtml(prescription.tempo)}</p></section><section class="detail-section"><h3>${escapeHtml(t('mistakes'))}</h3>${list(item.commonMistakes[state.lang])}</section><section class="detail-section"><h3>${escapeHtml(t('regression'))}</h3><p>${escapeHtml(local(item.regression))}</p><h3>${escapeHtml(t('progression'))}</h3><p>${escapeHtml(local(item.progression))}</p></section><section class="detail-section safety-card"><h3>${escapeHtml(t('safety'))}</h3><p>${escapeHtml(local(item.safety))}</p></section>`;
    $('detailSource').textContent = `${t('sourceText')} · ${item.provenance.commit.slice(0,12)} · ${item.provenance.sourcePath}`;
  }

  function makeSets(item) {
    const sets = []; const count = Math.max(1, Number(item.prescription.sets) || 1); const tracked = item.tracking.load;
    if (item.prescription.setTypes.includes('warmup') && tracked) sets.push({type:'warmup',load:0,reps:item.prescription.reps ? 8 : 0,rpe:4,rir:5,restSeconds:item.prescription.restSeconds||60,complete:false});
    for (let index=0;index<count;index++) sets.push({type:'working',load:0,reps:item.prescription.reps ? Number(String(item.prescription.reps).split(/[–-]/)[0]) || 8 : 0,rpe:7,rir:3,restSeconds:item.prescription.restSeconds||60,complete:false});
    return sets;
  }
  function makeProgramSets(reference,item) {
    const reps=reference.durationSeconds?0:(Number(String(reference.reps||'').split(/[–-]/)[0])||0);
    return Array.from({length:Math.max(1,Number(reference.sets)||1)},()=>({type:reference.role==='warmup'?'warmup':'working',load:0,reps,rpe:reference.targetRpe,rir:reference.targetRir,restSeconds:reference.restSeconds||60,durationSeconds:reference.durationSeconds||null,complete:false}));
  }
  function makeClientId() { return 'thf-v2-' + (globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`); }
  function sensorProfileForExercise(item) {
    const movement=String(item?.movement?.id||'').toLowerCase(), category=String(item?.category||'').toLowerCase();
    if(movement.includes('jump')||movement.includes('hop')||category.includes('plyometric'))return 'impact_jump';
    if(movement.includes('isometric')||movement.includes('hold')||movement.includes('plank'))return 'static_hold';
    if(movement==='step'||movement.includes('step-up')||movement.includes('step drill')||category.includes('agility-step'))return 'step_drill';
    return 'form_motion';
  }
  function beginNativeMotionSession(sessionId, profile) {
    if (!N || typeof N.beginMotionSession !== 'function') return {active:false,error:'ANDROID_ONLY'};
    try { return parse(N.beginMotionSession(sessionId, profile), {active:false}); } catch { return {active:false,error:'MOTION_START_FAILED'}; }
  }
  function readMotionSnapshot() {
    if (!N || typeof N.motionSnapshot !== 'function') return {available:false};
    try { return parse(N.motionSnapshot(), {available:false}); } catch { return {available:false}; }
  }
  function endNativeMotionSession() {
    if (!N || typeof N.endMotionSession !== 'function') return {available:false};
    try { return parse(N.endMotionSession(), {available:false}); } catch { return {available:false}; }
  }
  function renderMotionEvidence(evidence=readMotionSnapshot()) {
    state.motionEvidence=evidence;
    const panel=$('motionEvidencePanel'); if(!panel)return evidence;
    const available=Boolean(evidence?.available), profile=state.active?.sensorProfile||sensorProfileForExercise(activeExercise());
    const source=$('motionSourceBadge');
    source.textContent=available?t('sensorVerified'):t('sensorWaiting');
    source.classList.toggle('gold',available);
    let primaryLabel=t('motionSamplesShort'), primaryValue=Number(evidence?.accelerometerSampleCount||0);
    let secondaryLabel=t('rotationPeak'), secondaryValue=Number(evidence?.gyroscopeMagnitudePeak||0).toFixed(2);
    if(profile==='step_drill'){primaryLabel=t('stepsLive');primaryValue=Number(evidence?.stepDelta||0);secondaryLabel=t('stepEventsShort');secondaryValue=Number(evidence?.stepDetectorCount||0);}
    else if(profile==='impact_jump'){primaryLabel=t('impactPeak');primaryValue=`${(Number(evidence?.accelerometerMagnitudePeak||0)/9.80665).toFixed(2)} g`;secondaryLabel=t('rotationPeak');secondaryValue=`${Number(evidence?.gyroscopeMagnitudePeak||0).toFixed(2)} rad/s`;}
    else if(profile==='static_hold'){const variance=Math.max(0,Number(evidence?.accelerometerMagnitudeVariance||0));primaryLabel=t('stability');primaryValue=`${Math.round(100/(1+variance)*100)/100}%`;secondaryLabel=t('motionSamplesShort');secondaryValue=Number(evidence?.accelerometerSampleCount||0);}
    $('motionPrimaryMetricLabel').textContent=primaryLabel;$('motionPrimaryMetricValue').textContent=String(primaryValue);
    $('motionSecondaryMetricLabel').textContent=secondaryLabel;$('motionSecondaryMetricValue').textContent=String(secondaryValue);
    $('motionConfidence').textContent=`${Math.round(Math.max(0,Math.min(1,Number(evidence?.localConfidence||0)))*100)}%`;
    const samples=Number(evidence?.accelerometerSampleCount||0)+Number(evidence?.gyroscopeSampleCount||0);
    $('motionSensorDetail').textContent=available?`${profile} · ${t('sensorSamples')}: ${samples} · accel ${Number(evidence?.accelerometerSampleCount||0)} · gyro ${Number(evidence?.gyroscopeSampleCount||0)}`:t('sensorWaiting');
    return evidence;
  }
  function startMotionPolling() {
    stopMotionPolling();
    renderMotionEvidence();
    state.motionPoll=setInterval(()=>{if(state.active)renderMotionEvidence();},1000);
  }
  function stopMotionPolling() { if(state.motionPoll){clearInterval(state.motionPoll);state.motionPoll=null;} }
  function startExercise(item) {
    const clientRecordId=makeClientId(),sensorProfile=sensorProfileForExercise(item),motionSessionId=`${clientRecordId}:0:${item.id}`;
    state.active = {clientRecordId,exerciseId:item.id,startedAt:Date.now(),sets:makeSets(item),sensorProfile,motionSessionId}; state.demoFrame=0;
    store.setItem('pulse.v2.active', JSON.stringify(state.active)); closeDetail();
    beginNativeMotionSession(motionSessionId,sensorProfile); startMotionPolling(); renderActiveWorkout(); showScreen('activeWorkoutScreen', false); speakExercise(item);
  }
  function startProgramSession(programId,sessionId) {
    const program=PROGRAMS.find(value=>value.id===programId);const sessionIndex=program?.sessions.findIndex(value=>value.id===sessionId)??-1;const session=program?.sessions[sessionIndex];const reference=session?.exercises[0];const item=reference?exerciseFor(reference):null;if(!program||!session||!item)return;
    const now=Date.now();store.setItem('pulse.v2.program',JSON.stringify({programId:program.id,sessionIndex,selectedAt:new Date(now).toISOString()}));
    const clientRecordId=makeClientId(),sensorProfile=sensorProfileForExercise(item),motionSessionId=`${clientRecordId}:0:${item.id}`;
    state.active={clientRecordId,exerciseId:item.id,startedAt:now,sets:makeProgramSets(reference,item),programId:program.id,programSessionId:session.id,programSessionIndex:sessionIndex,programExerciseIndex:0,programStartedAt:now,programEntries:[],sensorProfile,motionSessionId};state.demoFrame=0;
    persistActive();closeProgramDetail();closeDetail();beginNativeMotionSession(motionSessionId,sensorProfile);startMotionPolling();renderActiveWorkout();showScreen('activeWorkoutScreen',false);speakExercise(item);
  }
  function activeExercise() { return EXERCISES.find(item => item.id === state.active?.exerciseId); }
  function speakExercise(item, options) {
    if (!item) return false;
    return voiceGuidance.speak({
      name: local(item.name),
      setup: local(item.setup),
      steps: item.steps?.[state.lang] || [],
      breathing: local(item.breathing),
      safety: local(item.safety),
    }, state.lang, options);
  }
  function completedVolume(sets) { return (sets||[]).filter(set=>set.complete).reduce((sum,set)=>sum + Math.max(0,Number(set.load)||0)*Math.max(0,Number(set.reps)||0),0); }
  function sessionVolume() { return completedVolume(state.active?.sets) + (state.active?.programEntries||[]).reduce((sum,entry)=>sum+completedVolume(entry.sets),0); }
  function persistActive() { store.setItem('pulse.v2.active', JSON.stringify(state.active)); }
  function fallbackActiveMotion(item, expectedSource) {
    const video = $('activeDemoVideo');
    if (!item || state.active?.exerciseId !== item.id
        || video.dataset.exerciseId !== item.id
        || video.getAttribute('src') !== expectedSource) return false;
    failedMotionExerciseIds.add(item.id);
    if (activeMotionErrorHandler) video.removeEventListener('error', activeMotionErrorHandler);
    activeMotionErrorHandler = null;
    renderActiveMotion(item);
    return true;
  }
  function renderActiveMotion(item) {
    const video = $('activeDemoVideo');
    const image = $('activeDemoImage');
    const motion = motionManifest[item.id];
    if (motion?.asset && !failedMotionExerciseIds.has(item.id)) {
      const nextSource = './' + motion.asset;
      const sourceChanged = video.getAttribute('src') !== nextSource || video.dataset.exerciseId !== item.id;
      if (sourceChanged) {
        if (activeMotionErrorHandler) video.removeEventListener('error', activeMotionErrorHandler);
        activeMotionErrorHandler = () => fallbackActiveMotion(item, nextSource);
        video.addEventListener('error', activeMotionErrorHandler, {once:true});
        video.dataset.exerciseId = item.id;
        video.setAttribute('src', nextSource);
      }
      video.setAttribute('aria-label', local(item.demo?.alt) || local(item.name));
      video.classList.remove('hidden');
      image.classList.add('hidden');
      const credit = $('activeDemoCredit');
      const sourceLink = $('activeDemoSource');
      const licenseLink = $('activeDemoLicense');
      if (credit && sourceLink && licenseLink && motion.sourceUrl && motion.licenseUrl) {
        sourceLink.href = motion.sourceUrl;
        sourceLink.textContent = state.lang === 'ar' ? `مصدر الفيديو: ${motion.author || 'Goulart'}` : `Video source: ${motion.author || 'Goulart'}`;
        licenseLink.href = motion.licenseUrl;
        credit.classList.remove('hidden');
      } else {
        credit?.classList.add('hidden');
      }
      $('activeDemoPhase').textContent = state.lang === 'ar' ? 'حركة كاملة تلقائية' : 'Automatic full movement';
      if (!document.hidden) {
        const playback = video.play();
        if (playback && typeof playback.catch === 'function') playback.catch(() => fallbackActiveMotion(item, nextSource));
      }
      return;
    }
    if (activeMotionErrorHandler) video.removeEventListener('error', activeMotionErrorHandler);
    activeMotionErrorHandler = null;
    $('activeDemoCredit')?.classList.add('hidden');
    $('activeDemoSource')?.removeAttribute('href');
    $('activeDemoLicense')?.removeAttribute('href');
    video.pause();
    video.removeAttribute('src');
    video.load();
    video.classList.add('hidden');
    image.classList.remove('hidden');
    const referenceAssets = Array.isArray(item.demo?.assets) ? item.demo.assets : [];
    if (referenceAssets.length) image.src = './' + referenceAssets[0];
    else image.removeAttribute('src');
    image.alt = local(item.demo?.alt) || local(item.name);
    $('activeDemoPhase').textContent = state.lang === 'ar'
      ? (referenceAssets.length >= 2 ? 'صور مرجعية — حركة تلقائية' : 'العرض المصوّر غير متاح')
      : (referenceAssets.length >= 2 ? 'Reference images — automatic motion' : 'Demonstration unavailable');
  }
  function renderActiveWorkout() {
    const item = activeExercise(); if (!item) { state.active=null; store.removeItem('pulse.v2.active'); return; }
    $('activeWorkoutScreen').dataset.exerciseId = item.id;
    renderActiveMotion(item);
    const program=PROGRAMS.find(value=>value.id===state.active.programId);const programSession=program?.sessions.find(value=>value.id===state.active.programSessionId);const programIndex=Number(state.active.programExerciseIndex)||0;
    $('activeSection').textContent = programSession?`${local(program.section)} · ${t('exerciseOf').replace('{current}',programIndex+1).replace('{total}',programSession.exercises.length)}`:local(item.section); $('activeExerciseName').textContent = local(item.name);
    $('activeExerciseCue').textContent = local(item.setup); $('activeMuscles').innerHTML = item.muscles.primary[state.lang].map(value=>`<span class="tag">${escapeHtml(value)}</span>`).join('');
    $('activeSteps').innerHTML = item.steps[state.lang].map(step=>`<li>${escapeHtml(step)}</li>`).join(''); $('activeBreathing').textContent = local(item.breathing); $('activeSafety').textContent = local(item.safety);
    renderMotionEvidence(state.motionEvidence||readMotionSnapshot());
    const done = state.active.sets.filter(set=>set.complete).length; $('setProgressTitle').textContent = t('setProgress').replace('{done}',done).replace('{total}',state.active.sets.length); $('sessionVolume').textContent = `${Math.round(sessionVolume())} kg`;
    $('finishWorkoutBtn').textContent=programSession?(programIndex<programSession.exercises.length-1?t('saveNext'):t('finishSession')):t('finishWorkout');
    $('setRows').innerHTML = state.active.sets.map((set,index)=>`<div class="set-row${set.complete?' complete':''}" data-index="${index}"><span class="set-number"><b>${index+1}</b>${escapeHtml(t(set.type))}</span><label class="set-field"><span>${escapeHtml(t('load'))}</span><input class="set-input" data-field="load" inputmode="decimal" type="number" min="0" step="0.5" value="${Number(set.load)||0}" ${item.tracking.load?'':'disabled'} aria-label="${escapeHtml(t('load'))}"></label><label class="set-field"><span>${escapeHtml(t('reps'))}</span><input class="set-input" data-field="reps" inputmode="numeric" type="number" min="0" max="999" value="${Number(set.reps)||0}" aria-label="${escapeHtml(t('reps'))}"></label><label class="set-field"><span>RPE</span><input class="set-input" data-field="rpe" inputmode="decimal" type="number" min="1" max="10" step="0.5" value="${Number(set.rpe)||7}" aria-label="RPE"></label><label class="set-field"><span>RIR</span><input class="set-input" data-field="rir" inputmode="numeric" type="number" min="0" max="10" value="${Number(set.rir)||0}" ${item.tracking.rir?'':'disabled'} aria-label="RIR"></label><button class="set-complete" type="button" aria-label="${escapeHtml(t('completed'))}">${set.complete?'✓':'○'}</button></div>`).join('');
    $('setRows').querySelectorAll('.set-row').forEach(row => {
      row.querySelectorAll('input').forEach(input => input.addEventListener('input', () => {
        state.active.sets[Number(row.dataset.index)][input.dataset.field]=Number(input.value)||0;
        persistActive();
      }));
      row.querySelector('button').addEventListener('click', () => completeSet(Number(row.dataset.index)));
    });
  }
  function completeSet(index) {
    const set = state.active.sets[index]; set.complete = !set.complete; persistActive(); renderActiveWorkout();
    if (set.complete && index < state.active.sets.length-1) startRest(set.restSeconds || activeExercise().prescription.restSeconds || 60);
  }
  function startRest(seconds) {
    clearInterval(state.restTick);
    if(!state.active)return;
    state.active.restEndsAtMs=restTimer.deadline(seconds);persistActive();
    $('restPanel').classList.remove('hidden');renderRest();
    state.restTick=setInterval(renderRest,1000);
  }
  function renderRest(){
    const seconds=restTimer.remaining(state.active?.restEndsAtMs);
    $('restTimer').textContent=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
    if(seconds<=0)stopRest();
  }
  function stopRest(){
    clearInterval(state.restTick);state.restTick=null;
    if(state.active&&Object.prototype.hasOwnProperty.call(state.active,'restEndsAtMs')){delete state.active.restEndsAtMs;persistActive();}
    $('restPanel').classList.add('hidden');
  }
  function resumeRest(){
    if(!state.active||restTimer.remaining(state.active.restEndsAtMs)<=0){
      if(state.active?.restEndsAtMs){delete state.active.restEndsAtMs;persistActive();}
      $('restPanel').classList.add('hidden');return;
    }
    clearInterval(state.restTick);$('restPanel').classList.remove('hidden');renderRest();state.restTick=setInterval(renderRest,1000);
  }
  function addSet(){ state.active.sets.push({type:'working',load:0,reps:8,rpe:7,rir:3,restSeconds:activeExercise()?.prescription?.restSeconds||60,complete:false});persistActive();renderActiveWorkout(); }
  function finishWorkout() {
    const item=activeExercise();if(!item)return;const now=Date.now();const currentEntry={exerciseId:item.id,exerciseName:item.name,sport:item.sport,sets:state.active.sets.map((set,index)=>({...set,exerciseId:item.id,ordinal:index+1}))};const entries=[...(state.active.programEntries||[]),currentEntry];
    const program=PROGRAMS.find(value=>value.id===state.active.programId);const programSession=program?.sessions.find(value=>value.id===state.active.programSessionId);const programIndex=Number(state.active.programExerciseIndex)||0;
    if(program&&programSession&&programIndex<programSession.exercises.length-1){const completedMotion=endNativeMotionSession();stopMotionPolling();currentEntry.motionEvidence=completedMotion;const nextIndex=programIndex+1;const reference=programSession.exercises[nextIndex];const next=exerciseFor(reference);if(next){const sensorProfile=sensorProfileForExercise(next),motionSessionId=`${state.active.clientRecordId}:${nextIndex}:${next.id}`;state.active={...state.active,exerciseId:next.id,startedAt:now,sets:makeProgramSets(reference,next),programExerciseIndex:nextIndex,programEntries:[...(state.active.programEntries||[]),currentEntry],sensorProfile,motionSessionId};state.demoFrame=0;stopRest();persistActive();beginNativeMotionSession(motionSessionId,sensorProfile);startMotionPolling();renderActiveWorkout();speakExercise(next);toast(t('nextExercise').replace('{name}',local(next.name)));window.scrollTo({top:0,behavior:'smooth'});return;}}
    const allSets=entries.flatMap(entry=>entry.sets);const completedSets=allSets.filter(set=>set.complete);const volume=Math.round(completedSets.reduce((sum,set)=>sum+Math.max(0,Number(set.load)||0)*Math.max(0,Number(set.reps)||0),0));const title=program&&programSession?programSession.name:item.name;const startedAt=state.active.programStartedAt||state.active.startedAt;
    const motionEvidence=endNativeMotionSession();stopMotionPolling();currentEntry.motionEvidence=motionEvidence;
    const measurementSource=motionEvidence?.available&&motionEvidence.sessionId===state.active.motionSessionId?'SENSOR':'MANUAL_OR_UNVERIFIED';
    const summary={clientRecordId:state.active.clientRecordId,recordVersion:1,exercise:local(title),exerciseName:title,id:program?.id||item.id,sport:program?.section?.id||item.sport,programId:program?.id||null,programSessionId:programSession?.id||null,startedAtMs:startedAt,endedAtMs:now,date:new Date(now).toISOString(),durationMin:Math.max(1,Math.round((now-startedAt)/60000)),reps:completedSets.reduce((sum,set)=>sum+(Number(set.reps)||0),0),volumeKg:volume,sets:allSets,completed:true,steps:Number(motionEvidence?.stepDelta||0),motionEvidence,measurementSource};
    const history=parse(store.getItem('pulse.v2.history'),[]).filter(entry=>entry.clientRecordId!==summary.clientRecordId);history.push(summary);store.setItem('pulse.v2.history',JSON.stringify(history.slice(-200)));
    try { N?.saveSummary?.(JSON.stringify(summary)); } catch {}
    if(program&&programSession){const nextSession=(Number(state.active.programSessionIndex)+1)%program.sessions.length;store.setItem('pulse.v2.program',JSON.stringify({programId:program.id,sessionIndex:nextSession,selectedAt:new Date().toISOString()}));}
    state.active=null;store.removeItem('pulse.v2.active');stopRest();toast(programSession?t('sessionComplete'):t('saved'));renderToday();renderProgress();showScreen('progressScreen');
  }

  function history(){ return parse(store.getItem('pulse.v2.history'),[]); }
  function renderToday(){
    const profile=parse(store.getItem('pulse.v2.profile'),{goal:'general_fitness',level:'beginner',days:3,equipment:['body only']});
    const storedProgram=parse(store.getItem('pulse.v2.program'),null);
    const profileSection=profile.goal==='muscle_gain'||profile.goal==='strength'?'gym':profile.goal==='endurance'?'running':profile.goal==='mobility'?'mobility':'home';
    const program=PROGRAMS.find(item=>item.id===storedProgram?.programId) || PROGRAMS.find(item=>item.goal.id===profile.goal&&item.level.id===profile.level) || PROGRAMS.find(item=>item.section.id===profileSection&&item.level.id===profile.level) || PROGRAMS[0];
    const session=program?.sessions[Math.min(Number(storedProgram?.sessionIndex)||0,(program?.sessions.length||1)-1)];
    const suggested=session?exerciseFor(session.exercises[0]):(EXERCISES.find(item=>item.goal.id===profile.goal&&item.level.id===profile.level&&profile.equipment.includes(item.equipment.id)) || EXERCISES.find(item=>item.section.id==='home') || EXERCISES[0]);
    if(program&&session&&suggested){$('todayPlanTag').textContent=local(program.section);$('todayWorkoutName').textContent=local(session.name);$('todayWorkoutMeta').textContent=`${local(program.name)} · ${session.exercises.length} ${t('exerciseCount')} · ${session.estimatedMinutes} ${t('min')}`;$('startTodayBtn').dataset.exercise=suggested.id;$('startTodayBtn').dataset.program=program.id;$('startTodayBtn').dataset.session=session.id;}
    else if(suggested){$('todayPlanTag').textContent=local(suggested.section);$('todayWorkoutName').textContent=local(suggested.name);$('todayWorkoutMeta').textContent=`${t('profilePlan')} · ${local(suggested.level)} · ${suggested.prescription.sets} ${t('setsLabel')}`;$('startTodayBtn').dataset.exercise=suggested.id;}
    $('todayDate').textContent=new Intl.DateTimeFormat(locale(),{weekday:'short',day:'numeric',month:'short'}).format(new Date());
    const entries=history(), today=new Date().toISOString().slice(0,10), todays=entries.filter(entry=>(entry.date||'').startsWith(today));
    $('todaySessions').textContent=todays.length;$('todayMinutes').textContent=todays.reduce((sum,e)=>sum+(e.durationMin||0),0);$('todayVolume').textContent=Math.round(todays.reduce((sum,e)=>sum+(e.volumeKg||0),0));
    const days=[...new Set(entries.map(entry=>(entry.date||'').slice(0,10)).filter(Boolean))];let streak=0,cursor=new Date();for(let offset=0;offset<90;offset++){const key=cursor.toISOString().slice(0,10);if(days.includes(key))streak++;else if(offset>0)break;cursor.setDate(cursor.getDate()-1);}$('streak').textContent=streak;
    const weekStart=Date.now()-7*86400000,weekCount=entries.filter(entry=>new Date(entry.date).getTime()>=weekStart).length,target=Number(profile.days)||3;$('weekProgress').textContent=`${Math.min(weekCount,target)}/${target}`;$('weekProgressBar').style.width=`${Math.min(100,weekCount/target*100)}%`;
  }
  function renderProgress(){
    const entries=history(), totalVolume=entries.reduce((sum,e)=>sum+(e.volumeKg||0),0), prs=new Map();entries.forEach(entry=>(entry.sets||[]).forEach(set=>{const key=set.exerciseId||entry.id,load=Number(set.load)||0;if(load>(prs.get(key)||0))prs.set(key,load);}));
    $('totalWorkouts').textContent=entries.length;$('totalVolume').textContent=Math.round(totalVolume).toLocaleString(locale());$('prCount').textContent=[...prs.values()].filter(Boolean).length;$('activeMinutes').textContent=entries.reduce((sum,e)=>sum+(e.durationMin||0),0);
    const recent=entries.slice(-7),max=Math.max(1,...recent.map(e=>e.volumeKg||0));$('volumeChart').innerHTML=recent.length?recent.map(e=>`<i class="volume-bar" style="height:${Math.max(8,(e.volumeKg||0)/max*100)}%"><span>${Math.round(e.volumeKg||0)}</span></i>`).join(''):`<p class="muted">${escapeHtml(t('emptyHistory'))}</p>`;
    $('historyList').innerHTML=entries.length?entries.slice().reverse().slice(0,20).map(entry=>`<article class="history-item"><div><h3>${escapeHtml(entry.exerciseName?.[state.lang]||entry.exercise||entry.id)}</h3><p class="small muted">${new Date(entry.date).toLocaleString(locale())} · ${entry.durationMin||0} ${escapeHtml(t('min'))} · ${entry.sets?.filter(set=>set.complete).length||0} ${escapeHtml(t('setsLabel'))}</p><span class="pill ${entry.measurementSource==='SENSOR'?'gold':''}">${escapeHtml(entry.measurementSource==='SENSOR'?t('sensorVerified'):t('manualUnverified'))}</span></div><strong>${Math.round(entry.volumeKg||0)} kg</strong></article>`).join(''):`<p class="muted">${escapeHtml(t('emptyHistory'))}</p>`;
  }

  function nativeStatus(){try{return N?parse(N.status(),{}):{mode:'browser_preview',online:navigator.onLine,syncConfigured:false,health:{availability:'BROWSER_PREVIEW',connected:false},sessionSteps:0}}catch{return{mode:'offline',online:false,health:{availability:'ERROR',connected:false},sessionSteps:0}}}
  function currentBilling(){try{return N&&typeof N.billingStatus==='function'?parse(N.billingStatus(),{}):{configured:false,connected:false,loading:false,available:false,owned:false,pending:false,errorCode:'ANDROID_ONLY'}}catch{return{configured:false,connected:false,loading:false,available:false,owned:false,pending:false,errorCode:'BILLING_ERROR'}}}
  function renderFoundingHero(value=currentBilling()){
    const badge=$('foundingHeroBadge'),buy=$('foundingHeroPurchaseBtn'),restore=$('foundingHeroRestoreBtn'),price=$('foundingHeroPrice'),status=$('foundingHeroStatus');
    if(!badge||!buy||!restore||!price||!status)return;
    document.body.classList.toggle('founding-hero-owned',Boolean(value.owned));badge.classList.toggle('hidden',!value.owned);
    restore.disabled=Boolean(!N||value.loading);buy.disabled=true;price.textContent=value.price||'—';
    if(value.owned){buy.textContent=t('foundingHeroOwned');status.textContent=t('foundingHeroOwned');return;}
    if(value.pending){buy.textContent=t('foundingHeroPending');status.textContent=t('foundingHeroPending');return;}
    if(!N){buy.textContent=t('foundingHeroAndroidOnly');status.textContent=t('foundingHeroAndroidOnly');return;}
    if(!value.configured){buy.textContent=t('foundingHeroUnavailable');status.textContent=t('foundingHeroConfigure');return;}
    if(value.loading){buy.textContent=t('foundingHeroLoading');status.textContent=t('foundingHeroLoading');return;}
    if(value.available){buy.disabled=false;buy.textContent=value.price?`${t('foundingHeroBuy')} · ${value.price}`:t('foundingHeroBuy');status.textContent=value.errorCode==='PURCHASE_CANCELED'?t('foundingHeroCanceled'):t('foundingHeroScope');return;}
    buy.textContent=t('foundingHeroUnavailable');status.textContent=t('foundingHeroUnavailable');
  }
  function currentHealth(){try{return N?parse(N.healthStatus(),{}):nativeStatus().health}catch{return{availability:'ERROR',connected:false}}}
  function renderNativeStatus(){
    const value=nativeStatus(),chip=$('modeChip');
    $('nativeStatus').textContent=`${value.online?t('statusOnline'):t('statusOffline')} · ${value.mode||'offline_first'} · ${EXERCISES.length} ${t('exercises')}`;
    chip.disabled=Boolean(!N||value.syncAuthenticated||value.accountAuthPending||!value.syncConfigured||!value.accountAuthConfigured);
    chip.dataset.action=value.syncConfigured&&value.accountAuthConfigured&&!value.syncAuthenticated?'account-sign-in':'';
    chip.textContent=value.syncAuthenticated?t('syncConnected'):value.accountAuthPending?t('syncConnecting'):(value.syncConfigured&&value.accountAuthConfigured?t('signInSync'):(value.online?t('syncUnavailable'):t('offlineReady')));
    chip.setAttribute('aria-label',chip.textContent);
  }
  const WELLNESS_KEY = 'pulse.v2.wellness.local';
  function wellnessTodayKey(){const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
  function readWellness(){const today=wellnessTodayKey();const base={day:today,waterMl:0,waterGoalMl:2000,vegetables:0,sweets:0,periodStart:'',cycleLength:28,habit:'sleep',habitCheckIns:0};const saved=parse(store.getItem(WELLNESS_KEY),{});const merged={...base,...saved};if(merged.day!==today){merged.day=today;merged.waterMl=0;merged.vegetables=0;merged.sweets=0;merged.habitCheckIns=0;}merged.waterMl=Math.max(0,Math.min(10000,Number(merged.waterMl)||0));merged.waterGoalMl=Math.max(500,Math.min(6000,Number(merged.waterGoalMl)||2000));merged.vegetables=Math.max(0,Math.min(20,Number(merged.vegetables)||0));merged.sweets=Math.max(0,Math.min(20,Number(merged.sweets)||0));merged.cycleLength=Math.max(21,Math.min(45,Number(merged.cycleLength)||28));return merged;}
  let wellnessData=null;
  function saveWellness(patch={}){wellnessData={...(wellnessData||readWellness()),...patch,day:wellnessTodayKey()};store.setItem(WELLNESS_KEY,JSON.stringify(wellnessData));renderWellness();}
  function renderWellness(){if(!wellnessData)return;const d=wellnessData;const water=$('wellnessWaterCount');if(!water)return;water.textContent=Number(d.waterMl).toLocaleString(locale());$('wellnessWaterGoalText').textContent=`/ ${Number(d.waterGoalMl).toLocaleString(locale())} ml`;$('wellnessWaterGoal').value=String(d.waterGoalMl);const percent=Math.min(100,Math.round(d.waterMl/Math.max(1,d.waterGoalMl)*100));$('wellnessWaterProgress').setAttribute('aria-valuenow',String(percent));$('wellnessWaterProgressFill').style.width=`${percent}%`;$('vegetablesCount').textContent=String(d.vegetables);$('sweetsCount').textContent=String(d.sweets);$('wellnessPeriodStart').value=d.periodStart||'';$('wellnessCycleLength').value=String(d.cycleLength);$('wellnessHabitSelect').value=d.habit;$('wellnessHabitCount').textContent=`${d.habitCheckIns} ${state.lang==='ar'?'تسجيلات ناجحة':'successful check-ins'}`;const next=$('wellnessNextPeriod');if(d.periodStart){const date=new Date(`${d.periodStart}T12:00:00`);date.setDate(date.getDate()+d.cycleLength);next.textContent=date.toLocaleDateString(locale(),{year:'numeric',month:'short',day:'numeric'});}else next.textContent='—';}
  function initWellnessTracker(){wellnessData=readWellness();const bindClick=(id,fn)=>$(id)?.addEventListener('click',fn);bindClick('wellnessWaterUndo',()=>saveWellness({waterMl:Math.max(0,wellnessData.waterMl-250)}));bindClick('wellnessWater250',()=>saveWellness({waterMl:Math.min(10000,wellnessData.waterMl+250)}));bindClick('wellnessWater500',()=>saveWellness({waterMl:Math.min(10000,wellnessData.waterMl+500)}));$('wellnessWaterGoal')?.addEventListener('change',e=>saveWellness({waterGoalMl:Math.max(500,Math.min(6000,Number(e.target.value)||2000))}));bindClick('vegetablesMinus',()=>saveWellness({vegetables:Math.max(0,wellnessData.vegetables-1)}));bindClick('vegetablesPlus',()=>saveWellness({vegetables:Math.min(20,wellnessData.vegetables+1)}));bindClick('sweetsMinus',()=>saveWellness({sweets:Math.max(0,wellnessData.sweets-1)}));bindClick('sweetsPlus',()=>saveWellness({sweets:Math.min(20,wellnessData.sweets+1)}));$('wellnessPeriodStart')?.addEventListener('change',e=>saveWellness({periodStart:e.target.value}));$('wellnessCycleLength')?.addEventListener('change',e=>saveWellness({cycleLength:Math.max(21,Math.min(45,Number(e.target.value)||28))}));$('wellnessHabitSelect')?.addEventListener('change',e=>saveWellness({habit:e.target.value}));bindClick('wellnessHabitLog',()=>saveWellness({habitCheckIns:wellnessData.habitCheckIns+1}));renderWellness();}

  function renderHealthStatus(value=currentHealth()){
    const dot=$('healthDot');dot.className='health-dot';const ux=String(value.uxState||'');
    const ar=state.lang==='ar';
    const states={
      UNAVAILABLE:[ar?'Health Connect غير متاح':'Health Connect unavailable',ar?'يبقى تسجيل التمرين المحلي متاحًا.':'Local workout logging remains available.'],
      PROVIDER_UPDATE_REQUIRED:[ar?'Health Connect يحتاج تحديث':'Health Connect update required',ar?'حدّث مزود Health Connect ثم أعد المحاولة.':'Update the Health Connect provider, then try again.'],
      PERMISSION_REQUIRED:[ar?'السماح بالقراءة مطلوب':'Read permission required',ar?`أذونات القراءة الناقصة: ${(value.missingReadPermissions||[]).length||value.requiredReadCount||4}`:`Missing read permissions: ${(value.missingReadPermissions||[]).length||value.requiredReadCount||4}`],
      READY_UNSYNCED:[ar?'متصل وجاهز للمزامنة':'Connected and ready to sync',ar?'تم منح قراءة البيانات. ابدأ أول مزامنة.':'Read access is granted. Start the first sync.'],
      SYNCING:[ar?'جارٍ مزامنة Health Connect':'Syncing Health Connect',ar?'نقرأ النشاط ونراجع مصدر كل سجل.':'Reading activity and checking each record source.'],
      SYNCED_VERIFIED:[ar?'نشاط موثّق متصل':'Verified activity connected',ar?`سجلات موثقة: ${value.verifiedRecords||0} · مستبعدة: ${value.excludedManualOrUnknownRecords||0}`:`Verified records: ${value.verifiedRecords||0} · excluded: ${value.excludedManualOrUnknownRecords||0}`],
      SYNCED_NO_RECORDS:[ar?'متصل — لا توجد سجلات':'Connected — no records found',ar?'المزامنة نجحت، لكن لا توجد بيانات في الفترة المقروءة.':'Sync succeeded, but no records exist in the read window.'],
      SYNCED_UNVERIFIED_ONLY:[ar?'متصل — البيانات غير مؤهلة للمكافآت':'Connected — data is not reward-eligible',ar?'وجدنا سجلات، لكن مصدرها/طريقة تسجيلها لا تحقق شروط التوثيق.':'Records were found, but their source/recording method does not meet verification rules.'],
      RATE_LIMITED:[ar?'المزامنة مؤجلة مؤقتًا':'Sync temporarily limited',ar?'Health Connect طلب الانتظار قبل محاولة جديدة.':'Health Connect asked us to wait before retrying.'],
      ERROR:[ar?'تعذرت المزامنة':'Sync failed',ar?'حدث خطأ أثناء قراءة Health Connect.':'An error occurred while reading Health Connect.'],
    };
    const pair=states[ux];
    if(ux==='SYNCED_VERIFIED'||ux==='SYNCED_NO_RECORDS'||ux==='SYNCED_UNVERIFIED_ONLY'||ux==='READY_UNSYNCED'||ux==='SYNCING')dot.classList.add('connected');
    if(ux==='UNAVAILABLE'||ux==='PROVIDER_UPDATE_REQUIRED'||ux==='RATE_LIMITED'||ux==='ERROR')dot.classList.add('error');
    if(pair){$('healthTitle').textContent=pair[0];$('healthDetail').textContent=pair[1];}
    else if(value.connected){dot.classList.add('connected');$('healthTitle').textContent=ar?'متصل بـ Health Connect':'Connected to Health Connect';$('healthDetail').textContent=ar?'جاهز للمزامنة.':'Ready to sync.';}
    else{$('healthTitle').textContent=value.availability==='BROWSER_PREVIEW'?(ar?'معاينة المتصفح':'Browser preview'):(ar?'غير متصل':'Not connected');$('healthDetail').textContent=value.availability==='BROWSER_PREVIEW'?t('browserHealth'):(ar?`أذونات القراءة الناقصة: ${(value.missingPermissions||[]).length||value.requiredCount||4}`:`Missing read permissions: ${(value.missingPermissions||[]).length||value.requiredCount||4}`);}
    $('healthLastSync').textContent=value.lastSync?`${ar?'آخر مزامنة':'Last sync'}: ${new Date(value.lastSync).toLocaleString(locale())}`:t('neverSynced');if(value.lastError){$('healthError').textContent=value.lastError;$('healthError').classList.remove('hidden')}else $('healthError').classList.add('hidden');
  }
  let healthSyncRetryTimer=0;
  function setHealthSyncBusy(busy,message=''){const button=$('healthSyncBtn');button.disabled=Boolean(busy);button.setAttribute('aria-busy',String(Boolean(busy)));if(message)$('healthEmpty').textContent=message;}
  function scheduleHealthRetry(retryAfterMs){clearTimeout(healthSyncRetryTimer);const delay=Math.max(1000,Math.min(Number(retryAfterMs)||5000,60000));setHealthSyncBusy(true,t('healthSyncWait'));healthSyncRetryTimer=setTimeout(()=>setHealthSyncBusy(false,t('healthEmpty')),delay);}
  function renderHealthError(data={}){const code=String(data.code||'');const retryAfterMs=Number(data.retryAfterMs||0);setHealthSyncBusy(false,code==='RATE_LIMITED'||code==='COOLDOWN'?t('healthSyncWait'):t('healthSyncFailed'));renderHealthStatus({...currentHealth(),lastError:data.message||'Health Connect error'});if(retryAfterMs>0)scheduleHealthRetry(retryAfterMs);}
  function renderHealthSnapshot(data){clearTimeout(healthSyncRetryTimer);setHealthSyncBusy(false);$('healthSteps').textContent=Number(data.steps||0).toLocaleString(locale());$('healthSessions').textContent=Number(data.exerciseSessions||0).toLocaleString(locale());$('healthDistance').textContent=(Number(data.distanceMeters||0)/1000).toFixed(1);$('healthCalories').textContent=Math.round(Number(data.activeCaloriesKcal||0)).toLocaleString(locale());$('healthSources').innerHTML=(data.origins||[]).map(origin=>`<span class="tag">${escapeHtml(origin)}</span>`).join('');$('healthEmpty').textContent=data.uxState==='SYNCED_UNVERIFIED_ONLY'?(state.lang==='ar'?'تمت القراءة، لكن السجلات الحالية غير مؤهلة للمكافآت.':'Records were read, but none are currently reward-eligible.'):data.uxState==='SYNCED_NO_RECORDS'?(state.lang==='ar'?'الاتصال ناجح ولا توجد سجلات في آخر 7 أيام.':'Connected; no records in the last 7 days.'):(state.lang==='ar'?'تم تحديث ملخص موثّق لآخر 7 أيام.':'The verified 7-day summary is up to date.');renderHealthStatus({...currentHealth(),...data,lastError:''});}

  function activityHistory(){return parse(store.getItem('pulse.v2.activities'),[]);}
  function profileWeightKg(){const profile=parse(store.getItem('pulse.v2.profile'),defaultProfile());return Math.max(30,Math.min(250,Number(profile.weightKg)||70));}
  function readActivitySnapshot(){if(!N||typeof N.activitySnapshot!=='function')return state.activitySnapshot||{active:false,mode:'',route:[]};try{return parse(N.activitySnapshot(),state.activitySnapshot||{active:false,mode:'',route:[]});}catch{return state.activitySnapshot||{active:false,mode:'',route:[]};}}
  function formatElapsed(ms){const total=Math.max(0,Math.floor(Number(ms||0)/1000)),h=Math.floor(total/3600),m=Math.floor((total%3600)/60),sec=total%60;return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;}
  function formatPace(value){const pace=Number(value);if(!Number.isFinite(pace)||pace<=0)return '—';const min=Math.floor(pace),sec=Math.max(0,Math.min(59,Math.round((pace-min)*60)));return `${min}:${String(sec).padStart(2,'0')}`;}
  function activityModeName(mode){return mode==='walk'?t('walk'):mode==='run'?t('run'):mode==='cycle'?t('cycle'):t('selectActivity');}
  function renderActivityRoute(route=[]){const line=$('activityRouteLine'),empty=$('activityMapEmpty');if(!line||!empty)return;const points=(Array.isArray(route)?route:[]).filter(p=>Number.isFinite(Number(p.lat))&&Number.isFinite(Number(p.lng)));empty.classList.toggle('hidden',points.length>0);if(!points.length){line.setAttribute('points','');return;}const lats=points.map(p=>Number(p.lat)),lngs=points.map(p=>Number(p.lng)),minLat=Math.min(...lats),maxLat=Math.max(...lats),minLng=Math.min(...lngs),maxLng=Math.max(...lngs),latSpan=Math.max(0.00005,maxLat-minLat),lngSpan=Math.max(0.00005,maxLng-minLng);const svgPoints=points.map(p=>{const x=60+(Number(p.lng)-minLng)/lngSpan*880,y=500-(Number(p.lat)-minLat)/latSpan*440;return `${x.toFixed(1)},${y.toFixed(1)}`;}).join(' ');line.setAttribute('points',svgPoints);}
  function renderActivity(snapshot=readActivitySnapshot()){state.activitySnapshot=snapshot||{active:false,route:[]};const mode=String(snapshot?.mode||'');$('activityModeLabel').textContent=activityModeName(mode);$('activityTimer').textContent=formatElapsed(snapshot?.elapsedMs);$('activityDistance').textContent=(Number(snapshot?.distanceMetres||0)/1000).toFixed(2);$('activityPace').textContent=mode==='cycle'?'—':formatPace(snapshot?.paceMinutesPerKm);$('activitySpeed').textContent=Number(snapshot?.averageSpeedKph||0).toFixed(1);$('activityCalories').textContent=Math.round(Number(snapshot?.estimatedCaloriesKcal||0));$('activitySteps').textContent=mode==='cycle'?'—':Number(snapshot?.steps||0).toLocaleString(locale());$('activityAccuracy').textContent=Number.isFinite(Number(snapshot?.lastAccuracyMetres))?Math.round(Number(snapshot.lastAccuracyMetres)):'—';const gpsFixState=String(snapshot?.gpsFixState||'acquiring');const observedAccuracy=Number(snapshot?.observedAccuracyMetres);$('activityGpsStatus').textContent=gpsFixState==='ready'?`GPS · ${Math.round(Number(snapshot.lastAccuracyMetres||0))}m`:gpsFixState==='weak'?`${t('gpsWeak')}${Number.isFinite(observedAccuracy)?` · ±${Math.round(observedAccuracy)}m`:''}`:gpsFixState==='stale'?t('gpsStale'):gpsFixState==='off'?t('gpsOff'):t('gpsWaiting');$('activityGpsStatus').classList.toggle('gold',gpsFixState==='ready');$('activityStopBtn').disabled=!snapshot?.active;$('activityPauseBtn').disabled=!snapshot?.active;$('activityPauseBtn').textContent=t(snapshot?.paused?'resumeActivity':'pauseActivity');document.querySelectorAll('[data-activity-mode]').forEach(button=>button.classList.toggle('active',snapshot?.active&&button.dataset.activityMode===mode));renderActivityRoute(snapshot?.route||[]);renderActivityHistory();return snapshot;}
  function startActivityPolling(){stopActivityPolling();state.activityPoll=setInterval(()=>renderActivity(readActivitySnapshot()),1000);}
  function stopActivityPolling(){if(state.activityPoll){clearInterval(state.activityPoll);state.activityPoll=null;}}
  function startActivity(mode){showScreen('activityScreen',false);const live=readActivitySnapshot();if(live?.active){state.activitySnapshot=live;renderActivity(live);startActivityPolling();return;}if(!N||typeof N.beginActivitySession!=='function'){toast(t('activityPermissionNeeded'));return;}const result=parse(N.beginActivitySession(mode,profileWeightKg()),{});state.activitySnapshot={...state.activitySnapshot,...result,mode:result.mode||mode,route:state.activitySnapshot?.route||[]};renderActivity(state.activitySnapshot);startActivityPolling();if(result.permissionRequired)toast(t('activityPermissionNeeded'));}
  function persistFinishedActivity(snapshot,notify=false){if(Number(snapshot?.startedAtWallMs)<=0||Number(snapshot?.elapsedMs)<=0)return false;const entry={id:`activity-${snapshot.startedAtWallMs}`,mode:snapshot.mode,startedAtWallMs:snapshot.startedAtWallMs,date:new Date(snapshot.startedAtWallMs).toISOString(),elapsedMs:snapshot.elapsedMs,distanceMetres:snapshot.distanceMetres||0,steps:snapshot.steps||0,averageSpeedKph:snapshot.averageSpeedKph||0,paceMinutesPerKm:snapshot.paceMinutesPerKm,estimatedCaloriesKcal:snapshot.estimatedCaloriesKcal||0,gpsPointCount:snapshot.gpsPointCount||0,route:snapshot.route||[]};const entries=activityHistory().filter(item=>item.id!==entry.id);entries.push(entry);store.setItem('pulse.v2.activities',JSON.stringify(entries.slice(-100)));renderActivityHistory();renderToday();if(notify)toast(t('activitySaved'));return true;}
  function recoverPendingActivitySession(){if(!N||typeof N.takePendingFinishedActivitySnapshot!=='function')return;const snapshot=parse(N.takePendingFinishedActivitySnapshot(),null);if(snapshot&&persistFinishedActivity(snapshot,false))toast(t('activitySaved'));}
  function stopAndSaveActivity(){if(!N||typeof N.endActivitySession!=='function')return;const snapshot=parse(N.endActivitySession(),{});stopActivityPolling();renderActivity(snapshot);persistFinishedActivity(snapshot,true);}
  function renderActivityHistory(){const node=$('activityHistory');if(!node)return;const entries=activityHistory().slice().reverse().slice(0,12);node.innerHTML=entries.length?entries.map(entry=>`<article class="history-item"><div><h3>${escapeHtml(activityModeName(entry.mode))}</h3><p class="small muted">${new Date(entry.date).toLocaleString(locale())} · ${(Number(entry.distanceMetres||0)/1000).toFixed(2)} km · ${formatElapsed(entry.elapsedMs)}</p></div><strong>${Math.round(Number(entry.estimatedCaloriesKcal||0))} kcal</strong></article>`).join(''):`<p class="muted">${escapeHtml(t('emptyHistory'))}</p>`;}

  function defaultProfile(){return{goal:'general_fitness',level:'beginner',days:3,weightKg:70,equipment:['body only']};}
  function equipmentOptions(){return[['body only',state.lang==='ar'?'وزن الجسم':'Bodyweight'],['dumbbell',state.lang==='ar'?'دمبل':'Dumbbells'],['barbell',state.lang==='ar'?'بار وأوزان':'Barbell'],['cable',state.lang==='ar'?'كيبل':'Cable'],['machine',state.lang==='ar'?'أجهزة':'Machines'],['kettlebells',state.lang==='ar'?'كيتل بيل':'Kettlebells'],['bands',state.lang==='ar'?'مطاط مقاومة':'Bands']];}
  function renderEquipmentChoices(node,selected){node.innerHTML=equipmentOptions().map(([id,label])=>`<label class="choice"><input type="checkbox" value="${escapeHtml(id)}" ${selected.includes(id)?'checked':''}><span>${escapeHtml(label)}</span></label>`).join('');}
  function renderProfile(){const profile={...defaultProfile(),...parse(store.getItem('pulse.v2.profile'),defaultProfile())};$('profileGoal').value=profile.goal;$('profileLevel').value=profile.level;$('profileDays').value=profile.days;$('profileDaysOutput').textContent=profile.days;$('profileWeightKg').value=Number(profile.weightKg)||70;renderEquipmentChoices($('equipmentChoices'),profile.equipment);}
  function saveProfile(event){event.preventDefault();const profile={goal:$('profileGoal').value,level:$('profileLevel').value,days:Number($('profileDays').value),weightKg:Math.max(30,Math.min(250,Number($('profileWeightKg').value)||70)),equipment:[...$('equipmentChoices').querySelectorAll('input:checked')].map(input=>input.value)};if(!profile.equipment.length)profile.equipment=['body only'];store.setItem('pulse.v2.profile',JSON.stringify(profile));store.removeItem('pulse.v2.program');$('profileSaved').classList.remove('hidden');setTimeout(()=>$('profileSaved').classList.add('hidden'),2500);renderToday();}

  function readOnboardingDraft(){const draft=state.onboardingDraft||parse(store.getItem('pulse.v2.profile'),defaultProfile());return{...defaultProfile(),...draft,equipment:Array.isArray(draft.equipment)&&draft.equipment.length?draft.equipment:['body only']};}
  function renderOnboarding(){const draft=readOnboardingDraft();$('onboardingGoal').value=draft.goal;$('onboardingLevel').value=draft.level;$('onboardingDays').value=draft.days;$('onboardingDaysOutput').textContent=draft.days;$('onboardingWeightKg').value=Number(draft.weightKg)||70;renderEquipmentChoices($('onboardingEquipmentChoices'),draft.equipment);}
  function captureOnboardingDraft(){state.onboardingDraft={goal:$('onboardingGoal').value,level:$('onboardingLevel').value,days:Number($('onboardingDays').value),weightKg:Math.max(30,Math.min(250,Number($('onboardingWeightKg').value)||70)),equipment:[...$('onboardingEquipmentChoices').querySelectorAll('input:checked')].map(input=>input.value)};$('onboardingDaysOutput').textContent=state.onboardingDraft.days;}
  function openOnboarding(){renderOnboarding();$('onboardingDialog').classList.remove('hidden');document.body.classList.add('onboarding-open');setTimeout(()=>$('onboardingGoal').focus(),0);}
  function closeOnboarding(){$('onboardingDialog').classList.add('hidden');document.body.classList.remove('onboarding-open');state.onboardingDraft=null;}
  function completeOnboarding(event){event.preventDefault();captureOnboardingDraft();const profile=readOnboardingDraft();if(!profile.equipment.length)profile.equipment=['body only'];store.setItem('pulse.v2.profile',JSON.stringify(profile));store.removeItem('pulse.v2.program');closeOnboarding();renderProfile();renderToday();showScreen('todayScreen');toast(t('planReady'));}
  function toggleLanguage(){state.lang=state.lang==='ar'?'en':'ar';store.setItem('pulse.v2.lang',state.lang);applyLanguage();}

  function preferredReducedMotion(){
    const saved=store.getItem('pulse.v2.reduceMotion');
    if(saved!==null)return saved==='1';
    return Boolean(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }
  function applyMotionPreference(reduced,persist=true){
    const enabled=Boolean(reduced);
    $('reduceMotion').checked=enabled;
    document.documentElement.style.setProperty('--motion',enabled?'0':'1');
    document.documentElement.classList.toggle('motion-reduced',enabled);
    document.querySelectorAll('video.exercise-motion').forEach(video=>{
      if(enabled) video.pause();
      else if(!document.hidden && video.isConnected && (video.dataset.context==='card' || !$('exerciseDetail').classList.contains('hidden'))) video.play().catch(()=>{});
    });
    if(persist)store.setItem('pulse.v2.reduceMotion',enabled?'1':'0');
  }

  function bind(){
    $('languageToggle').addEventListener('click',toggleLanguage);
    $('onboardingLanguageToggle').addEventListener('click',()=>{captureOnboardingDraft();toggleLanguage();});
    $('onboardingForm').addEventListener('submit',completeOnboarding);
    ['onboardingGoal','onboardingLevel','onboardingDays','onboardingWeightKg'].forEach(id=>$(id).addEventListener('input',captureOnboardingDraft));
    $('onboardingEquipmentChoices').addEventListener('change',captureOnboardingDraft);
    document.querySelectorAll('#primaryNav button').forEach(button=>button.addEventListener('click',()=>showScreen(button.dataset.screen)));
    document.querySelectorAll('#trainModeTabs button').forEach(button=>button.addEventListener('click',()=>{state.trainMode=button.dataset.mode;store.setItem('pulse.v2.trainMode',state.trainMode);renderTrainMode();}));
    $('exerciseSearch').addEventListener('input',renderExercises);$('clearSearch').addEventListener('click',()=>{$('exerciseSearch').value='';renderExercises();});
    [['bodyFilter','body'],['muscleFilter','muscle'],['equipmentFilter','equipment'],['movementFilter','movement'],['levelFilter','level'],['goalFilter','goal']].forEach(([id,key])=>$(id).addEventListener('change',event=>{state.filters[key]=event.target.value;renderExercises();}));
    $('resetFilters').addEventListener('click',()=>resetFilters());$('emptyReset').addEventListener('click',()=>resetFilters());$('filterToggle').addEventListener('click',()=>{const panel=$('filterPanel'),collapsed=panel.classList.toggle('collapsed');$('filterToggle').setAttribute('aria-expanded',String(!collapsed));});
    $('closeDetail').addEventListener('click',closeDetail);$('detailCloseButton').addEventListener('click',closeDetail);$('startExerciseBtn').addEventListener('click',()=>startExercise(state.selected));
    $('closeProgramDetail').addEventListener('click',closeProgramDetail);$('programDetailCloseButton').addEventListener('click',closeProgramDetail);$('useProgramBtn').addEventListener('click',()=>useProgram($('useProgramBtn').dataset.program));
    $('startTodayBtn').addEventListener('click',()=>{const button=$('startTodayBtn');if(button.dataset.program&&button.dataset.session){startProgramSession(button.dataset.program,button.dataset.session);return;}const item=EXERCISES.find(exercise=>exercise.id===button.dataset.exercise);if(item)startExercise(item);});
    $('addSetBtn').addEventListener('click',addSet);$('finishWorkoutBtn').addEventListener('click',finishWorkout);$('skipRest').addEventListener('click',stopRest);$('exitWorkoutBtn').addEventListener('click',()=>{persistActive();showScreen('trainScreen');});
    $('speakCue').addEventListener('click',()=>speakExercise(activeExercise(),{force:true}));
    document.querySelectorAll('[data-activity-mode]').forEach(button=>button.addEventListener('click',()=>startActivity(button.dataset.activityMode)));
    $('activityAutoPauseLeave').checked=store.getItem('pulse.v2.activityAutoPauseLeave')==='true';$('activityAutoPauseLeave').addEventListener('change',event=>store.setItem('pulse.v2.activityAutoPauseLeave',String(Boolean(event.target.checked))));const pauseIfLeavingActivity=()=>{if($('activityAutoPauseLeave').checked&&state.activitySnapshot?.active&&!state.activitySnapshot?.paused&&typeof N?.pauseActivitySession==='function'){state.activitySnapshot=parse(N.pauseActivitySession(),state.activitySnapshot);renderActivity(state.activitySnapshot);}};$('activityStopBtn').addEventListener('click',stopAndSaveActivity);$('activityPauseBtn').addEventListener('click',()=>{if(!N)return;const fn=state.activitySnapshot?.paused?N.resumeActivitySession:N.pauseActivitySession;if(typeof fn==='function'){state.activitySnapshot=parse(fn(),state.activitySnapshot||{});renderActivity(state.activitySnapshot);}});$('activityBackBtn').addEventListener('click',()=>{pauseIfLeavingActivity();stopActivityPolling();showScreen('todayScreen');});$('activityHealthBtn').addEventListener('click',()=>{pauseIfLeavingActivity();stopActivityPolling();showScreen('healthScreen');});
    window.addEventListener('thf:activity-started',()=>{renderActivity(readActivitySnapshot());startActivityPolling();});window.addEventListener('thf:location-permission',event=>{if(event.detail?.granted){setTimeout(()=>renderActivity(readActivitySnapshot()),400);}else toast(t('activityPermissionNeeded'));});
    $('clearHistoryBtn').addEventListener('click',()=>{const now=Date.now();if(now>state.clearArmedUntil){state.clearArmedUntil=now+3000;toast(t('clearConfirm'));return;}store.removeItem('pulse.v2.history');renderToday();renderProgress();});
    $('profileForm').addEventListener('submit',saveProfile);$('profileDays').addEventListener('input',event=>$('profileDaysOutput').textContent=event.target.value);$('refreshStatus').addEventListener('click',renderNativeStatus);$('voiceEnabled').addEventListener('change',event=>voiceGuidance.setEnabled(event.target.checked));$('reduceMotion').addEventListener('change',event=>applyMotionPreference(event.target.checked));
    $('privacyPolicyBtn').addEventListener('click',()=>{if(N)N.openPrivacyPolicy();else toast(t('accountResourceAndroidOnly'))});
    $('accountDeletionBtn').addEventListener('click',()=>{if(N)N.openAccountDeletion();else toast(t('accountResourceAndroidOnly'))});
    $('foundingHeroPurchaseBtn').addEventListener('click',()=>{if(N&&typeof N.purchaseFoundingHero==='function'){N.purchaseFoundingHero();renderFoundingHero({...currentBilling(),loading:true});}else toast(t('foundingHeroAndroidOnly'));});
    $('foundingHeroRestoreBtn').addEventListener('click',()=>{if(N&&typeof N.restoreFoundingHero==='function'){N.restoreFoundingHero();renderFoundingHero({...currentBilling(),loading:true});}else toast(t('foundingHeroAndroidOnly'));});
    $('modeChip').addEventListener('click',()=>{const value=nativeStatus();if(N&&value.syncConfigured&&value.accountAuthConfigured&&!value.syncAuthenticated){N.requestBackendSignIn();renderNativeStatus();}else if(!N)toast(t('syncUnavailable'));});
    initWellnessTracker();
    recoverPendingActivitySession();window.addEventListener('pageshow',recoverPendingActivitySession);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')recoverPendingActivitySession();});
    $('healthConnectBtn').addEventListener('click',()=>{if(N)N.requestHealthPermissions();else toast(t('browserHealth'));});$('healthSyncBtn').addEventListener('click',()=>{if(!N){toast(t('browserHealth'));return;}const result=parse(N.syncHealth(),{});if(result.status==='STARTED')setHealthSyncBusy(true,t('healthSyncing'));else renderHealthError({code:'COOLDOWN',message:t('healthSyncWait'),retryAfterMs:result.retryAfterMs||1000});});$('healthSettingsBtn').addEventListener('click',()=>{if(N)N.openHealthSettings();else toast(t('browserHealth'));});
    window.addEventListener('thf:health-status',event=>renderHealthStatus(event.detail));window.addEventListener('thf:health-permission',event=>renderHealthStatus(event.detail));window.addEventListener('thf:health-sync',event=>renderHealthSnapshot(event.detail));window.addEventListener('thf:health-write',()=>renderHealthStatus());window.addEventListener('thf:health-error',event=>renderHealthError(event.detail||{}));
    window.addEventListener('thf:backend-auth',event=>{renderNativeStatus();if(event.detail?.error)toast(event.detail.error);});window.addEventListener('thf:backend-sync',event=>{renderNativeStatus();if(event.detail?.lastError)toast(event.detail.lastError);});window.addEventListener('thf:backend-history',event=>{const detail=event.detail||{};if(detail.lastError){toast((state.lang==='ar'?'تعذرت استعادة سجل الحساب: ':'Account history restore failed: ')+detail.lastError);return;}const remote=Array.isArray(detail.items)?detail.items:[];const merged=new Map(history().map(item=>[item.clientRecordId,item]));for(const workout of remote){const id=String(workout.clientRecordId||'');if(!/^[A-Za-z0-9._:-]{8,120}$/.test(id)||merged.has(id))continue;const startedAtMs=Date.parse(workout.startedAt||'');const endedAtMs=Date.parse(workout.endedAt||'');if(!Number.isFinite(startedAtMs)||!Number.isFinite(endedAtMs)||endedAtMs<=startedAtMs)continue;const sets=(Array.isArray(workout.sets)?workout.sets:[]).map(set=>({exerciseId:String(set.exerciseId||workout.sport||'other'),type:String(set.setType||'working'),load:Number(set.loadKg)||0,reps:Number(set.reps)||0,restSeconds:Number(set.restSeconds)||0,rpe:set.rpe??null,rir:set.rir??null,complete:true}));const exercise=String(sets[0]?.exerciseId||workout.sport||'Workout');merged.set(id,{clientRecordId:id,recordVersion:Number(workout.clientRecordVersion)||1,id:exercise,exercise,exerciseName:exercise,sport:String(workout.sport||'other'),startedAtMs,endedAtMs,date:new Date(endedAtMs).toISOString(),durationMin:Math.max(1,Math.round((endedAtMs-startedAtMs)/60000)),reps:sets.reduce((sum,set)=>sum+set.reps,0),volumeKg:Number(workout.volumeKg)||sets.reduce((sum,set)=>sum+set.load*set.reps,0),sets,completed:true,steps:0,motionEvidence:null,measurementSource:'SERVER_RESTORED_UNVERIFIED',restoredFromAccount:true});}const next=[...merged.values()].sort((a,b)=>(a.endedAtMs||Date.parse(a.date)||0)-(b.endedAtMs||Date.parse(b.date)||0)).slice(-200);store.setItem('pulse.v2.history',JSON.stringify(next));renderToday();renderProgress();if(remote.length)toast(state.lang==='ar'?`تمت استعادة ${remote.length} جلسة من حسابك`:`Restored ${remote.length} workouts from your account`);});
    window.addEventListener('thf:billing-status',event=>renderFoundingHero(event.detail||{}));
    document.addEventListener('visibilitychange',()=>{const video=$('activeDemoVideo');if(document.hidden)video.pause();else{if($('activeWorkoutScreen').classList.contains('active')&&!video.classList.contains('hidden'))video.play().catch(()=>{});if(state.active?.restEndsAtMs)renderRest();if($('activityScreen').classList.contains('active'))renderActivity(readActivitySnapshot());}});
    window.addEventListener('keydown',event=>{if(event.key!=='Escape')return;if(!$('exerciseDetail').classList.contains('hidden'))closeDetail();else if(!$('programDetail').classList.contains('hidden'))closeProgramDetail();});
  }

  const shouldOnboard = !store.getItem('pulse.v2.profile') && !state.active;
  bind(); $('voiceEnabled').checked=voiceGuidance.isEnabled(); applyMotionPreference(preferredReducedMotion(),false); applyLanguage(); renderHealthStatus(); renderFoundingHero();
  if (shouldOnboard) openOnboarding();
  if (state.active && activeExercise()) { const item=activeExercise();state.active.sensorProfile=state.active.sensorProfile||sensorProfileForExercise(item);state.active.motionSessionId=state.active.motionSessionId||`${state.active.clientRecordId}:${Number(state.active.programExerciseIndex)||0}:${item.id}`;beginNativeMotionSession(state.active.motionSessionId,state.active.sensorProfile); startMotionPolling(); renderActiveWorkout(); resumeRest(); showScreen('activeWorkoutScreen', false); }
  else { const liveActivity=readActivitySnapshot(); if(liveActivity?.active){state.activitySnapshot=liveActivity;showScreen('activityScreen',false);startActivityPolling();} }

})();
