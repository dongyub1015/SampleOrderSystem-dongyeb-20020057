"""ReleaseView — 출고 처리 print() 전담."""
from view.console_view import ConsoleView


class ReleaseView:
    """출고 목록·결과 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_release_header(self) -> None:
        self._console.print_title("[출고 처리]")

    def print_confirmed_orders_numbered(self, orders: list) -> None:
        """번호 포함 CONFIRMED 목록 (번호 선택 UX용)."""
        self._console.print_title("출고 가능 주문 (CONFIRMED)")
        if not orders:
            self._console.print_info("출고 가능한 주문이 없습니다.")
            return
        headers = ["번호", "주문번호", "고객명", "시료명", "수량"]
        rows = [
            [f"[{i + 1}]", o.order_id, o.customer_name, o.sample_name, f"{o.quantity} ea"]
            for i, o in enumerate(orders)
        ]
        self._console.print_table(headers, rows)

    def print_confirmed_orders(self, orders: list) -> None:
        self._console.print_title("출고 대기 주문 (CONFIRMED)")
        if not orders:
            self._console.print_info("출고 가능한 주문이 없습니다.")
            return
        headers = ["주문번호", "시료명", "고객명", "수량"]
        rows = [[o.order_id, o.sample_name, o.customer_name, str(o.quantity)] for o in orders]
        self._console.print_table(headers, rows)

    def print_release_result(self, order) -> None:
        self._console.print_success(f"출고 완료: {order.order_id}")
        print(f"  시료: {order.sample_name}  수량: {order.quantity} ea")
        if order.released_at:
            print(f"  처리 일시: {order.released_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  상태: {order.status.value}")

    def print_error(self, msg: str) -> None:
        self._console.print_error(msg)
