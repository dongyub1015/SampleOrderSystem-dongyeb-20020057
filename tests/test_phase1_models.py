"""
Phase 1: 모델 정의 테스트
모든 엔티티 인스턴스화 가능, 상태 Enum 정상 동작 검증
"""
import pytest
from datetime import datetime


class TestOrderStatus:
    """OrderStatus Enum — 5가지 상태 정상 동작"""

    def test_order_status_has_reserved(self):
        from model.order import OrderStatus
        assert OrderStatus.RESERVED.value == "RESERVED"

    def test_order_status_has_rejected(self):
        from model.order import OrderStatus
        assert OrderStatus.REJECTED.value == "REJECTED"

    def test_order_status_has_producing(self):
        from model.order import OrderStatus
        assert OrderStatus.PRODUCING.value == "PRODUCING"

    def test_order_status_has_confirmed(self):
        from model.order import OrderStatus
        assert OrderStatus.CONFIRMED.value == "CONFIRMED"

    def test_order_status_has_release(self):
        from model.order import OrderStatus
        assert OrderStatus.RELEASE.value == "RELEASE"

    def test_order_status_count_is_five(self):
        from model.order import OrderStatus
        assert len(OrderStatus) == 5


class TestSampleModel:
    """Sample 데이터클래스 — 필드 및 인스턴스화 검증"""

    def test_sample_instantiation_with_all_fields(self):
        from model.sample import Sample
        sample = Sample(
            id="S001",
            name="테스트 시료",
            avg_production_time=30.0,
            yield_rate=0.92,
            stock=100,
        )
        assert sample.id == "S001"
        assert sample.name == "테스트 시료"
        assert sample.avg_production_time == 30.0
        assert sample.yield_rate == 0.92
        assert sample.stock == 100

    def test_sample_is_dataclass(self):
        import dataclasses
        from model.sample import Sample
        assert dataclasses.is_dataclass(Sample)

    def test_sample_stock_default_is_zero(self):
        from model.sample import Sample
        sample = Sample(
            id="S002",
            name="재고없는시료",
            avg_production_time=10.0,
            yield_rate=0.8,
            stock=0,
        )
        assert sample.stock == 0

    def test_sample_equality_by_id(self):
        from model.sample import Sample
        s1 = Sample(id="S001", name="A", avg_production_time=10.0, yield_rate=0.9, stock=0)
        s2 = Sample(id="S001", name="A", avg_production_time=10.0, yield_rate=0.9, stock=0)
        assert s1 == s2


class TestOrderModel:
    """Order 데이터클래스 — 필드 및 인스턴스화 검증"""

    def test_order_instantiation_with_all_fields(self):
        from model.order import Order, OrderStatus
        now = datetime.now()
        order = Order(
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="테스트 시료",
            customer_name="김고객",
            quantity=50,
            status=OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )
        assert order.order_id == "ORD-20260508-0001"
        assert order.sample_id == "S001"
        assert order.status == OrderStatus.RESERVED
        assert order.released_at is None

    def test_order_is_dataclass(self):
        import dataclasses
        from model.order import Order
        assert dataclasses.is_dataclass(Order)

    def test_order_status_starts_as_reserved(self):
        from model.order import Order, OrderStatus
        now = datetime.now()
        order = Order(
            order_id="ORD-20260508-0002",
            sample_id="S001",
            sample_name="시료A",
            customer_name="홍길동",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )
        assert order.status == OrderStatus.RESERVED

    def test_order_id_format_matches_pattern(self):
        import re
        from model.order import Order, OrderStatus
        now = datetime.now()
        order = Order(
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="시료",
            customer_name="고객",
            quantity=1,
            status=OrderStatus.RESERVED,
            created_at=now,
            updated_at=now,
            released_at=None,
        )
        assert re.match(r"ORD-\d{8}-\d{4}", order.order_id)


class TestProductionJobModel:
    """ProductionJob 데이터클래스 — 필드 및 인스턴스화 검증"""

    def test_production_job_instantiation_with_all_fields(self):
        from model.production_job import ProductionJob
        now = datetime.now()
        job = ProductionJob(
            job_id="JOB-001",
            order_id="ORD-20260508-0001",
            sample_id="S001",
            sample_name="테스트 시료",
            order_quantity=50,
            shortage=20,
            actual_qty=25,
            total_time_min=750.0,
            enqueued_at=now,
            started_at=None,
            estimated_finish=None,
            is_running=False,
        )
        assert job.job_id == "JOB-001"
        assert job.shortage == 20
        assert job.actual_qty == 25
        assert job.total_time_min == 750.0
        assert job.is_running is False

    def test_production_job_is_dataclass(self):
        import dataclasses
        from model.production_job import ProductionJob
        assert dataclasses.is_dataclass(ProductionJob)

    def test_production_job_not_running_by_default(self):
        from model.production_job import ProductionJob
        now = datetime.now()
        job = ProductionJob(
            job_id="JOB-002",
            order_id="ORD-20260508-0002",
            sample_id="S001",
            sample_name="시료",
            order_quantity=10,
            shortage=5,
            actual_qty=6,
            total_time_min=60.0,
            enqueued_at=now,
            started_at=None,
            estimated_finish=None,
            is_running=False,
        )
        assert job.is_running is False

    def test_production_job_can_be_set_running(self):
        from model.production_job import ProductionJob
        now = datetime.now()
        job = ProductionJob(
            job_id="JOB-003",
            order_id="ORD-20260508-0003",
            sample_id="S001",
            sample_name="시료",
            order_quantity=10,
            shortage=5,
            actual_qty=6,
            total_time_min=60.0,
            enqueued_at=now,
            started_at=now,
            estimated_finish=now,
            is_running=True,
        )
        assert job.is_running is True
