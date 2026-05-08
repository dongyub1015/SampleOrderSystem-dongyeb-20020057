"""Sample (시료) 엔티티 정의."""
from dataclasses import dataclass


@dataclass
class Sample:
    """시료 엔티티.

    Attributes:
        id: 시료 ID (시스템 내 고유)
        name: 시료 이름
        avg_production_time: 평균 생산시간 (min/ea)
        yield_rate: 수율 (0 < yield_rate <= 1.0)
        stock: 현재 재고 수량 (ea, 0 이상)
    """
    id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int
