from abc import ABC, abstractmethod
from collections import Sequence
from functools import cached_property
from typing import Generic, Optional, TypeVar, Union, cast

import numpy as np
from auxiliary.utils import sum_

from nashresolve.games import TreeGame
from nashresolve.solvers.bases import TreeSolver
from nashresolve.trees import ChanceNode, InfoSet, Node, PlayerNode, TerminalNode
from nashresolve.utils import replace

T = TypeVar('T', bound='CFRSolver')


class CFRSolver(TreeSolver):
    """CFRSolver is the class for vanilla counterfactual regret minimization solvers."""

    def __init__(self, game: TreeGame):
        super().__init__(game)

        self.__iter_count = 0
        self.__data: dict[InfoSet, CFRSolver._BaseData] = {
            info_set: self._Data(self, info_set) for info_set in game.info_sets
        }

    @property
    def iter_count(self) -> int:
        return self.__iter_count

    def query(self, data: Union[Node, InfoSet]) -> Sequence[float]:
        if isinstance(data, TerminalNode):
            return []
        elif isinstance(data, ChanceNode):
            return data.probabilities
        elif isinstance(data, PlayerNode):
            return self.query(data.info_set)
        elif isinstance(data, InfoSet):
            return tuple(map(float, self.__data[data].average_strategy))
        else:
            raise TypeError('Unknown queried type')

    def step(self) -> Sequence[float]:
        self.__iter_count += 1
        counterfactuals = self._traverse(self.game.root, 1, np.ones(self.game.player_count))

        for data in self.__data.values():
            data.collect()
            data.clear()

        return tuple(map(float, counterfactuals))

    def ev(self, node: Optional[Node] = None) -> np.ndarray:
        if node is None:
            return self.ev(self.game.root)
        elif isinstance(node, TerminalNode):
            return np.array(node.payoffs)
        elif isinstance(node, ChanceNode):
            return sum_(cast(np.ndarray, self.ev(child) * probability)
                        for child, probability in zip(node.children, node.probabilities))
        elif isinstance(node, PlayerNode):
            return sum_(cast(np.ndarray, self.ev(child) * probability)
                        for child, probability in zip(node.children, self.query(node)))
        else:
            raise TypeError('Argument is not of valid node type.')

    def _traverse(self, node: Node, nature_contrib: float, player_contribs: np.ndarray) -> np.ndarray:
        if isinstance(node, TerminalNode):
            return np.array(node.payoffs)
        elif isinstance(node, ChanceNode):
            return cast(np.ndarray, sum_(
                self._traverse(child, nature_contrib * probability, player_contribs) * probability
                for child, probability in zip(node.children, node.probabilities)
            ))
        elif isinstance(node, PlayerNode):
            return self._solve(node, nature_contrib, player_contribs)
        else:
            raise TypeError('Argument is not of valid node type.')

    def _solve(self, node: PlayerNode, nature_contrib: float, player_contribs: np.ndarray) -> np.ndarray:
        data = self.__data[node.info_set]
        results = [
            self._traverse(child, nature_contrib, replace(
                player_contribs, node.info_set.player, player_contribs[node.info_set.player] * probability,
            )) for child, probability in zip(node.children, data.strategy)
        ]

        data.update(
            player_contribs[node.info_set.player],
            nature_contrib * np.delete(player_contribs, node.info_set.player).prod(),
            np.array(results)[:, node.info_set.player],
        )

        return cast(np.ndarray, sum_(result * probability for result, probability in zip(results, data.strategy)))

    class _BaseData(ABC):
        @property
        @abstractmethod
        def strategy(self) -> np.ndarray:
            pass

        @property
        @abstractmethod
        def average_strategy(self) -> np.ndarray:
            pass

        @abstractmethod
        def update(self, contrib: float, partial_contrib: float, counterfactuals: np.ndarray) -> None:
            pass

        @abstractmethod
        def collect(self) -> None:
            pass

        @abstractmethod
        def clear(self) -> None:
            pass

    class _Data(_BaseData, Generic[T]):
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

            return cast(np.ndarray, pos_regrets / pos_regrets.sum()) if pos_regrets.any() else self.default_strategy

        @property
        def average_strategy(self) -> np.ndarray:
            return cast(np.ndarray, self.strategy_sum / self.weight_sum) if self.weight_sum else self.default_strategy

        @cached_property
        def default_strategy(self) -> np.ndarray:
            return np.full(self.info_set.action_count, 1 / self.info_set.action_count)

        def update(self, contrib: float, partial_contrib: float, counterfactuals: np.ndarray) -> None:
            self.weight += contrib
            self.counterfactuals += partial_contrib * counterfactuals

        def collect(self) -> None:
            self.strategy_sum += self.weight * self.strategy
            self.weight_sum += self.weight
            self.regrets += self.counterfactuals - self.counterfactuals @ self.strategy

        def clear(self) -> None:
            self.weight = 0
            self.counterfactuals.fill(0)


class CFRPSolver(CFRSolver):
    """CFRPSolver is the class for CFR+ solvers."""

    class _Data(CFRSolver._Data['CFRPSolver']):
        @property
        def strategy(self) -> np.ndarray:
            return cast(np.ndarray, self.regrets / self.regrets.sum()) if self.regrets.any() else self.default_strategy

        def collect(self) -> None:
            super().collect()

            multiplier = self.solver.iter_count / (self.solver.iter_count + 1)

            self.strategy_sum *= multiplier
            self.weight_sum *= multiplier
            self.regrets = np.maximum(0, self.regrets)


class DCFRSolver(CFRSolver):
    """DCFRSolver is the class for Discounted CFR solvers."""

    def __init__(self, game: TreeGame, alpha: float = 3 / 2, beta: float = 0, gamma: float = 2):
        super().__init__(game)

        self.__alpha = alpha
        self.__beta = beta
        self.__gamma = gamma

        self._regret_multipliers = np.vectorize(self.regret_multiplier)

    @property
    def alpha(self) -> float:
        return self.__alpha

    @property
    def beta(self) -> float:
        return self.__beta

    @property
    def gamma(self) -> float:
        return self.__gamma

    @property
    def alpha_multiplier(self) -> float:
        return self.iter_count ** self.alpha / (self.iter_count ** self.alpha + 1)

    @property
    def beta_multiplier(self) -> float:
        return self.iter_count ** self.beta / (self.iter_count ** self.beta + 1)

    @property
    def gamma_multiplier(self) -> float:
        return (self.iter_count / (self.iter_count + 1)) ** self.gamma

    def regret_multiplier(self, regret: float) -> float:
        return self.alpha_multiplier if regret > 0 else self.beta_multiplier

    class _Data(CFRSolver._Data['DCFRSolver']):
        def collect(self) -> None:
            super().collect()

            self.strategy_sum *= self.solver.gamma_multiplier
            self.weight_sum *= self.solver.gamma_multiplier
            self.regrets *= self.solver._regret_multipliers(self.regrets)
