"""Order 엔티티 + OrderStatus Enum 정의."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderStatus(Enum):
    """주문 상태 열거형."""
    RESERVED  = "RESERVED"   # 주문 접수
    REJECTED  = "REJECTED"   # 주문 거절
    PRODUCING = "PRODUCING"  # 생산 중
    CONFIRMED = "CONFIRMED"  # 출고 대기
    RELEASE   = "RELEASE"    # 출고 완료


@dataclass
class Order:
    """주문 엔티티."""
    order_id: str           # 주문번호 (ORD-YYYYMMDD-NNNN)
    sample_id: str          # 시료 ID (Sample.id 참조)
    sample_name: str        # 시료 이름 (조회 편의)
    customer_name: str      # 고객명
    quantity: int           # 주문 수량 (ea)
    status: OrderStatus     # 현재 주문 상태
    created_at: datetime    # 주문 접수 시각
    updated_at: datetime    # 상태 변경 시각
    released_at: Optional[datetime]  # 출고 처리 시각 (RELEASE 시 기록)
