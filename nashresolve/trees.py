from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Sequence
from functools import cached_property


class InfoSet:
    def __init__(self, action_count: int, player: int):
        self.__action_count = action_count
        self.__player = player

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

    @cached_property
    def descendents(self) -> Sequence[Node]:
        return [self] + sum((list(child.descendents) for child in self.children), start=[])

    @property
    @abstractmethod
    def children(self) -> Sequence[Node]:
        pass


class TerminalNode(Node):
    def __init__(self, label: str, payoffs: Sequence[float]):
        super().__init__(label)

        self.__payoffs = tuple(payoffs)

    @property
    def payoffs(self) -> Sequence[float]:
        return self.__payoffs

    @property
    def children(self) -> Sequence[Node]:
        return []


class NonTerminalNode(Node, ABC):
    def __init__(self, label: str, children: Sequence[Node]):
        super().__init__(label)

        self.__children = tuple(children)

    @property
    def children(self) -> Sequence[Node]:
        return self.__children


class ChanceNode(NonTerminalNode):
    def __init__(self, label: str, children: Sequence[Node], probabilities: Sequence[float]):
        super().__init__(label, children)

        self.__probabilities = tuple(probabilities)

    @property
    def probabilities(self) -> Sequence[float]:
        return self.__probabilities


class PlayerNode(NonTerminalNode):
    def __init__(self, label: str, children: Sequence[Node], info_set: InfoSet):
        super().__init__(label, children)

        self.__info_set = info_set

    @property
    def info_set(self) -> InfoSet:
        return self.__info_set
