from datetime import date
from app.schemas.report import SalesReport
from app.use_cases.sales_report_use_case import SalesReportUseCase


class ReportService:
    def __init__(self, sales_report_use_case: SalesReportUseCase):
        self.sales_report_use_case = sales_report_use_case

    def sales_report(self, date_from: date | None, date_to: date | None) -> SalesReport:
        return self.sales_report_use_case.execute(date_from, date_to)
