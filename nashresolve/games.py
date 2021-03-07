from abc import ABC
from collections import Iterator, Set
from functools import cached_property
from typing import Final

from nashresolve.trees import InfoSet, Node, PlayerNode


class Game(ABC):
    def __init__(self, player_count: int):
        self.player_count: Final = player_count


class TreeGame(Game):
    def __init__(self, root: Node):
        super().__init__(max(node.info_set.player for node in root.descendents if isinstance(node, PlayerNode)) + 1)

        self.root: Final = root

    @property
    def nodes(self) -> Iterator[Node]:
        return self.root.descendents

    @cached_property
    def info_sets(self) -> Set[InfoSet]:
        return frozenset(node.info_set for node in self.nodes if isinstance(node, PlayerNode))
