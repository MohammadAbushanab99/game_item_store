from datetime import date
from decimal import Decimal
from app.repositories.order_repository import OrderRepository
from app.schemas.report import SalesReport, SalesRow


class SalesReportUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, date_from: date | None, date_to: date | None) -> SalesReport:
        raw_rows = self.order_repository.sales_by_day_and_country(date_from, date_to)
        rows = [SalesRow(**row) for row in raw_rows]
        return SalesReport(
            rows=rows,
            total_orders=sum((r.orders for r in rows)),
            total_revenue=sum((r.revenue for r in rows), Decimal("0")),
        )
