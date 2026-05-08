"""ApprovalController — 주문 승인/거절 input() 처리."""
from model.order import OrderStatus
from service.order_service import OrderService
from view.order_view import OrderView


class ApprovalController:
    """주문 승인·거절 메뉴 처리."""

    def __init__(self, order_service: OrderService, view: OrderView):
        self._svc = order_service
        self._view = view

    def run(self) -> None:
        """주문 승인/거절 서브 메뉴."""
        while True:
            print("\n[주문 승인/거절]")
            print("  [1] RESERVED 주문 목록")
            print("  [2] 주문 승인")
            print("  [3] 주문 거절")
            print("  [0] 뒤로")
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.list_reserved()
                case "2":
                    self.approve_order()
                case "3":
                    self.reject_order()
                case "0":
                    break
                case _:
                    print("[오류] 올바른 메뉴를 선택하세요.")

    def list_reserved(self) -> None:
        orders = self._svc.list_orders_by_status(OrderStatus.RESERVED)
        print("=== 접수 대기 주문 (RESERVED) ===")
        self._view.print_order_list(orders)

    def approve_order(self) -> None:
        order_id = input("승인할 주문번호 > ").strip()
        try:
            order = self._svc.approve_order(order_id)
            self._view.print_order_approved(order)
        except Exception as e:
            print(f"[오류] {e}")

    def reject_order(self) -> None:
        order_id = input("거절할 주문번호 > ").strip()
        try:
            order = self._svc.reject_order(order_id)
            self._view.print_order_rejected(order)
        except Exception as e:
            print(f"[오류] {e}")
