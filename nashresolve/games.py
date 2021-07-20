from nashresolve.trees import Node, PlayerNode


class Game:
    def __init__(self, players):
        self.__players = tuple(players)

    @property
    def players(self):
        return self.__players


class TreeGame(Game):
    def __init__(self, root):
        self.__root = root

        super().__init__(range(max(map(PlayerNode.player.fget, self.player_nodes)) + 1))

    @property
    def root(self):
        return self.__root

    @property
    def nodes(self):
        return self.root.descendents

    @property
    def terminal_nodes(self):
        return filter(Node.is_terminal, self.nodes)

    @property
    def chance_nodes(self):
        return filter(Node.is_chance, self.nodes)

    @property
    def player_nodes(self):
        return filter(Node.is_player, self.nodes)

    @property
    def info_sets(self):
        return map(PlayerNode.info_set.fget, self.player_nodes)
