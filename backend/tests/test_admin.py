from tests.conftest import login


def _csv(rows: str) -> dict:
    content = ("id,title,description,price,country\n" + rows).encode("utf-8")
    return {"file": ("games.csv", content, "text/csv")}


def test_login_reports_admin_flag(client):
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "Admin@12345"}
        ).json()["is_admin"]
        is True
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "demo", "password": "Demo@12345"}
        ).json()["is_admin"]
        is False
    )


def test_list_countries_available_to_any_user(client):
    body = client.get("/api/v1/countries", headers=login(client)).json()
    assert {c["code"] for c in body} == {"JO", "SA"}


def test_non_admin_cannot_add_country(client):
    res = client.post(
        "/api/v1/countries", json={"code": "AE", "name": "UAE"}, headers=login(client)
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_add_country_and_it_appears(client):
    admin = login(client, "admin", "Admin@12345")
    created = client.post(
        "/api/v1/countries",
        json={"code": "uae", "name": "United Arab Emirates"},
        headers=admin,
    )
    assert created.status_code == 201
    assert created.json()["code"] == "UAE"
    codes = {c["code"] for c in client.get("/api/v1/countries", headers=admin).json()}
    assert "UAE" in codes


def test_admin_can_add_single_product_for_new_country(client):
    admin = login(client, "admin", "Admin@12345")
    client.post(
        "/api/v1/countries",
        json={"code": "UAE", "name": "United Arab Emirates"},
        headers=admin,
    )
    res = client.post(
        "/api/v1/products",
        json={
            "title": "Desert Blade",
            "description": "A rare blade",
            "price": "199.99",
            "location": "UAE",
        },
        headers=admin,
    )
    assert res.status_code == 201
    assert res.json()["location"] == "UAE" and res.json()["price"] == "199.99"


def test_non_admin_cannot_add_product(client):
    res = client.post(
        "/api/v1/products",
        json={"title": "X", "description": "Y", "price": "1.00", "location": "JO"},
        headers=login(client),
    )
    assert res.status_code == 403


def test_import_valid_file_inserts_rows(client):
    admin = login(client, "admin", "Admin@12345")
    files = _csv("500,New Sword,Shiny,150.00,JO\n501,New Shield,Sturdy,120.50,SA\n")
    res = client.post("/api/v1/products/import", files=files, headers=admin)
    assert res.status_code == 200
    assert res.json()["inserted"] == 2
    assert (
        client.get("/api/v1/products/500", headers=admin).json()["title"] == "New Sword"
    )


def test_non_admin_cannot_import(client):
    files = _csv("500,New Sword,Shiny,150.00,JO\n")
    assert (
        client.post(
            "/api/v1/products/import", files=files, headers=login(client)
        ).status_code
        == 403
    )


def test_import_missing_column_is_general_error(client):
    admin = login(client, "admin", "Admin@12345")
    content = "id,title,description,price\n500,S,d,1.00\n".encode("utf-8")
    res = client.post(
        "/api/v1/products/import",
        files={"file": ("g.csv", content, "text/csv")},
        headers=admin,
    )
    assert res.status_code == 400
    body = res.json()["error"]
    assert body["code"] == "IMPORT_VALIDATION_ERROR"
    assert "country" in body["message"]
    assert body["details"] == []


def test_import_duplicate_id_in_file_aborts(client):
    admin = login(client, "admin", "Admin@12345")
    files = _csv("500,A,d,1.00,JO\n500,B,d,2.00,JO\n")
    res = client.post("/api/v1/products/import", files=files, headers=admin)
    assert res.status_code == 400
    assert any(
        ("duplicate id 500" in d["message"] for d in res.json()["error"]["details"])
    )
    assert client.get("/api/v1/products/500", headers=admin).status_code == 404


def test_import_existing_id_aborts(client):
    admin = login(client, "admin", "Admin@12345")
    res = client.post(
        "/api/v1/products/import", files=_csv("1,Dup,d,1.00,JO\n"), headers=admin
    )
    assert res.status_code == 400
    assert any(
        ("already exists" in d["message"] for d in res.json()["error"]["details"])
    )


def test_import_unknown_country_aborts(client):
    admin = login(client, "admin", "Admin@12345")
    res = client.post(
        "/api/v1/products/import", files=_csv("500,A,d,1.00,US\n"), headers=admin
    )
    assert res.status_code == 400
    assert any(
        (
            "unknown country" in d["message"].lower()
            for d in res.json()["error"]["details"]
        )
    )


def test_import_bad_price_aborts(client):
    admin = login(client, "admin", "Admin@12345")
    res = client.post(
        "/api/v1/products/import",
        files=_csv("500,A,d,not-a-number,JO\n"),
        headers=admin,
    )
    assert res.status_code == 400
    assert any(
        (
            "price" in d["message"] and "row 2" in d["field"]
            for d in res.json()["error"]["details"]
        )
    )


def test_import_missing_cell_aborts(client):
    admin = login(client, "admin", "Admin@12345")
    res = client.post(
        "/api/v1/products/import", files=_csv("500,,d,1.00,JO\n"), headers=admin
    )
    assert res.status_code == 400
    assert any(
        ("missing required" in d["message"] for d in res.json()["error"]["details"])
    )


def test_import_reports_all_bad_rows_and_inserts_nothing(client):
    admin = login(client, "admin", "Admin@12345")
    files = _csv("500,Good,d,1.00,JO\n501,Bad,d,xx,JO\n502,Bad2,d,1.00,US\n")
    res = client.post("/api/v1/products/import", files=files, headers=admin)
    assert res.status_code == 400
    fields = {d["field"] for d in res.json()["error"]["details"]}
    assert fields == {"row 3", "row 4"}
    assert client.get("/api/v1/products/500", headers=admin).status_code == 404
