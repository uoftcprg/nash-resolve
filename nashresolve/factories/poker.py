from abc import ABC
from copy import deepcopy

from pokertools import KuhnPoker, PokerPlayer

from nashresolve.factories.sequential import SequentialTreeFactory
from nashresolve.trees import Action


class PokerTreeFactory(SequentialTreeFactory, ABC):
    def _create_action(self, game, token):
        return Action(self._create_node(deepcopy(game).parse(token)), token)

    def _create_actions(self, player):
        ...

    def _create_chance_actions(self, nature):
        ...

    def _get_payoffs(self, game):
        yield from map(PokerPlayer.payoff.fget, game.players)

    def _get_info_set(self, player):
        game = player.game

        return (game.actor.index, game.pot, tuple(map(str, game.board)), (
            (other.bet, other.stack, (other.hole if other is player else None)) for other in game.players
        ))


class KuhnPokerTreeFactory(PokerTreeFactory):
    def _create_game(self):
        return KuhnPoker()
