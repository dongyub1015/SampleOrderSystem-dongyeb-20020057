"""
Phase 3: Service 레이어 테스트
비즈니스 로직 검증 — 주문 접수/승인/거절/생산/출고
"""
import pytest
import tempfile
from datetime import datetime
from math import ceil


# ─── Helpers ───────────────────────────────────────────────────────

def make_sample_repo(tmp_path):
    from repository.sample_repository import SampleRepository
    return SampleRepository(file_path=str(tmp_path / "samples.json"))

def make_order_repo(tmp_path):
    from repository.order_repository import OrderRepository
    return OrderRepository(file_path=str(tmp_path / "orders.json"))

def make_prod_repo(tmp_path):
    from repository.production_repository import ProductionRepository
    return ProductionRepository(file_path=str(tmp_path / "jobs.json"))

def make_sample(id="S001", name="시료A", avg_time=30.0, yield_rate=0.92, stock=100):
    from model.sample import Sample
    return Sample(id=id, name=name, avg_production_time=avg_time, yield_rate=yield_rate, stock=stock)


# ─── SampleService ─────────────────────────────────────────────────

class TestSampleService:

    def _make_service(self, tmp_path):
        from service.sample_service import SampleService
        repo = make_sample_repo(tmp_path)
        return SampleService(sample_repo=repo), repo

    def test_register_sample_succeeds(self, tmp_path):
        svc, repo = self._make_service(tmp_path)
        sample = svc.register_sample(id="S001", name="시료A", avg_production_time=30.0, yield_rate=0.92, stock=100)
        assert sample.id == "S001"
        assert repo.find_by_id("S001") is not None

    def test_register_duplicate_sample_raises(self, tmp_path):
        svc, _ = self._make_service(tmp_path)
        svc.register_sample(id="S001", name="시료A", avg_production_time=30.0, yield_rate=0.92, stock=0)
        with pytest.raises(Exception):
            svc.register_sample(id="S001", name="시료B", avg_production_time=10.0, yield_rate=0.9, stock=0)

    def test_list_samples_returns_all(self, tmp_path):
        svc, _ = self._make_service(tmp_path)
        svc.register_sample("S001", "A", 10.0, 0.9, 0)
        svc.register_sample("S002", "B", 20.0, 0.8, 5)
        samples = svc.list_samples()
        assert len(samples) == 2

    def test_search_samples_by_name(self, tmp_path):
        svc, _ = self._make_service(tmp_path)
        svc.register_sample("S001", "알파 시료", 10.0, 0.9, 0)
        svc.register_sample("S002", "베타 시료", 20.0, 0.8, 0)
        results = svc.search_samples("알파")
        assert len(results) == 1
        assert results[0].id == "S001"

    def test_get_sample_by_id(self, tmp_path):
        svc, _ = self._make_service(tmp_path)
        svc.register_sample("S001", "시료A", 30.0, 0.92, 100)
        sample = svc.get_sample("S001")
        assert sample.name == "시료A"


# ─── OrderService ──────────────────────────────────────────────────

