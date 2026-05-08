"""
Phase 2: Repository 레이어 테스트
JsonDataStore를 래핑한 CRUD 저장소 검증
"""
import os
import tempfile
import pytest
from datetime import datetime, date


@pytest.fixture
def temp_data_dir(tmp_path):
    """각 테스트마다 임시 데이터 디렉토리 사용."""
    return str(tmp_path)


# ─── SampleRepository ───────────────────────────────────────────────

class TestSampleRepository:

    def _make_repo(self, tmp_path):
        from repository.sample_repository import SampleRepository
        path = str(tmp_path / "samples.json")
        return SampleRepository(file_path=path)

    def test_save_and_find_sample_by_id(self, tmp_path):
        repo = self._make_repo(tmp_path)
        from model.sample import Sample
        sample = Sample(id="S001", name="시료A", avg_production_time=30.0, yield_rate=0.92, stock=100)
        repo.save(sample)
        found = repo.find_by_id("S001")
        assert found.id == "S001"
        assert found.name == "시료A"
        assert found.stock == 100

    def test_find_by_id_raises_when_not_found(self, tmp_path):
        from exceptions import RecordNotFoundError
        repo = self._make_repo(tmp_path)
        with pytest.raises(RecordNotFoundError):
            repo.find_by_id("NONEXISTENT")

    def test_save_duplicate_id_raises_error(self, tmp_path):
        from exceptions import DuplicateKeyError
        from model.sample import Sample
        repo = self._make_repo(tmp_path)
        sample = Sample(id="S001", name="시료A", avg_production_time=30.0, yield_rate=0.92, stock=0)
        repo.save(sample)
        with pytest.raises(DuplicateKeyError):
            repo.save(sample)

    def test_find_all_returns_all_samples(self, tmp_path):
        from model.sample import Sample
        repo = self._make_repo(tmp_path)
        repo.save(Sample(id="S001", name="A", avg_production_time=10.0, yield_rate=0.9, stock=0))
        repo.save(Sample(id="S002", name="B", avg_production_time=20.0, yield_rate=0.8, stock=10))
        all_samples = repo.find_all()
        assert len(all_samples) == 2

    def test_find_all_empty_returns_empty_list(self, tmp_path):
        repo = self._make_repo(tmp_path)
        assert repo.find_all() == []

    def test_update_stock(self, tmp_path):
        from model.sample import Sample
        repo = self._make_repo(tmp_path)
        repo.save(Sample(id="S001", name="A", avg_production_time=10.0, yield_rate=0.9, stock=50))
        repo.update_stock("S001", 80)
        found = repo.find_by_id("S001")
        assert found.stock == 80

    def test_find_by_name_keyword(self, tmp_path):
        from model.sample import Sample
        repo = self._make_repo(tmp_path)
        repo.save(Sample(id="S001", name="알파 시료", avg_production_time=10.0, yield_rate=0.9, stock=0))
        repo.save(Sample(id="S002", name="베타 시료", avg_production_time=10.0, yield_rate=0.9, stock=0))
        results = repo.find_by_name("알파")
        assert len(results) == 1
        assert results[0].id == "S001"


# ─── OrderRepository ───────────────────────────────────────────────

