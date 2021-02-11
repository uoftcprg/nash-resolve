from collections import Sequence
from functools import cached_property

from nashresolve.trees import InfoSet, Node, PlayerNode


class Game:
    def __init__(self, player_count: int):
        self.__player_count = player_count

    @property
    def player_count(self) -> int:
        return self.__player_count


class TreeGame(Game):
    def __init__(self, player_count: int, root: Node):
        super().__init__(player_count)

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