class TestOrderService:

    def _make_services(self, tmp_path):
        from service.sample_service import SampleService
        from service.order_service import OrderService
        from service.production_service import ProductionService
        sample_repo = make_sample_repo(tmp_path)
        order_repo = make_order_repo(tmp_path)
        prod_repo = make_prod_repo(tmp_path)
        sample_svc = SampleService(sample_repo=sample_repo)
        prod_svc = ProductionService(prod_repo=prod_repo, order_repo=order_repo, sample_repo=sample_repo)
        order_svc = OrderService(order_repo=order_repo, sample_repo=sample_repo, production_service=prod_svc)
        return order_svc, sample_svc, prod_svc, sample_repo, order_repo

    def _register_sample(self, sample_svc, stock=100):
        return sample_svc.register_sample("S001", "시료A", 30.0, 0.92, stock)

    def test_place_order_creates_reserved_order(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc)
        order = order_svc.place_order(sample_id="S001", customer_name="고객A", quantity=10)
        assert order.status == OrderStatus.RESERVED
        assert order.customer_name == "고객A"

    def test_place_order_generates_order_id(self, tmp_path):
        import re
        order_svc, sample_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc)
        order = order_svc.place_order("S001", "고객A", 10)
        assert re.match(r"ORD-\d{8}-\d{4}", order.order_id)

    def test_place_order_with_unknown_sample_raises(self, tmp_path):
        order_svc, *_ = self._make_services(tmp_path)
        with pytest.raises(Exception):
            order_svc.place_order("UNKNOWN", "고객A", 10)

    def test_approve_order_with_sufficient_stock_becomes_confirmed(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc, stock=100)
        order = order_svc.place_order("S001", "고객A", 50)
        approved = order_svc.approve_order(order.order_id)
        assert approved.status == OrderStatus.CONFIRMED

    def test_approve_order_with_insufficient_stock_becomes_producing(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, prod_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc, stock=5)  # 재고 5, 주문 50 → 부족
        order = order_svc.place_order("S001", "고객A", 50)
        approved = order_svc.approve_order(order.order_id)
        assert approved.status == OrderStatus.PRODUCING

    def test_approve_order_with_insufficient_stock_creates_production_job(self, tmp_path):
        order_svc, sample_svc, prod_svc, sample_repo, order_repo = self._make_services(tmp_path)
        from repository.production_repository import ProductionRepository
        prod_repo = ProductionRepository(file_path=str(tmp_path / "jobs.json"))
        self._register_sample(sample_svc, stock=5)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)
        job = prod_repo.find_by_order_id(order.order_id)
        assert job is not None

    def test_reject_order_changes_status_to_rejected(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc)
        order = order_svc.place_order("S001", "고객A", 10)
        rejected = order_svc.reject_order(order.order_id)
        assert rejected.status == OrderStatus.REJECTED

    def test_list_reserved_orders(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, *_ = self._make_services(tmp_path)
        self._register_sample(sample_svc)
        order_svc.place_order("S001", "고객A", 10)
        order_svc.place_order("S001", "고객B", 20)
        reserved = order_svc.list_orders_by_status(OrderStatus.RESERVED)
        assert len(reserved) == 2


# ─── ProductionService ─────────────────────────────────────────────

class TestProductionService:

    def _make_services(self, tmp_path):
        from service.sample_service import SampleService
        from service.order_service import OrderService
        from service.production_service import ProductionService
        sample_repo = make_sample_repo(tmp_path)
        order_repo = make_order_repo(tmp_path)
        prod_repo = make_prod_repo(tmp_path)
        sample_svc = SampleService(sample_repo=sample_repo)
        prod_svc = ProductionService(prod_repo=prod_repo, order_repo=order_repo, sample_repo=sample_repo)
        order_svc = OrderService(order_repo=order_repo, sample_repo=sample_repo, production_service=prod_svc)
        return order_svc, sample_svc, prod_svc

    def test_actual_qty_formula(self, tmp_path):
        from service.production_service import ProductionService
        prod_svc = ProductionService(
            prod_repo=make_prod_repo(tmp_path),
            order_repo=make_order_repo(tmp_path),
            sample_repo=make_sample_repo(tmp_path),
        )
        # shortage=45, yield_rate=0.92 → ceil(45 / (0.92 * 0.9)) = ceil(45/0.828) = ceil(54.35) = 55
        actual = prod_svc.calculate_actual_qty(shortage=45, yield_rate=0.92)
        assert actual == ceil(45 / (0.92 * 0.9))

    def test_total_time_formula(self, tmp_path):
        from service.production_service import ProductionService
        prod_svc = ProductionService(
            prod_repo=make_prod_repo(tmp_path),
            order_repo=make_order_repo(tmp_path),
            sample_repo=make_sample_repo(tmp_path),
        )
        total = prod_svc.calculate_total_time(avg_production_time=30.0, actual_qty=55)
        assert total == 30.0 * 55

    def test_complete_production_changes_order_to_confirmed(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, prod_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 5)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)  # → PRODUCING, job 생성
        prod_svc.complete_production(order.order_id)
        from repository.order_repository import OrderRepository
        order_repo = OrderRepository(file_path=str(tmp_path / "orders.json"))
        updated = order_repo.find_by_id(order.order_id)
        assert updated.status == OrderStatus.CONFIRMED

    def test_complete_production_adds_stock(self, tmp_path):
        order_svc, sample_svc, prod_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 5)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)
        # shortage=45, actual_qty = ceil(45/(0.92*0.9)) = 55
        expected_actual_qty = ceil(45 / (0.92 * 0.9))
        prod_svc.complete_production(order.order_id)
        from repository.sample_repository import SampleRepository
        sample_repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
        sample = sample_repo.find_by_id("S001")
        assert sample.stock == 5 + expected_actual_qty

    def test_get_current_production_returns_running_job(self, tmp_path):
        order_svc, sample_svc, prod_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 5)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)
        running = prod_svc.get_current_production()
        assert running is not None
        assert running.order_id == order.order_id

    def test_get_waiting_queue_returns_waiting_jobs_in_fifo(self, tmp_path):
        order_svc, sample_svc, prod_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 0)
        o1 = order_svc.place_order("S001", "고객A", 10)
        o2 = order_svc.place_order("S001", "고객B", 10)
        order_svc.approve_order(o1.order_id)  # 첫 번째 → running
        order_svc.approve_order(o2.order_id)  # 두 번째 → waiting
        waiting = prod_svc.get_waiting_queue()
        assert len(waiting) == 1
        assert waiting[0].order_id == o2.order_id


