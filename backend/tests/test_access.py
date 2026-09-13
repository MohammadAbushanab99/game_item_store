from tests.conftest import login

RESTRICTED = ("restricted", "Restrict@12345")


def _user_id(client, admin, username: str) -> int:
    users = client.get("/api/v1/admin/users", headers=admin).json()
    return next((u["id"] for u in users if u["username"] == username))


def test_restricted_user_sees_only_allowed_countries(client):
    body = client.get("/api/v1/countries", headers=login(client, *RESTRICTED)).json()
    assert {c["code"] for c in body} == {"JO"}


def test_restricted_user_lists_only_allowed_products(client):
    body = client.get("/api/v1/products", headers=login(client, *RESTRICTED)).json()
    assert body["total_items"] == 14
    assert all((item["location"] == "JO" for item in body["items"]))


def test_restricted_user_cannot_open_disallowed_product(client):
    headers = login(client, *RESTRICTED)
    assert client.get("/api/v1/products/1", headers=headers).status_code == 200
    assert client.get("/api/v1/products/2", headers=headers).status_code == 404


def test_restricted_user_cannot_buy_disallowed_product(client):
    headers = login(client, *RESTRICTED)
    sa = {"items": [{"product_id": 2, "quantity": 1}]}
    jo = {"items": [{"product_id": 1, "quantity": 1}]}
    assert client.post("/api/v1/orders", json=sa, headers=headers).status_code == 404
    assert client.post("/api/v1/orders", json=jo, headers=headers).status_code == 201


def test_admin_sees_everything(client):
    admin = login(client, "admin", "Admin@12345")
    body = client.get("/api/v1/products", headers=admin).json()
    assert body["total_items"] == 26


def test_admin_lists_users_with_access(client):
    admin = login(client, "admin", "Admin@12345")
    users = {
        u["username"]: u
        for u in client.get("/api/v1/admin/users", headers=admin).json()
    }
    assert users["restricted"]["countries"] == ["JO"]
    assert users["restricted"]["has_all_countries"] is False
    assert users["admin"]["is_admin"] is True


def test_non_admin_cannot_list_users(client):
    assert (
        client.get(
            "/api/v1/admin/users", headers=login(client, *RESTRICTED)
        ).status_code
        == 403
    )


def test_admin_can_grant_more_countries(client):
    admin = login(client, "admin", "Admin@12345")
    uid = _user_id(client, admin, "restricted")
    res = client.put(
        f"/api/v1/admin/users/{uid}/access",
        json={"has_all_countries": False, "countries": ["JO", "SA"]},
        headers=admin,
    )
    assert res.status_code == 200
    assert set(res.json()["countries"]) == {"JO", "SA"}
    assert (
        client.get("/api/v1/products/2", headers=login(client, *RESTRICTED)).status_code
        == 200
    )


def test_admin_can_grant_all_countries(client):
    admin = login(client, "admin", "Admin@12345")
    uid = _user_id(client, admin, "restricted")
    client.put(
        f"/api/v1/admin/users/{uid}/access",
        json={"has_all_countries": True, "countries": []},
        headers=admin,
    )
    body = client.get("/api/v1/products", headers=login(client, *RESTRICTED)).json()
    assert body["total_items"] == 26


def test_admin_rejects_unknown_country_in_access(client):
    admin = login(client, "admin", "Admin@12345")
    uid = _user_id(client, admin, "restricted")
    res = client.put(
        f"/api/v1/admin/users/{uid}/access",
        json={"has_all_countries": False, "countries": ["US"]},
        headers=admin,
    )
    assert res.status_code == 400
