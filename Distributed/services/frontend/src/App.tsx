import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { RequireAuth, SessionGate, Shell } from "./components/Chrome";
import { LoginPage, RegisterPage } from "./pages/AuthPages";
import { CartPage, CheckoutPage } from "./pages/CartPages";
import { ProductDetailPage, ProductListPage } from "./pages/CatalogPages";
import { OrderListPage, OrderPage } from "./pages/OrderPages";

export function App() {
  return (
    <BrowserRouter>
      <SessionGate>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<Shell />}>
              <Route path="/" element={<Navigate to="/products" replace />} />
              <Route path="/products" element={<ProductListPage />} />
              <Route path="/products/:productId" element={<ProductDetailPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/orders" element={<OrderListPage />} />
              <Route path="/orders/:orderId" element={<OrderPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/products" replace />} />
        </Routes>
      </SessionGate>
    </BrowserRouter>
  );
}
