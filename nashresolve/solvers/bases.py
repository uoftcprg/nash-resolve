from abc import ABC, abstractmethod
from collections.abc import Sequence

from nashresolve.games import TreeGame
from nashresolve.trees import InfoSet


class TreeSolver(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def query(self, info_set):
        pass
