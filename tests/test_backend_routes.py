import json


def test_index_served():
    from backend_app_Version2 import create_app

    app = create_app()
    client = app.test_client()

    resp = client.get("/")
    assert resp.status_code == 200


def test_keys_endpoint(monkeypatch):
    # monkeypatch the load_keys and save_keys used by the routes to avoid writing to user home
    import backend_routes_Version2 as routes

    monkeypatch.setattr(routes, "load_keys", lambda: {"TEST_KEY": "VALUE"})
    monkeypatch.setattr(routes, "save_keys", lambda k: None)

    from backend_app_Version2 import create_app

    app = create_app()
    client = app.test_client()

    get_resp = client.get("/api/keys")
    assert get_resp.status_code == 200
    assert get_resp.is_json
    assert get_resp.get_json() == {"TEST_KEY": "VALUE"}

    post_resp = client.post("/api/keys", json={"NEW": "VALUE2"})
    assert post_resp.status_code == 200
    assert post_resp.get_json().get("status") == "ok"
