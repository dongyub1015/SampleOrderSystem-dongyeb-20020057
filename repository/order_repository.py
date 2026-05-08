"""OrderRepository — JsonDataStore를 래핑한 주문 저장소."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from typing import Optional

from data_store import JsonDataStore
from exceptions import RecordNotFoundError
from model.order import Order, OrderStatus


class OrderRepository:
    """주문 CRUD 저장소."""

    def __init__(self, file_path: str = "data/orders.json"):
        self._store = JsonDataStore(file_path)
        self._daily_counter: dict[str, int] = {}  # key: YYYYMMDD, value: 마지막 일련번호
        self._restore_counter()

    def _restore_counter(self) -> None:
        """재시작 시 기존 주문에서 일련번호 최댓값을 복원."""
        import re
        for record in self._store.read_all():
            m = re.match(r"ORD-(\d{8})-(\d{4})", record.get("order_id", ""))
            if m:
                date_str, seq = m.group(1), int(m.group(2))
                self._daily_counter[date_str] = max(
                    self._daily_counter.get(date_str, 0), seq
                )

    def _to_model(self, record: dict) -> Order:
        return Order(
            order_id=record["order_id"],
            sample_id=record["sample_id"],
            sample_name=record["sample_name"],
            customer_name=record["customer_name"],
            quantity=int(record["quantity"]),
            status=OrderStatus(record["status"]),
            created_at=datetime.fromisoformat(record["created_at"]),
            updated_at=datetime.fromisoformat(record["updated_at"]),
            released_at=(
                datetime.fromisoformat(record["released_at"])
                if record.get("released_at")
                else None
            ),
        )

    def _to_dict(self, order: Order) -> dict:
        return {
            "order_id": order.order_id,
            "sample_id": order.sample_id,
            "sample_name": order.sample_name,
            "customer_name": order.customer_name,
            "quantity": order.quantity,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "released_at": order.released_at.isoformat() if order.released_at else None,
        }

    def generate_order_id(self) -> str:
        """ORD-YYYYMMDD-NNNN 형식 주문번호 생성."""
        today_str = date.today().strftime("%Y%m%d")
        counter = self._daily_counter.get(today_str, 0) + 1
        self._daily_counter[today_str] = counter
        return f"ORD-{today_str}-{counter:04d}"

    def save(self, order: Order) -> Order:
        """주문 저장."""
        record = self._to_dict(order)
        self._store.create(record, record_id=order.order_id)
        return order

    def find_by_id(self, order_id: str) -> Order:
        """ID로 단건 조회. 없으면 RecordNotFoundError."""
        record = self._store.read(order_id)
        return self._to_model(record)

    def find_all(self) -> list[Order]:
        """전체 주문 목록 반환."""
        return [self._to_model(r) for r in self._store.read_all()]

    def find_by_status(self, status: OrderStatus) -> list[Order]:
        """특정 상태의 주문 목록 반환."""
        return [
            self._to_model(r)
            for r in self._store.read_all()
            if r["status"] == status.value
        ]

    def update_status(self, order_id: str, status: OrderStatus) -> Order:
        """주문 상태 업데이트."""
        now = datetime.now()
        record = self._store.update(order_id, {
            "status": status.value,
            "updated_at": now.isoformat(),
        })
        return self._to_model(record)

    def update_released_at(self, order_id: str, released_at: datetime) -> Order:
        """출고 시각 기록."""
        now = datetime.now()
        record = self._store.update(order_id, {
            "released_at": released_at.isoformat(),
            "updated_at": now.isoformat(),
        })
        return self._to_model(record)
