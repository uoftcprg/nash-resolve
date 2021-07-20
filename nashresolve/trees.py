from abc import ABC, abstractmethod
from collections.abc import Hashable
from itertools import chain

from auxiliary import flatten


class InfoSet(Hashable, ABC):
    ...


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


class Node:
    def __init__(self, actions):
        self.__actions = tuple(actions)

    @property
    def actions(self):
        return self.__actions

    @property
    def labels(self):
        return map(Action.label.fget, self.actions)

    @property
    def children(self):
        return map(Action.child.fget, self.actions)

    @property
    def descendants(self):
        return chain((self,), flatten(map(Node.descendants.fget, self.children)))

    @abstractmethod
    def is_terminal(self): ...

    @abstractmethod
    def is_chance(self): ...

    @abstractmethod
    def is_player(self): ...


class TerminalNode(Node):
    def __init__(self, payoffs):
        super().__init__(())

        self.__payoffs = tuple(payoffs)

    @property
    def payoffs(self):
        return self.__payoffs

    def is_terminal(self):
        return True

    def is_chance(self):
        return False

    def is_player(self):
        return False


class ChanceNode(Node):
    @property
    def chances(self):
        return map(ChanceAction.chance.fget, self.actions)

    def is_terminal(self):
        return False

    def is_chance(self):
        return True

    def is_player(self):
        return False


class PlayerNode(Node):
    def __init__(self, player, info_set, actions):
        super().__init__(actions)

        self.__player = player
        self.__info_set = info_set

    @property
    def player(self):
        return self.__player

    @property
    def info_set(self):
        return self.__info_set

    def is_terminal(self):
        return False

    def is_chance(self):
        return False

    def is_player(self):
        return True
