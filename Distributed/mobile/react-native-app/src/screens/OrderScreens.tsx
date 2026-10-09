import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';

import { errorMessage } from '../api/errors';
import {
  cancelOrder,
  confirmOrder,
  getOrder,
  listOrders,
} from '../api/resources';
import type { Order } from '../api/types';
import { formatMoney } from '../money';
import { sessionNotices } from '../notices';
import { ErrorText, LinkButton, Note, PrimaryButton, styles } from '../ui';

const PAGE_SIZE = 20;

export function OrdersScreen({
  onOpenOrder,
}: {
  onOpenOrder: (orderId: string) => void;
}) {
  const [cursor, setCursor] = useState<string | null>(null);
  const [previous, setPrevious] = useState<(string | null)[]>([]);
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    listOrders(PAGE_SIZE, cursor)
      .then(page => {
        if (cancelled) {
          return;
        }
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

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Orders</Text>
      <ErrorText message={error} />
      {orders === null ? (
        <Text style={styles.body}>Loading orders…</Text>
      ) : null}
      {orders !== null && orders.length === 0 ? (
        <Text style={styles.body}>No orders on this page.</Text>
      ) : null}
      {orders?.map(order => (
        <View key={order.id} style={styles.card}>
          <LinkButton
            label={`${order.status} · ${formatMoney(
              order.total.amount_minor,
              order.total.currency,
            )}`}
            onPress={() => onOpenOrder(order.id)}
          />
          {order.saga_status ? (
            <Note>{`Saga status: ${order.saga_status}`}</Note>
          ) : null}
        </View>
      ))}
      <View style={styles.row}>
        <PrimaryButton
          disabled={previous.length === 0}
          label="Previous"
          onPress={() => {
            const prior = previous.at(-1);
            if (prior === undefined) {
              return;
            }
            setPrevious(stack => stack.slice(0, -1));
            setCursor(prior);
          }}
        />
        <PrimaryButton
          disabled={!nextCursor}
          label="Next"
          onPress={() => {
            if (!nextCursor) {
              return;
            }
            setPrevious(stack => [...stack, cursor]);
            setCursor(nextCursor);
          }}
        />
      </View>
    </ScrollView>
  );
}

export function OrderScreen({
  orderId,
  onBack,
}: {
  orderId: string;
  onBack: () => void;
}) {
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState<'confirm' | 'cancel' | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getOrder(orderId)
      .then(found => {
        if (!cancelled) {
          setOrder(found);
        }
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          setError(errorMessage(caught));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [orderId]);

  async function onConfirm() {
    setPending('confirm');
    setError(null);
    try {
      const next = await confirmOrder(orderId);
      setOrder(next);
      sessionNotices.add(`Confirmed order ${orderId}.`);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(null);
    }
  }

  async function onCancel() {
    setPending('cancel');
    setError(null);
    try {
      const next = await cancelOrder(orderId);
      setOrder(next);
      sessionNotices.add(`Cancelled order ${orderId}.`);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(null);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <LinkButton label="Back to orders" onPress={onBack} />
      <Text style={styles.title}>Order</Text>
      <ErrorText message={error} />
      {order ? (
        <View style={styles.card}>
          <Text style={styles.body}>Status: {order.status}</Text>
          {order.saga_status ? (
            <Note>{`Saga status: ${order.saga_status}`}</Note>
          ) : null}
          <Text style={styles.body}>
            Total: {formatMoney(order.total.amount_minor, order.total.currency)}
          </Text>
          {order.items.map(item => (
            <Text key={`${item.product_id}-${item.sku}`} style={styles.note}>
              {item.sku} · quantity {item.quantity} ·{' '}
              {formatMoney(
                item.unit_price.amount_minor,
                item.unit_price.currency,
              )}
            </Text>
          ))}
          {order.tracking_reference ? (
            <Note>{`Tracking: ${order.tracking_reference}`}</Note>
          ) : null}
          {order.cancel_reason ? (
            <Note>{`Cancel reason: ${order.cancel_reason}`}</Note>
          ) : null}
          {order.status === 'PENDING' ? (
            <View style={styles.row}>
              <PrimaryButton
                disabled={pending !== null}
                label={pending === 'confirm' ? 'Confirming…' : 'Confirm'}
                onPress={() => {
                  onConfirm().catch(() => undefined);
                }}
              />
              <PrimaryButton
                disabled={pending !== null}
                label={pending === 'cancel' ? 'Cancelling…' : 'Cancel'}
                onPress={() => {
                  onCancel().catch(() => undefined);
                }}
              />
            </View>
          ) : null}
        </View>
      ) : error ? null : (
        <Text style={styles.body}>Loading order…</Text>
      )}
    </ScrollView>
  );
}
