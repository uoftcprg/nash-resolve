from collections.abc import Sequence
from functools import cached_property
from typing import Any, Final, Generic, Optional, TypeVar, Union

from math2.linalg import Vector, full, ones, replaced, zeros
from math2.misc import product, sum_

from nashresolve.games import TreeGame
from nashresolve.solvers.bases import TreeSolver
from nashresolve.trees import ChanceNode, InfoSet, Node, PlayerNode, TerminalNode

T = TypeVar('T', bound='CFRSolver')


class CFRSolver(TreeSolver):
    """CFRSolver is the class for vanilla counterfactual regret minimization solvers."""

    def __init__(self, game: TreeGame):
        super().__init__(game)

        self._iter_count = 0
        self.__data: dict[InfoSet, CFRSolver._Data[Any]] = {
            info_set: self._Data(self, info_set) for info_set in game.info_sets
        }

    @property
    def iter_count(self) -> int:
        return self._iter_count

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

    def ev(self, node: Optional[Node] = None) -> Sequence[float]:
        return self._ev(self.game.root if node is None else node)

    def step(self) -> Sequence[float]:
        self._iter_count += 1
        counterfactuals = self._traverse(self.game.root, 1, ones(self.game.player_count))

        for data in self.__data.values():
            data.collect()
            data.clear()

        return tuple(map(float, counterfactuals))

    def _ev(self, node: Node) -> Vector:
        if node is None:
            return self._ev(self.game.root)
        elif isinstance(node, TerminalNode):
            return Vector(node.payoffs)
        elif isinstance(node, ChanceNode):
            return sum_(self._ev(child) * probability for child, probability in zip(node.children, node.probabilities))
        elif isinstance(node, PlayerNode):
            return sum_(self._ev(child) * probability for child, probability in zip(node.children, self.query(node)))
        else:
            raise TypeError('Argument is not of valid node type.')

    def _traverse(self, node: Node, nature_contrib: float, player_contribs: Vector) -> Vector:
        if isinstance(node, TerminalNode):
            return Vector(node.payoffs)
        elif isinstance(node, ChanceNode):
            return sum_(self._traverse(child, nature_contrib * probability, player_contribs) * probability
                        for child, probability in zip(node.children, node.probabilities))
        elif isinstance(node, PlayerNode):
            return self._solve(node, nature_contrib, player_contribs)
        else:
            raise TypeError('Argument is not of valid node type.')

    def _solve(self, node: PlayerNode, nature_contrib: float, player_contribs: Vector) -> Vector:
        data = self.__data[node.info_set]
        results = [
            self._traverse(child, nature_contrib, replaced(
                player_contribs, node.info_set.player, player_contribs[node.info_set.player] * probability,
            )) for child, probability in zip(node.children, data.strategy)
        ]

        data.update(
            player_contribs[node.info_set.player],
            nature_contrib * product(contrib for i, contrib in enumerate(player_contribs) if i != node.info_set.player),
            Vector(result[node.info_set.player] for result in results),
        )

        return sum_(result * probability for result, probability in zip(results, data.strategy))

    class _Data(Generic[T]):
        def __init__(self, solver: T, info_set: InfoSet):
            self.solver = solver
            self.info_set = info_set

            self.weight = 0.0
            self.counterfactuals = zeros(info_set.action_count)

            self.strategy_sum = zeros(info_set.action_count)
            self.weight_sum = 0.0
            self.regrets = zeros(info_set.action_count)

        @property
        def strategy(self) -> Vector:
            pos_regrets = Vector(max(0.0, regret) for regret in self.regrets)

            return pos_regrets / sum(pos_regrets) if any(pos_regrets) else self.default_strategy

        @property
        def average_strategy(self) -> Vector:
            return self.strategy_sum / self.weight_sum if self.weight_sum else self.default_strategy

        @cached_property
        def default_strategy(self) -> Vector:
            return full(self.info_set.action_count, 1 / self.info_set.action_count)

        def update(self, contrib: float, partial_contrib: float, counterfactuals: Vector) -> None:
            self.weight += contrib
            self.counterfactuals += partial_contrib * counterfactuals

        def collect(self) -> None:
            self.strategy_sum += self.weight * self.strategy
            self.weight_sum += self.weight
            self.regrets += self.counterfactuals - full(self.info_set.action_count,
                                                        self.counterfactuals @ self.strategy)

        def clear(self) -> None:
            self.weight = 0
            self.counterfactuals = zeros(self.info_set.action_count)


class CFRPSolver(CFRSolver):
    """CFRPSolver is the class for CFR+ solvers."""

    class _Data(CFRSolver._Data['CFRPSolver']):
        @property
        def strategy(self) -> Vector:
            return self.regrets / sum(self.regrets) if any(self.regrets) else self.default_strategy

        def collect(self) -> None:
            super().collect()

            multiplier = self.solver._iter_count / (self.solver._iter_count + 1)

            self.strategy_sum *= multiplier
            self.weight_sum *= multiplier
            self.regrets = Vector(max(0.0, regret) for regret in self.regrets)


class DCFRSolver(CFRSolver):
    """DCFRSolver is the class for Discounted CFR solvers."""

    def __init__(self, game: TreeGame, alpha: float = 3 / 2, beta: float = 0, gamma: float = 2):
        super().__init__(game)

        self.alpha: Final = alpha
        self.beta: Final = beta
        self.gamma: Final = gamma

    @property
    def alpha_multiplier(self) -> float:
        return self._iter_count ** self.alpha / (self._iter_count ** self.alpha + 1)

    @property
    def beta_multiplier(self) -> float:
        return self._iter_count ** self.beta / (self._iter_count ** self.beta + 1)

    @property
    def gamma_multiplier(self) -> float:
        return (self._iter_count / (self._iter_count + 1)) ** self.gamma

    def regret_multiplier(self, regret: float) -> float:
        return self.alpha_multiplier if regret > 0 else self.beta_multiplier

    class _Data(CFRSolver._Data['DCFRSolver']):
        def collect(self) -> None:
            super().collect()

            self.strategy_sum *= self.solver.gamma_multiplier
            self.weight_sum *= self.solver.gamma_multiplier
            self.regrets = Vector(self.solver.regret_multiplier(regret) * regret for regret in self.regrets)
