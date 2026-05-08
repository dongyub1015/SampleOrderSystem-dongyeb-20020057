"""ProductionJob (생산 작업) 엔티티 정의."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProductionJob:
    """생산 작업 엔티티.

    Attributes:
        job_id: 작업 ID (자동 생성)
        order_id: 연결된 주문번호
        sample_id: 생산할 시료 ID
        sample_name: 시료 이름 (조회 편의)
        order_quantity: 원래 주문 수량 (ea)
        shortage: 부족분 = max(0, 주문수량 - 승인 시점 재고)
        actual_qty: 실 생산량 = ceil(shortage / (yield_rate * 0.9))
        total_time_min: 총 생산 시간 = avg_production_time * actual_qty
        enqueued_at: 큐 등록 시각
        started_at: 생산 시작 시각
        estimated_finish: 예상 완료 시각
        is_running: True=현재 생산 중 / False=대기 중
    """
    job_id: str
    order_id: str
    sample_id: str
    sample_name: str
    order_quantity: int
    shortage: int
    actual_qty: int
    total_time_min: float
    enqueued_at: datetime
    started_at: Optional[datetime]
    estimated_finish: Optional[datetime]
    is_running: bool
