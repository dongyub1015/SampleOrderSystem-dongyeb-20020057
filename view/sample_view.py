"""SampleView — 시료 관련 print() 전담."""
from view.console_view import ConsoleView


class SampleView:
    """시료 목록·검색 결과 출력."""

    def __init__(self):
        self._console = ConsoleView()

    def print_sample_list(self, samples: list) -> None:
        if not samples:
            print("  등록된 시료가 없습니다.")
            return
        headers = ["시료 ID", "이름", "평균생산시간(min)", "수율", "재고(ea)"]
        rows = [
            [s.id, s.name, f"{s.avg_production_time:.1f}", f"{s.yield_rate:.2f}", str(s.stock)]
            for s in samples
        ]
        self._console.print_table(headers, rows)

    def print_sample_register_prompt(self) -> None:
        print("=== 시료 등록 ===")

    def print_sample_registered(self, sample) -> None:
        print(f"[성공] 시료 등록 완료: {sample.id} — {sample.name}")

    def print_sample_menu(self) -> None:
        print("\n[시료 관리]")
        print("  [1] 시료 등록")
        print("  [2] 시료 목록 조회")
        print("  [3] 시료 검색")
        print("  [0] 뒤로")

    def print_search_result(self, samples: list, keyword: str) -> None:
        print(f"=== 검색 결과 (키워드: '{keyword}') ===")
        self.print_sample_list(samples)
