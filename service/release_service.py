"""ReleaseService — 출고 처리 비즈니스 로직."""
from datetime import datetime

from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class ReleaseService:
    """CONFIRMED 주문 출고 처리 서비스."""

    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository):
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def list_confirmed_orders(self) -> list[Order]:
        """CONFIRMED 상태의 주문 목록 반환."""
        return self._order_repo.find_by_status(OrderStatus.CONFIRMED)

    def release_order(self, order_id: str) -> Order:
        """출고 처리 — CONFIRMED → RELEASE, 재고 차감.

        Raises:
            ValueError: CONFIRMED 상태가 아닌 주문 출고 시도 시
        """
        order = self._order_repo.find_by_id(order_id)
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(
                f"CONFIRMED 상태의 주문만 출고 가능합니다. 현재 상태: {order.status.value}"
            )

        # 재고 차감
        sample = self._sample_repo.find_by_id(order.sample_id)
        new_stock = sample.stock - order.quantity
        self._sample_repo.update_stock(order.sample_id, new_stock)

        # 상태 변경 및 출고 시각 기록
        now = datetime.now()
        self._order_repo.update_status(order_id, OrderStatus.RELEASE)
        return self._order_repo.update_released_at(order_id, now)
