(() => {
  'use strict';
  const N = window.PulseNative || null;
  const EXERCISES = Array.isArray(window.THF_EXERCISES) ? window.THF_EXERCISES : [];
  const PROGRAMS = Array.isArray(window.THF_PROGRAMS) ? window.THF_PROGRAMS : [];
  const motionManifest = window.THF_MOTION_MANIFEST || {};
  const $ = id => document.getElementById(id);
  const store = (() => {
    try { localStorage.setItem('__thf_probe', '1'); localStorage.removeItem('__thf_probe'); return localStorage; }
    catch { const memory = new Map(); return {getItem:key=>memory.get(key)||null,setItem:(key,value)=>memory.set(key,String(value)),removeItem:key=>memory.delete(key)}; }
  })();
  const parse = (value, fallback) => { try { return value ? JSON.parse(value) : fallback; } catch { return fallback; } };
  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[match]));
  const locale = () => state.lang === 'ar' ? 'ar-EG' : 'en-US';
  const local = value => value?.[state.lang] ?? value?.en ?? '';

  const COPY = {
    ar: {
      skip:'انتقل إلى المحتوى',brandTag:'تدريب واضح. تقدم حقيقي.',offlineBanner:'مكتبة التمارين والدليل المصور متاحان دون إنترنت.',todayEyebrow:'خطتك اليوم',todayTitle:'خطوة واحدة واضحة',startWorkout:'ابدأ التمرين',readiness:'جاهزية',sessions:'جلسات',today:'اليوم',minutes:'دقائق',volume:'الحجم',streak:'الاستمرار',days:'أيام',weeklyGoal:'هدف الأسبوع',consistency:'الاستمرارية قبل الشدة',weeklyHint:'أكمل جلسات مناسبة لمستواك ثم تدرّج بهدوء.',trainEyebrow:'26 برنامجًا · 80 تمرينًا موثقًا',trainTitle:'اختر خطتك وتدرّب بوضوح',searchLabel:'ابحث في التمارين',searchPlaceholder:'اسم التمرين أو العضلة أو المعدة',gymLibrary:'مكتبة الجيم',gymTitle:'ابنِ جلستك حسب جسمك ومعداتك',gymHint:'فلترة حقيقية للعضلة والمعدة ونمط الحركة والمستوى والهدف.',exercises:'تمرين',filters:'الفلاتر',bodyPart:'جزء الجسم',muscle:'العضلة',equipment:'المعدة',movement:'نمط الحركة',level:'المستوى',goal:'الهدف',resetFilters:'إعادة ضبط الفلاتر',noResults:'لا توجد نتائج مطابقة',noResultsHint:'جرّب مسح البحث أو تقليل عدد الفلاتر.',backToLibrary:'العودة للمكتبة',toggleFrame:'بدّل الوضع',technique:'طريقة الأداء',sessionLog:'سجل الجلسة',set:'المجموعة',load:'الحمل',reps:'العدات',addSet:'+ إضافة مجموعة',rest:'راحة',skipRest:'تخطّي',safety:'السلامة أولًا',finishWorkout:'إنهاء التمرين وحفظه',progressEyebrow:'افهم تقدمك',progressTitle:'قوة وحجم واستمرارية',totalWorkouts:'كل الجلسات',totalVolume:'إجمالي الحجم',personalRecords:'أرقام شخصية',activeMinutes:'دقائق نشطة',volumeTrend:'حجم آخر 7 جلسات',localData:'محلي',recentHistory:'السجل الأخير',clearHistory:'مسح السجل',healthTitle:'نشاطك في مكان واحد',beforeConnect:'قبل الاتصال',yourChoice:'بياناتك واختيارك',healthRationale:'نقرأ الخطوات وجلسات التمرين والمسافة والسعرات النشطة لعرض ملخصك، ونكتب فقط جلسات THF المكتملة. لا نطلب نبض القلب أو النوم أو الوزن.',healthBullet1:'يمكن رفض أي إذن أو سحبه لاحقًا.',healthBullet2:'يبقى تسجيل التمرين المحلي عاملًا دون اتصال.',healthBullet3:'معرّف ثابت يمنع تكرار الجلسة عند إعادة المحاولة.',reviewPermissions:'راجع الأذونات واتصل',steps7:'خطوات / 7 أيام',distance:'المسافة',activeCalories:'سعرات نشطة',healthEmpty:'اتصل ثم اضغط مزامنة لقراءة البيانات.',neverSynced:'آخر مزامنة: لم تتم',syncNow:'مزامنة الآن',managePermissions:'إدارة الأذونات',samsungPath:'المسار المعتمد: Samsung Health ← Health Connect ← Top Hero Fit. لا نعتبر الربط ناجحًا قبل ظهور بيانات Samsung فعلية.',profileEyebrow:'خطتك تتكيف معك',profileTitle:'ملف التدريب',goalFitness:'لياقة عامة',goalMuscle:'بناء العضلات',goalStrength:'القوة',goalEndurance:'التحمل',goalMobility:'الحركة والاستشفاء',beginner:'مبتدئ',intermediate:'متوسط',advanced:'متقدم',daysPerWeek:'أيام التدريب أسبوعيًا',availableEquipment:'المعدات المتاحة',savePlan:'احفظ وحدّث خطة اليوم',profileSaved:'تم حفظ ملفك وتحديث اقتراح اليوم.',privacyOffline:'الخصوصية والوضع المحلي',refreshStatus:'تحديث الحالة',voiceGuidance:'الدليل الصوتي',reduceMotion:'تقليل الحركة',navToday:'اليوم',navTrain:'تدريب',navProgress:'التقدم',navHealth:'الصحة',navProfile:'ملفي',startThisExercise:'ابدأ هذا التمرين',sourceLicense:'المصدر والترخيص',all:'الكل',offline:'أوفلاين',start:'البداية',finish:'النهاية',setup:'الاستعداد',breathing:'التنفس',defaults:'الجرعة المقترحة',mistakes:'أخطاء شائعة',regression:'نسخة أسهل',progression:'التدرج',working:'أساسية',warmup:'إحماء',completed:'مكتملة',saved:'تم حفظ التمرين محليًا.',emptyHistory:'ابدأ أول تمرين ليظهر تقدمك هنا.',noCatalog:'تعذر تحميل مكتبة التمارين الأوفلاين.',browserHealth:'Health Connect متاح داخل تطبيق Android فقط.',statusOffline:'وضع أوفلاين جاهز',statusOnline:'متصل وجاهز للمزامنة',clearConfirm:'اضغط مرة أخرى خلال 3 ثوانٍ لمسح السجل.',profilePlan:'جلسة مناسبة لهدفك',oneExercise:'حركة واحدة واضحة',min:'د',setsLabel:'مجموعات',sourceText:'free-exercise-db · Unlicense · نسخة أوفلاين موثقة',setProgress:'{done} من {total} مكتملة',dateLabel:'التاريخ',volumeLabel:'الحجم',rpeHelp:'RPE من 1 إلى 10',rirHelp:'RIR عدد العدات المتبقية',programs:'البرامج',exerciseLibrary:'مكتبة التمارين',programLibrary:'برامج أوفلاين منظمة',programTitle:'ابدأ بمسار واضح وتدرّج آمن',programHint:'كل برنامج يحدد الأسابيع والجلسات والتمارين وRPE وRIR ومعيار التدرج.',noPrograms:'لا توجد برامج في هذا القسم',weeks:'أسابيع',daysWeekly:'أيام أسبوعيًا',useProgram:'استخدم هذا البرنامج',programSelected:'تم اختيار البرنامج وتحديث اليوم.',programSessions:'جلسات البرنامج',session:'جلسة',exerciseCount:'تمارين',programSource:'تكوين تحريري أصلي من THF · بيانات وصور التمارين: free-exercise-db / Unlicense'
    },
    en: {
      skip:'Skip to content',brandTag:'Clear training. Real progress.',offlineBanner:'The exercise library and visual demos work fully offline.',todayEyebrow:"Today's plan",todayTitle:'One clear next action',startWorkout:'Start workout',readiness:'Readiness',sessions:'Sessions',today:'Today',minutes:'Minutes',volume:'Volume',streak:'Streak',days:'days',weeklyGoal:'Weekly goal',consistency:'Consistency before intensity',weeklyHint:'Complete sessions that fit your level, then progress gradually.',trainEyebrow:'26 programs · 80 documented exercises',trainTitle:'Choose your plan and train clearly',searchLabel:'Search exercises',searchPlaceholder:'Exercise, muscle, or equipment',gymLibrary:'Gym library',gymTitle:'Build around your body and equipment',gymHint:'Real filters for muscle, equipment, movement, level, and goal.',exercises:'exercises',filters:'Filters',bodyPart:'Body part',muscle:'Muscle',equipment:'Equipment',movement:'Movement',level:'Level',goal:'Goal',resetFilters:'Reset filters',noResults:'No matching exercises',noResultsHint:'Clear the search or remove some filters.',backToLibrary:'Back to library',toggleFrame:'Change position',technique:'Technique',sessionLog:'Session log',set:'Set',load:'Load',reps:'Reps',addSet:'+ Add set',rest:'Rest',skipRest:'Skip',safety:'Safety first',finishWorkout:'Finish and save workout',progressEyebrow:'Understand your progress',progressTitle:'Strength, volume, consistency',totalWorkouts:'All sessions',totalVolume:'Total volume',personalRecords:'Personal records',activeMinutes:'Active minutes',volumeTrend:'Last 7 session volume',localData:'Local',recentHistory:'Recent history',clearHistory:'Clear history',healthTitle:'Your activity in one place',beforeConnect:'Before connecting',yourChoice:'Your data, your choice',healthRationale:'We read steps, exercise sessions, distance, and active calories for your summary, and write only completed THF sessions. We do not request heart rate, sleep, or weight.',healthBullet1:'You may deny or revoke any permission later.',healthBullet2:'Local workout logging remains available offline.',healthBullet3:'A stable identifier prevents duplicate writes on retry.',reviewPermissions:'Review permissions and connect',steps7:'Steps / 7 days',distance:'Distance',activeCalories:'Active calories',healthEmpty:'Connect, then sync to read activity.',neverSynced:'Last sync: never',syncNow:'Sync now',managePermissions:'Manage permissions',samsungPath:'Supported path: Samsung Health ← Health Connect ← Top Hero Fit. We do not call it connected until real Samsung data appears.',profileEyebrow:'Your plan adapts to you',profileTitle:'Training profile',goalFitness:'General fitness',goalMuscle:'Build muscle',goalStrength:'Strength',goalEndurance:'Endurance',goalMobility:'Mobility & recovery',beginner:'Beginner',intermediate:'Intermediate',advanced:'Advanced',daysPerWeek:'Training days per week',availableEquipment:'Available equipment',savePlan:'Save and update Today',profileSaved:'Profile saved and Today updated.',privacyOffline:'Privacy and offline mode',refreshStatus:'Refresh status',voiceGuidance:'Voice guidance',reduceMotion:'Reduce motion',navToday:'Today',navTrain:'Train',navProgress:'Progress',navHealth:'Health',navProfile:'Profile',startThisExercise:'Start this exercise',sourceLicense:'Source and license',all:'All',offline:'Offline',start:'Start',finish:'Finish',setup:'Setup',breathing:'Breathing',defaults:'Suggested prescription',mistakes:'Common mistakes',regression:'Regression',progression:'Progression',working:'Working',warmup:'Warm-up',completed:'Complete',saved:'Workout saved locally.',emptyHistory:'Start your first workout to see progress here.',noCatalog:'The offline exercise library could not be loaded.',browserHealth:'Health Connect is available in the Android app only.',statusOffline:'Offline mode ready',statusOnline:'Online and ready to sync',clearConfirm:'Press again within 3 seconds to clear history.',profilePlan:'A session aligned to your goal',oneExercise:'one clear movement',min:'min',setsLabel:'sets',sourceText:'free-exercise-db · Unlicense · audited offline copy',setProgress:'{done} of {total} complete',dateLabel:'Date',volumeLabel:'Volume',rpeHelp:'RPE from 1 to 10',rirHelp:'RIR is reps left in reserve',programs:'Programs',exerciseLibrary:'Exercise library',programLibrary:'Structured offline programs',programTitle:'Start with a clear path and safe progression',programHint:'Every program defines its weeks, sessions, exercises, RPE, RIR and progression rule.',noPrograms:'No programs in this section',weeks:'weeks',daysWeekly:'days weekly',useProgram:'Use this program',programSelected:'Program selected and Today updated.',programSessions:'Program sessions',session:'Session',exerciseCount:'exercises',programSource:'Original THF editorial composition · exercise data and images: free-exercise-db / Unlicense'
    }
  };
  COPY.ar.trainEyebrow = `26 برنامجًا · ${EXERCISES.length} تمرينًا موثقًا`;
  COPY.en.trainEyebrow = `26 programs · ${EXERCISES.length} documented exercises`;
  Object.assign(COPY.ar, {startSession:'ابدأ الجلسة',saveNext:'احفظ وانتقل للتمرين التالي',finishSession:'أنهِ الجلسة واحفظها',exerciseOf:'تمرين {current} من {total}',nextExercise:'تم حفظ التمرين. التالي: {name}',sessionComplete:'اكتملت الجلسة وحُفظت.',signInSync:'سجّل للدخول والمزامنة',syncConnected:'المزامنة متصلة',syncConnecting:'جارٍ ربط الحساب',offlineReady:'أوفلاين جاهز',syncUnavailable:'المزامنة غير مهيأة',foundingHeroEyebrow:'حزمة تجميلية لمرة واحدة',foundingHeroTitle:'البطل المؤسس',foundingHeroBadge:'البطل المؤسس',foundingHeroBody:'شراء رقمي لمرة واحدة يضيف شارة البطل المؤسس ولمسة ذهبية لملفك.',foundingHeroScope:'شارة تجميلية فقط؛ لا تحجب التمارين أو الصحة، ولا تمنح أفضلية تنافسية أو توكنات أو عائدًا ماليًا.',foundingHeroLoading:'جارٍ التحقق من Google Play…',foundingHeroBuy:'احصل على الحزمة',foundingHeroRestore:'استعادة الشراء',foundingHeroOwned:'حزمة البطل المؤسس مفعلة على هذا الحساب.',foundingHeroPending:'عملية الشراء معلقة؛ ستتفعل الشارة بعد تأكيد Google Play.',foundingHeroUnavailable:'المنتج غير متاح في هذه النسخة بعد. لم يتم تحصيل أي مبلغ.',foundingHeroConfigure:'يلزم ربط مفتاح الترخيص العام ومنتج Play قبل إتاحة الشراء.',foundingHeroAndroidOnly:'متاح داخل نسخة Android المثبتة من Google Play.',foundingHeroCanceled:'تم إلغاء نافذة الشراء ولم يتم تحصيل مبلغ.'});
  Object.assign(COPY.en, {startSession:'Start session',saveNext:'Save and continue',finishSession:'Finish and save session',exerciseOf:'Exercise {current} of {total}',nextExercise:'Exercise saved. Next: {name}',sessionComplete:'Session complete and saved.',signInSync:'Sign in to sync',syncConnected:'Sync connected',syncConnecting:'Connecting account',offlineReady:'Offline ready',syncUnavailable:'Sync not configured',foundingHeroEyebrow:'One-time cosmetic pack',foundingHeroTitle:'Founding Hero',foundingHeroBadge:'Founding Hero',foundingHeroBody:'A one-time digital purchase that adds the Founding Hero badge and a gold profile accent.',foundingHeroScope:'Cosmetic badge only; workouts and Health remain free, with no competitive advantage, tokens, or financial return.',foundingHeroLoading:'Checking Google Play…',foundingHeroBuy:'Get the pack',foundingHeroRestore:'Restore purchase',foundingHeroOwned:'The Founding Hero pack is active for this account.',foundingHeroPending:'Purchase pending; the badge activates after Google Play confirms payment.',foundingHeroUnavailable:'This product is not available in this build yet. No charge was made.',foundingHeroConfigure:'Connect the public Play license key and Play product before enabling purchases.',foundingHeroAndroidOnly:'Available in the Android app installed through Google Play.',foundingHeroCanceled:'The purchase sheet was canceled and no charge was made.'});
  Object.assign(COPY.ar, {onboardingBrand:'خطتك تبدأ منك',onboardingStep:'إعداد سريع · يعمل أوفلاين',onboardingTitle:'ابنِ خطتك الأولى',onboardingIntro:'اختر هدفك وخبرتك وما يتوفر لديك. سنضع جلسة واضحة في «اليوم» ويمكنك تعديل كل شيء لاحقًا.',onboardingBenefitOffline:'دليل مصور أوفلاين',onboardingBenefitSafe:'تدرج وتعليمات سلامة',onboardingBenefitFlexible:'تعديل الخطة في أي وقت',onboardingPrivacy:'يُحفظ هذا الاختيار على جهازك أولًا. لا يلزم حساب للبدء.',createMyPlan:'أنشئ خطتي وابدأ',planReady:'خطتك جاهزة. ابدأ من جلسة اليوم.'});
  Object.assign(COPY.en, {onboardingBrand:'Your plan starts with you',onboardingStep:'Quick setup · works offline',onboardingTitle:'Build your first plan',onboardingIntro:'Choose your goal, experience and available equipment. We will put one clear session in Today, and you can change everything later.',onboardingBenefitOffline:'Offline visual guidance',onboardingBenefitSafe:'Safe progression and cues',onboardingBenefitFlexible:'Change your plan anytime',onboardingPrivacy:'Your choices are saved on this device first. No account is required to begin.',createMyPlan:'Create my plan and start',planReady:'Your plan is ready. Start with Today.'});
  Object.assign(COPY.ar, {accountPrivacyHint:'تستطيع مراجعة السياسة وبدء حذف بيانات حساب THF Fitness من المتصفح الآمن.',privacyPolicy:'سياسة الخصوصية',accountDeletion:'حذف بيانات الحساب',accountResourceAndroidOnly:'هذا الرابط متاح داخل تطبيق Android.'});
  Object.assign(COPY.en, {accountPrivacyHint:'Review the policy or start deleting your THF Fitness account data in the secure browser.',privacyPolicy:'Privacy policy',accountDeletion:'Delete account data',accountResourceAndroidOnly:'This link is available in the Android app.'});
  Object.assign(COPY.ar, {readinessToday:'جاهزية اليوم',todaySummary:'ملخص اليوم',trainContentType:'نوع محتوى التدريب',programSections:'أقسام البرامج',clearSearch:'مسح البحث',trainingSections:'أقسام التدريب',volumeChartLabel:'مخطط حجم التدريب',onboardingBenefitsLabel:'مزايا الخطة',close:'إغلاق'});
  Object.assign(COPY.en, {readinessToday:"Today's readiness",todaySummary:"Today's summary",trainContentType:'Training content type',programSections:'Program sections',clearSearch:'Clear search',trainingSections:'Training sections',volumeChartLabel:'Training volume chart',onboardingBenefitsLabel:'Plan benefits',close:'Close'});

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
    restRemaining: 0,
    restTick: null,
    demoFrame: 0,
    clearArmedUntil: 0,
    onboardingDraft: null
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
    $('primaryNav').classList.toggle('hidden', id === 'activeWorkoutScreen');
    document.body.classList.toggle('workout-active', id === 'activeWorkoutScreen');
    const demoVideo = $('activeDemoVideo');
    if (id === 'activeWorkoutScreen' && !demoVideo.classList.contains('hidden')) demoVideo.play().catch(() => {});
    else demoVideo.pause();
    window.scrollTo({top: 0, behavior: 'smooth'});
    if (id === 'progressScreen') renderProgress();
    if (id === 'healthScreen') renderHealthStatus();
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
    renderTrainMode(); renderSections(); renderProgramSections(); populateFilters(); renderExercises(); renderPrograms(); renderToday(); renderProgress(); renderProfile(); renderOnboarding(); renderNativeStatus(); renderFoundingHero();
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

  function renderExercises() {
    if (!EXERCISES.length) { $('exerciseGrid').innerHTML = `<p class="error-message">${escapeHtml(t('noCatalog'))}</p>`; return; }
    const results = EXERCISES.filter(matches);
    $('resultsCount').textContent = String(results.length);
    $('emptyResults').classList.toggle('hidden', results.length > 0);
    $('activeFilterCount').textContent = String(Object.values(state.filters).filter(Boolean).length);
    $('exerciseGrid').innerHTML = results.map(item => `<button class="exercise-card" type="button" data-id="${escapeHtml(item.id)}"><span class="media"><img src="./${escapeHtml(item.demo.assets[0])}" alt="${escapeHtml(item.demo.alt[state.lang])}" loading="lazy"><span class="offline-badge">✓ ${escapeHtml(t('offline'))}</span></span><span class="copy"><span class="pill">${escapeHtml(local(item.section))}</span><h3>${escapeHtml(local(item.name))}</h3><span class="meta">${escapeHtml(local(item.muscles.primary))} · ${escapeHtml(local(item.equipment))}</span><span class="tag-row"><span class="tag">${escapeHtml(local(item.level))}</span><span class="tag">${escapeHtml(local(item.movement))}</span></span></span></button>`).join('');
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
    $('detailDemo').innerHTML = item.demo.assets.map((asset,index) => `<div class="detail-frame"><img src="./${escapeHtml(asset)}" alt="${escapeHtml(item.demo.alt[state.lang])}"><span>${escapeHtml(t(index ? 'finish' : 'start'))}</span></div>`).join('');
    $('detailBadges').innerHTML = `<span class="pill gold">${escapeHtml(local(item.section))}</span><span class="pill">✓ ${escapeHtml(t('offline'))}</span><span class="pill">${escapeHtml(local(item.level))}</span>`;
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
  function startExercise(item) {
    state.active = {clientRecordId:makeClientId(),exerciseId:item.id,startedAt:Date.now(),sets:makeSets(item)}; state.demoFrame=0;
    store.setItem('pulse.v2.active', JSON.stringify(state.active)); closeDetail(); renderActiveWorkout(); showScreen('activeWorkoutScreen', false);
    try { N?.beginStepSession?.(); } catch {}
  }
  function startProgramSession(programId,sessionId) {
    const program=PROGRAMS.find(value=>value.id===programId);const sessionIndex=program?.sessions.findIndex(value=>value.id===sessionId)??-1;const session=program?.sessions[sessionIndex];const reference=session?.exercises[0];const item=reference?exerciseFor(reference):null;if(!program||!session||!item)return;
    const now=Date.now();store.setItem('pulse.v2.program',JSON.stringify({programId:program.id,sessionIndex,selectedAt:new Date(now).toISOString()}));
    state.active={clientRecordId:makeClientId(),exerciseId:item.id,startedAt:now,sets:makeProgramSets(reference,item),programId:program.id,programSessionId:session.id,programSessionIndex:sessionIndex,programExerciseIndex:0,programStartedAt:now,programEntries:[]};state.demoFrame=0;
    persistActive();closeProgramDetail();closeDetail();renderActiveWorkout();showScreen('activeWorkoutScreen',false);try{N?.beginStepSession?.();}catch{}
  }
  function activeExercise() { return EXERCISES.find(item => item.id === state.active?.exerciseId); }
  function completedVolume(sets) { return (sets||[]).filter(set=>set.complete).reduce((sum,set)=>sum + Math.max(0,Number(set.load)||0)*Math.max(0,Number(set.reps)||0),0); }
  function sessionVolume() { return completedVolume(state.active?.sets) + (state.active?.programEntries||[]).reduce((sum,entry)=>sum+completedVolume(entry.sets),0); }
  function persistActive() { store.setItem('pulse.v2.active', JSON.stringify(state.active)); }
  function renderActiveMotion(item) {
    const video = $('activeDemoVideo');
    const image = $('activeDemoImage');
    const motion = motionManifest[item.id];
    if (motion?.asset) {
      const nextSource = './' + motion.asset;
      if (video.getAttribute('src') !== nextSource) video.setAttribute('src', nextSource);
      video.setAttribute('aria-label', item.demo.alt[state.lang]);
      video.classList.remove('hidden');
      image.classList.add('hidden');
      $('activeDemoPhase').textContent = state.lang === 'ar' ? 'حركة كاملة تلقائية' : 'Automatic full movement';
      if (!document.hidden) video.play().catch(() => {});
      return;
    }
    video.pause();
    video.removeAttribute('src');
    video.load();
    video.classList.add('hidden');
    image.classList.remove('hidden');
    image.src = './' + item.demo.assets[0];
    image.alt = item.demo.alt[state.lang];
    $('activeDemoPhase').textContent = state.lang === 'ar' ? 'صور مرجعية — الحركة قيد الإضافة' : 'Reference images — motion pending';
  }
  function renderActiveWorkout() {
    const item = activeExercise(); if (!item) { state.active=null; store.removeItem('pulse.v2.active'); return; }
    renderActiveMotion(item);
    const program=PROGRAMS.find(value=>value.id===state.active.programId);const programSession=program?.sessions.find(value=>value.id===state.active.programSessionId);const programIndex=Number(state.active.programExerciseIndex)||0;
    $('activeSection').textContent = programSession?`${local(program.section)} · ${t('exerciseOf').replace('{current}',programIndex+1).replace('{total}',programSession.exercises.length)}`:local(item.section); $('activeExerciseName').textContent = local(item.name);
    $('activeExerciseCue').textContent = local(item.setup); $('activeMuscles').innerHTML = item.muscles.primary[state.lang].map(value=>`<span class="tag">${escapeHtml(value)}</span>`).join('');
    $('activeSteps').innerHTML = item.steps[state.lang].map(step=>`<li>${escapeHtml(step)}</li>`).join(''); $('activeBreathing').textContent = local(item.breathing); $('activeSafety').textContent = local(item.safety);
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
  function startRest(seconds) { clearInterval(state.restTick); state.restRemaining=seconds; $('restPanel').classList.remove('hidden'); renderRest(); state.restTick=setInterval(()=>{ state.restRemaining--; renderRest(); if(state.restRemaining<=0)stopRest(); },1000); }
  function renderRest(){ const seconds=Math.max(0,state.restRemaining); $('restTimer').textContent=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`; }
  function stopRest(){ clearInterval(state.restTick);state.restTick=null;$('restPanel').classList.add('hidden'); }
  function addSet(){ state.active.sets.push({type:'working',load:0,reps:8,rpe:7,rir:3,restSeconds:activeExercise()?.prescription?.restSeconds||60,complete:false});persistActive();renderActiveWorkout(); }
  function finishWorkout() {
    const item=activeExercise();if(!item)return;const now=Date.now();const currentEntry={exerciseId:item.id,exerciseName:item.name,sport:item.sport,sets:state.active.sets.map((set,index)=>({...set,exerciseId:item.id,ordinal:index+1}))};const entries=[...(state.active.programEntries||[]),currentEntry];
    const program=PROGRAMS.find(value=>value.id===state.active.programId);const programSession=program?.sessions.find(value=>value.id===state.active.programSessionId);const programIndex=Number(state.active.programExerciseIndex)||0;
    if(program&&programSession&&programIndex<programSession.exercises.length-1){const nextIndex=programIndex+1;const reference=programSession.exercises[nextIndex];const next=exerciseFor(reference);if(next){state.active={...state.active,exerciseId:next.id,startedAt:now,sets:makeProgramSets(reference,next),programExerciseIndex:nextIndex,programEntries:entries};state.demoFrame=0;stopRest();persistActive();renderActiveWorkout();toast(t('nextExercise').replace('{name}',local(next.name)));window.scrollTo({top:0,behavior:'smooth'});return;}}
    const allSets=entries.flatMap(entry=>entry.sets);const completedSets=allSets.filter(set=>set.complete);const volume=Math.round(completedSets.reduce((sum,set)=>sum+Math.max(0,Number(set.load)||0)*Math.max(0,Number(set.reps)||0),0));const title=program&&programSession?programSession.name:item.name;const startedAt=state.active.programStartedAt||state.active.startedAt;
    const summary={clientRecordId:state.active.clientRecordId,recordVersion:1,exercise:local(title),exerciseName:title,id:program?.id||item.id,sport:program?.section?.id||item.sport,programId:program?.id||null,programSessionId:programSession?.id||null,startedAtMs:startedAt,endedAtMs:now,date:new Date(now).toISOString(),durationMin:Math.max(1,Math.round((now-startedAt)/60000)),reps:completedSets.reduce((sum,set)=>sum+(Number(set.reps)||0),0),volumeKg:volume,sets:allSets,completed:true,steps:nativeStatus().sessionSteps||0};
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
    $('historyList').innerHTML=entries.length?entries.slice().reverse().slice(0,20).map(entry=>`<article class="history-item"><div><h3>${escapeHtml(entry.exerciseName?.[state.lang]||entry.exercise||entry.id)}</h3><p class="small muted">${new Date(entry.date).toLocaleString(locale())} · ${entry.durationMin||0} ${escapeHtml(t('min'))} · ${entry.sets?.filter(set=>set.complete).length||0} ${escapeHtml(t('setsLabel'))}</p></div><strong>${Math.round(entry.volumeKg||0)} kg</strong></article>`).join(''):`<p class="muted">${escapeHtml(t('emptyHistory'))}</p>`;
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
  function renderHealthStatus(value=currentHealth()){
    const dot=$('healthDot');dot.className='health-dot';
    if(value.connected){dot.classList.add('connected');$('healthTitle').textContent=state.lang==='ar'?'متصل بـ Health Connect':'Connected to Health Connect';$('healthDetail').textContent=state.lang==='ar'?`الأذونات المستخدمة مفعلة · كتابة معلقة: ${value.pendingWrites||0}`:`Used permissions granted · pending writes: ${value.pendingWrites||0}`;}
    else if(value.availability==='UNAVAILABLE'||value.availability==='ERROR'){dot.classList.add('error');$('healthTitle').textContent=state.lang==='ar'?'Health Connect غير متاح':'Health Connect unavailable';$('healthDetail').textContent=state.lang==='ar'?'يبقى تسجيل التمرين المحلي متاحًا.':'Local workout logging remains available.';}
    else{$('healthTitle').textContent=value.availability==='BROWSER_PREVIEW'?(state.lang==='ar'?'معاينة المتصفح':'Browser preview'):(state.lang==='ar'?'غير متصل':'Not connected');$('healthDetail').textContent=value.availability==='BROWSER_PREVIEW'?t('browserHealth'):(state.lang==='ar'?`الأذونات الناقصة: ${(value.missingPermissions||[]).length||value.requiredCount||5}`:`Missing permissions: ${(value.missingPermissions||[]).length||value.requiredCount||5}`);}
    $('healthLastSync').textContent=value.lastSync?`${state.lang==='ar'?'آخر مزامنة':'Last sync'}: ${new Date(value.lastSync).toLocaleString(locale())}`:t('neverSynced');if(value.lastError){$('healthError').textContent=value.lastError;$('healthError').classList.remove('hidden')}else $('healthError').classList.add('hidden');
  }
  function renderHealthSnapshot(data){$('healthSteps').textContent=Number(data.steps||0).toLocaleString(locale());$('healthSessions').textContent=Number(data.exerciseSessions||0).toLocaleString(locale());$('healthDistance').textContent=(Number(data.distanceMeters||0)/1000).toFixed(1);$('healthCalories').textContent=Math.round(Number(data.activeCaloriesKcal||0)).toLocaleString(locale());$('healthSources').innerHTML=(data.origins||[]).map(origin=>`<span class="tag">${escapeHtml(origin)}</span>`).join('');$('healthEmpty').textContent=(data.steps||data.exerciseSessions||data.distanceMeters||data.activeCaloriesKcal)?(state.lang==='ar'?'تم تحديث ملخص آخر 7 أيام.':'The last 7 days are up to date.'):(state.lang==='ar'?'الاتصال ناجح ولا توجد بيانات في آخر 7 أيام.':'Connected; no data in the last 7 days.');renderHealthStatus({...currentHealth(),lastSync:data.lastSync});}

  function defaultProfile(){return{goal:'general_fitness',level:'beginner',days:3,equipment:['body only']};}
  function equipmentOptions(){return[['body only',state.lang==='ar'?'وزن الجسم':'Bodyweight'],['dumbbell',state.lang==='ar'?'دمبل':'Dumbbells'],['barbell',state.lang==='ar'?'بار وأوزان':'Barbell'],['cable',state.lang==='ar'?'كيبل':'Cable'],['machine',state.lang==='ar'?'أجهزة':'Machines'],['kettlebells',state.lang==='ar'?'كيتل بيل':'Kettlebells'],['bands',state.lang==='ar'?'مطاط مقاومة':'Bands']];}
  function renderEquipmentChoices(node,selected){node.innerHTML=equipmentOptions().map(([id,label])=>`<label class="choice"><input type="checkbox" value="${escapeHtml(id)}" ${selected.includes(id)?'checked':''}><span>${escapeHtml(label)}</span></label>`).join('');}
  function renderProfile(){const profile=parse(store.getItem('pulse.v2.profile'),defaultProfile());$('profileGoal').value=profile.goal;$('profileLevel').value=profile.level;$('profileDays').value=profile.days;$('profileDaysOutput').textContent=profile.days;renderEquipmentChoices($('equipmentChoices'),profile.equipment);}
  function saveProfile(event){event.preventDefault();const profile={goal:$('profileGoal').value,level:$('profileLevel').value,days:Number($('profileDays').value),equipment:[...$('equipmentChoices').querySelectorAll('input:checked')].map(input=>input.value)};if(!profile.equipment.length)profile.equipment=['body only'];store.setItem('pulse.v2.profile',JSON.stringify(profile));store.removeItem('pulse.v2.program');$('profileSaved').classList.remove('hidden');setTimeout(()=>$('profileSaved').classList.add('hidden'),2500);renderToday();}

  function readOnboardingDraft(){const draft=state.onboardingDraft||parse(store.getItem('pulse.v2.profile'),defaultProfile());return{...defaultProfile(),...draft,equipment:Array.isArray(draft.equipment)&&draft.equipment.length?draft.equipment:['body only']};}
  function renderOnboarding(){const draft=readOnboardingDraft();$('onboardingGoal').value=draft.goal;$('onboardingLevel').value=draft.level;$('onboardingDays').value=draft.days;$('onboardingDaysOutput').textContent=draft.days;renderEquipmentChoices($('onboardingEquipmentChoices'),draft.equipment);}
  function captureOnboardingDraft(){state.onboardingDraft={goal:$('onboardingGoal').value,level:$('onboardingLevel').value,days:Number($('onboardingDays').value),equipment:[...$('onboardingEquipmentChoices').querySelectorAll('input:checked')].map(input=>input.value)};$('onboardingDaysOutput').textContent=state.onboardingDraft.days;}
  function openOnboarding(){renderOnboarding();$('onboardingDialog').classList.remove('hidden');document.body.classList.add('onboarding-open');setTimeout(()=>$('onboardingGoal').focus(),0);}
  function closeOnboarding(){$('onboardingDialog').classList.add('hidden');document.body.classList.remove('onboarding-open');state.onboardingDraft=null;}
  function completeOnboarding(event){event.preventDefault();captureOnboardingDraft();const profile=readOnboardingDraft();if(!profile.equipment.length)profile.equipment=['body only'];store.setItem('pulse.v2.profile',JSON.stringify(profile));store.removeItem('pulse.v2.program');closeOnboarding();renderProfile();renderToday();showScreen('todayScreen');toast(t('planReady'));}
  function toggleLanguage(){state.lang=state.lang==='ar'?'en':'ar';store.setItem('pulse.v2.lang',state.lang);applyLanguage();}

  function bind(){
    $('languageToggle').addEventListener('click',toggleLanguage);
    $('onboardingLanguageToggle').addEventListener('click',()=>{captureOnboardingDraft();toggleLanguage();});
    $('onboardingForm').addEventListener('submit',completeOnboarding);
    ['onboardingGoal','onboardingLevel','onboardingDays'].forEach(id=>$(id).addEventListener('input',captureOnboardingDraft));
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
    $('speakCue').addEventListener('click',()=>{const item=activeExercise();const text=[local(item.name),...item.steps[state.lang]].join('. ');try{if(N)N.speak(text,state.lang==='ar'?'ar-EG':'en-US');else if('speechSynthesis'in window){const utterance=new SpeechSynthesisUtterance(text);utterance.lang=state.lang==='ar'?'ar-EG':'en-US';speechSynthesis.speak(utterance);}}catch{}});
    $('clearHistoryBtn').addEventListener('click',()=>{const now=Date.now();if(now>state.clearArmedUntil){state.clearArmedUntil=now+3000;toast(t('clearConfirm'));return;}store.removeItem('pulse.v2.history');renderToday();renderProgress();});
    $('profileForm').addEventListener('submit',saveProfile);$('profileDays').addEventListener('input',event=>$('profileDaysOutput').textContent=event.target.value);$('refreshStatus').addEventListener('click',renderNativeStatus);$('reduceMotion').addEventListener('change',event=>document.documentElement.style.setProperty('--motion',event.target.checked?'0':'1'));
    $('privacyPolicyBtn').addEventListener('click',()=>{if(N)N.openPrivacyPolicy();else toast(t('accountResourceAndroidOnly'))});
    $('accountDeletionBtn').addEventListener('click',()=>{if(N)N.openAccountDeletion();else toast(t('accountResourceAndroidOnly'))});
    $('foundingHeroPurchaseBtn').addEventListener('click',()=>{if(N&&typeof N.purchaseFoundingHero==='function'){N.purchaseFoundingHero();renderFoundingHero({...currentBilling(),loading:true});}else toast(t('foundingHeroAndroidOnly'));});
    $('foundingHeroRestoreBtn').addEventListener('click',()=>{if(N&&typeof N.restoreFoundingHero==='function'){N.restoreFoundingHero();renderFoundingHero({...currentBilling(),loading:true});}else toast(t('foundingHeroAndroidOnly'));});
    $('modeChip').addEventListener('click',()=>{const value=nativeStatus();if(N&&value.syncConfigured&&value.accountAuthConfigured&&!value.syncAuthenticated){N.requestBackendSignIn();renderNativeStatus();}else if(!N)toast(t('syncUnavailable'));});
    $('healthConnectBtn').addEventListener('click',()=>{if(N)N.requestHealthPermissions();else toast(t('browserHealth'));});$('healthSyncBtn').addEventListener('click',()=>{if(N){N.syncHealth();$('healthEmpty').textContent=state.lang==='ar'?'جاري المزامنة…':'Syncing…';}else toast(t('browserHealth'));});$('healthSettingsBtn').addEventListener('click',()=>{if(N)N.openHealthSettings();else toast(t('browserHealth'));});
    window.addEventListener('thf:health-status',event=>renderHealthStatus(event.detail));window.addEventListener('thf:health-permission',event=>renderHealthStatus(event.detail));window.addEventListener('thf:health-sync',event=>renderHealthSnapshot(event.detail));window.addEventListener('thf:health-write',()=>renderHealthStatus());window.addEventListener('thf:health-error',event=>{renderHealthStatus({...currentHealth(),lastError:event.detail?.message||'Health Connect error'});});
    window.addEventListener('thf:backend-auth',event=>{renderNativeStatus();if(event.detail?.error)toast(event.detail.error);});window.addEventListener('thf:backend-sync',event=>{renderNativeStatus();if(event.detail?.lastError)toast(event.detail.lastError);});
    window.addEventListener('thf:billing-status',event=>renderFoundingHero(event.detail||{}));
    document.addEventListener('visibilitychange',()=>{const video=$('activeDemoVideo');if(document.hidden)video.pause();else if($('activeWorkoutScreen').classList.contains('active')&&!video.classList.contains('hidden'))video.play().catch(()=>{});});
    window.addEventListener('keydown',event=>{if(event.key!=='Escape')return;if(!$('exerciseDetail').classList.contains('hidden'))closeDetail();else if(!$('programDetail').classList.contains('hidden'))closeProgramDetail();});
  }

  const shouldOnboard = !store.getItem('pulse.v2.profile') && !state.active;
  bind(); applyLanguage(); renderHealthStatus(); renderFoundingHero();
  if (shouldOnboard) openOnboarding();
  if (state.active && activeExercise()) { renderActiveWorkout(); showScreen('activeWorkoutScreen', false); }
})();
