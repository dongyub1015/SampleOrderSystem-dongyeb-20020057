"""MonitoringController — 모니터링 input() 처리."""
from model.order import OrderStatus
from service.order_service import OrderService
from service.sample_service import SampleService
from view.monitoring_view import MonitoringView


class MonitoringController:
    """주문 현황·재고 현황 메뉴 처리."""

    def __init__(
        self,
        order_service: OrderService,
        sample_service: SampleService,
        view: MonitoringView,
    ):
        self._order_svc = order_service
        self._sample_svc = sample_service
        self._view = view

    def run(self) -> None:
        """모니터링 서브 메뉴."""
        while True:
            print("\n[모니터링]")
            print("  [1] 주문 현황")
            print("  [2] 재고 현황")
            print("  [0] 뒤로")
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.show_order_status()
                case "2":
                    self.show_stock_status()
                case "0":
                    break
                case _:
                    print("[오류] 올바른 메뉴를 선택하세요.")

    def show_order_status(self) -> None:
        """REJECTED 제외 상태별 주문 현황 표시."""
        visible_statuses = [
            OrderStatus.RESERVED,
            OrderStatus.PRODUCING,
            OrderStatus.CONFIRMED,
            OrderStatus.RELEASE,
        ]
        orders_by_status = {
            s.value: self._order_svc.list_orders_by_status(s)
            for s in visible_statuses
        }
        self._view.print_order_status(orders_by_status)

    def show_stock_status(self) -> None:
        """시료별 재고 및 pending 상태 표시."""
        samples = self._sample_svc.list_samples()
        # pending_qty = RESERVED + PRODUCING 상태 주문의 합산 수량
        all_orders = self._order_svc.list_all_orders()
        pending_orders = [
            o for o in all_orders
            if o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING)
        ]

        # 시료별 pending 수량 집계
        pending_by_sample: dict[str, int] = {}
        for order in pending_orders:
            pending_by_sample[order.sample_id] = (
                pending_by_sample.get(order.sample_id, 0) + order.quantity
            )

        stock_items = []
        for s in samples:
            pending = pending_by_sample.get(s.id, 0)
            if s.stock == 0:
                status = "고갈"
            elif s.stock < pending:
                status = "부족"
            else:
                status = "여유"
            stock_items.append({
                "id": s.id,
                "name": s.name,
                "stock": s.stock,
                "pending": pending,
                "stock_status": status,
            })
        self._view.print_stock_status(stock_items)
