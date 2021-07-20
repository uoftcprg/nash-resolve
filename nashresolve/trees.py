from abc import ABC, abstractmethod
from collections.abc import Hashable
from itertools import chain

from auxiliary import flatten


class InfoSet(Hashable, ABC):
    ...


class Node:
    def __init__(self, label, children):
        self.__label = label
        self.__children = tuple(children)

    def __repr__(self):
        return f'<{type(self).__name__} \'{self.label}\'>'

    @property
    def label(self):
        return self.__label

    @property
    def children(self):
        return self.__children

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
    def __init__(self, label, payoffs):
        super().__init__(label, ())

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
    def __init__(self, label, children, chances):
        super().__init__(label, children)

        self.__chances = tuple(chances)

    @property
    def chances(self):
        return self.__chances

    def is_terminal(self):
        return False

    def is_chance(self):
        return True

    def is_player(self):
        return False


class PlayerNode(Node):
    def __init__(self, label, children, player, info_set):
        super().__init__(label, children)

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