# ─── ReleaseService ────────────────────────────────────────────────

class TestReleaseService:

    def _make_services(self, tmp_path):
        from service.sample_service import SampleService
        from service.order_service import OrderService
        from service.production_service import ProductionService
        from service.release_service import ReleaseService
        sample_repo = make_sample_repo(tmp_path)
        order_repo = make_order_repo(tmp_path)
        prod_repo = make_prod_repo(tmp_path)
        sample_svc = SampleService(sample_repo=sample_repo)
        prod_svc = ProductionService(prod_repo=prod_repo, order_repo=order_repo, sample_repo=sample_repo)
        order_svc = OrderService(order_repo=order_repo, sample_repo=sample_repo, production_service=prod_svc)
        release_svc = ReleaseService(order_repo=order_repo, sample_repo=sample_repo)
        return order_svc, sample_svc, prod_svc, release_svc

    def test_release_changes_status_to_release(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, prod_svc, release_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 100)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)  # → CONFIRMED (재고 충분)
        released = release_svc.release_order(order.order_id)
        assert released.status == OrderStatus.RELEASE

    def test_release_deducts_stock(self, tmp_path):
        order_svc, sample_svc, prod_svc, release_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 100)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)
        release_svc.release_order(order.order_id)
        from repository.sample_repository import SampleRepository
        sample_repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
        sample = sample_repo.find_by_id("S001")
        assert sample.stock == 50  # 100 - 50

    def test_release_sets_released_at(self, tmp_path):
        order_svc, sample_svc, prod_svc, release_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 100)
        order = order_svc.place_order("S001", "고객A", 50)
        order_svc.approve_order(order.order_id)
        released = release_svc.release_order(order.order_id)
        assert released.released_at is not None

    def test_list_confirmed_orders_for_release(self, tmp_path):
        from model.order import OrderStatus
        order_svc, sample_svc, prod_svc, release_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 200)
        o1 = order_svc.place_order("S001", "고객A", 50)
        o2 = order_svc.place_order("S001", "고객B", 30)
        order_svc.approve_order(o1.order_id)
        order_svc.approve_order(o2.order_id)
        confirmed = release_svc.list_confirmed_orders()
        assert len(confirmed) == 2

    def test_release_non_confirmed_order_raises(self, tmp_path):
        order_svc, sample_svc, prod_svc, release_svc = self._make_services(tmp_path)
        sample_svc.register_sample("S001", "시료A", 30.0, 0.92, 100)
        order = order_svc.place_order("S001", "고객A", 50)
        # RESERVED 상태 → 출고 불가
        with pytest.raises(Exception):
            release_svc.release_order(order.order_id)
