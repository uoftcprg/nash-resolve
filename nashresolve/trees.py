from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Hashable, Iterable, Iterator, Sequence
from itertools import chain
from typing import Any


class InfoSet:
    def __init__(self, action_count: int, player: int, data: Hashable):
        self.__action_count = action_count
        self.__player = player
        self.__data = data

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, InfoSet):
            return self.__action_count == other.__action_count and self.__player == other.__player \
                   and self.__data == other.__data
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.action_count) ^ hash(self.player) ^ hash(self.__data)

    @property
    def action_count(self) -> int:
        return self.__action_count

    @property
    def player(self) -> int:
        return self.__player


class Node(ABC):
    def __init__(self, label: str) -> None:
        self.__label = label

    def __repr__(self) -> str:
        return self.__label

    @property
    def descendents(self) -> Iterator[Node]:
        return chain([self], *(child.descendents for child in self.children))

    @property
    @abstractmethod
    def children(self) -> Sequence[Node]:
        ...


class TerminalNode(Node):
    def __init__(self, label: str, payoffs: Iterable[float]):
        super().__init__(label)

        self.__payoffs = tuple(payoffs)

    @property
    def children(self) -> Sequence[Node]:
        return ()

    @property
    def payoffs(self) -> Sequence[float]:
        return self.__payoffs


class NonTerminalNode(Node, ABC):
    def __init__(self, label: str, children: Iterable[Node]):
        super().__init__(label)

        self.__children = tuple(children)

    @property
    def children(self) -> Sequence[Node]:
        return self.__children


class ChanceNode(NonTerminalNode):
    def __init__(self, label: str, children: Iterable[Node], probabilities: Iterable[float]):
        super().__init__(label, children)

        self.__probabilities = tuple(probabilities)

    @property
    def probabilities(self) -> Sequence[float]:
        return self.__probabilities


class PlayerNode(NonTerminalNode):
    def __init__(self, label: str, children: Iterable[Node], player: int, data: Hashable):
        super().__init__(label, children)

        self.__info_set = InfoSet(len(self.children), player, data)

    @property
    def info_set(self) -> InfoSet:
        return self.__info_set
