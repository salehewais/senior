import { useState } from 'react';
import { ScrollView, Text, TextInput, View } from 'react-native';

import { errorMessage } from '../api/errors';
import { createOrder } from '../api/resources';
import { describeCartTotal } from '../cart';
import { cartStore, useCart } from '../cartStore';
import { formatMoney } from '../money';
import { sessionNotices } from '../notices';
import { ErrorText, LinkButton, Note, PrimaryButton, styles } from '../ui';

export function CartScreen({ onCheckout }: { onCheckout: () => void }) {
  const lines = useCart();

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Cart</Text>
      <Note>
        The cart is kept on this device. It is not an order until checkout.
      </Note>
      {lines.length === 0 ? (
        <Text style={styles.body}>The cart is empty.</Text>
      ) : (
        lines.map(line => (
          <View key={line.productId} style={styles.card}>
            <Text style={styles.body}>
              {line.name} ({line.sku}) ·{' '}
              {formatMoney(line.unitAmountMinor, line.currency)} each
            </Text>
            <Text style={styles.label}>Quantity for {line.name}</Text>
            <TextInput
              accessibilityLabel={`Quantity for ${line.name}`}
              keyboardType="number-pad"
              onChangeText={value => {
                const next = Number(value);
                if (Number.isInteger(next) && next >= 1) {
                  cartStore.setQuantity(line.productId, next);
                }
              }}
              style={styles.input}
              value={String(line.quantity)}
            />
            <LinkButton
              label={`Remove ${line.name}`}
              onPress={() => cartStore.remove(line.productId)}
            />
          </View>
        ))
      )}
      <Text style={styles.body}>{describeCartTotal(lines)}</Text>
      <Note>The server recomputes the real total.</Note>
      {lines.length > 0 ? (
        <PrimaryButton label="Checkout" onPress={onCheckout} />
      ) : null}
    </ScrollView>
  );
}

export function CheckoutScreen({
  onPlaced,
}: {
  onPlaced: (orderId: string) => void;
}) {
  const lines = useCart();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function placeOrder() {
    setPending(true);
    setError(null);
    try {
      const order = await createOrder(lines);
      cartStore.clear();
      sessionNotices.add(`Placed order ${order.id}.`);
      onPlaced(order.id);
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Checkout</Text>
      <ErrorText message={error} />
      {lines.length === 0 ? (
        <Text style={styles.body}>The cart is empty.</Text>
      ) : (
        <>
          {lines.map(line => (
            <Text key={line.productId} style={styles.body}>
              {line.name} · quantity {line.quantity}
            </Text>
          ))}
          <Text style={styles.body}>{describeCartTotal(lines)}</Text>
          <Note>
            The server recomputes the real total. This screen does not send a
            price.
          </Note>
          <PrimaryButton
            disabled={pending}
            label={pending ? 'Placing order…' : 'Place order'}
            onPress={() => {
              placeOrder().catch(() => undefined);
            }}
          />
        </>
      )}
    </ScrollView>
  );
}
