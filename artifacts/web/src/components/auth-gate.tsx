import { createContext, type ReactNode, useContext, useEffect } from 'react';
import { useGetCurrentUser, getGetCurrentUserQueryKey, type User } from '@workspace/api-client-react';
import { useLocation } from 'wouter';

type AuthContextValue = { user: User | undefined };

const AuthContext = createContext<AuthContextValue>({ user: undefined });

export function useAuthUser() {
  return useContext(AuthContext).user;
}

function AuthState({ label, testId }: { label: string; testId: string }) {
  return (
    <div className="auth-state-screen" data-testid={testId}>
      <div className="auth-state-mark">W</div>
      <div className="skeleton auth-state-line" />
      <p>{label}</p>
    </div>
  );
}

export function AuthGate({ children }: { children: ReactNode }) {
  const [location, setLocation] = useLocation();
  const userQuery = useGetCurrentUser({
    query: {
      retry: false,
      queryKey: getGetCurrentUserQueryKey(),
    },
  });
  const isAuthRoute = location === '/login' || location === '/register';
  const authenticatedUser = userQuery.isError ? undefined : userQuery.data;
  const shouldRedirectToLogin = !userQuery.isLoading && !authenticatedUser && !isAuthRoute;
  const shouldRedirectHome = !userQuery.isLoading && !!authenticatedUser && isAuthRoute;

  useEffect(() => {
    if (shouldRedirectToLogin) setLocation('/login');
    if (shouldRedirectHome) setLocation('/');
  }, [setLocation, shouldRedirectHome, shouldRedirectToLogin]);

  if (userQuery.isLoading) {
    return (
      <AuthContext.Provider value={{ user: undefined }}>
        <AuthState label="Checking your session" testId="auth-state-loading" />
      </AuthContext.Provider>
    );
  }

  if (shouldRedirectToLogin) {
    return (
      <AuthContext.Provider value={{ user: undefined }}>
        <AuthState label="Taking you to sign in" testId="auth-state-redirecting" />
      </AuthContext.Provider>
    );
  }

  if (shouldRedirectHome) {
    return (
      <AuthContext.Provider value={{ user: authenticatedUser }}>
        <AuthState label="Opening your workspace" testId="auth-state-redirecting" />
      </AuthContext.Provider>
    );
  }

  return (
    <AuthContext.Provider value={{ user: authenticatedUser }}>
      {children}
    </AuthContext.Provider>
  );
}