"""ReleaseController — 출고 처리 input() 처리."""
from service.release_service import ReleaseService
from view.release_view import ReleaseView


class ReleaseController:
    """출고 목록·실행 메뉴 처리."""

    def __init__(self, release_service: ReleaseService, view: ReleaseView):
        self._svc = release_service
        self._view = view

    def run(self) -> None:
        """출고 처리 서브 메뉴."""
        while True:
            print("\n[출고 처리]")
            print("  [1] 출고 대기 목록")
            print("  [2] 출고 실행")
            print("  [0] 뒤로")
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.list_confirmed()
                case "2":
                    self.release_order()
                case "0":
                    break
                case _:
                    print("[오류] 올바른 메뉴를 선택하세요.")

    def list_confirmed(self) -> None:
        orders = self._svc.list_confirmed_orders()
        self._view.print_confirmed_orders(orders)

    def release_order(self) -> None:
        order_id = input("출고할 주문번호 > ").strip()
        try:
            order = self._svc.release_order(order_id)
            self._view.print_release_result(order)
        except Exception as e:
            print(f"[오류] {e}")
