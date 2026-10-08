import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { errorMessage } from "../api/errors";
import { createOrder } from "../api/resources";
import { describeCartTotal } from "../cart";
import { cartStore, useCart } from "../cartStore";
import { ErrorText } from "../components/Chrome";
import { formatMoney } from "../money";

export function CartPage() {
  const lines = useCart();

  useEffect(() => {
    document.title = "Cart · Storefront";
  }, []);

  return (
    <>
      <h1>Cart</h1>
      <p className="note">The cart is kept in this browser. It is not an order until checkout.</p>
      {lines.length === 0 ? (
        <p>
          The cart is empty. <Link to="/products">Browse products</Link>
        </p>
      ) : (
        <ul className="stack">
          {lines.map((line) => (
            <li key={line.productId}>
              <p>
                {line.name} ({line.sku}) · {formatMoney(line.unitAmountMinor, line.currency)} each
              </p>
              <label htmlFor={`qty-${line.productId}`}>Quantity for {line.name}</label>
              <input
                id={`qty-${line.productId}`}
                type="number"
                min={1}
                step={1}
                value={line.quantity}
                onChange={(event) => {
                  const next = Number(event.target.value);
                  if (Number.isInteger(next) && next >= 1) cartStore.setQuantity(line.productId, next);
                }}
              />
              <button type="button" onClick={() => cartStore.remove(line.productId)}>
                Remove {line.name}
              </button>
            </li>
          ))}
        </ul>
      )}
      <p>{describeCartTotal(lines)}</p>
      <p className="note">The server recomputes the real total.</p>
      {lines.length > 0 ? (
        <p>
          <Link to="/checkout">Checkout</Link>
        </p>
      ) : null}
    </>
  );
}

export function CheckoutPage() {
  const lines = useCart();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    document.title = "Checkout · Storefront";
  }, []);

  async function placeOrder() {
    setPending(true);
    setError(null);
    try {
      const order = await createOrder(lines);
      cartStore.clear();
      void navigate(`/orders/${order.id}`, { replace: true });
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <>
      <h1>Checkout</h1>
      <ErrorText message={error} />
      {lines.length === 0 ? (
        <p>
          The cart is empty. <Link to="/products">Browse products</Link>
        </p>
      ) : (
        <>
          <ul className="stack">
            {lines.map((line) => (
              <li key={line.productId}>
                {line.name} · quantity {line.quantity}
              </li>
            ))}
          </ul>
          <p>{describeCartTotal(lines)}</p>
          <p className="note">The server recomputes the real total. This page does not send a price.</p>
          <button type="button" onClick={() => void placeOrder()} disabled={pending} aria-busy={pending}>
            {pending ? "Placing order…" : "Place order"}
          </button>
        </>
      )}
    </>
  );
}
