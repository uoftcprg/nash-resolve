from abc import ABC, abstractmethod


class Solver(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def query(self, info_set): ...


class TreeSolver(Solver, ABC):
    ...
