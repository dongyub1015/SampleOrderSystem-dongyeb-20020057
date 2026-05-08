"""ProductionView — 생산 라인 print() 전담."""
from view.console_view import ConsoleView


class ProductionView:
    """생산 현황·대기 큐 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_current_production(self, job) -> None:
        if job is None:
            print("  현재 생산 중인 작업이 없습니다.")
            return
        print("=== 현재 생산 중 ===")
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
        print("=== 생산 대기 큐 ===")
        if not jobs:
            print("  대기 중인 작업이 없습니다.")
            return
        headers = ["순서", "주문번호", "시료명", "주문량", "부족분", "실생산량", "총시간(min)"]
        rows = [
            [str(i + 1), j.order_id, j.sample_name,
             str(j.order_quantity), str(j.shortage), str(j.actual_qty),
             f"{j.total_time_min:.0f}"]
            for i, j in enumerate(jobs)
        ]
        self._console.print_table(headers, rows)

    def print_production_completed(self, order_id: str) -> None:
        print(f"[성공] 생산 완료 처리: {order_id} → CONFIRMED")
