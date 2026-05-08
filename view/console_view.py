"""ConsoleView — 공통 출력 헬퍼 (테이블, 구분선, 메시지 등)."""
from datetime import datetime


class ConsoleView:
    """공통 콘솔 출력 유틸리티."""

    WIDTH = 60

    def print_separator(self) -> None:
        print("─" * self.WIDTH)

    def print_title(self) -> None:
        print("=" * self.WIDTH)
        print("   반도체 시료 생산주문관리 시스템")
        print("=" * self.WIDTH)

    def print_success(self, message: str) -> None:
        print(f"[성공] {message}")

    def print_error(self, message: str) -> None:
        print(f"[오류] {message}")

    def print_info(self, message: str) -> None:
        print(f"[정보] {message}")

    def print_main_menu(
        self,
        total_samples: int,
        total_stock: int,
        active_orders: int,
        waiting_jobs: int,
    ) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n시스템 현황: {now}")
        print(f"등록 시료 {total_samples}개  총 재고 {total_stock} ea  "
              f"진행 주문 {active_orders}건  생산대기 {waiting_jobs}건")
        print()
        print("[1] 시료 관리        [2] 시료 주문")
        print("[3] 주문 승인/거절   [4] 모니터링")
        print("[5] 생산라인 조회    [6] 출고 처리")
        print("[0] 종료")
        print()

    def print_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """간단한 텍스트 테이블 출력."""
        # 컬럼 너비 계산
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
        print(fmt.format(*headers))
        print("  ".join("-" * w for w in col_widths))
        for row in rows:
            padded = list(row) + [""] * (len(headers) - len(row))
            print(fmt.format(*[str(c) for c in padded[:len(headers)]]))
