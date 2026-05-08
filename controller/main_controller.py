"""MainController — 메인 루프 + 메뉴 선택."""
from service.sample_service import SampleService
from service.order_service import OrderService
from service.production_service import ProductionService
from service.release_service import ReleaseService
from view.console_view import ConsoleView
from view.sample_view import SampleView
from view.order_view import OrderView
from view.monitoring_view import MonitoringView
from view.production_view import ProductionView
from view.release_view import ReleaseView
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from controller.approval_controller import ApprovalController
from controller.monitoring_controller import MonitoringController
from controller.production_controller import ProductionController
from controller.release_controller import ReleaseController
from model.order import OrderStatus


class MainController:
    """메인 메뉴 루프 및 하위 컨트롤러 위임."""

    def __init__(
        self,
        sample_service: SampleService,
        order_service: OrderService,
        production_service: ProductionService,
        release_service: ReleaseService,
    ):
        self._sample_svc = sample_service
        self._order_svc = order_service
        self._prod_svc = production_service
        self._release_svc = release_service
        self._console_view = ConsoleView()

        # 하위 컨트롤러 초기화
        self._sample_ctrl = SampleController(
            sample_service=sample_service,
            view=SampleView(),
        )
        self._order_ctrl = OrderController(
            order_service=order_service,
            view=OrderView(),
        )
        self._approval_ctrl = ApprovalController(
            order_service=order_service,
            view=OrderView(),
        )
        self._monitoring_ctrl = MonitoringController(
            order_service=order_service,
            sample_service=sample_service,
            view=MonitoringView(),
        )
        self._production_ctrl = ProductionController(
            production_service=production_service,
            view=ProductionView(),
        )
        self._release_ctrl = ReleaseController(
            release_service=release_service,
            view=ReleaseView(),
        )

    def _get_summary(self) -> tuple[int, int, int, int]:
        """시스템 요약 정보 반환: (시료 수, 총 재고, 진행 주문, 생산 대기)."""
        samples = self._sample_svc.list_samples()
        total_samples = len(samples)
        total_stock = sum(s.stock for s in samples)

        active_statuses = [OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED]
        active_orders = sum(
            len(self._order_svc.list_orders_by_status(s)) for s in active_statuses
        )
        waiting_jobs = len(self._prod_svc.get_waiting_queue())
        return total_samples, total_stock, active_orders, waiting_jobs

    def run(self) -> None:
        """메인 메뉴 루프. '0' 입력 시 종료."""
        self._console_view.print_title()
        while True:
            total_samples, total_stock, active_orders, waiting_jobs = self._get_summary()
            self._console_view.print_main_menu(
                total_samples=total_samples,
                total_stock=total_stock,
                active_orders=active_orders,
                waiting_jobs=waiting_jobs,
            )
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self._sample_ctrl.run()
                case "2":
                    self._order_ctrl.run()
                case "3":
                    self._approval_ctrl.run()
                case "4":
                    self._monitoring_ctrl.run()
                case "5":
                    self._production_ctrl.run()
                case "6":
                    self._release_ctrl.run()
                case "0":
                    self._console_view.print_info("시스템을 종료합니다.")
                    break
                case _:
                    self._console_view.print_error("0~6 사이의 번호를 입력하세요.")
