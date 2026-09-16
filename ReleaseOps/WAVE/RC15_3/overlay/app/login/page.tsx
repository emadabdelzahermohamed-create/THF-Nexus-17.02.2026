"use client";

import { useState, type FormEvent } from "react";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setMessage("");
    const form = new FormData(event.currentTarget);
    const requestedReturnTo = new URLSearchParams(window.location.search).get("return_to") || "/";
    const returnTo = requestedReturnTo.startsWith("/") && !requestedReturnTo.startsWith("//") ? requestedReturnTo : "/";
    const payload = {
      email: String(form.get("email") || ""),
      password: String(form.get("password") || ""),
      displayName: String(form.get("displayName") || ""),
      returnTo,
    };
    try {
      const response = await fetch(mode === "login" ? "/api/auth/login" : "/api/auth/register", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
      const result = await response.json() as { error?: string; redirectTo?: string };
      if (!response.ok) {
        setMessage(result.error === "invalid_credentials" ? "البريد أو كلمة المرور غير صحيحة." : result.error === "account_exists" ? "هذا البريد مسجل بالفعل. استخدم تسجيل الدخول." : "تعذر إكمال العملية. راجع البيانات وحاول مرة أخرى.");
        return;
      }
      window.location.href = result.redirectTo || "/";
    } catch { setMessage("تعذر الاتصال بالخدمة الآن."); }
    finally { setBusy(false); }
  }

  return <main className="auth-page"><section className="auth-card">
    <a className="auth-brand" href="/">wave_موجة</a>
    <span className="kicker">WAVE ACCOUNT</span>
    <h1>{mode === "login" ? "تسجيل الدخول" : "إنشاء حساب"}</h1>
    <p>حساب موجة يعمل داخل الموقع والتطبيق بنفس الجلسة، دون تحويلك إلى نطاق خارجي.</p>
    <div className="auth-tabs"><button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">دخول</button><button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">حساب جديد</button></div>
    <form onSubmit={submit}>
      {mode === "register" && <label>الاسم<input name="displayName" minLength={2} maxLength={100} required autoComplete="name" /></label>}
      <label>البريد الإلكتروني<input name="email" type="email" required autoComplete="email" inputMode="email" /></label>
      <label>كلمة المرور<input name="password" type="password" minLength={10} maxLength={200} required autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
      <button className="primary-button" disabled={busy}>{busy ? "جارٍ التنفيذ…" : mode === "login" ? "دخول" : "إنشاء الحساب"}</button>
    </form>
    {message && <p className="auth-message" role="status">{message}</p>}
    <small>الجلسة محفوظة في Cookie آمنة HttpOnly/Secure، وكلمة المرور لا تُحفظ كنص صريح.</small>
  </section></main>;
}
