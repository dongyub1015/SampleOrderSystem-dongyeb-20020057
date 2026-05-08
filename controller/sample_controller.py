"""SampleController — 시료 관리 input() 처리."""
from exceptions import DuplicateKeyError, RecordNotFoundError
from service.sample_service import SampleService
from view.sample_view import SampleView


class SampleController:
    """시료 등록·목록·검색 메뉴 처리."""

    def __init__(self, sample_service: SampleService, view: SampleView):
        self._svc = sample_service
        self._view = view

    def run(self) -> None:
        """시료 관리 서브 메뉴."""
        while True:
            self._view.print_sample_menu()
            choice = input("선택 > ").strip()
            match choice:
                case "1":
                    self.register_sample()
                case "2":
                    self.list_samples()
                case "3":
                    self.search_samples()
                case "0":
                    break
                case _:
                    self._view.print_error("올바른 메뉴를 선택하세요.")

    def register_sample(self) -> None:
        self._view.print_sample_register_prompt()
        sample_id = input("시료 ID > ").strip()
        name = input("시료 이름 > ").strip()
        try:
            avg_time = float(input("평균 생산시간 (min/ea) > ").strip())
            yield_rate = float(input("수율 (0~1) > ").strip())
            stock = int(input("현재 재고 (ea) > ").strip())
        except ValueError:
            self._view.print_error("숫자를 올바르게 입력하세요.")
            return
        try:
            sample = self._svc.register_sample(sample_id, name, avg_time, yield_rate, stock)
            self._view.print_sample_registered(sample)
        except DuplicateKeyError as e:
            self._view.print_error(f"이미 존재하는 시료 ID입니다: {e.record_id}")
        except Exception as e:
            self._view.print_error(str(e))

    def list_samples(self) -> None:
        samples = self._svc.list_samples()
        self._view.print_sample_list(samples)

    def search_samples(self) -> None:
        keyword = input("검색어 > ").strip()
        results = self._svc.search_samples(keyword)
        self._view.print_search_result(results, keyword)
