from abc import ABC, abstractmethod


class Solver(ABC):
    def __init__(self, game):
        self.__game = game

    @property
    def game(self):
        return self.__game

    @abstractmethod
    def get_probabilities(self, node): ...


class TreeSolver(Solver, ABC):
    ...
