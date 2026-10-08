import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useLocation, useNavigate } from "react-router-dom";

import { restoreSession } from "../api/client";
import { getMe, logoutAccount } from "../api/resources";
import { useSession } from "../auth/session";
import { useCart } from "../cartStore";

export function ErrorText({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p role="alert" className="error">
      {message}
    </p>
  );
}

export function SessionGate({ children }: { children: ReactNode }) {
  const snapshot = useSession();
  useEffect(() => {
    void restoreSession();
  }, []);
  if (!snapshot.ready) {
    return (
      <main>
        <p className="status">Checking your session…</p>
      </main>
    );
  }
  return children;
}

export function RequireAuth() {
  const snapshot = useSession();
  const location = useLocation();
  if (!snapshot.accessToken) {
    return <Navigate to="/login" replace state={{ from: `${location.pathname}${location.search}` }} />;
  }
  return <Outlet />;
}

export function Shell() {
  const snapshot = useSession();
  const lines = useCart();
  const navigate = useNavigate();
  const [name, setName] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const count = lines.reduce((sum, line) => sum + line.quantity, 0);

  useEffect(() => {
    if (snapshot.role !== "customer") return;
    let cancelled = false;
    void getMe()
      .then((customer) => {
        if (!cancelled) setName(customer.display_name);
      })
      .catch(() => {
        if (!cancelled) setName(null);
      });
    return () => {
      cancelled = true;
    };
  }, [snapshot.accessToken, snapshot.role]);

  async function onLogout() {
    setPending(true);
    try {
      await logoutAccount();
    } finally {
      void navigate("/login", { replace: true });
    }
  }

  const who = accountLabel(snapshot.role, name);

  return (
    <>
      <header className="top">
        <p className="brand">Storefront</p>
        <nav aria-label="Main">
          <NavLink to="/products" end>
            Products
          </NavLink>
          <NavLink to="/cart">Cart{count > 0 ? ` (${count})` : ""}</NavLink>
          <NavLink to="/orders">Orders</NavLink>
          <button type="button" onClick={() => void onLogout()} disabled={pending}>
            Log out
          </button>
        </nav>
        {who ? <p className="who">{who}</p> : null}
      </header>
      <main>
        <Outlet />
      </main>
    </>
  );
}

function accountLabel(role: string | null, name: string | null): string | null {
  if (role === "customer") return name;
  if (role === "admin") return "Admin";
  if (role === "manager") return "Manager";
  return null;
}
