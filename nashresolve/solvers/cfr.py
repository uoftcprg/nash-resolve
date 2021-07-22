import numpy as np

from nashresolve.solvers.bases import TreeSolver


class CFRSolver(TreeSolver):
    """CFRSolver is the class for vanilla counterfactual regret minimization solvers."""

    class Datum:
        def __init__(self, player, action_count):
            self.player = player
            self.action_count = action_count

            self.weight = 0
            self.counterfactuals = np.zeros(action_count)

            self.strategy_sum = np.zeros(action_count)
            self.weight_sum = 0
            self.regrets = np.zeros(action_count)

        @property
        def strategy(self):
            pos_regrets = self.regrets.clip(0)

            return pos_regrets / pos_regrets.sum() if pos_regrets.any() else self.default_strategy

        @property
        def average_strategy(self):
            return self.strategy_sum / self.weight_sum if self.weight_sum else self.default_strategy

        @property
        def default_strategy(self):
            return np.full(self.action_count, 1 / self.action_count)

        def update(self, contribution, other_contribution, counterfactuals):
            self.weight += contribution
            self.counterfactuals += other_contribution * counterfactuals

        def collect(self):
            self.strategy_sum += self.weight * self.strategy
            self.weight_sum += self.weight
            self.regrets += self.counterfactuals - np.full(self.action_count, self.counterfactuals @ self.strategy)

        def clear(self):
            self.weight = 0
            self.counterfactuals = np.zeros(self.action_count)

    def __init__(self, game):
        super().__init__(game)

        self._iteration_count = 0
        self._data = {}

    @property
    def iteration_count(self):
        return self._iteration_count

    @property
    def data(self):
        return self._data

    def get_datum(self, node):
        if node.info_set in self.data:
            return self.data[node.info_set]
        else:
            self.data[node.info_set] = self.Datum(node.action_count)

            return self.data[node.info_set]

    def get_probabilities(self, node):
        if node.is_terminal_node():
            return np.empty(0)
        elif node.is_chance_node():
            return node.chances
        elif node.is_player_node():
            return self.get_datum(node).average_strategy
        else:
            raise ValueError('Unknown node type')

    def get_ev(self, node):
        if node.is_terminal_node():
            return node.payoffs
        else:
            return self.get_probabilities(node) @ np.fromiter(map(self.get_ev, node.children), float)

    def step(self):
        self._iteration_count += 1
        counterfactuals = self._traverse(self.game.root, 1, np.ones(self.game.player_count))

        for datum in self.data.values():
            datum.collect()
            datum.clear()

        return counterfactuals

    def _traverse(self, node, nature_contribution, player_contributions):
        if node.is_terminal_node():
            return node.payoffs
        elif node.is_chance_node():
            counterfactuals = 0

            for child, probability in zip(node.children, node.probabilities):
                counterfactuals += probability * self._traverse(
                    child, nature_contribution * probability, player_contributions,
                )

            return counterfactuals
        elif node.is_player_node():
            return self._solve(node, nature_contribution, player_contributions)
        else:
            raise ValueError('Unknown node type')

    def _solve(self, node, nature_contribution, player_contributions):
        datum = self.get_datum(node)
        counterfactuals = [
            self._traverse(child, nature_contribution, np.hstack(
                player_contributions[:node.info_set.player],
                (player_contributions[node.info_set.player] * probability,),
                player_contributions[node.info_set.player + 1:],
            )) for child, probability in zip(node.children, datum.strategy)
        ]

        datum.update(
            player_contributions[node.info_set.player],
            nature_contribution * np.hstack(
                player_contributions[:node.info_set.player], player_contributions[node.info_set.player + 1:],
            ).prod(),
            counterfactuals[:, node.info_set.player],
        )

        return datum.strategy @ counterfactuals


'''
class CFRPSolver(CFRSolver):
    """CFRPSolver is the class for CFR+ solvers."""

    class _Data(CFRSolver._Data['CFRPSolver']):
        @property
        def strategy(self):
            return self.regrets / sum(self.regrets) if any(self.regrets) else self.default_strategy

        def collect(self):
            super().collect()

            multiplier = self.solver._iter_count / (self.solver._iter_count + 1)

            self.strategy_sum *= multiplier
            self.weight_sum *= multiplier
            self.regrets = Vector(max(0.0, regret) for regret in self.regrets)


class DCFRSolver(CFRSolver):
    """DCFRSolver is the class for Discounted CFR solvers."""

    def __init__(self, game, alpha=3 / 2, beta=0, gamma=2):
        super().__init__(game)

        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    @property
    def alpha_multiplier(self):
        return self._iter_count ** self.alpha / (self._iter_count ** self.alpha + 1)

    @property
    def beta_multiplier(self):
        return self._iter_count ** self.beta / (self._iter_count ** self.beta + 1)

    @property
    def gamma_multiplier(self):
        return (self._iter_count / (self._iter_count + 1)) ** self.gamma

    def regret_multiplier(self, regret):
        return self.alpha_multiplier if regret > 0 else self.beta_multiplier

    class _Data(CFRSolver._Data['DCFRSolver']):
        def collect(self):
            super().collect()

            self.strategy_sum *= self.solver.gamma_multiplier
            self.weight_sum *= self.solver.gamma_multiplier
            self.regrets = Vector(self.solver.regret_multiplier(regret) * regret for regret in self.regrets)
'''
