import { useEffect, useMemo, useState } from 'react';
import { api } from '@appdeploy/client';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Blocks,
  CheckCircle2,
  CircleDollarSign,
  ClipboardCheck,
  Coins,
  Flame,
  Landmark,
  LockKeyhole,
  Network,
  RefreshCw,
  Search,
  ShieldCheck,
  Users,
  Vault,
  WalletCards,
} from 'lucide-react';
import './tokenManager.css';

type Overview = {
  mint: string;
  network: string;
  slot: number;
  contextSlots: {
    anchor: number;
    supply: number;
    mintAccount: number;
  };
  supplyUi: string;
  supplyRaw: string;
  decimals: number;
  programId: string;
  mintAuthority: string | null;
  freezeAuthority: string | null;
  recentCount: number;
  status: string;
  invariantFailures: string[];
  observedAt: string;
};

type HolderResult = {
  status: string;
  top1Bps?: number | null;
  top5Bps?: number | null;
  top20Bps?: number | null;
  accounts?: Array<{ address: string; uiAmountString: string | null }>;
  reason?: string;
};

type Plan = {
  id: string;
  kind: string;
  amountUi: string;
  amountRaw: string;
  status: string;
  minimumApprovals: number;
  executionAuthorized: boolean;
  simulationRequired: boolean;
  externalSignerRequired: boolean;
  signerBoundary: string;
  sign: boolean;
  broadcast: boolean;
  chainSnapshot: {
    slot: number;
    supplyUi: string;
    digest: string;
    contextSlots: {
      anchor: number;
      supply: number;
      mintAccount: number;
    };
  };
  expiresAt: string;
  notes: string[];
  createdAt: string;
};

const mint = 'HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv';

function formatTokenUi(value: string) {
  const [whole, fraction] = value.split('.');
  const grouped = BigInt(whole).toLocaleString('ar-EG');
  return fraction ? `${grouped}.${fraction}` : grouped;
}

const modules = [
  [
    'مراقبة الشبكة',
    'فعلي',
    'قراءة supply والسلطات والـslot وآخر نشاط',
    Activity,
  ],
  [
    'الخزينة',
    'جاهز للربط',
    'سجل محافظ الخزينة، الأدوار والأرصدة والمطابقة',
    Vault,
  ],
  [
    'Multisig',
    'تكامل',
    'Squads v4 للموافقات المتعددة والـtimelock وحدود الإنفاق',
    ShieldCheck,
  ],
  [
    'التوزيعات',
    'تخطيط آمن',
    '35% من الإيراد للمستخدمين النشطين مع سقوف ومنع Sybil',
    Users,
  ],
  [
    'Airdrop جماعي',
    'تكامل',
    'توزيع دفعات كبيرة مع سجل إثبات ومراجعة قبل التنفيذ',
    Network,
  ],
  [
    'Vesting',
    'تكامل',
    'خطط الفريق/الشركاء/المستثمرين مع cliff وجدول فتح',
    LockKeyhole,
  ],
  [
    'Locking Rewards',
    'سياسة مطلوبة',
    'قفل THF ومكافآت بدون خلق توكنات جديدة',
    Coins,
  ],
  [
    'الحرق',
    'تخطيط آمن',
    'حرق تدريجي مع أرضية إجمالي 8B وموافقات متعددة',
    Flame,
  ],
  [
    'السيولة',
    'سياسة مطلوبة',
    'إدارة الاحتياطي، إضافة/سحب السيولة وحدود المخاطر',
    CircleDollarSign,
  ],
  [
    'DEX / Swap',
    'تكامل',
    'تكامل Jupiter للمسارات والأسعار والتنفيذ عند الاعتماد',
    BarChart3,
  ],
  ['DAO', 'تكامل', 'مقترحات وتصويت وtimelock وسجل تنفيذ', Landmark],
  [
    'Metadata',
    'فحص أولًا',
    'الاسم والشعار والروابط حسب حالة Update Authority',
    Blocks,
  ],
  [
    'المحافظ والحيتان',
    'فعلي',
    'فحص حيازات وأكبر الحسابات ومؤشرات التركّز',
    WalletCards,
  ],
  [
    'الحوادث',
    'فعلي',
    'Quarantine وFail-Closed عند أي اختلاف في الثوابت',
    AlertTriangle,
  ],
  [
    'سجل التدقيق',
    'فعلي',
    'حزم قرار قابلة للتتبع بدون حفظ أسرار أو مفاتيح',
    ClipboardCheck,
  ],
  [
    'تقارير وتصدير',
    'مخطط',
    'CSV/JSON للحركة والخزينة والتوزيع والمراجعة',
    BarChart3,
  ],
];

