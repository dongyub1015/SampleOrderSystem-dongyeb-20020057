"""
Phase 5: 통합 테스트
전체 시나리오 검증 — 시료 등록 → 주문 → 승인 → 생산 → 출고
"""
import pytest
from datetime import datetime
from math import ceil


def make_all(tmp_path):
    """전체 스택 인스턴스 생성 헬퍼."""
    from repository.sample_repository import SampleRepository
    from repository.order_repository import OrderRepository
    from repository.production_repository import ProductionRepository
    from service.sample_service import SampleService
    from service.production_service import ProductionService
    from service.order_service import OrderService
    from service.release_service import ReleaseService

    sample_repo = SampleRepository(file_path=str(tmp_path / "samples.json"))
    order_repo = OrderRepository(file_path=str(tmp_path / "orders.json"))
    prod_repo = ProductionRepository(file_path=str(tmp_path / "jobs.json"))

    sample_svc = SampleService(sample_repo=sample_repo)
    prod_svc = ProductionService(prod_repo=prod_repo, order_repo=order_repo, sample_repo=sample_repo)
    order_svc = OrderService(order_repo=order_repo, sample_repo=sample_repo, production_service=prod_svc)
    release_svc = ReleaseService(order_repo=order_repo, sample_repo=sample_repo)

    return sample_svc, order_svc, prod_svc, release_svc


class TestScenario1_SufficientStock:
    """시나리오 1: 시료 등록 → 주문 접수 → 재고 충분 승인 → 출고."""

    def test_full_flow_sufficient_stock(self, tmp_path):
        from model.order import OrderStatus
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)

        # 시료 등록
        sample_svc.register_sample("S001", "AlphaChip", 30.0, 0.92, 100)

        # 주문 접수
        order = order_svc.place_order("S001", "삼성전자", 50)
        assert order.status == OrderStatus.RESERVED

        # 재고 충분 승인 → CONFIRMED
        approved = order_svc.approve_order(order.order_id)
        assert approved.status == OrderStatus.CONFIRMED

        # 출고
        released = release_svc.release_order(order.order_id)
        assert released.status == OrderStatus.RELEASE
        assert released.released_at is not None

        # 재고 차감 확인
        sample = sample_svc.get_sample("S001")
        assert sample.stock == 50  # 100 - 50


class TestScenario2_InsufficientStock:
    """시나리오 2: 재고 부족 → 생산 → CONFIRMED → 출고."""

    def test_full_flow_insufficient_stock(self, tmp_path):
        from model.order import OrderStatus
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)

        # 시료 등록 (재고 5ea)
        sample_svc.register_sample("S001", "BetaChip", 20.0, 0.80, 5)

        # 주문 접수 (50ea — 재고 부족)
        order = order_svc.place_order("S001", "SK하이닉스", 50)

        # 재고 부족 승인 → PRODUCING
        approved = order_svc.approve_order(order.order_id)
        assert approved.status == OrderStatus.PRODUCING

        # 생산 완료 처리 → CONFIRMED + 재고 반영
        prod_svc.complete_production(order.order_id)

        from repository.order_repository import OrderRepository
        from repository.sample_repository import SampleRepository
        order_repo = OrderRepository(file_path=str(tmp_path / "orders.json"))
        sample_repo = SampleRepository(file_path=str(tmp_path / "samples.json"))

        updated_order = order_repo.find_by_id(order.order_id)
        assert updated_order.status == OrderStatus.CONFIRMED

        # shortage=45, actual_qty=ceil(45/(0.80*0.9))=ceil(62.5)=63
        expected_actual = ceil(45 / (0.80 * 0.9))
        sample = sample_repo.find_by_id("S001")
        assert sample.stock == 5 + expected_actual

        # 출고
        released = release_svc.release_order(order.order_id)
        assert released.status == OrderStatus.RELEASE
        final_stock = sample_repo.find_by_id("S001").stock
        assert final_stock == 5 + expected_actual - 50


class TestScenario3_RejectedOrderExcludedFromMonitoring:
    """시나리오 3: 주문 거절 후 모니터링에 미표시."""

    def test_rejected_order_not_in_active_statuses(self, tmp_path):
        from model.order import OrderStatus
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)
        sample_svc.register_sample("S001", "시료", 10.0, 0.9, 100)
        order = order_svc.place_order("S001", "고객", 10)
        order_svc.reject_order(order.order_id)

        # REJECTED 제외 상태에서 조회
        for status in [OrderStatus.RESERVED, OrderStatus.PRODUCING,
                       OrderStatus.CONFIRMED, OrderStatus.RELEASE]:
            orders = order_svc.list_orders_by_status(status)
            ids = [o.order_id for o in orders]
            assert order.order_id not in ids, \
                f"Rejected order appeared in {status.value} list"


