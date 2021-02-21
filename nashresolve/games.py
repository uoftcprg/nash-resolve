from abc import ABC, abstractmethod
from collections import Sequence
from functools import cached_property

from nashresolve.trees import InfoSet, Node, PlayerNode


class Game(ABC):
    @property
    @abstractmethod
    def player_count(self) -> int:
        pass


class TreeGame(Game):
    def __init__(self, root: Node):
        self.__root = root

    @cached_property
    def player_count(self) -> int:  # type: ignore
        return max(info_set.player for info_set in self.info_sets) + 1

    @property
    def root(self) -> Node:
        return self.__root

    @property
    def nodes(self) -> Sequence[Node]:
        return self.root.descendents

    @cached_property
    def info_sets(self) -> frozenset[InfoSet]:
        return frozenset(node.info_set for node in self.nodes if isinstance(node, PlayerNode))