class TestOrderRepository:

    def _make_repo(self, tmp_path):
        from repository.order_repository import OrderRepository
        path = str(tmp_path / "orders.json")
        return OrderRepository(file_path=path)

    def _make_order(self, order_id="ORD-20260508-0001", status=None):
        from model.order import Order, OrderStatus
        s = status or OrderStatus.RESERVED
        now = datetime.now()
        return Order(
            order_id=order_id,
            sample_id="S001",
            sample_name="시료A",
            customer_name="고객A",
            quantity=10,
            status=s,
            created_at=now,
            updated_at=now,
            released_at=None,
        )

    def test_save_and_find_order_by_id(self, tmp_path):
        repo = self._make_repo(tmp_path)
        order = self._make_order()
        repo.save(order)
        found = repo.find_by_id("ORD-20260508-0001")
        assert found.order_id == "ORD-20260508-0001"
        assert found.customer_name == "고객A"

    def test_generate_order_id_format(self, tmp_path):
        repo = self._make_repo(tmp_path)
        order_id = repo.generate_order_id()
        today = date.today().strftime("%Y%m%d")
        assert order_id == f"ORD-{today}-0001"

    def test_generate_order_id_increments_daily_counter(self, tmp_path):
        repo = self._make_repo(tmp_path)
        id1 = repo.generate_order_id()
        id2 = repo.generate_order_id()
        today = date.today().strftime("%Y%m%d")
        assert id1 == f"ORD-{today}-0001"
        assert id2 == f"ORD-{today}-0002"

    def test_find_by_status_reserved(self, tmp_path):
        from model.order import OrderStatus
        repo = self._make_repo(tmp_path)
        repo.save(self._make_order("ORD-20260508-0001", OrderStatus.RESERVED))
        repo.save(self._make_order("ORD-20260508-0002", OrderStatus.CONFIRMED))
        reserved = repo.find_by_status(OrderStatus.RESERVED)
        assert len(reserved) == 1
        assert reserved[0].order_id == "ORD-20260508-0001"

    def test_find_all_returns_all_orders(self, tmp_path):
        from model.order import OrderStatus
        repo = self._make_repo(tmp_path)
        repo.save(self._make_order("ORD-20260508-0001", OrderStatus.RESERVED))
        repo.save(self._make_order("ORD-20260508-0002", OrderStatus.CONFIRMED))
        all_orders = repo.find_all()
        assert len(all_orders) == 2

    def test_update_order_status(self, tmp_path):
        from model.order import OrderStatus
        repo = self._make_repo(tmp_path)
        order = self._make_order()
        repo.save(order)
        repo.update_status("ORD-20260508-0001", OrderStatus.CONFIRMED)
        found = repo.find_by_id("ORD-20260508-0001")
        assert found.status == OrderStatus.CONFIRMED

    def test_update_released_at(self, tmp_path):
        from model.order import OrderStatus
        repo = self._make_repo(tmp_path)
        order = self._make_order(status=OrderStatus.CONFIRMED)
        repo.save(order)
        now = datetime.now()
        repo.update_released_at("ORD-20260508-0001", now)
        found = repo.find_by_id("ORD-20260508-0001")
        assert found.released_at is not None


# ─── ProductionRepository ───────────────────────────────────────────

class TestProductionRepository:

    def _make_repo(self, tmp_path):
        from repository.production_repository import ProductionRepository
        path = str(tmp_path / "production_jobs.json")
        return ProductionRepository(file_path=path)

    def _make_job(self, job_id="JOB-001", is_running=False):
        from model.production_job import ProductionJob
        now = datetime.now()
        return ProductionJob(
            job_id=job_id,
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="시료A",
            order_quantity=50,
            shortage=20,
            actual_qty=25,
            total_time_min=750.0,
            enqueued_at=now,
            started_at=now if is_running else None,
            estimated_finish=None,
            is_running=is_running,
        )

    def test_enqueue_and_find_running(self, tmp_path):
        repo = self._make_repo(tmp_path)
        job = self._make_job(is_running=True)
        repo.enqueue(job)
        running = repo.find_running()
        assert running is not None
        assert running.job_id == "JOB-001"

    def test_find_running_returns_none_when_no_running_job(self, tmp_path):
        repo = self._make_repo(tmp_path)
        assert repo.find_running() is None

    def test_find_waiting_returns_fifo_order(self, tmp_path):
        from model.production_job import ProductionJob
        repo = self._make_repo(tmp_path)
        now = datetime.now()
        import time
        j1 = ProductionJob("JOB-001", "ORD-0001", "S001", "시료A", 10, 5, 6, 60.0, now, None, None, False)
        time.sleep(0.01)
        j2 = ProductionJob("JOB-002", "ORD-0002", "S001", "시료A", 10, 5, 6, 60.0, datetime.now(), None, None, False)
        repo.enqueue(j1)
        repo.enqueue(j2)
        waiting = repo.find_waiting()
        assert waiting[0].job_id == "JOB-001"
        assert waiting[1].job_id == "JOB-002"

    def test_complete_running_job_removes_it(self, tmp_path):
        repo = self._make_repo(tmp_path)
        job = self._make_job(is_running=True)
        repo.enqueue(job)
        repo.complete_job("JOB-001")
        assert repo.find_running() is None

    def test_find_by_order_id(self, tmp_path):
        repo = self._make_repo(tmp_path)
        job = self._make_job()
        repo.enqueue(job)
        found = repo.find_by_order_id("ORD-20260508-0001")
        assert found is not None
        assert found.job_id == "JOB-001"

    def test_find_waiting_excludes_running(self, tmp_path):
        repo = self._make_repo(tmp_path)
        repo.enqueue(self._make_job("JOB-001", is_running=True))
        repo.enqueue(self._make_job("JOB-002", is_running=False))
        waiting = repo.find_waiting()
        assert len(waiting) == 1
        assert waiting[0].job_id == "JOB-002"