class TestScenario4_FIFOProductionQueue:
    """시나리오 4: 생산 큐 FIFO 순서 확인."""

    def test_production_queue_fifo_order(self, tmp_path):
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)
        sample_svc.register_sample("S001", "시료", 10.0, 0.9, 0)  # 재고 0 → 모두 PRODUCING

        o1 = order_svc.place_order("S001", "고객A", 10)
        o2 = order_svc.place_order("S001", "고객B", 10)
        o3 = order_svc.place_order("S001", "고객C", 10)

        order_svc.approve_order(o1.order_id)  # → running (첫 번째)
        order_svc.approve_order(o2.order_id)  # → waiting[0]
        order_svc.approve_order(o3.order_id)  # → waiting[1]

        running = prod_svc.get_current_production()
        waiting = prod_svc.get_waiting_queue()

        assert running.order_id == o1.order_id
        assert waiting[0].order_id == o2.order_id
        assert waiting[1].order_id == o3.order_id

    def test_next_job_starts_after_completion(self, tmp_path):
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)
        sample_svc.register_sample("S001", "시료", 10.0, 0.9, 0)

        o1 = order_svc.place_order("S001", "고객A", 10)
        o2 = order_svc.place_order("S001", "고객B", 10)
        order_svc.approve_order(o1.order_id)
        order_svc.approve_order(o2.order_id)

        # o1 완료 후 o2가 running으로 승격
        prod_svc.complete_production(o1.order_id)
        running = prod_svc.get_current_production()
        assert running is not None
        assert running.order_id == o2.order_id


class TestScenario5_StockStatusMonitoring:
    """시나리오 5: 재고 상태(여유/부족/고갈) 정확성 확인."""

    def _get_stock_status(self, sample, pending_qty):
        if sample.stock == 0:
            return "고갈"
        elif sample.stock < pending_qty:
            return "부족"
        else:
            return "여유"

    def test_stock_status_abundant_when_stock_exceeds_pending(self, tmp_path):
        from model.sample import Sample
        s = Sample(id="S001", name="시료", avg_production_time=10.0, yield_rate=0.9, stock=100)
        assert self._get_stock_status(s, 50) == "여유"

    def test_stock_status_shortage_when_stock_less_than_pending(self, tmp_path):
        from model.sample import Sample
        s = Sample(id="S001", name="시료", avg_production_time=10.0, yield_rate=0.9, stock=30)
        assert self._get_stock_status(s, 50) == "부족"

    def test_stock_status_depleted_when_zero(self, tmp_path):
        from model.sample import Sample
        s = Sample(id="S001", name="시료", avg_production_time=10.0, yield_rate=0.9, stock=0)
        assert self._get_stock_status(s, 0) == "고갈"

    def test_pending_qty_includes_reserved_and_producing(self, tmp_path):
        from model.order import OrderStatus
        sample_svc, order_svc, prod_svc, release_svc = make_all(tmp_path)
        sample_svc.register_sample("S001", "시료", 10.0, 0.9, 10)

        o1 = order_svc.place_order("S001", "고객A", 30)  # RESERVED
        o2 = order_svc.place_order("S001", "고객B", 20)  # → will be PRODUCING
        order_svc.approve_order(o2.order_id)  # 재고 10 < 20 → PRODUCING

        all_orders = order_svc.list_all_orders()
        pending = sum(
            o.quantity for o in all_orders
            if o.status in (OrderStatus.RESERVED, OrderStatus.PRODUCING)
        )
        # o1=30(RESERVED) + o2=20(PRODUCING) = 50
        assert pending == 50


class TestScenario6_DataPersistence:
    """시나리오 6: JSON 파일 저장·로드 검증."""

    def test_sample_persists_across_repository_instances(self, tmp_path):
        from repository.sample_repository import SampleRepository
        from model.sample import Sample

        path = str(tmp_path / "samples.json")
        repo1 = SampleRepository(file_path=path)
        repo1.save(Sample(id="S001", name="시료A", avg_production_time=30.0, yield_rate=0.92, stock=100))

        # 새 인스턴스로 다시 로드
        repo2 = SampleRepository(file_path=path)
        sample = repo2.find_by_id("S001")
        assert sample.name == "시료A"
        assert sample.stock == 100

    def test_order_persists_across_repository_instances(self, tmp_path):
        from repository.order_repository import OrderRepository
        from model.order import Order, OrderStatus

        path = str(tmp_path / "orders.json")
        repo1 = OrderRepository(file_path=path)
        now = datetime.now()
        order = Order(
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="시료A",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )
        repo1.save(order)

        repo2 = OrderRepository(file_path=path)
        loaded = repo2.find_by_id("ORD-20260508-0001")
        assert loaded.customer_name == "고객A"
        assert loaded.status == OrderStatus.RESERVED


class TestAppBootstrap:
    """Phase 5: app.py + main.py 진입점 테스트."""

    def test_app_can_be_instantiated(self, tmp_path):
        from app import App
        app = App(data_dir=str(tmp_path))
        assert app is not None

    def test_app_run_exits_on_zero_input(self, tmp_path):
        from app import App
        from unittest.mock import patch
        app = App(data_dir=str(tmp_path))
        with patch("builtins.input", return_value="0"):
            app.run()  # 무한루프 없이 종료

    def test_main_module_is_runnable(self, tmp_path):
        """main.py가 존재하고 App().run() 구조를 가진다."""
        import os
        assert os.path.exists("main.py")
        with open("main.py", encoding="utf-8") as f:
            content = f.read()
        assert "App" in content
        assert "run" in content
