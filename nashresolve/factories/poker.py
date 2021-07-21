from abc import ABC
from copy import deepcopy
from itertools import combinations

from pokertools import KuhnPoker, PokerPlayer

from nashresolve.factories.sequential import SequentialTreeFactory
from nashresolve.trees import Action


class PokerTreeFactory(SequentialTreeFactory, ABC):
    @classmethod
    def _get_player_info_set(cls, player, other):
        return other.bet, other.stack, tuple(map(repr if player is other else str, other.hole))

    def _create_actions(self, player):
        game = player.game

        if player.can_fold():
            yield Action(self._create_node(deepcopy(game).parse('f')), 'Fold')
        elif player.can_check_call():
            yield Action(self._create_node(deepcopy(game).parse(f'cc')), f'Check/call {player.check_call_amount}')
        elif player.can_bet_raise():
            for amount in {player.bet_raise_min_amount, player.bet_raise_max_amount}:
                yield Action(self._create_node(deepcopy(game).parse(f'br {amount}')), f'Bet/raise {amount}')
        elif player.can_discard_draw():
            raise ValueError('Discard-draw is not yet supported')
        elif player.can_showdown():
            yield Action(self._create_node(deepcopy(game).parse('s 0')), 'Muck')
            yield Action(self._create_node(deepcopy(game).parse('s 1')), 'Show')
        else:
            raise ValueError('No action available')

    def _create_chance_actions(self, nature):
        game = nature.game
        population = sorted(game.deck)

        if nature.can_deal_hole():
            for sample in combinations(population, nature.deal_hole_count):
                sample_str = ''.join(map(str, sample))
                yield Action(
                    self._create_node(deepcopy(game).parse(f'dh {sample_str}')),
                    f'Deal {nature.deal_hole_player} {sample_str}',
                )
        elif nature.can_deal_board():
            for sample in combinations(population, nature.deal_board_count):
                sample_str = ''.join(map(str, sample))
                yield Action(self._create_node(deepcopy(game).parse(f'db {sample_str}')), f'Deal board {sample_str}')
        else:
            raise ValueError('No action available')

    def _get_payoffs(self, game):
        yield from map(PokerPlayer.payoff.fget, game.players)

    def _get_info_set(self, player):
        game = player.game

        return str((
            game.actor.index,
            game.pot,
            tuple(map(str, game.board)),
            tuple(map(self._get_player_info_set, game.players)),
        ))


class KuhnPokerTreeFactory(PokerTreeFactory):
    def _create_game(self):
        return KuhnPoker()
