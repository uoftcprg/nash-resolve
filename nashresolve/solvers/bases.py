from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Final

from nashresolve.games import TreeGame
from nashresolve.trees import InfoSet


class TreeSolver(ABC):
    def __init__(self, game: TreeGame):
        self.game: Final = game

    @abstractmethod
    def query(self, info_set: InfoSet) -> Sequence[float]:
        pass
