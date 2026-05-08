"""
DataPersistence 패키지의 예외 클래스 구현.
DataPersistence-dongyeb-20020057 레포지토리의 exceptions.py를 로컬 구현.
"""


class DuplicateKeyError(Exception):
    """동일한 ID로 레코드를 생성하려 할 때 발생."""
    def __init__(self, record_id: str):
        self.record_id = record_id
        super().__init__(f"Record with id '{record_id}' already exists.")


class RecordNotFoundError(Exception):
    """존재하지 않는 ID로 조회·수정·삭제 시 발생."""
    def __init__(self, record_id: str):
        self.record_id = record_id
        super().__init__(f"Record with id '{record_id}' not found.")
