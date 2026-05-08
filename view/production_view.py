"""ProductionView — 생산 라인 print() 전담."""
from view.console_view import ConsoleView


class ProductionView:
    """생산 현황·대기 큐 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_production_summary(self, job, waiting: list) -> None:
        """현재 작업 + 대기 큐 자동 표시 (ui-flow.md [5] 자동 표시 후 뒤로)."""
        self._console.print_title("[생산라인 조회]  FIFO 방식")
        self.print_current_production(job)
        self.print_waiting_queue(waiting)

    def print_current_production(self, job) -> None:
        print("\n  ── 현재 생산 중 ──")
        if job is None:
            self._console.print_info("현재 생산 중인 작업이 없습니다.")
            return
        print(f"  작업 ID   : {job.job_id}")
        print(f"  주문번호  : {job.order_id}")
        print(f"  시료명    : {job.sample_name}")
        print(f"  주문 수량 : {job.order_quantity} ea")
        print(f"  부족분    : {job.shortage} ea")
        print(f"  실 생산량 : {job.actual_qty} ea")
        print(f"  총 생산시간: {job.total_time_min:.0f} 분")
        if job.started_at:
            print(f"  생산 시작 : {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if job.estimated_finish:
            print(f"  예상 완료 : {job.estimated_finish.strftime('%Y-%m-%d %H:%M:%S')}")

    def print_waiting_queue(self, jobs: list) -> None:
        print("\n  ── 대기 중인 주문 (FIFO 순) ──")
        if not jobs:
            self._console.print_info("대기 중인 작업이 없습니다.")
            return
        headers = ["순서", "주문번호", "시료명", "주문량", "부족분", "실생산량", "완료예정"]
        rows = []
        for i, j in enumerate(jobs):
            finish = j.estimated_finish.strftime("%H:%M") if j.estimated_finish else "-"
            rows.append([
                str(i + 1), j.order_id, j.sample_name,
                f"{j.order_quantity} ea", f"{j.shortage} ea",
                f"{j.actual_qty} ea", finish,
            ])
        self._console.print_table(headers, rows)

    def print_complete_prompt(self, order_id: str) -> None:
        print(f"\n  현재 작업: {order_id}")
        print("  [C] 생산 완료 처리  [0] 뒤로")

    def print_production_completed(self, order_id: str) -> None:
        self._console.print_success(f"생산 완료 처리: {order_id} → CONFIRMED")

    def print_error(self, msg: str) -> None:
        self._console.print_error(msg)