const integrations = [
  ['Solana SPL Token', 'التحويل، الحرق، الحسابات والسلطات الأساسية'],
  ['Squads v4', 'Multisig، timelocks، spending limits وأدوار الخزينة'],
  ['Streamflow', 'Vesting، locks والتوزيعات الجماعية'],
  ['SPL Governance / Realms', 'DAO ومقترحات وتصويت'],
  ['Jupiter', 'Routing وDEX swaps والسيولة السوقية'],
  [
    'Metaplex Token Metadata',
    'قراءة/إدارة بيانات التوكن إذا كانت الصلاحية متاحة',
  ],
  [
    'Solana ConnectorKit / Mobile Wallet Adapter',
    'توقيع المستخدم من الويب والهاتف بدون تخزين seed',
  ],
];

function App() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [holders, setHolders] = useState<HolderResult | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [wallet, setWallet] = useState('');
  const [walletResult, setWalletResult] = useState<any>(null);
  const [walletError, setWalletError] = useState('');
  const [kind, setKind] = useState('burn');
  const [amount, setAmount] = useState('');
  const [plan, setPlan] = useState<Plan | null>(null);
  const [planError, setPlanError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [o, h] = await Promise.all([
        api.get('/api/token/overview'),
        api.get('/api/token/holders'),
      ]);
      setOverview(o.data);
      setHolders(h.data);
    } catch (e) {
      setError(
        'تعذر قراءة بيانات Solana الآن. أعد المحاولة؛ لم يتم تنفيذ أي معاملة.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const invariantOk = useMemo(
    () =>
      !!overview &&
      overview.status === 'PASS' && overview.invariantFailures.length === 0,
    [overview]
  );

  const inspectWallet = async () => {
    setWalletError('');
    setWalletResult(null);
    try {
      const r = await api.post('/api/wallet/inspect', { wallet });
      setWalletResult(r.data);
    } catch (e) {
      setWalletError('عنوان المحفظة غير صالح أو تعذر فحصه.');
    }
  };

  const createPlan = async () => {
    setPlanError('');
    setPlan(null);
    try {
      const r = await api.post('/api/operations/plan', {
        kind,
        amountUi: amount,
      });
      setPlan(r.data);
    } catch (e) {
      setPlanError('أدخل كمية صحيحة أكبر من صفر وضمن القيود الحالية.');
    }
  };

  return (
    <main dir="rtl" className="shell">
      <header className="hero">
        <div>
          <div className="eyebrow">THF · Solana Mainnet · مركز تحكم عربي</div>
          <h1>THF Token Manager</h1>
          <p>
            لوحة موحدة لإدارة دورة حياة THF: مراقبة، خزينة، توزيعات، حرق،
            Vesting، سيولة، DAO، تقارير وحزم موافقة آمنة.
          </p>
        </div>
        <button
          className="refresh"
          onClick={() => void load()}
          disabled={loading}
        >
          <RefreshCw size={17} /> {loading ? 'جارِ التحقق' : 'تحديث الشبكة'}
        </button>
      </header>

      <section className="safety">
        <ShieldCheck size={22} />
        <div>
          <strong>وضع التنفيذ الحالي: Fail-Closed</strong>
          <span>
            لا يتم حفظ private keys أو seed phrases، ولا توجد أي عملية توقيع أو
            بث تلقائي من هذه اللوحة.
          </span>
        </div>
      </section>

      {error && (
        <section className="errorBox">
          <AlertTriangle size={20} /> <span>{error}</span>
          <button onClick={() => void load()}>إعادة المحاولة</button>
        </section>
      )}

      <section className="grid stats">
        <article className="card stat">
          <span>إجمالي المعروض</span>
          <strong>{overview?.supplyUi ?? '—'} THF</strong>
          <small>الهدف الأدنى المعتمد للحرق: 8,000,000,000</small>
        </article>
        <article className="card stat">
          <span>Mint Authority</span>
          <strong>
            {overview
              ? overview.mintAuthority === null
                ? 'ملغاة نهائيًا'
                : 'موجودة'
              : '—'}
          </strong>
          <small>لا يمكن إنشاء THF إضافي عندما تكون None.</small>
        </article>
        <article className="card stat">
          <span>Freeze Authority</span>
          <strong>
            {overview
              ? overview.freezeAuthority === null
                ? 'ملغاة نهائيًا'
                : 'موجودة'
              : '—'}
          </strong>
          <small>لا توجد سلطة مركزية لتجميد حسابات التوكن.</small>
        </article>
        <article className="card stat">
          <span>سلامة الثوابت</span>
          <strong className={invariantOk ? 'ok' : 'warn'}>
            {overview ? (invariantOk ? 'PASS' : 'تحقق مطلوب') : '—'}
          </strong>
          <small>Program + decimals + authorities.</small>
        </article>
      </section>

      <section className="card tokenIdentity">
        <div>
          <span>Mint</span>
          <code>{mint}</code>
        </div>
        <div>
          <span>Decimals</span>
          <b>{overview?.decimals ?? 8}</b>
        </div>
        <div>
          <span>Slot</span>
          <b>{overview?.slot?.toLocaleString('ar-EG') ?? '—'}</b>
        </div>
        <div>
          <span>نشاط حديث</span>
          <b>{overview?.recentCount ?? '—'} معاملات/إشارات</b>
        </div>
      </section>

      <section className="sectionHead">
        <div>
          <h2>وحدات الإدارة</h2>
          <p>
            كل ما قد نحتاجه لاحقًا موجود كوحدة مستقلة حتى لا نعيد بناء النظام
            عند كل مرحلة.
          </p>
        </div>
      </section>
      <section className="modules">
        {modules.map(([name, status, desc, Icon]) => (
          <article className="module" key={String(name)}>
            <div className="moduleIcon">
              <Icon size={20} />
            </div>
            <div>
              <h3>{name}</h3>
              <p>{desc}</p>
            </div>
            <span className="badge">{status}</span>
          </article>
        ))}
      </section>

      <section className="twoCol">
        <article className="card">
          <div className="cardTitle">
            <Search size={19} />
            <div>
              <h2>فحص محفظة</h2>
              <p>اعرض رصيد THF المرتبط بعنوان عام بدون طلب أي مفتاح.</p>
            </div>
          </div>
          <div className="formRow">
            <input
              aria-label="عنوان المحفظة"
              value={wallet}
              onChange={e => setWallet(e.target.value)}
              placeholder="أدخل Solana wallet address"
            />
            <button onClick={() => void inspectWallet()}>فحص</button>
          </div>
          {walletError && <p className="inlineError">{walletError}</p>}
          {walletResult && (
            <div className="resultBox">
              <b>إجمالي THF: {walletResult.totalUi} THF</b>
              <span>عدد حسابات التوكن: {walletResult.accountCount}</span>
            </div>
          )}
        </article>

        <article className="card">
          <div className="cardTitle">
            <BarChart3 size={19} />
            <div>
              <h2>تركيز الحيازة</h2>
              <p>مؤشر سريع لمراقبة الحيتان ومخاطر التركّز.</p>
            </div>
          </div>
          {holders?.status === 'ok' ? (
            <div className="concentration">
              <div>
                <span>Top 1</span>
                <b>{((holders.top1Bps ?? 0) / 100).toFixed(2)}%</b>
              </div>
              <div>
                <span>Top 5</span>
                <b>{((holders.top5Bps ?? 0) / 100).toFixed(2)}%</b>
              </div>
              <div>
                <span>Top 20</span>
                <b>{((holders.top20Bps ?? 0) / 100).toFixed(2)}%</b>
              </div>
            </div>
          ) : (
            <p className="muted">
              RPC الحالي لم يوفّر getTokenLargestAccounts. اللوحة تبقى Read-Only
              Degraded بدل إعطاء رقم غير موثوق.
            </p>
          )}
        </article>
      </section>

      <section className="card planner">
        <div className="cardTitle">
          <ClipboardCheck size={19} />
          <div>
            <h2>مخطط العمليات الحساسة</h2>
            <p>
              ينشئ حزمة مراجعة فقط. لا ينشئ transaction bytes ولا يوقّع ولا يبث.
            </p>
          </div>
        </div>
        <div className="planGrid">
          <label>
            نوع العملية
            <select value={kind} onChange={e => setKind(e.target.value)}>
              <option value="burn">حرق THF</option>
              <option value="treasury_transfer">تحويل من الخزينة</option>
              <option value="reward_epoch">توزيع مكافآت دورة</option>
              <option value="vesting_settlement">تسوية Vesting</option>
              <option value="liquidity">عملية سيولة</option>
              <option value="dao_execution">تنفيذ قرار DAO</option>
            </select>
          </label>
          <label>
            الكمية THF
            <input
              aria-label="الكمية THF"
              inputMode="decimal"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              placeholder="مثال: 1000000"
            />
          </label>
          <button onClick={() => void createPlan()}>إنشاء حزمة مراجعة</button>
        </div>
        {planError && <p className="inlineError">{planError}</p>}
        {plan && (
          <div className="planResult" role="status" aria-live="polite">
            <div className="planTop">
              <CheckCircle2 size={20} />
              <b>تم إنشاء حزمة غير تنفيذية</b>
              <span>{plan.id}</span>
            </div>
            <div className="planFacts">
              <span>النوع: {plan.kind}</span>
              <span>الكمية: {formatTokenUi(plan.amountUi)} THF</span>
              <span>الحد الأدنى للموافقات: {plan.minimumApprovals}</span>
              <span>Sign: لا</span>
              <span>Broadcast: لا</span>
              <span>الموقّع: خارجي عبر Multisig فقط</span>
              <span>لقطة الشبكة: slot {plan.chainSnapshot.slot}</span>
              <span>سياق المعروض: {plan.chainSnapshot.contextSlots.supply}</span>
              <span>سياق هوية التوكن: {plan.chainSnapshot.contextSlots.mintAccount}</span>
            </div>
            <ul>
              {plan.notes.map(x => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="twoCol">
        <article className="card">
          <h2>مكونات مفتوحة المصدر سنعتمد عليها</h2>
          <div className="integrationList">
            {integrations.map(([name, desc]) => (
              <div key={name}>
                <b>{name}</b>
                <span>{desc}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="card">
          <h2>قواعد التشغيل الدائمة</h2>
          <ul className="rules">
            <li>أي تغيير مالي يبدأ بـSimulation ثم Review ثم Multisig.</li>
            <li>
              لا أسرار أو seed أو private keys داخل Git أو قاعدة البيانات.
            </li>
            <li>الحرق لا يسمح بخفض إجمالي THF تحت 8B وفق السياسة الحالية.</li>
            <li>
              توزيع 35% من الإيراد لا يتحول تلقائيًا إلى THF قبل اعتماد طريقة
              تقييم واضحة وسقف لكل دورة ولكل مستخدم.
            </li>
            <li>كل عملية تحمل معرفًا وسجل أدلة وموافقات وقابلية تدقيق.</li>
            <li>
              أي اختلاف في mint/program/decimals/authorities يوقف المسار المالي
              تلقائيًا.
            </li>
          </ul>
        </article>
      </section>

      <footer>
        THF Token Manager · Arabic-first control plane · لا توجد معاملة مالية
        تلقائية في هذه النسخة.
      </footer>
    </main>
  );
}

export default App;
