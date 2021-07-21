from abc import ABC, abstractmethod


class TreeSolver(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def query(self, info_set):
        pass
