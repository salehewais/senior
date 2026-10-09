import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';

import { errorMessage } from '../api/errors';
import { getProduct, listProducts } from '../api/resources';
import type { Product } from '../api/types';
import { cartStore } from '../cartStore';
import { formatMoney } from '../money';
import { ErrorText, LinkButton, Note, PrimaryButton, styles } from '../ui';

const PAGE_SIZE = 20;

export function CatalogScreen({
  onOpenProduct,
}: {
  onOpenProduct: (productId: string) => void;
}) {
  const [offset, setOffset] = useState(0);
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    listProducts(PAGE_SIZE, offset)
      .then(page => {
        if (!cancelled) {
          setProducts(page.items);
        }
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          setProducts([]);
          setError(errorMessage(caught));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [offset]);

  function add(product: Product) {
    const added = cartStore.add(
      {
        id: product.id,
        sku: product.sku,
        name: product.name,
        unitAmountMinor: product.unit_price.amount_minor,
        currency: product.unit_price.currency,
        active: product.active,
      },
      1,
    );
    setNotice(
      added
        ? `${product.name} added to the cart.`
        : 'Inactive products cannot be added to the cart.',
    );
  }

  const hasPrevious = offset > 0;
  const hasNext = products !== null && products.length === PAGE_SIZE;

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Products</Text>
      <Note>
        Prices come from the order service. The cart is on this device.
      </Note>
      <ErrorText message={error} />
      {notice ? <Note>{notice}</Note> : null}
      {products === null ? (
        <Text style={styles.body}>Loading products…</Text>
      ) : null}
      {products !== null && products.length === 0 ? (
        <Text style={styles.body}>No products on this page.</Text>
      ) : null}
      {products?.map(product => (
        <View key={product.id} style={styles.card}>
          <Text style={styles.body}>
            {product.name} ({product.sku})
          </Text>
          <Text style={styles.note}>
            {formatMoney(
              product.unit_price.amount_minor,
              product.unit_price.currency,
            )}
            {product.active ? '' : ' · inactive'}
          </Text>
          <LinkButton
            label={`Open ${product.name}`}
            onPress={() => onOpenProduct(product.id)}
          />
          <PrimaryButton
            label={`Add ${product.name}`}
            onPress={() => add(product)}
          />
        </View>
      ))}
      <View style={styles.row}>
        <PrimaryButton
          disabled={!hasPrevious}
          label="Previous"
          onPress={() => setOffset(current => Math.max(0, current - PAGE_SIZE))}
        />
        <PrimaryButton
          disabled={!hasNext}
          label="Next"
          onPress={() => setOffset(current => current + PAGE_SIZE)}
        />
      </View>
    </ScrollView>
  );
}

export function ProductScreen({
  productId,
  onBack,
}: {
  productId: string;
  onBack: () => void;
}) {
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getProduct(productId)
      .then(found => {
        if (!cancelled) {
          setProduct(found);
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
  }, [productId]);

  function add() {
    if (!product) {
      return;
    }
    const added = cartStore.add(
      {
        id: product.id,
        sku: product.sku,
        name: product.name,
        unitAmountMinor: product.unit_price.amount_minor,
        currency: product.unit_price.currency,
        active: product.active,
      },
      1,
    );
    setNotice(
      added
        ? `${product.name} added to the cart.`
        : 'Inactive products cannot be added to the cart.',
    );
  }

  return (
    <View style={styles.screen}>
      <LinkButton label="Back to products" onPress={onBack} />
      <Text style={styles.title}>Product</Text>
      <ErrorText message={error} />
      {notice ? <Note>{notice}</Note> : null}
      {product ? (
        <View style={styles.card}>
          <Text style={styles.body}>
            {product.name} ({product.sku})
          </Text>
          <Text style={styles.note}>
            {formatMoney(
              product.unit_price.amount_minor,
              product.unit_price.currency,
            )}
          </Text>
          <PrimaryButton label="Add to cart" onPress={add} />
        </View>
      ) : error ? null : (
        <Text style={styles.body}>Loading product…</Text>
      )}
    </View>
  );
}
