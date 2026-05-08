"""OrderView — 주문 관련 print() 전담."""
from view.console_view import ConsoleView


class OrderView:
    """주문 목록·상세·결과 출력."""

    def __init__(self):
        self._console = ConsoleView()

    # ── 메뉴 출력 ──────────────────────────────────────────────────────────────

    def print_order_menu(self) -> None:
        self._console.print_title("[시료 주문]")
        print("  [1] 주문 접수")
        print("  [2] 전체 주문 조회")
        print("  [0] 뒤로")

    def print_approval_header(self) -> None:
        self._console.print_title("[주문 승인/거절]")

    # ── 목록 출력 ──────────────────────────────────────────────────────────────

    def print_order_list(self, orders: list) -> None:
        if not orders:
            self._console.print_info("주문이 없습니다.")
            return
        headers = ["주문번호", "시료명", "고객명", "수량", "상태"]
        rows = [
            [o.order_id, o.sample_name, o.customer_name, str(o.quantity), o.status.value]
            for o in orders
        ]
        self._console.print_table(headers, rows)

    def print_reserved_list_numbered(self, orders: list) -> None:
        """승인/거절용 번호 포함 RESERVED 목록."""
        self._console.print_title("승인 대기 중인 예약 목록 (RESERVED)")
        if not orders:
            self._console.print_info("대기 중인 주문이 없습니다.")
            return
        headers = ["번호", "주문번호", "시료명", "고객명", "수량"]
        rows = [
            [f"[{i + 1}]", o.order_id, o.sample_name, o.customer_name, f"{o.quantity} ea"]
            for i, o in enumerate(orders)
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

    # ── 결과 출력 ──────────────────────────────────────────────────────────────

    def print_order_placed(self, order) -> None:
        self._console.print_success(f"주문 접수 완료: {order.order_id} (상태: {order.status.value})")

    def print_order_approved(self, order) -> None:
        self._console.print_success(f"주문 승인: {order.order_id} → {order.status.value}")

    def print_order_rejected(self, order) -> None:
        self._console.print_success(f"주문 거절: {order.order_id} → {order.status.value}")

    def print_order_released(self, order) -> None:
        self._console.print_success(f"출고 완료: {order.order_id}")
        print(f"  시료: {order.sample_name}  수량: {order.quantity} ea")
        if order.released_at:
            print(f"  출고일시: {order.released_at.strftime('%Y-%m-%d %H:%M:%S')}")

    def print_error(self, msg: str) -> None:
        self._console.print_error(msg)
