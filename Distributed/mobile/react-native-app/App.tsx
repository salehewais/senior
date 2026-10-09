import { useEffect, useState } from 'react';
import { Pressable, StatusBar, StyleSheet, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

import { getMe, logoutAccount } from './src/api/resources';
import { useSession } from './src/auth/session';
import { cartStore, useCart } from './src/cartStore';
import { sessionNotices } from './src/notices';
import { isTab, type Route, type TabName } from './src/routes';
import { LoginScreen, RegisterScreen } from './src/screens/AuthScreens';
import { CartScreen, CheckoutScreen } from './src/screens/CartScreens';
import { CatalogScreen, ProductScreen } from './src/screens/CatalogScreens';
import { NotificationsScreen } from './src/screens/NotificationsScreen';
import { OrderScreen, OrdersScreen } from './src/screens/OrderScreens';

const tabLabel: Record<TabName, string> = {
  catalog: 'Catalog',
  cart: 'Cart',
  orders: 'Orders',
  notifications: 'Notifications',
};

function CommerceApp() {
  const snapshot = useSession();
  const lines = useCart();
  const [stack, setStack] = useState<Route[]>([{ name: 'login' }]);
  const [displayName, setDisplayName] = useState<string | null>(null);
  const route = stack[stack.length - 1];
  const count = lines.reduce((sum, line) => sum + line.quantity, 0);

  useEffect(() => {
    if (!snapshot.accessToken) {
      setDisplayName(null);
      setStack(current =>
        current[0]?.name === 'login' || current[0]?.name === 'register'
          ? current
          : [{ name: 'login' }],
      );
      return;
    }
    let cancelled = false;
    getMe()
      .then(customer => {
        if (!cancelled) {
          setDisplayName(customer.display_name);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDisplayName(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [snapshot.accessToken]);

  function openTab(name: TabName) {
    setStack([{ name }]);
  }

  function push(next: Route) {
    setStack(current => [...current, next]);
  }

  function enterApp() {
    setStack([{ name: 'catalog' }]);
  }

  async function onLogout() {
    await logoutAccount();
    cartStore.clear();
    sessionNotices.clear();
    setStack([{ name: 'login' }]);
  }

  let screen = null;
  if (route.name === 'login') {
    screen = (
      <LoginScreen
        onLoggedIn={enterApp}
        onRegister={() => setStack([{ name: 'register' }])}
      />
    );
  } else if (route.name === 'register') {
    screen = (
      <RegisterScreen
        onRegistered={enterApp}
        onSignIn={() => setStack([{ name: 'login' }])}
      />
    );
  } else if (route.name === 'catalog') {
    screen = (
      <CatalogScreen
        onOpenProduct={productId => push({ name: 'product', productId })}
      />
    );
  } else if (route.name === 'product') {
    screen = (
      <ProductScreen
        onBack={() => openTab('catalog')}
        productId={route.productId}
      />
    );
  } else if (route.name === 'cart') {
    screen = <CartScreen onCheckout={() => push({ name: 'checkout' })} />;
  } else if (route.name === 'checkout') {
    screen = (
      <CheckoutScreen
        onPlaced={orderId => setStack([{ name: 'order', orderId }])}
      />
    );
  } else if (route.name === 'orders') {
    screen = (
      <OrdersScreen onOpenOrder={orderId => push({ name: 'order', orderId })} />
    );
  } else if (route.name === 'order') {
    screen = (
      <OrderScreen onBack={() => openTab('orders')} orderId={route.orderId} />
    );
  } else {
    screen = <NotificationsScreen />;
  }

  return (
    <SafeAreaView style={shell.safe}>
      {snapshot.accessToken ? (
        <View style={shell.header}>
          <Text style={shell.brand}>Commerce</Text>
          <Text style={shell.who}>{displayName ?? 'Signed in'}</Text>
          <Pressable
            accessibilityRole="button"
            onPress={() => {
              onLogout().catch(() => undefined);
            }}
          >
            <Text style={shell.signOut}>Sign out</Text>
          </Pressable>
        </View>
      ) : null}
      <View style={shell.body}>{screen}</View>
      {snapshot.accessToken ? (
        <View style={shell.tabs}>
          {(['catalog', 'cart', 'orders', 'notifications'] as const).map(
            name => {
              const selected = isTab(route.name) ? route.name === name : false;
              const label =
                name === 'cart' && count > 0 ? `Cart ${count}` : tabLabel[name];
              return (
                <Pressable
                  accessibilityRole="button"
                  accessibilityState={{ selected }}
                  key={name}
                  onPress={() => openTab(name)}
                  style={shell.tab}
                >
                  <Text style={selected ? shell.tabSelected : shell.tabText}>
                    {label}
                  </Text>
                </Pressable>
              );
            },
          )}
        </View>
      ) : null}
    </SafeAreaView>
  );
}

const shell = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#f7f8fa',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  brand: {
    fontSize: 18,
    fontWeight: '700',
    color: '#142033',
  },
  who: {
    flex: 1,
    color: '#445066',
  },
  signOut: {
    color: '#1d4e89',
    fontSize: 16,
  },
  body: {
    flex: 1,
  },
  tabs: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#d5dde6',
    backgroundColor: '#ffffff',
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
  },
  tabText: {
    color: '#445066',
    fontSize: 13,
  },
  tabSelected: {
    color: '#1d4e89',
    fontSize: 13,
    fontWeight: '700',
  },
});

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" />
      <CommerceApp />
    </SafeAreaProvider>
  );
}
