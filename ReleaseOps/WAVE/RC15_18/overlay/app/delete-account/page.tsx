import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "حذف حساب WAVE MAWJA",
  description: "صفحة عامة لطلب وحذف حساب WAVE MAWJA وبياناته المرتبطة.",
};

export default function DeleteAccountPage() {
  return (
    <main dir="rtl" style={{ minHeight: "100vh", background: "#07111f", color: "#eef7ff", padding: "32px 18px" }}>
      <article style={{ maxWidth: 860, margin: "0 auto", lineHeight: 1.9 }}>
        <a href="/" style={{ color: "#79ddff", textDecoration: "none" }}>← العودة إلى WAVE</a>
        <h1 style={{ fontSize: "clamp(2rem,5vw,3.4rem)", marginBottom: 8 }}>حذف حساب WAVE MAWJA</h1>
        <p style={{ opacity: 0.75, marginTop: 0 }}>آخر تحديث: 26 سبتمبر 2026</p>

        <p>
          يمكنك حذف حساب WAVE والبيانات المرتبطة به من داخل الخدمة. يلزم تسجيل الدخول أولًا حتى نتحقق
          من ملكية الحساب قبل تنفيذ الحذف.
        </p>

        <section style={{ marginTop: 28 }}>
          <h2 style={{ fontSize: "1.35rem" }}>الطريقة الأسرع</h2>
          <ol>
            <li>سجّل الدخول إلى حسابك في WAVE.</li>
            <li>افتح صفحة الحساب أو الملف الشخصي.</li>
            <li>اختر حذف الحساب وأكّد الطلب.</li>
          </ol>
          <p>
            <a href="/login" style={{ color: "#79ddff" }}>تسجيل الدخول إلى WAVE</a>
            {" — "}
            <a href="/profile" style={{ color: "#79ddff" }}>فتح صفحة الحساب</a>
          </p>
        </section>

        <section style={{ marginTop: 28 }}>
          <h2 style={{ fontSize: "1.35rem" }}>ما الذي يُحذف؟</h2>
          <p>
            عند تنفيذ حذف الحساب، تُزال بيانات الحساب والمكتبة والمفضلة وتقدم المشاهدة المرتبطة بالحساب
            حيثما ينطبق. قد نحتفظ فقط بسجلات أمنية أو قانونية محدودة عندما يكون الاحتفاظ مطلوبًا، أو نحول
            المراجع التقنية إلى بيانات غير معرّفة عندما يكون ذلك مناسبًا.
          </p>
        </section>

        <section style={{ marginTop: 28 }}>
          <h2 style={{ fontSize: "1.35rem" }}>إذا تعذر الدخول</h2>
          <p>
            يمكنك التواصل عبر بريد الدعم المنشور للتطبيق:
            {" "}
            <a href="mailto:TopHeroFit@gmail.com" style={{ color: "#79ddff" }}>TopHeroFit@gmail.com</a>.
            اذكر أنك تريد حذف حساب WAVE، ولن نطلب منك إرسال كلمة المرور.
          </p>
        </section>

        <section style={{ marginTop: 28 }}>
          <h2 style={{ fontSize: "1.35rem" }}>الخصوصية</h2>
          <p>
            راجع <a href="/privacy" style={{ color: "#79ddff" }}>سياسة الخصوصية</a> لمعرفة تفاصيل المعالجة والاحتفاظ.
          </p>
        </section>
      </article>
    </main>
  );
}
