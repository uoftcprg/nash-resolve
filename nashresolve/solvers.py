from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, Optional, Sequence, TypeVar

import numpy as np

from nashresolve.games import TreeGame
from nashresolve.trees import ChanceNode, InfoSet, Node, PlayerNode, TerminalNode


class TreeSolver(ABC):
    def __init__(self, game: TreeGame):
        self.__game = game

    @property
    def game(self) -> TreeGame:
        return self.__game

    @abstractmethod
    def query(self, info_set: InfoSet) -> Sequence[float]:
        pass


T = TypeVar('T', bound='CFRSolver')


class CFRSolver(TreeSolver):
    """CFRSolver is the class for vanilla CFR solvers."""

    class _Data(Generic[T]):
        def __init__(self, solver: T, info_set: InfoSet):
            self.solver = solver
            self.info_set = info_set

            self.weight = float()
            self.counterfactuals = np.zeros(info_set.action_count)

            self.strategy_sum = np.zeros(info_set.action_count)
            self.weight_sum = float()
            self.regrets = np.zeros(info_set.action_count)

        @property
        def strategy(self) -> np.ndarray:
            pos_regrets = np.maximum(0, self.regrets)

            return pos_regrets / pos_regrets.sum() if pos_regrets.any() else self.default_strategy  # type: ignore

        @property
        def average_strategy(self) -> np.ndarray:
            return self.strategy_sum / self.weight_sum if self.weight_sum else self.default_strategy  # type: ignore

        @cached_property
        def default_strategy(self) -> np.ndarray:
            return np.full(self.info_set.action_count, 1 / self.info_set.action_count)

        def update(self, contrib: float, partial_contrib: float, counterfactuals: np.ndarray) -> None:
            self.weight += contrib
            self.counterfactuals += partial_contrib * counterfactuals

        def collect(self) -> None:
            strategy = self.strategy

            self.strategy_sum += self.weight * strategy
            self.weight_sum += self.weight
            self.regrets += self.counterfactuals - self.counterfactuals @ strategy

        def clear(self) -> None:
            self.weight = 0
            self.counterfactuals.fill(0)

    def __init__(self: T, game: TreeGame):
        super().__init__(game)

        self._data: dict[InfoSet, CFRSolver._Data[T]] = {
            info_set: self._Data(self, info_set) for info_set in game.info_sets
        }

    def query(self, info_set: InfoSet) -> Sequence[float]:
        return tuple(map(float, self._data[info_set].average_strategy))

    def step(self) -> Sequence[float]:
        counterfactuals = self._traverse(self.game.root, 1, np.ones(self.game.player_count))

        for data in self._data.values():
            data.collect()
            data.clear()

        return tuple(map(float, counterfactuals))

    def ev(self, node: Optional[Node] = None) -> np.ndarray:
        if node is None:
            return self.ev(self.game.root)
        elif isinstance(node, TerminalNode):
            return np.array(node.payoffs)
        elif isinstance(node, ChanceNode):
            return sum(ev * probability for ev, probability in
                       zip(map(self.ev, node.children), node.probabilities))  # type: ignore
        elif isinstance(node, PlayerNode):
            return sum(ev * probability for ev, probability in
                       zip(map(self.ev, node.children), self._data[node.info_set].average_strategy))  # type: ignore
        else:
            raise TypeError('Argument is not of valid node type.')

    def _traverse(self, node: Node, nature_contrib: float, player_contribs: np.ndarray) -> np.ndarray:
        if isinstance(node, TerminalNode):
            return np.array(node.payoffs)
        elif isinstance(node, ChanceNode):
            return sum(self._traverse(child, nature_contrib * probability, player_contribs) * probability
                       for child, probability in zip(node.children, node.probabilities))  # type: ignore
        elif isinstance(node, PlayerNode):
            return self._solve(node, nature_contrib, player_contribs)
        else:
            raise TypeError('Argument is not of valid node type.')

    def _solve(self, node: PlayerNode, nature_contrib: float, player_contribs: np.ndarray) -> np.ndarray:
        data = self._data[node.info_set]
        results: list[np.ndarray] = []

        for i, (child, probability) in enumerate(zip(node.children, data.strategy)):
            temp_contribs = player_contribs.copy()
            temp_contribs[node.info_set.player] *= probability

            results.append(self._traverse(child, nature_contrib, temp_contribs))

        data.update(
            player_contribs[node.info_set.player],
            nature_contrib * np.delete(player_contribs, node.info_set.player).prod(),
            np.array(results)[:, node.info_set.player],
        )

        return sum(result * probability for result, probability in zip(results, data.strategy))  # type: ignore


class CFRPSolver(CFRSolver):
    """CFRPSolver is the class for CFR+ solvers."""

    class _Data(CFRSolver._Data['CFRPSolver']):
        @property
        def strategy(self) -> np.ndarray:
            return self.regrets / self.regrets.sum() if self.regrets.any() else self.default_strategy  # type: ignore

        def collect(self) -> None:
            strategy = self.strategy

            self.strategy_sum += (self.weight_sum + self.weight) * strategy
            self.weight_sum += self.weight_sum + self.weight
            self.regrets = np.maximum(0, self.regrets + (self.counterfactuals - self.counterfactuals @ strategy))
