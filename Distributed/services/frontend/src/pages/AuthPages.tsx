import type { FormEvent } from "react";
import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { errorMessage } from "../api/errors";
import { loginAccount, registerAccount } from "../api/resources";
import { useSession } from "../auth/session";
import { ErrorText } from "../components/Chrome";

function safeNext(value: unknown): string {
  if (typeof value === "string" && value.startsWith("/") && !value.startsWith("//")) return value;
  return "/products";
}

export function LoginPage() {
  const snapshot = useSession();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (snapshot.accessToken) return <Navigate to="/products" replace />;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await loginAccount(email, password);
      const from = (location.state as { from?: unknown } | null)?.from;
      void navigate(safeNext(from), { replace: true });
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <main>
      <h1>Sign in</h1>
      <ErrorText message={error} />
      <form onSubmit={(event) => void onSubmit(event)}>
        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          name="email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label htmlFor="login-password">Password</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          minLength={8}
          maxLength={128}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button type="submit" disabled={pending} aria-busy={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p>
        <Link to="/register">Create an account</Link>
      </p>
    </main>
  );
}

export function RegisterPage() {
  const snapshot = useSession();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (snapshot.accessToken) return <Navigate to="/products" replace />;

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await registerAccount(email, displayName, password);
      void navigate("/products", { replace: true });
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <main>
      <h1>Create an account</h1>
      <p className="note">Registration creates a customer. The server chooses the role.</p>
      <ErrorText message={error} />
      <form onSubmit={(event) => void onSubmit(event)}>
        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          name="email"
          type="email"
          autoComplete="username"
          required
          maxLength={254}
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <label htmlFor="register-name">Display name</label>
        <input
          id="register-name"
          name="display_name"
          type="text"
          autoComplete="nickname"
          required
          maxLength={120}
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
        />
        <label htmlFor="register-password">Password</label>
        <input
          id="register-password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          maxLength={128}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button type="submit" disabled={pending} aria-busy={pending}>
          {pending ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p>
        <Link to="/login">Sign in</Link>
      </p>
    </main>
  );
}
