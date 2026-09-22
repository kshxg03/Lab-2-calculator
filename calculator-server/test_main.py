from fastapi.testclient import TestClient
import re
from main import app  # or whatever your app module is

client = TestClient(app)

def test_basic_division():
    r = client.post("/calculate", json={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", json={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_get_empty_history():
    r = client.delete("/history")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["cleared"] is True
    r = client.get("/history")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 0

def test_get_one_history():
    r = client.post("/calculate", json={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    r = client.get("/history")
    assert r.status_code == 200
    h = r.json()
    assert len(h) == 1
    assert h[0]['expr'] == "6%"
    assert abs(h[0]['result'] - 0.06) < 1e-9

def test_get_three_history():
    r = client.delete("/history")
    assert r.status_code == 200
    for expr in ["6%", "100 - 6%", "30/4"]:
        r = client.post("/calculate", json={"expr": expr})
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True

    r = client.get("/history")
    assert r.status_code == 200
    h = r.json()
    assert len(h) == 3
    for i, (expr, expected) in enumerate([("30/4", 7.5), ("100 - 6%", 94.0), ("6%", 0.06)]):
        assert h[i]['expr'] == expr
        assert abs(h[i]['result'] - expected) < 1e-9