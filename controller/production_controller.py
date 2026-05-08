"""ProductionController — 생산 라인 input() 처리 (자동 표시 후 완료 처리 옵션)."""
from service.production_service import ProductionService
from view.production_view import ProductionView


class ProductionController:
    """생산 현황·대기 큐 자동 표시 후 완료 처리 메뉴."""

    def __init__(self, production_service: ProductionService, view: ProductionView):
        self._svc = production_service
        self._view = view

    def run(self) -> None:
        """진입 시 현황 자동 표시 후 [C] 완료처리 / [0] 뒤로 선택."""
        job = self._svc.get_current_production()
        waiting = self._svc.get_waiting_queue()
        self._view.print_production_summary(job, waiting)

        if job is not None:
            self._view.print_complete_prompt(job.order_id)
            choice = input("선택 > ").strip().upper()
            if choice == "C":
                self._complete_production(job)
        else:
            input("  [Enter] 메인 메뉴로 > ")

    def _complete_production(self, job) -> None:
        confirm = input(f"  '{job.order_id}' 생산 완료 처리하시겠습니까? (y/n) > ").strip().lower()
        if confirm == "y":
            try:
                self._svc.complete_production(job.order_id)
                self._view.print_production_completed(job.order_id)
            except Exception as e:
                self._view.print_error(str(e))
