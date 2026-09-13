from tests.conftest import login


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login", json={"username": "demo", "password": "Demo@12345"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login", json={"username": "demo", "password": "wrong-pass"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_validation_error(client):
    response = client.post("/api/v1/auth/login", json={"username": "de"})
    assert response.status_code == 400
    fields = {d["field"] for d in response.json()["error"]["details"]}
    assert fields == {"username", "password"}


def test_products_require_token(client):
    assert client.get("/api/v1/products").status_code == 401
    bad = client.get("/api/v1/products", headers={"Authorization": "Bearer not-a-jwt"})
    assert bad.status_code == 401


def test_list_products_default_pagination(client):
    body = client.get("/api/v1/products", headers=login(client)).json()
    assert body["page"] == 1 and body["size"] == 12
    assert len(body["items"]) == 12
    assert body["total_items"] == 26 and body["total_pages"] == 3
    assert body["items"][0]["price"] == "10.50"


def test_list_products_filter_and_page(client):
    body = client.get(
        "/api/v1/products?location=SA&page=2&size=5", headers=login(client)
    ).json()
    assert body["total_items"] == 12
    assert len(body["items"]) == 5
    assert all((item["location"] == "SA" for item in body["items"]))


def test_list_products_invalid_page(client):
    response = client.get("/api/v1/products?page=0", headers=login(client))
    assert response.status_code == 400
    assert {d["field"] for d in response.json()["error"]["details"]} == {"page"}


def test_list_products_unknown_location_is_empty(client):
    body = client.get("/api/v1/products?location=US", headers=login(client)).json()
    assert body["total_items"] == 0 and body["items"] == []


def test_product_details_and_404(client):
    headers = login(client)
    assert client.get("/api/v1/products/1", headers=headers).json()["title"] == "Item 1"
    not_found = client.get("/api/v1/products/12345", headers=headers)
    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "NOT_FOUND"


def test_purchase_single_item_creates_bill(client):
    headers = login(client)
    response = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": 3, "quantity": 1}]},
        headers=headers,
    )
    assert response.status_code == 201
    order = response.json()
    assert order["order_number"].startswith("ORD-")
    assert order["total_amount"] == "10.50"
    assert len(order["items"]) == 1
    assert (
        order["items"][0]["product_title"] == "Item 3"
        and order["items"][0]["line_total"] == "10.50"
    )
    receipt = client.get(f"/api/v1/orders/{order['id']}", headers=headers)
    assert (
        receipt.status_code == 200
        and receipt.json()["items"][0]["product_title"] == "Item 3"
    )


def test_purchase_multiple_items_and_quantities(client):
    headers = login(client)
    body = {
        "items": [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}]
    }
    order = client.post("/api/v1/orders", json=body, headers=headers).json()
    assert len(order["items"]) == 2
    assert order["total_amount"] == "31.50"
    line1 = next((i for i in order["items"] if i["product_id"] == 1))
    assert line1["quantity"] == 2 and line1["line_total"] == "21.00"


def test_purchase_merges_duplicate_ids(client):
    headers = login(client)
    body = {
        "items": [{"product_id": 1, "quantity": 1}, {"product_id": 1, "quantity": 2}]
    }
    order = client.post("/api/v1/orders", json=body, headers=headers).json()
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 3 and order["total_amount"] == "31.50"


def test_purchase_rules(client):
    headers = login(client)
    assert (
        client.post(
            "/api/v1/orders", json={"items": [{"product_id": 12345}]}, headers=headers
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/orders", json={"items": [{"product_id": 99}]}, headers=headers
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/orders", json={"items": [{"product_id": -1}]}, headers=headers
        ).status_code
        == 400
    )
    assert (
        client.post("/api/v1/orders", json={"items": []}, headers=headers).status_code
        == 400
    )


def test_cannot_see_other_users_order(client):
    body = {"items": [{"product_id": 1, "quantity": 1}]}
    order_id = client.post("/api/v1/orders", json=body, headers=login(client)).json()[
        "id"
    ]
    other = login(client, "other", "Other@12345")
    assert client.get(f"/api/v1/orders/{order_id}", headers=other).status_code == 404
