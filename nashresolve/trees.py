from __future__ import annotations

from abc import ABC
from collections import Hashable, Iterable, Iterator
from itertools import chain
from typing import Any, Final


class InfoSet:
    def __init__(self, action_count: int, player: int, data: Hashable):
        self.action_count: Final = action_count
        self.player: Final = player
        self.data: Final = data

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, InfoSet):
            return self.action_count == other.action_count and self.player == other.player and self.data == other.data
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.action_count) ^ hash(self.player) ^ hash(self.data)


class Node(ABC):
    def __init__(self, label: str, children: Iterable[Node]) -> None:
        self.label: Final = label
        self.children: Final = tuple(children)

    def __repr__(self) -> str:
        return self.label

    @property
    def descendents(self) -> Iterator[Node]:
        return chain((self,), *(child.descendents for child in self.children))


class TerminalNode(Node):
    def __init__(self, label: str, payoffs: Iterable[float]):
        super().__init__(label, ())

        self.payoffs: Final = tuple(payoffs)


class ChanceNode(Node):
    def __init__(self, label: str, children: Iterable[Node], probabilities: Iterable[float]):
        super().__init__(label, children)

        self.probabilities: Final = tuple(probabilities)


class PlayerNode(Node):
    def __init__(self, label: str, children: Iterable[Node], player: int, data: Hashable):
        super().__init__(label, children)

        self.info_set: Final = InfoSet(len(self.children), player, data)
