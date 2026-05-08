"""OrderView — 주문 관련 print() 전담."""
from view.console_view import ConsoleView


class OrderView:
    """주문 목록·상세·결과 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_order_list(self, orders: list) -> None:
        if not orders:
            print("  주문이 없습니다.")
            return
        headers = ["주문번호", "시료명", "고객명", "수량", "상태"]
        rows = [
            [o.order_id, o.sample_name, o.customer_name, str(o.quantity), o.status.value]
            for o in orders
        ]
        self._console.print_table(headers, rows)

    def print_order_detail(self, order) -> None:
        print(f"주문번호: {order.order_id}")
        print(f"시료: {order.sample_name} ({order.sample_id})")
        print(f"고객명: {order.customer_name}")
        print(f"수량: {order.quantity} ea")
        print(f"상태: {order.status.value}")
        print(f"접수: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if order.released_at:
            print(f"출고: {order.released_at.strftime('%Y-%m-%d %H:%M:%S')}")

    def print_order_placed(self, order) -> None:
        print(f"[성공] 주문 접수 완료: {order.order_id}")

    def print_order_approved(self, order) -> None:
        print(f"[성공] 주문 승인: {order.order_id} → {order.status.value}")

    def print_order_rejected(self, order) -> None:
        print(f"[성공] 주문 거절: {order.order_id} → {order.status.value}")

    def print_order_released(self, order) -> None:
        print(f"[성공] 출고 완료: {order.order_id}")
        print(f"  시료: {order.sample_name}  수량: {order.quantity} ea")
        if order.released_at:
            print(f"  출고일시: {order.released_at.strftime('%Y-%m-%d %H:%M:%S')}")
