"""ProductionController — 생산 라인 input() 처리."""
from service.production_service import ProductionService
from view.production_view import ProductionView


class ProductionController:
    """생산 현황·대기 큐·완료 처리 메뉴."""

    def __init__(self, production_service: ProductionService, view: ProductionView):
        self._svc = production_service
        self._view = view

    def run(self) -> None:
        """생산라인 서브 메뉴."""
        while True:
            print("\n[생산라인 조회]")
            print("  [1] 현재 생산 현황")
            print("  [2] 생산 대기 큐")
            print("  [3] 생산 완료 처리")
            print("  [0] 뒤로")
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.show_current()
                case "2":
                    self.show_waiting()
                case "3":
                    self.complete_production()
                case "0":
                    break
                case _:
                    print("[오류] 올바른 메뉴를 선택하세요.")

    def show_current(self) -> None:
        job = self._svc.get_current_production()
        self._view.print_current_production(job)

    def show_waiting(self) -> None:
        jobs = self._svc.get_waiting_queue()
        self._view.print_waiting_queue(jobs)

    def complete_production(self) -> None:
        job = self._svc.get_current_production()
        if job is None:
            print("[오류] 현재 생산 중인 작업이 없습니다.")
            return
        confirm = input(f"'{job.order_id}' 생산 완료 처리하시겠습니까? (y/n) > ").strip().lower()
        if confirm == "y":
            try:
                self._svc.complete_production(job.order_id)
                self._view.print_production_completed(job.order_id)
            except Exception as e:
                print(f"[오류] {e}")
