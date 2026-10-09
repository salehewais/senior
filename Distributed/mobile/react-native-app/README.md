# Commerce React Native app

Extension Phase 6. Community CLI project `CommerceApp` at `mobile/react-native-app`. The browser storefront stays in `services/frontend`. This app calls the existing gateway paths. It does not add a gateway or a backend route.

`/home/asm/.cursor/plans/extension_phase_0_audit_35b1a0bc.plan.md` names the same screens as [docs/extension-gap-analysis.md](../../docs/extension-gap-analysis.md): auth, catalog, cart, checkout, orders, and in-app notifications. Those two pages do not name different routes. The order service has no `/cart` or `/checkout` route. Cart lines stay on the device. Checkout is `POST /api/v1/orders` with `product_id` and `quantity` only. The server prices the order. That matches `services/frontend`.

There is no notification inbox endpoint. The notifications screen lists `GET /api/v1/device-tokens` and notes this process keeps for the signed-in session. It does not show `notification_deliveries`. Email and push on the server stay the mock adapters in `services/notification-service`.

## Toolchain on this machine

Recorded when this phase started. Package numbers below are the ones npm installed, from `npm ls --depth=0`.

| Tool | What the command printed |
| --- | --- |
| Node | `v24.14.1` (`node --version`) |
| npm | `11.17.0` (`npm --version`) |
| Java runtime | `openjdk version "21.0.12.1" 2026-08-18` (`java -version`) |
| `javac` | `Command 'javac' not found` |
| `ANDROID_HOME` | unset |
| Android SDK directory | `/home/asm/Android/Sdk` exists |
| SDK platform | `platforms/android-37.0`, `Pkg.Revision=2`, `AndroidVersion.ApiLevel=37.0` |
| Build-tools | `36.0.0` |
| Platform-tools | `Pkg.Revision=37.0.1`. `adb version` printed `Android Debug Bridge version 1.0.41` and `Version 37.0.1-15733141` |
| Emulator | `Pkg.Revision=37.1.11`. `emulator -list-avds` printed `Pixel_8` |
| `adb devices` | `List of devices attached` and no serials |
| `sdkmanager` | not on `PATH`. No `cmdline-tools` directory |
| watchman | not installed |
| ruby | not installed |

`npx --yes @react-native-community/cli@latest --version` printed `20.2.0`.

`npm ls react react-native typescript jest @react-native-community/cli --depth=0` printed:

```text
├── @react-native-community/cli@20.2.0
├── jest@29.7.0
├── react-native@0.87.1
├── react@19.2.3
└── typescript@6.0.3
```

React Native doctor's supported JDK range, printed by the command below, is `>= 17 <= 20`. This machine's Java is a 21 runtime without `javac`. Doctor reported JDK `Version found: N/A`.

## Commands that were run

Init, from `/home/asm/senior/Distributed`. CocoaPods was skipped because `ruby` is not installed.

```bash
npx --yes @react-native-community/cli@latest init CommerceApp --pm npm --directory /home/asm/senior/Distributed/mobile/react-native-app --skip-git-init --install-pods false --title Commerce
```

Exit 0. The log printed `Welcome to React Native 0.87.1!` and the Android instruction `cd "/home/asm/senior/Distributed/mobile/react-native-app" && npx react-native run-android`. `run-android` was not run. The app was not installed on a device or emulator.

From `mobile/react-native-app`:

```bash
npm run typecheck
```

Exit 0. The script is `tsc --noEmit`. No TypeScript errors were printed.

```bash
npm test
```

Exit 0. Jest printed:

```text
PASS __tests__/cart.test.ts
PASS __tests__/claims.test.ts
PASS __tests__/App.test.tsx

Test Suites: 3 passed, 3 total
Tests:       9 passed, 9 total
```

```bash
npx eslint App.tsx src __tests__
```

Exit 0. ESLint printed no problems.

```bash
npx react-native doctor
```

`adb` was not on `PATH` (`/bin/sh: 1: adb: not found`). Doctor printed `Errors: 5` and `Warnings: 1`: Node.js and npm passed, Metro was not running, no device was connected, JDK was `N/A` (supported `>= 17 <= 20`), Android Studio was missing, `ANDROID_HOME` was missing, Gradlew passed, Android SDK was `Versions found: N/A` (supported `37.0.0`).

The same doctor command with `ANDROID_HOME` and `PATH` set only for that process:

```bash
ANDROID_HOME=/home/asm/Android/Sdk ANDROID_SDK_ROOT=/home/asm/Android/Sdk PATH="$PATH:/home/asm/Android/Sdk/platform-tools:/home/asm/Android/Sdk/emulator" npx react-native doctor
```

Exit 0. `ANDROID_HOME` then passed. Doctor still printed `Errors: 4` and `Warnings: 1`: no device connected, JDK `N/A`, Android Studio missing, Android SDK `Versions found: N/A` with supported `37.0.0`. The platform directory on disk is `android-37.0`. Doctor did not report that directory as version `37.0.0`.

`npx react-native run-android` was not run. There is no JDK compiler on `PATH`, and no emulator was started.

## API

Base URL is `http://127.0.0.1:8080` in `src/config.ts`. That is the gateway port in `deploy/gateway/compose.yaml`. An Android emulator would need the host alias `10.0.2.2` instead of `127.0.0.1`. That change was not made, because the app was not launched.

| Screen | HTTP |
| --- | --- |
| Sign in | `POST /api/v1/auth/login` |
| Create account | `POST /api/v1/auth/register` |
| Sign out | `POST /api/v1/auth/logout` |
| Refresh | `POST /api/v1/auth/refresh` when a call returns 401 |
| Products | `GET /api/v1/products`, `GET /api/v1/products/{id}` |
| Header name | `GET /api/v1/customers/me` |
| Checkout | `POST /api/v1/orders` |
| Orders | `GET /api/v1/orders`, `GET /api/v1/orders/{id}`, `POST …/confirm`, `POST …/cancel` with `{"reason":"customer_request"}` |
| Notifications | `GET`, `POST`, and `DELETE /api/v1/device-tokens` |

[docs/api.md](../../docs/api.md) says order create, confirm, and cancel require `Idempotency-Key`. The handlers in `services/order-service/src/order_service/presentation/routes/orders.py` do not read that header. This app does not send one.

Access and refresh tokens stay in process memory. A restart asks for sign-in again. How the gateway and the order service treat those tokens is [docs/security.md](../../docs/security.md). The cart is also only in memory. A device token saved from the notifications screen is whatever string you type, with platform `android` or `ios`. The screen does not mint an FCM token.

## FCM

FCM was not added. The app has not been launched on a device or emulator, so this phase does not add FCM credentials or a Firebase project. Server email and push stay mocks.

## Left for later extension phases

Extension Phase 7 added [docs/project-structure.md](../../docs/project-structure.md) and [docs/run-the-project.md](../../docs/run-the-project.md). Extension Phase 8 added [docs/system-architecture.html](../../docs/system-architecture.html). Extension Phase 9 is [docs/testing.md](../../docs/testing.md). Extension Phase 10 links the extension pages to [docs/rabbitmq.md](../../docs/rabbitmq.md), [docs/outbox.md](../../docs/outbox.md), [docs/kubernetes.md](../../docs/kubernetes.md), [docs/observability.md](../../docs/observability.md), [docs/testing.md](../../docs/testing.md), and [docs/security.md](../../docs/security.md).
