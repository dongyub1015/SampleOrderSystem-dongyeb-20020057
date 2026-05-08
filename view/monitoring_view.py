"""MonitoringView — 모니터링 print() 전담."""
from view.console_view import ConsoleView


class MonitoringView:
    """주문 현황·재고 현황 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_monitoring_menu(self) -> None:
        self._console.print_title("[모니터링]")
        print("  [1] 주문 현황")
        print("  [2] 재고 현황")
        print("  [0] 뒤로")

    def print_order_status(self, orders_by_status: dict) -> None:
        """상태별 주문 현황 출력 (REJECTED 제외)."""
        self._console.print_title("주문 현황")
        for status, orders in orders_by_status.items():
            print(f"\n[{status}] — {len(orders)}건")
            if not orders:
                print("  (없음)")
                continue
            headers = ["주문번호", "시료명", "고객명", "수량"]
            rows = [[o.order_id, o.sample_name, o.customer_name, str(o.quantity)] for o in orders]
            self._console.print_table(headers, rows)

    def print_stock_status(self, stock_items: list) -> None:
        """시료별 재고 현황 출력."""
        self._console.print_title("재고 현황")
        if not stock_items:
            self._console.print_info("등록된 시료가 없습니다.")
            return
        headers = ["시료 ID", "이름", "재고(ea)", "pending", "상태"]
        rows = [
            [item["id"], item["name"], str(item["stock"]),
             str(item["pending"]), item["stock_status"]]
            for item in stock_items
        ]
        self._console.print_table(headers, rows)

    def print_error(self, msg: str) -> None:
        self._console.print_error(msg)
