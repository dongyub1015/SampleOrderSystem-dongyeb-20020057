"""OrderController — 시료 주문 접수 input() 처리."""
from exceptions import RecordNotFoundError
from service.order_service import OrderService
from view.order_view import OrderView


class OrderController:
    """주문 접수 메뉴 처리."""

    def __init__(self, order_service: OrderService, view: OrderView):
        self._svc = order_service
        self._view = view

    def run(self) -> None:
        """주문 접수 서브 메뉴."""
        while True:
            self._view.print_order_menu()
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.place_order()
                case "2":
                    self.list_all_orders()
                case "0":
                    break
                case _:
                    self._view.print_error("올바른 메뉴를 선택하세요.")

    def place_order(self) -> None:
        sample_id = input("시료 ID > ").strip()
        customer_name = input("고객명 > ").strip()
        try:
            quantity = int(input("주문 수량 (ea) > ").strip())
        except ValueError:
            self._view.print_error("수량은 정수로 입력하세요.")
            return
        try:
            order = self._svc.place_order(sample_id, customer_name, quantity)
            self._view.print_order_placed(order)
        except RecordNotFoundError:
            self._view.print_error(f"존재하지 않는 시료 ID입니다: {sample_id}")
        except Exception as e:
            self._view.print_error(str(e))

    def list_all_orders(self) -> None:
        orders = self._svc.list_all_orders()
        self._view.print_order_list(orders)
