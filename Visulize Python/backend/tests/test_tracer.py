from fastapi.testclient import TestClient

from app.main import app
from app.runner import run_trace


def _names(bindings):
    return {item["name"]: item["value"] for item in bindings}


def test_assignment():
    result = run_trace("x = 1\ny = x + 2\n")
    assert result["error"] is None
    assert result["stopped"] is None
    found = False
    for step in result["steps"]:
        names = _names(step["globals"])
        if names.get("x") == {"kind": "int", "v": 1} and names.get("y") == {"kind": "int", "v": 3}:
            found = True
    assert found


def test_function_call_and_return():
    code = "def add(x, y):\n    return x + y\n\nresult = add(1, 2)\n"
    result = run_trace(code)
    assert result["error"] is None
    steps = result["steps"]
    assert any(step["event"] == "call" and step["func"] == "add" for step in steps)
    assert any(step["event"] == "return" and step["func"] == "add" for step in steps)

    saw_call = False
    saw_frame_gone = False
    for step in steps:
        funcs = [frame["func"] for frame in step["stack"]]
        if step["event"] == "call" and step["func"] == "add":
            saw_call = True
            assert "add" in funcs
            locals_ = _names(next(frame["locals"] for frame in step["stack"] if frame["func"] == "add"))
            assert locals_["x"] == {"kind": "int", "v": 1}
            assert locals_["y"] == {"kind": "int", "v": 2}
        if saw_call and step["func"] == "<module>" and "add" not in funcs:
            saw_frame_gone = True
    assert saw_frame_gone

    returned = next(step for step in steps if step["event"] == "return" and step["func"] == "add")
    assert returned["return_value"] == {"kind": "int", "v": 3}
    names = _names(steps[-1]["globals"])
    assert names["result"] == {"kind": "int", "v": 3}


def test_list_aliasing():
    result = run_trace("nums = [10, 20]\nalias = nums\n")
    assert result["error"] is None
    found = False
    for step in result["steps"]:
        names = _names(step["globals"])
        nums = names.get("nums")
        alias = names.get("alias")
        if not nums or not alias:
            continue
        assert nums["kind"] == "ref"
        assert alias["kind"] == "ref"
        assert nums["id"] == alias["id"]
        heap_object = step["heap"][str(nums["id"])]
        assert heap_object["kind"] == "list"
        assert heap_object["items"] == [{"kind": "int", "v": 10}, {"kind": "int", "v": 20}]
        found = True
    assert found


def test_print_stdout():
    result = run_trace('print("hi")\n')
    assert result["error"] is None
    assert any("hi" in step["stdout"] for step in result["steps"])


def test_input_reads_stdin():
    result = run_trace("name = input()\n", stdin="Ada\n")
    assert result["error"] is None
    found = False
    for step in result["steps"]:
        names = _names(step["globals"])
        if names.get("name") == {"kind": "str", "v": "Ada"}:
            found = True
    assert found


def test_class_instance_and_shared_object():
    code = (
        "class Counter:\n"
        "    def __init__(self, start):\n"
        "        self.value = start\n"
        "\n"
        "    def bump(self):\n"
        "        self.value = self.value + 1\n"
        "\n"
        "first = Counter(10)\n"
        "second = first\n"
        "second.bump()\n"
    )
    result = run_trace(code)
    assert result["error"] is None
    assert any(step["event"] == "call" and step["func"] == "__init__" for step in result["steps"])
    assert any(step["event"] == "call" and step["func"] == "bump" for step in result["steps"])

    step = result["steps"][-1]
    names = _names(step["globals"])
    assert names["first"]["kind"] == "ref"
    assert names["first"]["id"] == names["second"]["id"]
    instance = step["heap"][str(names["first"]["id"])]
    assert instance["kind"] == "instance"
    assert instance["type"] == "Counter"
    attrs = {item["name"]: item["value"] for item in instance["attrs"]}
    assert attrs["value"] == {"kind": "int", "v": 11}

    class_object = step["heap"][str(names["Counter"]["id"])]
    assert class_object["kind"] == "class"
    methods = {item["name"] for item in class_object["attrs"]}
    assert {"__init__", "bump"} <= methods
    bump = next(item for item in class_object["attrs"] if item["name"] == "bump")
    assert step["heap"][str(bump["value"]["id"])]["params"] == ["self"]


def test_subclass_records_bases():
    result = run_trace("class A:\n    pass\nclass B(A):\n    def greet(self, name):\n        return name\n")
    step = result["steps"][-1]
    names = _names(step["globals"])
    klass = step["heap"][str(names["B"]["id"])]
    assert klass["kind"] == "class"
    assert klass["bases"] == ["A"]
    greet = next(item for item in klass["attrs"] if item["name"] == "greet")
    assert step["heap"][str(greet["value"]["id"])]["params"] == ["self", "name"]


def test_syntax_error():
    result = run_trace("def (\n")
    assert result["steps"] == []
    assert result["error"]["type"] == "SyntaxError"
    assert result["error"]["line"] == 1


def test_zero_division_partial_trace():
    result = run_trace("x = 1\ny = x / 0\n")
    assert result["error"] is None
    assert result["steps"]
    assert any(
        any(item["name"] == "x" and item["value"] == {"kind": "int", "v": 1} for item in step["globals"])
        for step in result["steps"]
    )
    exceptions = [step["exception"] for step in result["steps"] if step["exception"]]
    assert exceptions
    assert exceptions[-1]["type"] == "ZeroDivisionError"
    assert result["steps"][-1]["exception"]["type"] == "ZeroDivisionError"


def test_step_limit_on_tight_loop():
    result = run_trace("while True:\n    x = 1\n", max_steps=40)
    assert result["error"] is None
    assert result["stopped"] == "step_limit"
    assert result["steps"]
    assert len(result["steps"]) <= 40


def test_health_and_trace_api():
    client = TestClient(app)
    assert client.get("/api/health").json() == {"ok": True}
    response = client.post("/api/trace", json={"code": "x = 1\n", "stdin": ""})
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["stopped"] is None
    assert any(
        item["name"] == "x" and item["value"] == {"kind": "int", "v": 1}
        for step in body["steps"]
        for item in step["globals"]
    )
