"""ApprovalController — 주문 승인/거절 input() 처리 (번호 선택 UX)."""
from model.order import OrderStatus
from service.order_service import OrderService
from view.order_view import OrderView


class ApprovalController:
    """주문 승인·거절 메뉴 처리 — ui-flow.md [3] 번호 선택 방식."""

    def __init__(self, order_service: OrderService, view: OrderView):
        self._svc = order_service
        self._view = view

    def run(self) -> None:
        """RESERVED 목록 → 번호 선택 → 승인/거절."""
        self._view.print_approval_header()
        orders = self._svc.list_orders_by_status(OrderStatus.RESERVED)
        self._view.print_reserved_list_numbered(orders)

        if not orders:
            return

        raw = input("승인할 번호 (0: 뒤로) > ").strip()
        if raw == "0":
            return

        try:
            idx = int(raw) - 1
        except ValueError:
            self._view.print_error("번호를 입력하세요.")
            return

        if not (0 <= idx < len(orders)):
            self._view.print_error(f"1~{len(orders)} 사이의 번호를 입력하세요.")
            return

        order = orders[idx]
        action = input(f"  '{order.order_id}' — [Y] 승인  [N] 거절 > ").strip().upper()
        match action:
            case "Y":
                try:
                    updated = self._svc.approve_order(order.order_id)
                    self._view.print_order_approved(updated)
                except Exception as e:
                    self._view.print_error(str(e))
            case "N":
                try:
                    updated = self._svc.reject_order(order.order_id)
                    self._view.print_order_rejected(updated)
                except Exception as e:
                    self._view.print_error(str(e))
            case _:
                self._view.print_error("Y 또는 N을 입력하세요.")
