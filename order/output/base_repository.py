from contextlib import contextmanager
from enum import Enum
from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    conn_str: str = None

    @classmethod
    @contextmanager
    def connect(cls):
        raise NotImplementedError()

    @abstractmethod
    def add(self, item: T) -> int:
        raise NotImplementedError()

    @abstractmethod
    def update_state(self, item_id: int, state: Enum):
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[T]:
        raise NotImplementedError()
