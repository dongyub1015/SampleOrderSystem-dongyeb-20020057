"""app.py — DI Root: 저장소 → 서비스 → 컨트롤러 생성·주입."""
import os

from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from repository.production_repository import ProductionRepository
from service.sample_service import SampleService
from service.production_service import ProductionService
from service.order_service import OrderService
from service.release_service import ReleaseService
from controller.main_controller import MainController


class App:
    """애플리케이션 진입점 — DI Root."""

    def __init__(self, data_dir: str = "data"):
        os.makedirs(data_dir, exist_ok=True)

        # 저장소 인스턴스 생성 (싱글턴 공유)
        sample_repo = SampleRepository(
            file_path=os.path.join(data_dir, "samples.json")
        )
        order_repo = OrderRepository(
            file_path=os.path.join(data_dir, "orders.json")
        )
        prod_repo = ProductionRepository(
            file_path=os.path.join(data_dir, "production_jobs.json")
        )

        # 서비스 인스턴스 생성 (저장소 주입)
        sample_svc = SampleService(sample_repo=sample_repo)
        prod_svc = ProductionService(
            prod_repo=prod_repo,
            order_repo=order_repo,
            sample_repo=sample_repo,
        )
        order_svc = OrderService(
            order_repo=order_repo,
            sample_repo=sample_repo,
            production_service=prod_svc,
        )
        release_svc = ReleaseService(
            order_repo=order_repo,
            sample_repo=sample_repo,
        )

        # 메인 컨트롤러 생성 (서비스 주입)
        self._main_ctrl = MainController(
            sample_service=sample_svc,
            order_service=order_svc,
            production_service=prod_svc,
            release_service=release_svc,
        )

    def run(self) -> None:
        """애플리케이션 메인 루프 실행."""
        self._main_ctrl.run()
