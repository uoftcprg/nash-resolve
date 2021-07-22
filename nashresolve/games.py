from abc import ABC, abstractmethod

from nashresolve.trees import Node, PlayerNode


class Game(ABC):
    def __init__(self, player_count):
        self.__player_count = player_count

    @property
    def player_count(self):
        return self.__player_count

    @abstractmethod
    def is_zero_sum(self): ...


class TreeGame(Game):
    def __init__(self, root):
        self.__root = root

        super().__init__(max(map(PlayerNode.player_index.fget, self.player_nodes), default=-1) + 1)

    @property
    def root(self):
        return self.__root

    @property
    def nodes(self):
        return self.root.descendants

    @property
    def terminal_nodes(self):
        return filter(Node.is_terminal_node, self.nodes)

    @property
    def chance_nodes(self):
        return filter(Node.is_chance_node, self.nodes)

    @property
    def player_nodes(self):
        return filter(Node.is_player_node, self.nodes)

    @property
    def info_sets(self):
        return map(PlayerNode.info_set.fget, self.player_nodes)

    def is_zero_sum(self):
        for node in self.terminal_nodes:
            if node.payoffs.sum():
                return False

        return True
