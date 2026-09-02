import { type FormEvent, useState } from 'react';
import { getGetCurrentUserQueryKey, useLogin, useRegister } from '@workspace/api-client-react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRight, Eye, EyeOff, KeyRound, Target } from 'lucide-react';
import { Link, useLocation } from 'wouter';

type AuthMode = 'login' | 'register';

function errorMessage(error: unknown) {
  if (error instanceof Error) return error.message.replace(/^HTTP \d+ [^:]+:\s*/, '');
  return 'We could not complete that request. Try again.';
}

function AuthWordmark() {
  return (
    <div className="auth-wordmark" data-testid="display-auth-brand">
      <span className="auth-wordmark-mark"><Target size={17} /></span>
      <span>workbench</span>
    </div>
  );
}

export function AuthPage({ mode }: { mode: AuthMode }) {
  const isRegister = mode === 'register';
  const [location, setLocation] = useLocation();
  const queryClient = useQueryClient();
  const login = useLogin();
  const register = useRegister();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState('');
  const mutation = isRegister ? register : login;
  const pending = mutation.isPending;
  const mutationError = mutation.error ? errorMessage(mutation.error) : '';

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError('');
    if (isRegister && name.trim().length < 2) {
      setFormError('Use your name as you would like teammates to see it.');
      return;
    }
    if (!email.trim()) {
      setFormError('Enter the email address for your account.');
      return;
    }
    if (password.length < (isRegister ? 8 : 1)) {
      setFormError(isRegister ? 'Your password needs at least 8 characters.' : 'Enter your password.');
      return;
    }

    const onSuccess = (user: { id: number; name: string; email: string; createdAt: string }) => {
      queryClient.clear();
      queryClient.setQueryData(getGetCurrentUserQueryKey(), user);
      setLocation('/');
    };

    if (isRegister) {
      register.mutate({ data: { name: name.trim(), email: email.trim(), password } }, { onSuccess });
    } else {
      login.mutate({ data: { email: email.trim(), password } }, { onSuccess });
    }
  };

  return (
    <main className="auth-page" data-testid={`page-${mode}`}>
      <div className="auth-corner-note"><KeyRound size={14} />Private workspace access</div>
      <section className="auth-panel" aria-labelledby="auth-title">
        <AuthWordmark />
        <div className="auth-heading">
          <p className="eyebrow">Northstar / Workbench</p>
          <h1 id="auth-title">{isRegister ? 'Make space for the work.' : 'Welcome back to the room.'}</h1>
          <p>{isRegister ? 'Create an account and keep the team’s next steps in view.' : 'Sign in to pick up exactly where you left off.'}</p>
        </div>

        <form className="auth-form" onSubmit={submit} noValidate>
          {isRegister && (
            <label>
              Your name
              <input
                autoComplete="name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Your name"
                data-testid="input-register-name"
              />
            </label>
          )}
          <label>
            Email address
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              data-testid={`input-${mode}-email`}
            />
          </label>
          <label>
            Password
            <span className="auth-password-field">
              <input
                type={showPassword ? 'text' : 'password'}
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder={isRegister ? 'At least 8 characters' : 'Your password'}
                data-testid={`input-${mode}-password`}
              />
              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                data-testid={`button-${showPassword ? 'hide' : 'show'}-password`}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </span>
          </label>

          {(formError || mutationError) && (
            <div className="auth-error" role="alert" data-testid="auth-state-error">
              {formError || mutationError}
            </div>
          )}
          <button className="auth-submit" type="submit" disabled={pending} data-testid={`button-submit-${mode}`}>
            <span>{pending ? (isRegister ? 'Creating your account' : 'Signing you in') : (isRegister ? 'Create account' : 'Sign in')}</span>
            {pending ? <span className="auth-submit-dots" aria-hidden="true">···</span> : <ArrowRight size={16} />}
          </button>
          <p className="auth-state-caption" aria-live="polite" data-testid="auth-state-status">
            {pending ? 'Securing your session…' : isRegister ? 'Your session stays active on this device.' : 'Your session is protected by a secure cookie.'}
          </p>
        </form>

        <div className="auth-switch">
          <span>{isRegister ? 'Already have an account?' : 'New to Workbench?'}</span>
          <Link href={isRegister ? '/login' : '/register'} data-testid={`link-${isRegister ? 'login' : 'register'}`}>
            {isRegister ? 'Sign in' : 'Create an account'}
          </Link>
        </div>
      </section>
      <footer className="auth-footer">
        <span>Quiet tools for focused teams</span>
        <span className="auth-footer-rule" />
        <span>{location === '/register' ? '01 / 02' : '02 / 02'}</span>
      </footer>
    </main>
  );
}