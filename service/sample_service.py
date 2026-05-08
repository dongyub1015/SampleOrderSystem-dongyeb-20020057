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
