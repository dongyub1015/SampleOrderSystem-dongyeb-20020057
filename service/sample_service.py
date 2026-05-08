"""SampleService — 시료 관리 비즈니스 로직."""
from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleService:
    """시료 등록·조회·검색 서비스."""

    def __init__(self, sample_repo: SampleRepository):
        self._sample_repo = sample_repo

    def register_sample(
        self,
        id: str,
        name: str,
        avg_production_time: float,
        yield_rate: float,
        stock: int,
    ) -> Sample:
        """시료 등록. 중복 ID이면 DuplicateKeyError."""
        if not id or not id.strip():
            raise ValueError("시료 ID는 빈 문자열일 수 없습니다.")
        if not name or not name.strip():
            raise ValueError("시료 이름은 빈 문자열일 수 없습니다.")
        if not (0 < yield_rate <= 1.0):
            raise ValueError(f"수율은 0 초과 1 이하여야 합니다: {yield_rate}")
        if avg_production_time <= 0:
            raise ValueError(f"평균 생산시간은 0 초과여야 합니다: {avg_production_time}")
        if stock < 0:
            raise ValueError(f"재고는 0 이상이어야 합니다: {stock}")
        sample = Sample(
            id=id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=stock,
        )
        return self._sample_repo.save(sample)

    def get_sample(self, sample_id: str) -> Sample:
        """ID로 시료 조회. 없으면 RecordNotFoundError."""
        return self._sample_repo.find_by_id(sample_id)

    def list_samples(self) -> list[Sample]:
        """전체 시료 목록 반환."""
        return self._sample_repo.find_all()

    def search_samples(self, keyword: str) -> list[Sample]:
        """이름 기반 시료 검색."""
        return self._sample_repo.find_by_name(keyword)
