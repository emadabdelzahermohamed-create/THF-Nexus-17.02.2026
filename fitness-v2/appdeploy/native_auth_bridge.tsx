import { useMemo, useState } from 'react';
import { api, auth } from '@appdeploy/client';

const ANDROID_REDIRECT = 'topherofit://auth/v2/complete';
const B64URL_SHA256 = /^[A-Za-z0-9_-]{43}$/;

type AndroidRequest = { codeChallenge: string; redirectUri: typeof ANDROID_REDIRECT };

export function readAndroidAuthRequest(search = window.location.search): AndroidRequest | null {
  const query = new URLSearchParams(search);
  if (query.get('nativeAuth') !== 'android-v2') return null;
  const codeChallenge = query.get('code_challenge') || '';
  const method = query.get('code_challenge_method');
  const redirectUri = query.get('redirect_uri');
  if (!B64URL_SHA256.test(codeChallenge) || method !== 'S256' || redirectUri !== ANDROID_REDIRECT) return null;
  return { codeChallenge, redirectUri };
}

/**
 * Explicit user-gesture screen for Android account linking. Keeping sign-in behind the
 * button avoids popup blocking and leaves the provider flow in the system browser.
 */
export function AndroidAuthBridgeScreen() {
  const request = useMemo(() => readAndroidAuthRequest(), []);
  const [status, setStatus] = useState<'ready' | 'working' | 'error'>('ready');
  const [message, setMessage] = useState('');
  const arabic = navigator.language.toLowerCase().startsWith('ar');
  if (!request) return null;

  async function continueToAccount() {
    if (status === 'working') return;
    setStatus('working');
    setMessage('');
    try {
      if (!auth.isSignedIn()) await auth.signIn({ scope: 'openid email profile offline_access' });
      const response = await api.post('/api/v2/auth/android/tickets', {
        codeChallenge: request!.codeChallenge,
        redirectUri: request!.redirectUri,
      });
      const ticket = String(response.data?.ticket || '');
      if (!/^[A-Za-z0-9_-]{32,256}$/.test(ticket)) throw new Error('Invalid Android account ticket');
      window.location.replace(`${ANDROID_REDIRECT}?ticket=${encodeURIComponent(ticket)}`);
    } catch (cause) {
      setStatus('error');
      setMessage(cause instanceof Error ? cause.message : 'Account connection failed');
    }
  }

  return (
    <main dir={arabic ? 'rtl' : 'ltr'} style={{ minHeight:'100vh', display:'grid', placeItems:'center', background:'#07141b', color:'#f3f7f8', padding:24, fontFamily:'Inter, system-ui, sans-serif' }}>
      <section style={{ width:'min(440px, 100%)', background:'#0c1d25', border:'1px solid #38545f', borderRadius:24, padding:24, boxShadow:'0 20px 60px #0008' }}>
        <p style={{ color:'#f0ce7b', fontWeight:900, letterSpacing:1 }}>TOP HERO FIT</p>
        <h1>{arabic ? 'اربط حسابك بالتطبيق' : 'Connect your app account'}</h1>
        <p style={{ color:'#b8c9cf', lineHeight:1.7 }}>{arabic ? 'سجّل الدخول من المتصفح الآمن. سيعود التطبيق بتذكرة قصيرة أحادية الاستخدام؛ لا تُرسل كلمة المرور أو ملفات الارتباط إلى التطبيق.' : 'Sign in in this secure browser. The app receives a short-lived, single-use ticket—never your password or browser cookies.'}</p>
        <button type="button" onClick={continueToAccount} disabled={status === 'working'} style={{ width:'100%', minHeight:52, border:0, borderRadius:14, background:'#f0ce7b', color:'#09141a', fontWeight:900, fontSize:16 }}>
          {status === 'working' ? (arabic ? 'جارٍ الربط…' : 'Connecting…') : (arabic ? 'متابعة إلى تسجيل الدخول' : 'Continue to sign in')}
        </button>
        {status === 'error' && <p role="alert" style={{ color:'#ff8d87' }}>{message}</p>}
      </section>
    </main>
  );
}
