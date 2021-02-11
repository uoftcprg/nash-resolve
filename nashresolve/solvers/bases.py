from abc import ABC, abstractmethod
from collections import Sequence

from nashresolve.games import TreeGame
from nashresolve.trees import InfoSet


class TreeSolver(ABC):
    def __init__(self, game: TreeGame):
        self.__game = game

    @property
    def game(self) -> TreeGame:
        return self.__game

    @abstractmethod
    def query(self, info_set: InfoSet) -> Sequence[float]:
        pass
