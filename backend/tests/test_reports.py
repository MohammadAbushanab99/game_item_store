from tests.conftest import login


def test_sales_report_totals_across_countries(client):
    demo = login(client)
    client.post("/api/v1/orders", json={"items": [{"product_id": 1}]}, headers=demo)
    client.post("/api/v1/orders", json={"items": [{"product_id": 2}]}, headers=demo)
    admin = login(client, "admin", "Admin@12345")
    report = client.get("/api/v1/admin/reports/sales", headers=admin)
    assert report.status_code == 200
    body = report.json()
    assert body["total_orders"] == 2
    assert body["total_revenue"] == "21.00"
    locations = {row["location"] for row in body["rows"]}
    assert locations == {"JO", "SA"}
    assert all((row["orders"] == 1 and row["items_sold"] == 1 for row in body["rows"]))


def test_sales_report_requires_admin(client):
    assert (
        client.get("/api/v1/admin/reports/sales", headers=login(client)).status_code
        == 403
    )
