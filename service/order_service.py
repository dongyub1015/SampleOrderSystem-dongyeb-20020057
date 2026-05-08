"""OrderService — 주문 접수/승인/거절 비즈니스 로직."""
from datetime import datetime

from exceptions import RecordNotFoundError
from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository
from service.production_service import ProductionService


class OrderService:
    """주문 생성·승인·거절 서비스."""

    def __init__(
        self,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
        production_service: ProductionService,
    ):
        self._order_repo = order_repo
        self._sample_repo = sample_repo
        self._prod_svc = production_service

    def place_order(self, sample_id: str, customer_name: str, quantity: int) -> Order:
        """주문 접수 — RESERVED 상태로 생성.

        Raises:
            RecordNotFoundError: 시료 ID가 존재하지 않을 때
            ValueError: 수량이 1 미만일 때
        """
        if quantity < 1:
            raise ValueError("주문 수량은 1 이상이어야 합니다.")

        # 시료 존재 확인 (없으면 RecordNotFoundError)
        sample = self._sample_repo.find_by_id(sample_id)
        order_id = self._order_repo.generate_order_id()
        now = datetime.now()
        order = Order(
            order_id=order_id,
            sample_id=sample_id,
            sample_name=sample.name,
            customer_name=customer_name,
            quantity=quantity,
            status=OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )
        return self._order_repo.save(order)

    def approve_order(self, order_id: str) -> Order:
        """주문 승인.

        재고 충분 → CONFIRMED
        재고 부족 → PRODUCING + 생산 큐 등록
        """
        order = self._order_repo.find_by_id(order_id)
        if order.status != OrderStatus.RESERVED:
            raise ValueError(f"RESERVED 상태의 주문만 승인 가능합니다. 현재 상태: {order.status.value}")

        sample = self._sample_repo.find_by_id(order.sample_id)

        # CONFIRMED 상태 주문의 선점 수량을 제외한 가용 재고로 판단
        confirmed = self._order_repo.find_by_status(OrderStatus.CONFIRMED)
        reserved = sum(o.quantity for o in confirmed if o.sample_id == order.sample_id)
        available = sample.stock - reserved

        if available >= order.quantity:
            # 재고 충분 → CONFIRMED
            return self._order_repo.update_status(order_id, OrderStatus.CONFIRMED)
        else:
            # 재고 부족 → PRODUCING + 생산 큐 등록
            updated_order = self._order_repo.update_status(order_id, OrderStatus.PRODUCING)
            self._prod_svc.create_production_job(updated_order)
            return updated_order

    def reject_order(self, order_id: str) -> Order:
        """주문 거절 — REJECTED 상태로 전환."""
        order = self._order_repo.find_by_id(order_id)
        if order.status != OrderStatus.RESERVED:
            raise ValueError(f"RESERVED 상태의 주문만 거절 가능합니다. 현재 상태: {order.status.value}")
        return self._order_repo.update_status(order_id, OrderStatus.REJECTED)

    def list_orders_by_status(self, status: OrderStatus) -> list[Order]:
        """특정 상태의 주문 목록 반환."""
        return self._order_repo.find_by_status(status)

    def list_all_orders(self) -> list[Order]:
        """전체 주문 목록 반환."""
        return self._order_repo.find_all()
