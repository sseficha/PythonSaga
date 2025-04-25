from enum import Enum
from typing import TypeVar, Generic, Type, Optional
from abc import ABC, abstractmethod

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    def add(self, item: T) -> int:
        raise NotImplementedError()

    @abstractmethod
    def update_state(self, item_id: int, state: Enum):
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[T]:
        raise NotImplementedError()
