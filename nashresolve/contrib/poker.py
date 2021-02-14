from abc import ABC
from collections import Hashable, Iterable, Sequence
from copy import deepcopy
from itertools import combinations
from typing import cast

from gameframe.poker import PokerGame, PokerNature, PokerPlayer
from pokertools import HoleCard

from nashresolve.factories import Action, ChanceAction, SeqTreeFactory
from nashresolve.utils import limit


class PokerFactory(SeqTreeFactory[PokerGame, PokerNature, PokerPlayer], ABC):
    def _get_payoff(self, player: PokerPlayer) -> float:
        return player.stack - player.starting_stack

    def _get_chance_actions(self, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        game = nature.game
        actions: list[ChanceAction[PokerGame]] = []

        if nature.can_deal_board():
            card_sets = list(combinations(game.deck, nature.board_deal_count))

            for cards in card_sets:
                temp_nature = deepcopy(nature)
                temp_nature.deal_board(*cards)

                actions.append(ChanceAction('Deal Board ' + ' '.join(map(str, cards)), temp_nature.game,
                                            1 / len(card_sets)))
        else:
            player = next(player for player in game.players if nature.can_deal_player(player))
            card_sets = list(combinations(game.deck, nature.player_deal_count))

            for cards in card_sets:
                temp_nature = deepcopy(nature)
                temp_nature.deal_player(temp_nature.game.players[player.index], *cards)

                actions.append(ChanceAction(f'Deal Player {player.index} ' + ' '.join(map(str, cards)),
                                            temp_nature.game, 1 / len(card_sets)))

        return actions

    def _get_player_actions(self, player: PokerPlayer) -> Sequence[Action[PokerGame]]:
        actions: list[Action[PokerGame]] = []

        if player.can_fold():
            temp_player = deepcopy(player)
            temp_player.fold()

            actions.append(Action('Fold', temp_player.game))

        if player.can_check_call():
            temp_player = deepcopy(player)
            temp_player.check_call()

            actions.append(Action('Check/Call', temp_player.game))

        if player.can_bet_raise():
            for amount in self._get_bet_raise_amounts(player):
                temp_player = deepcopy(player)
                temp_player.bet_raise(amount)

                actions.append(Action(f'Bet/Raise {amount}', temp_player.game))

        if player.can_showdown():
            for force in [False, True]:
                temp_player = deepcopy(player)
                temp_player.showdown(force)

                actions.append(Action('Force showdown' if force else 'Showdown', temp_player.game))

        return actions

    def _get_info_set_data(self, player: PokerPlayer) -> Hashable:
        game = player.game

        return str((
            ('pot', game.pot),
            ('board_cards', tuple(game.board_cards)),
            ('players', tuple(
                (('bet', game.players[i].bet),
                 ('stack', game.players[i].stack),
                 ('hole_cards', (
                     tuple(map(lambda hole_card: hole_card.rank.value + hole_card.suit.value,
                               cast(Sequence[HoleCard], player.hole_cards))) if i == player.index else
                     (None if (hole_cards := game.players[i].hole_cards) is None else (None,) * len(hole_cards))))
                 ) for i in range(len(player.game.players))
            )),
        ))

    def _get_bet_raise_amounts(self, player: PokerPlayer) -> Iterable[int]:
        return range(player.min_bet_raise_amount, player.max_bet_raise_amount)


class ReducedPokerFactory(PokerFactory):
    def __init__(self, initial_state: PokerGame, bet_raise_scalars: Sequence[float]):
        self.__initial_state = deepcopy(initial_state)
        self.__bet_raise_scalars = tuple(bet_raise_scalars)

    def _get_chance_actions(self, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        return list(map(
            lambda action: ChanceAction(action.label, self.skip_showdown(action.substate), action.probability),
            super()._get_chance_actions(nature),
        ))

    def _get_player_actions(self, player: PokerPlayer) -> Sequence[Action[PokerGame]]:
        return list(map(lambda action: Action(action.label, self.skip_showdown(action.substate)),
                        super()._get_player_actions(player)))

    def _create_game(self) -> PokerGame:
        return self.__initial_state

    def _get_bet_raise_amounts(self, player: PokerPlayer) -> Iterable[int]:
        bets = [player.bet for player in player.game.players]
        pot_bet = player.game.pot + sum(bets) + max(bets) - player.bet
        amounts = set()

        for scalar in self.__bet_raise_scalars:
            amounts.add(
                limit(int(max(bets) + pot_bet * scalar), player.min_bet_raise_amount, player.max_bet_raise_amount))

        return sorted(amounts)

    @staticmethod
    def skip_showdown(game: PokerGame) -> PokerGame:
        while any(player.can_showdown() for player in game.players):
            next(player for player in game.players if player.can_showdown()).showdown(True)

        return game
