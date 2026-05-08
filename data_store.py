"""
DataPersistence 패키지의 JsonDataStore 구현.
DataPersistence-dongyeb-20020057 레포지토리의 data_store.py를 로컬 구현.

JSON 파일 기반 간단한 Key-Value 저장소.
"""
import json
import os
import uuid
from typing import Optional

from exceptions import DuplicateKeyError, RecordNotFoundError


class JsonDataStore:
    """JSON 파일 기반 데이터 저장소."""

    def __init__(self, file_path: str):
        self._file_path = file_path
        # 파일이 없으면 빈 저장소로 초기화
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._write({})

    def _read(self) -> dict:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self._file_path) or ".", exist_ok=True)
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, record: dict, record_id: Optional[str] = None) -> dict:
        """레코드 생성. record_id가 None이면 UUID 자동 생성."""
        data = self._read()
        if record_id is None:
            record_id = str(uuid.uuid4())
        if record_id in data:
            raise DuplicateKeyError(record_id)
        record = dict(record)
        record["_id"] = record_id
        data[record_id] = record
        self._write(data)
        return record

    def read(self, record_id: str) -> dict:
        """단건 조회. 없으면 RecordNotFoundError."""
        data = self._read()
        if record_id not in data:
            raise RecordNotFoundError(record_id)
        return dict(data[record_id])

    def read_all(self) -> list[dict]:
        """전체 레코드 반환 (삽입 순서 유지)."""
        data = self._read()
        return [dict(v) for v in data.values()]

    def update(self, record_id: str, fields: dict) -> dict:
        """지정 필드만 업데이트. ID 보호."""
        data = self._read()
        if record_id not in data:
            raise RecordNotFoundError(record_id)
        record = data[record_id]
        for key, value in fields.items():
            if key != "_id":
                record[key] = value
        data[record_id] = record
        self._write(data)
        return dict(record)

    def delete(self, record_id: str) -> None:
        """레코드 삭제."""
        data = self._read()
        if record_id not in data:
            raise RecordNotFoundError(record_id)
        del data[record_id]
        self._write(data)
