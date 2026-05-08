"""ProductionRepository — JsonDataStore를 래핑한 생산 작업 저장소."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Optional

from data_store import JsonDataStore
from model.production_job import ProductionJob


class ProductionRepository:
    """생산 작업 CRUD 저장소 (FIFO 큐 지원)."""

    def __init__(self, file_path: str = "data/production_jobs.json"):
        self._store = JsonDataStore(file_path)

    def _to_model(self, record: dict) -> ProductionJob:
        return ProductionJob(
            job_id=record["job_id"],
            order_id=record["order_id"],
            sample_id=record["sample_id"],
            sample_name=record["sample_name"],
            order_quantity=int(record["order_quantity"]),
            shortage=int(record["shortage"]),
            actual_qty=int(record["actual_qty"]),
            total_time_min=float(record["total_time_min"]),
            enqueued_at=datetime.fromisoformat(record["enqueued_at"]),
            started_at=(
                datetime.fromisoformat(record["started_at"])
                if record.get("started_at")
                else None
            ),
            estimated_finish=(
                datetime.fromisoformat(record["estimated_finish"])
                if record.get("estimated_finish")
                else None
            ),
            is_running=bool(record["is_running"]),
        )

    def _to_dict(self, job: ProductionJob) -> dict:
        return {
            "job_id": job.job_id,
            "order_id": job.order_id,
            "sample_id": job.sample_id,
            "sample_name": job.sample_name,
            "order_quantity": job.order_quantity,
            "shortage": job.shortage,
            "actual_qty": job.actual_qty,
            "total_time_min": job.total_time_min,
            "enqueued_at": job.enqueued_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "estimated_finish": job.estimated_finish.isoformat() if job.estimated_finish else None,
            "is_running": job.is_running,
        }

    def enqueue(self, job: ProductionJob) -> ProductionJob:
        """생산 큐에 작업 추가."""
        record = self._to_dict(job)
        self._store.create(record, record_id=job.job_id)
        return job

    def find_running(self) -> Optional[ProductionJob]:
        """현재 실행 중인 작업 반환. 없으면 None."""
        for record in self._store.read_all():
            if record["is_running"]:
                return self._to_model(record)
        return None

    def find_waiting(self) -> list[ProductionJob]:
        """대기 중인 작업 목록 (enqueued_at ASC = FIFO 순서)."""
        waiting = [
            self._to_model(r)
            for r in self._store.read_all()
            if not r["is_running"]
        ]
        return sorted(waiting, key=lambda j: j.enqueued_at)

    def find_by_order_id(self, order_id: str) -> Optional[ProductionJob]:
        """주문번호로 생산 작업 조회."""
        for record in self._store.read_all():
            if record["order_id"] == order_id:
                return self._to_model(record)
        return None

    def complete_job(self, job_id: str) -> None:
        """생산 작업 완료 처리 — 저장소에서 제거."""
        self._store.delete(job_id)

    def mark_running(self, job_id: str, started_at: datetime) -> ProductionJob:
        """작업을 실행 중 상태로 변경."""
        record = self._store.update(job_id, {
            "is_running": True,
            "started_at": started_at.isoformat(),
        })
        return self._to_model(record)
