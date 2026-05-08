"""ReleaseController — 출고 처리 input() 처리 (번호 선택 UX)."""
from service.release_service import ReleaseService
from view.release_view import ReleaseView


class ReleaseController:
    """출고 목록·실행 메뉴 처리 — ui-flow.md [6] 번호 선택 방식."""

    def __init__(self, release_service: ReleaseService, view: ReleaseView):
        self._svc = release_service
        self._view = view

    def run(self) -> None:
        """CONFIRMED 목록 표시 → 번호 선택 → 출고 실행."""
        self._view.print_release_header()
        orders = self._svc.list_confirmed_orders()
        self._view.print_confirmed_orders_numbered(orders)

        if not orders:
            return

        raw = input("출고할 번호 (0: 뒤로) > ").strip()
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

        try:
            order = self._svc.release_order(orders[idx].order_id)
            self._view.print_release_result(order)
        except Exception as e:
            self._view.print_error(str(e))
