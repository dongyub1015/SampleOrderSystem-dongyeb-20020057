"""SampleRepository — JsonDataStore를 래핑한 시료 저장소."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_store import JsonDataStore
from exceptions import DuplicateKeyError, RecordNotFoundError
from model.sample import Sample


class SampleRepository:
    """시료 CRUD 저장소."""

    def __init__(self, file_path: str = "data/samples.json"):
        self._store = JsonDataStore(file_path)

    def _to_model(self, record: dict) -> Sample:
        return Sample(
            id=record["id"],
            name=record["name"],
            avg_production_time=float(record["avg_production_time"]),
            yield_rate=float(record["yield_rate"]),
            stock=int(record["stock"]),
        )

    def _to_dict(self, sample: Sample) -> dict:
        return {
            "id": sample.id,
            "name": sample.name,
            "avg_production_time": sample.avg_production_time,
            "yield_rate": sample.yield_rate,
            "stock": sample.stock,
        }

    def save(self, sample: Sample) -> Sample:
        """시료 저장. 중복 ID이면 DuplicateKeyError."""
        record = self._to_dict(sample)
        self._store.create(record, record_id=sample.id)
        return sample

    def find_by_id(self, sample_id: str) -> Sample:
        """ID로 단건 조회. 없으면 RecordNotFoundError."""
        record = self._store.read(sample_id)
        return self._to_model(record)

    def find_all(self) -> list[Sample]:
        """전체 시료 목록 반환."""
        return [self._to_model(r) for r in self._store.read_all()]

    def find_by_name(self, keyword: str) -> list[Sample]:
        """이름에 keyword가 포함된 시료 목록 반환 (대소문자 무시)."""
        keyword_lower = keyword.lower()
        return [
            self._to_model(r)
            for r in self._store.read_all()
            if keyword_lower in r["name"].lower()
        ]

    def update_stock(self, sample_id: str, new_stock: int) -> Sample:
        """재고 수량 업데이트."""
        record = self._store.update(sample_id, {"stock": new_stock})
        return self._to_model(record)
