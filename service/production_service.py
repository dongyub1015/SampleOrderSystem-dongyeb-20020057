"""ProductionService — 생산 라인 비즈니스 로직."""
import uuid
from datetime import datetime, timedelta
from math import ceil
from typing import Optional

from model.order import Order, OrderStatus
from model.production_job import ProductionJob
from repository.order_repository import OrderRepository
from repository.production_repository import ProductionRepository
from repository.sample_repository import SampleRepository


class ProductionService:
    """생산 수량 계산·큐 관리·완료 처리 서비스."""

    def __init__(
        self,
        prod_repo: ProductionRepository,
        order_repo: OrderRepository,
        sample_repo: SampleRepository,
    ):
        self._prod_repo = prod_repo
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def calculate_actual_qty(self, shortage: int, yield_rate: float) -> int:
        """실 생산량 = ceil(부족분 / (수율 * 0.9))."""
        if shortage <= 0:
            return 0
        return ceil(shortage / (yield_rate * 0.9))

    def calculate_total_time(self, avg_production_time: float, actual_qty: int) -> float:
        """총 생산 시간 = 평균 생산시간 * 실 생산량."""
        return avg_production_time * actual_qty

    def _calculate_estimated_finish(self, total_time_min: float, now: datetime, running=None) -> datetime:
        """새 작업의 예상 완료 시각 계산.

        실행 중 작업이 없으면 now + own_time.
        있으면 running.estimated_finish + 대기 중 작업 합산 + own_time.
        """
        if running is None:
            running = self._prod_repo.find_running()
        waiting = self._prod_repo.find_waiting()

        if running is None:
            return now + timedelta(minutes=total_time_min)

        base_time = running.estimated_finish or (
            (running.started_at or now) + timedelta(minutes=running.total_time_min)
        )
        waiting_total = sum(j.total_time_min for j in waiting)
        return base_time + timedelta(minutes=waiting_total + total_time_min)

    def create_production_job(self, order: Order) -> ProductionJob:
        """주문에 대한 생산 작업 생성 및 큐 등록."""
        sample = self._sample_repo.find_by_id(order.sample_id)
        shortage = max(0, order.quantity - sample.stock)
        actual_qty = self.calculate_actual_qty(shortage, sample.yield_rate)
        total_time_min = self.calculate_total_time(sample.avg_production_time, actual_qty)

        now = datetime.now()
        running = self._prod_repo.find_running()
        is_first = running is None
        estimated_finish = self._calculate_estimated_finish(total_time_min, now, running)

        job = ProductionJob(
            job_id=f"JOB-{uuid.uuid4().hex[:8].upper()}",
            order_id=order.order_id,
            sample_id=order.sample_id,
            sample_name=order.sample_name,
            order_quantity=order.quantity,
            shortage=shortage,
            actual_qty=actual_qty,
            total_time_min=total_time_min,
            enqueued_at=now,
            started_at=now if is_first else None,
            estimated_finish=estimated_finish,
            is_running=is_first,
        )
        self._prod_repo.enqueue(job)
        return job

    def complete_production(self, order_id: str) -> Order:
        """생산 완료 처리: PRODUCING → CONFIRMED, 재고 반영, 다음 작업 시작."""
        job = self._prod_repo.find_by_order_id(order_id)
        if job is None:
            raise ValueError(f"No production job found for order {order_id}")
        if not job.is_running:
            raise ValueError(f"해당 작업은 현재 실행 중이 아닙니다: {order_id}")

        # 재고 반영 (actual_qty >= shortage 이므로 stock >= quantity 보장)
        sample = self._sample_repo.find_by_id(job.sample_id)
        self._sample_repo.update_stock(job.sample_id, sample.stock + job.actual_qty)

        # 주문 상태 변경
        updated_order = self._order_repo.update_status(order_id, OrderStatus.CONFIRMED)

        # 완료된 작업 제거 후 다음 작업 시작
        self._prod_repo.complete_job(job.job_id)
        waiting = self._prod_repo.find_waiting()
        if waiting:
            self._prod_repo.mark_running(waiting[0].job_id, datetime.now())

        return updated_order

    def get_current_production(self) -> Optional[ProductionJob]:
        """현재 실행 중인 생산 작업 반환."""
        return self._prod_repo.find_running()

    def get_waiting_queue(self) -> list[ProductionJob]:
        """대기 중인 생산 작업 목록 (FIFO 순서)."""
        return self._prod_repo.find_waiting()
