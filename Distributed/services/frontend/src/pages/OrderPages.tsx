import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { errorMessage } from "../api/errors";
import { cancelOrder, confirmOrder, getOrder, listOrders } from "../api/resources";
import type { Order } from "../api/types";
import { ErrorText } from "../components/Chrome";
import { formatMoney } from "../money";

const PAGE_SIZE = 20;

export function OrderListPage() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [previous, setPrevious] = useState<(string | null)[]>([]);
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.title = "Orders · Storefront";
  }, []);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void listOrders(PAGE_SIZE, cursor)
      .then((page) => {
        if (cancelled) return;
        setOrders(page.items);
        setNextCursor(page.next_cursor);
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          setOrders([]);
          setError(errorMessage(caught));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [cursor]);

  function onNext() {
    if (!nextCursor) return;
    setPrevious((stack) => [...stack, cursor]);
    setCursor(nextCursor);
  }

  function onPrevious() {
    const prior = previous.at(-1);
    if (prior === undefined) return;
    setPrevious((stack) => stack.slice(0, -1));
    setCursor(prior);
  }

  return (
    <>
      <h1>Orders</h1>
      <ErrorText message={error} />
      {orders === null ? <p className="status">Loading orders…</p> : null}
      {orders !== null && orders.length === 0 ? <p>No orders on this page.</p> : null}
      <ul className="stack">
        {orders?.map((order) => (
          <li key={order.id}>
            <Link to={`/orders/${order.id}`}>
              {order.status} · {formatMoney(order.total.amount_minor, order.total.currency)}
            </Link>
            {order.saga_status ? <p>Saga status: {order.saga_status}</p> : null}
          </li>
        ))}
      </ul>
      <div className="row">
        <button type="button" onClick={onPrevious} disabled={previous.length === 0}>
          Previous
        </button>
        <button type="button" onClick={onNext} disabled={!nextCursor}>
          Next
        </button>
      </div>
    </>
  );
}

export function OrderPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState<"confirm" | "cancel" | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    document.title = "Order · Storefront";
  }, []);

  useEffect(() => {
    if (!orderId) return;
    let cancelled = false;
    setError(null);
    void getOrder(orderId)
      .then((found) => {
        if (!cancelled) setOrder(found);
      })
      .catch((caught: unknown) => {
        if (!cancelled) setError(errorMessage(caught));
      });
    return () => {
      cancelled = true;
    };
  }, [orderId, reload]);

  async function onConfirm() {
    if (!orderId) return;
    setPending("confirm");
    setError(null);
    try {
      setOrder(await confirmOrder(orderId));
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(null);
    }
  }

  async function onCancel() {
    if (!orderId) return;
    setPending("cancel");
    setError(null);
    try {
      setOrder(await cancelOrder(orderId));
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(null);
    }
  }

  const pendingOrder = order?.status === "PENDING";

  return (
    <>
      <p>
        <Link to="/orders">Back to orders</Link>
      </p>
      <h1>Order</h1>
      <ErrorText message={error} />
      {!order && !error ? <p className="status">Loading order…</p> : null}
      {order ? (
        <>
          <p>
            Status: {order.status}
            {order.saga_status ? ` · Saga status: ${order.saga_status}` : ""}
          </p>
          <ul className="stack">
            {order.items.map((item) => (
              <li key={`${item.product_id}-${item.sku}`}>
                {item.sku} · quantity {item.quantity} ·{" "}
                {formatMoney(item.unit_price.amount_minor, item.unit_price.currency)} each
              </li>
            ))}
          </ul>
          <p>Total: {formatMoney(order.total.amount_minor, order.total.currency)}</p>
          <p className="note">This total was computed by the order service.</p>
          {order.tracking_reference ? <p>Tracking reference: {order.tracking_reference}</p> : null}
          {order.cancel_reason ? <p>Cancel reason: {order.cancel_reason}</p> : null}
          <p className="note">Version {order.version}</p>
          <div className="row">
            {pendingOrder ? (
              <button type="button" onClick={() => void onConfirm()} disabled={pending !== null} aria-busy={pending === "confirm"}>
                {pending === "confirm" ? "Confirming…" : "Confirm order"}
              </button>
            ) : null}
            {pendingOrder ? (
              <button type="button" onClick={() => void onCancel()} disabled={pending !== null} aria-busy={pending === "cancel"}>
                {pending === "cancel" ? "Cancelling…" : "Cancel order"}
              </button>
            ) : null}
            <button type="button" onClick={() => setReload((value) => value + 1)} disabled={pending !== null}>
              Refresh status
            </button>
          </div>
        </>
      ) : null}
    </>
  );
}
