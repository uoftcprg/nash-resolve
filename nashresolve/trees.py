from abc import ABC
from itertools import chain

import numpy as np


class Action:
    def __init__(self, child, label):
        self.__child = child
        self.__label = label

    @property
    def child(self):
        return self.__child

    @property
    def label(self):
        return self.__label


class ChanceAction(Action):
    def __init__(self, chance, child, label):
        super().__init__(child, label)

        self.__chance = chance

    @property
    def chance(self):
        return self.__chance


class Node(ABC):
    def __init__(self, actions):
        self.__actions = tuple(actions)

    @property
    def actions(self):
        return self.__actions

    @property
    def action_count(self):
        return len(self.actions)

    @property
    def labels(self):
        return map(Action.label.fget, self.actions)

    @property
    def children(self):
        return map(Action.child.fget, self.actions)

    @property
    def descendants(self):
        yield self
        yield from chain.from_iterable(map(Node.descendants.fget, self.children))

    def is_terminal_node(self):
        return isinstance(self, TerminalNode)

    def is_chance_node(self):
        return isinstance(self, ChanceNode)

    def is_player_node(self):
        return isinstance(self, PlayerNode)


class TerminalNode(Node):
    def __init__(self, payoffs):
        super().__init__(())

        self.__payoffs = np.fromiter(payoffs, float)

    @property
    def payoffs(self):
        return self.__payoffs


class ChanceNode(Node):
    def __init__(self, actions):
        super().__init__(actions)

        self.__chances = np.fromiter(map(ChanceAction.chance.fget, self.actions), float)

    @property
    def chances(self):
        return self.__chances


class PlayerNode(Node):
    def __init__(self, player_index, info_set, actions):
        super().__init__(actions)

        self.__player_index = player_index
        self.__info_set = info_set

    @property
    def player_index(self):
        return self.__player_index

    @property
    def info_set(self):
        return self.__info_set
