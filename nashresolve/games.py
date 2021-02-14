from abc import ABC, abstractmethod
from collections import Sequence
from functools import cached_property

from nashresolve.trees import InfoSet, Node, PlayerNode


class Game(ABC):
    @cached_property
    @abstractmethod
    def player_count(self) -> int:
        pass


class TreeGame(Game):
    def __init__(self, root: Node):
        self.__root = root

    @property
    def root(self) -> Node:
        return self.__root

    @property
    def nodes(self) -> Sequence[Node]:
        return self.root.descendents

    @cached_property
    def info_sets(self) -> Sequence[InfoSet]:
        return list({node.info_set for node in self.nodes if isinstance(node, PlayerNode)})

    @cached_property
    def player_count(self) -> int:
        return max(info_set.player for info_set in self.info_sets) + 1
