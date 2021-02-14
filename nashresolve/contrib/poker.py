from abc import ABC
from collections import Hashable, Sequence
from copy import deepcopy
from itertools import combinations
from typing import cast

from gameframe.poker import PokerGame, PokerNature, PokerPlayer
from pokertools import HoleCard

from nashresolve.factories import Action, ChanceAction, SeqTreeFactory


class PokerFactory(SeqTreeFactory[PokerGame, PokerNature, PokerPlayer], ABC):
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        self.ante = ante
        self.blinds = blinds
        self.starting_stacks = starting_stacks

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
            for amount in range(player.min_bet_raise_amount, player.max_bet_raise_amount + 1):
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
                (
                    ('bet', game.players[i].bet),
                    ('stack', game.players[i].stack),
                    ('hole_cards', (
                        tuple(map(lambda hole_card: hole_card.rank.value + hole_card.suit.value,
                                  cast(Sequence[HoleCard], player.hole_cards))) if i == player.index else
                        (None if (hole_cards := game.players[i].hole_cards) is None else (None,) * len(hole_cards))
                    )),
                ) for i in range(len(player.game.players))
            )),
        ))
