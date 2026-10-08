import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { errorMessage } from "../api/errors";
import { createProduct, getProduct, listProducts } from "../api/resources";
import type { Product } from "../api/types";
import { useSession } from "../auth/session";
import { cartStore } from "../cartStore";
import { ErrorText } from "../components/Chrome";
import { formatMoney, parseDollarsToMinor } from "../money";

const PAGE_SIZE = 20;

function readOffset(raw: string | null): number {
  if (!raw || !/^\d+$/.test(raw)) return 0;
  const value = Number(raw);
  return Number.isSafeInteger(value) ? value : 0;
}

export function ProductListPage() {
  const snapshot = useSession();
  const [params, setParams] = useSearchParams();
  const offset = readOffset(params.get("offset"));
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    document.title = "Products · Storefront";
  }, []);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void listProducts(PAGE_SIZE, offset)
      .then((page) => {
        if (!cancelled) setProducts(page.items);
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
  }, [offset, reload]);

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
    setNotice(added ? `${product.name} added to the cart.` : "Inactive products cannot be added to the cart.");
  }

  const hasPrevious = offset > 0;
  const hasNext = products !== null && products.length === PAGE_SIZE;

  return (
    <>
      <h1>Products</h1>
      {/* role is an unverified payload claim; see readAccessClaims. The API still rejects a forged admin token. */}
      {snapshot.role === "admin" ? <NewProductForm onCreated={() => setReload((value) => value + 1)} /> : null}
      <ErrorText message={error} />
      {notice ? (
        <p role="status" className="note">
          {notice}
        </p>
      ) : null}
      {products === null ? <p className="status">Loading products…</p> : null}
      {products !== null && products.length === 0 ? <p>No products on this page.</p> : null}
      <ul className="stack">
        {products?.map((product) => (
          <li key={product.id}>
            <Link to={`/products/${product.id}`}>{product.name}</Link>
            <p>
              {product.sku} · {formatMoney(product.unit_price.amount_minor, product.unit_price.currency)}
              {product.active ? "" : " · Inactive"}
            </p>
            <button type="button" onClick={() => add(product)} disabled={!product.active}>
              {product.active ? "Add to cart" : "Unavailable"}
            </button>
          </li>
        ))}
      </ul>
      <div className="row">
        <button
          type="button"
          disabled={!hasPrevious}
          onClick={() => setParams({ offset: String(Math.max(0, offset - PAGE_SIZE)) })}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={!hasNext}
          onClick={() => setParams({ offset: String(offset + PAGE_SIZE) })}
        >
          Next
        </button>
      </div>
    </>
  );
}

function NewProductForm({ onCreated }: { onCreated: () => void }) {
  const [sku, setSku] = useState("");
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const amountMinor = parseDollarsToMinor(price);
    if (amountMinor === null) {
      setError("Enter a price in dollars with at most two decimal places, such as 12.50.");
      return;
    }
    if (!/^[A-Za-z]{3}$/.test(currency.trim())) {
      setError("Currency must be a three-letter code.");
      return;
    }
    setPending(true);
    setError(null);
    try {
      await createProduct({
        sku,
        name,
        amountMinor,
        currency: currency.trim().toUpperCase(),
      });
      setSku("");
      setName("");
      setPrice("");
      onCreated();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <form className="panel" onSubmit={(event) => void onSubmit(event)}>
      <h2>New product</h2>
      <ErrorText message={error} />
      <label htmlFor="product-sku">SKU</label>
      <input id="product-sku" value={sku} required maxLength={64} onChange={(event) => setSku(event.target.value)} />
      <label htmlFor="product-name">Name</label>
      <input id="product-name" value={name} required maxLength={200} onChange={(event) => setName(event.target.value)} />
      <label htmlFor="product-price">Price in dollars</label>
      <input
        id="product-price"
        inputMode="decimal"
        value={price}
        required
        onChange={(event) => setPrice(event.target.value)}
      />
      <label htmlFor="product-currency">Currency</label>
      <input
        id="product-currency"
        value={currency}
        required
        maxLength={3}
        onChange={(event) => setCurrency(event.target.value)}
      />
      <button type="submit" disabled={pending} aria-busy={pending}>
        {pending ? "Saving…" : "Save product"}
      </button>
    </form>
  );
}

export function ProductDetailPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    document.title = "Product · Storefront";
  }, []);

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setError(null);
    void getProduct(productId)
      .then((found) => {
        if (!cancelled) setProduct(found);
      })
      .catch((caught: unknown) => {
        if (!cancelled) setError(errorMessage(caught));
      });
    return () => {
      cancelled = true;
    };
  }, [productId]);

  function add() {
    if (!product) return;
    const added = cartStore.add(
      {
        id: product.id,
        sku: product.sku,
        name: product.name,
        unitAmountMinor: product.unit_price.amount_minor,
        currency: product.unit_price.currency,
        active: product.active,
      },
      quantity,
    );
    setNotice(added ? "Added to the cart." : "Inactive products cannot be added to the cart.");
  }

  return (
    <>
      <p>
        <Link to="/products">Back to products</Link>
      </p>
      <h1>{product?.name ?? "Product"}</h1>
      <ErrorText message={error} />
      {notice ? (
        <p role="status" className="note">
          {notice}
        </p>
      ) : null}
      {product ? (
        <>
          <p>
            {product.sku} · {formatMoney(product.unit_price.amount_minor, product.unit_price.currency)}
            {product.active ? "" : " · Inactive"}
          </p>
          <label htmlFor="detail-quantity">Quantity</label>
          <input
            id="detail-quantity"
            type="number"
            min={1}
            step={1}
            value={quantity}
            onChange={(event) => {
              const next = Number(event.target.value);
              if (Number.isInteger(next) && next >= 1) setQuantity(next);
            }}
          />
          <button type="button" onClick={add} disabled={!product.active}>
            {product.active ? "Add to cart" : "Unavailable"}
          </button>
        </>
      ) : error ? null : (
        <p className="status">Loading product…</p>
      )}
    </>
  );
}
