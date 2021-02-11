from abc import ABC
from collections import Hashable, Sequence
from copy import deepcopy
from itertools import combinations
from random import choices
from typing import cast

from gameframe.poker import HoleCard, NLTHEGame, PokerGame, PokerNature, PokerPlayer

from nashresolve.factories import Action, ChanceAction, SeqTreeFactory


class PokerFactory(SeqTreeFactory[PokerGame, PokerNature, PokerPlayer], ABC):
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        self.ante = ante
        self.blinds = blinds
        self.starting_stacks = starting_stacks

    def _get_chance_actions(self, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        game = nature.game
        actions: list[ChanceAction[PokerGame]] = []

        if card_count := game.board_card_target - len(game.board_cards):
            samples = list(combinations(game.deck, card_count))

            for cards in samples:
                temp_nature = deepcopy(nature)
                temp_nature.deal_board(*cards)

                actions.append(ChanceAction('Deal Board ' + ' '.join(map(str, cards)), temp_nature.game,
                                            1 / len(samples)))
        else:
            player = next(
                player for player in game.players if not player.mucked and nature.can_deal_player(
                    player,
                    *choices(game.deck, k=game.hole_card_target - len(cast(Sequence[HoleCard], player.hole_cards)))
                )
            )
            samples = list(combinations(game.deck, card_count))

            for cards in samples:
                temp_nature = deepcopy(nature)
                temp_nature.deal_player(player, *cards)

                actions.append(ChanceAction(f'Deal Player {player.index} ' + ' '.join(map(str, cards)),
                                            temp_nature.game, 1 / len(samples)))

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

        if (interval := player.game.bet_raise_interval) is not None:
            for amount in range(interval[0], interval[1] + 1):
                temp_player = deepcopy(player)
                temp_player.bet_raise(amount)

                actions.append(Action(f'Bet/Raise {amount}', temp_player.game))

        if player.can_showdown():
            temp_player = deepcopy(player)
            temp_player.showdown()

            actions.append(Action(f'Showdown', temp_player.game))

        return actions

    def _get_payoff(self, player: PokerPlayer) -> float:
        return player.stack - player.starting_stack

    def _get_info_set_data(self, player: PokerPlayer) -> Hashable:
        return ''  # TODO


class NLTHEFactory(PokerFactory):
    def _create_game(self) -> NLTHEGame:
        return NLTHEGame(self.ante, self.blinds, self.starting_stacks)
