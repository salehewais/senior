"""One customer path: register or reuse, log in, browse products, create one order, read it.

Gentle mode stays under the Redis order-create limit. Flood mode crosses it on purpose.
Neither mode calls an internal route. Run instructions are in the README.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gevent.lock import Semaphore

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import scenario
from locust import HttpUser, events, task

_LOCK = Semaphore()
_SESSION = Semaphore()
_order_attempts = 0
_order_created = 0
_order_rate_limited = 0
_token: str | None = None


def _reset_counts() -> None:
    global _order_attempts, _order_created, _order_rate_limited, _token
    with _LOCK:
        _order_attempts = 0
        _order_created = 0
        _order_rate_limited = 0
    with _SESSION:
        _token = None


def _count_attempt() -> int:
    global _order_attempts
    with _LOCK:
        _order_attempts += 1
        return _order_attempts


def _count_created() -> None:
    global _order_created
    with _LOCK:
        _order_created += 1


def _count_rate_limited() -> None:
    global _order_rate_limited
    with _LOCK:
        _order_rate_limited += 1


def _counts() -> tuple[int, int, int]:
    with _LOCK:
        return _order_attempts, _order_created, _order_rate_limited


class CustomerUser(HttpUser):
    host = scenario.base_url()

    def wait_time(self) -> float:
        return scenario.wait_seconds()

    def on_start(self) -> None:
        self.ready = False
        try:
            self.auth = {"Authorization": f"Bearer {_shared_token(self)}"}
            self.product_id = _browse_for_product(self)
            self.ready = True
        except scenario.ScenarioStop as exc:
            _stop(self.environment, str(exc))

    @task
    def browse_and_order(self) -> None:
        if not getattr(self, "ready", False):
            return
        if scenario.mode() == scenario.FLOOD and _counts()[0] >= scenario.FLOOD_ORDER_ATTEMPTS:
            _quit(self.environment)
            return
        try:
            _browse_for_product(self)
            self._create_and_maybe_read()
        except scenario.ScenarioStop as exc:
            _stop(self.environment, str(exc))
            return
        if scenario.mode() == scenario.FLOOD and _counts()[0] >= scenario.FLOOD_ORDER_ATTEMPTS:
            _quit(self.environment)


    def _create_and_maybe_read(self) -> None:
        _count_attempt()
        with self.client.post(
            scenario.ORDERS_PATH,
            json=scenario.order_create_body(self.product_id),
            headers=self.auth,
            name=scenario.ORDERS_PATH,
            catch_response=True,
        ) as response:
            body = _json(response)
            created: object = None
            if response.status_code == 201:
                _count_created()
                response.success()
                created = body
            elif scenario.is_rate_limited(response.status_code, body):
                _count_rate_limited()
                if scenario.mode() == scenario.FLOOD:
                    response.success()
                else:
                    response.failure("429 RATE_LIMITED during the gentle run")
                return
            else:
                response.failure(f"POST {scenario.ORDERS_PATH} returned {response.status_code}")
                return
        _read_order(self, scenario.order_id_from_create(created))


def _shared_token(user: CustomerUser) -> str:
    """One customer for every virtual user. Later users reuse the first login."""
    global _token
    with _SESSION:
        if _token is not None:
            return _token
        email, password = _account()
        _token = _login(user, email, password)
        return _token


def _account() -> tuple[str, str]:
    existing = scenario.existing_account()
    if existing is not None:
        return existing
    email, password = scenario.new_account()
    return email, password


def _register(user: CustomerUser, email: str, password: str) -> None:
    stop: str | None = None
    with user.client.post(
        scenario.REGISTER_PATH,
        json=scenario.register_body(email, password),
        name=scenario.REGISTER_PATH,
        catch_response=True,
    ) as response:
        body = _json(response)
        if response.status_code == 201:
            response.success()
            return
        if scenario.is_rate_limited(response.status_code, body):
            response.failure("429 RATE_LIMITED on register")
            stop = scenario.REUSE_ACCOUNT
        else:
            response.failure(f"POST {scenario.REGISTER_PATH} returned {response.status_code}")
            stop = f"Register returned {response.status_code}. No account was stored for a later run."
    raise scenario.ScenarioStop(stop or "Register did not complete.")


def _login(user: CustomerUser, email: str, password: str) -> str:
    if scenario.existing_account() is None:
        _register(user, email, password)
    token: str | None = None
    stop: str | None = None
    with user.client.post(
        scenario.LOGIN_PATH,
        json=scenario.login_body(email, password),
        name=scenario.LOGIN_PATH,
        catch_response=True,
    ) as response:
        body = _json(response)
        if response.status_code == 200:
            response.success()
            try:
                token = scenario.access_token(body)
            except scenario.ScenarioStop as exc:
                stop = str(exc)
        elif scenario.is_rate_limited(response.status_code, body):
            response.failure("429 RATE_LIMITED on login")
            stop = scenario.REUSE_ACCOUNT
        else:
            response.failure(f"POST {scenario.LOGIN_PATH} returned {response.status_code}")
            stop = (
                "Login was rejected. If you set LOAD_EMAIL, check that pair. "
                "The password is not printed."
            )
    if stop or token is None:
        raise scenario.ScenarioStop(stop or "Login did not return an access token.")
    return token


def _browse_for_product(user: CustomerUser) -> str:
    body: object = None
    stop: str | None = None
    with user.client.get(
        scenario.PRODUCTS_PATH,
        headers=user.auth,
        name=scenario.PRODUCTS_PATH,
        catch_response=True,
    ) as response:
        body = _json(response)
        if response.status_code != 200:
            response.failure(f"GET {scenario.PRODUCTS_PATH} returned {response.status_code}")
            stop = f"Browse returned {response.status_code}."
        else:
            response.success()
    if stop:
        raise scenario.ScenarioStop(stop)
    return scenario.product_id_from_catalog(body, scenario.product_id_override())


def _read_order(user: CustomerUser, order_id: str) -> None:
    path = scenario.order_read_path(order_id)
    with user.client.get(
        path,
        headers=user.auth,
        name=f"{scenario.ORDERS_PATH}/{{id}}",
        catch_response=True,
    ) as response:
        if response.status_code == 200:
            response.success()
            return
        response.failure(f"GET order returned {response.status_code}")


def _json(response: object) -> object:
    try:
        return response.json()
    except ValueError:
        return None


def _quit(environment: object) -> None:
    runner = getattr(environment, "runner", None)
    if runner is not None:
        runner.quit()


def _stop(environment: object, message: str) -> None:
    print(message)
    if getattr(environment, "process_exit_code", 0) in (None, 0):
        environment.process_exit_code = 2
    _quit(environment)


def _summary(environment: object) -> scenario.RunSummary:
    stats = environment.stats.total
    # num_requests counts every call, including ones Locust also stores in num_failures.
    requests = int(stats.num_requests)
    failures = int(stats.num_failures)
    p95: float | None = None
    if requests > 0:
        try:
            p95 = float(stats.get_response_time_percentile(0.95))
        except (TypeError, ValueError, ZeroDivisionError):
            p95 = None
    _attempts, created, limited = _counts()
    return scenario.RunSummary(
        mode=scenario.mode(),
        requests=requests,
        failures=failures,
        order_created=created,
        order_rate_limited=limited,
        p95_ms=p95,
    )


def _write_note(text: str) -> None:
    Path(__file__).with_name("RESULTS.md").write_text(text, encoding="utf-8")


@events.test_start.add_listener
def _on_start(environment, **_kwargs) -> None:
    _reset_counts()
    try:
        run_mode = scenario.mode()
    except scenario.ScenarioStop as exc:
        _stop(environment, str(exc))
        return
    runner = environment.runner
    users = 0 if runner is None else int(runner.target_user_count)
    problem = scenario.shape_problem(run_mode, users)
    if problem:
        _stop(environment, problem)


@events.quitting.add_listener
def _on_quit(environment, **_kwargs) -> None:
    recorded = int(environment.stats.total.num_requests)
    if environment.runner is None or recorded == 0:
        if environment.process_exit_code in (None, 0):
            print("No requests were recorded. The stack was not called, or the run stopped first.")
        return
    summary = _summary(environment)
    ok, message = scenario.evaluate(summary)
    text = scenario.results_note(summary, ok, message)
    print(text)
    _write_note(text)
    if ok:
        return
    if environment.process_exit_code in (None, 0):
        environment.process_exit_code = 1
