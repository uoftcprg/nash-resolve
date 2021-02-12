# type: ignore
# TODO REMOVE IGNORE
from abc import ABC
from collections import Hashable, Sequence
from copy import deepcopy
from itertools import combinations
from random import choices

from gameframe.poker import NLTHEGame, PokerGame, PokerNature, PokerPlayer

from nashresolve.factories import Action, ChanceAction, SeqTreeFactory


class Settings:
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        self.ante = ante
        self.blinds = blinds
        self.starting_stacks = starting_stacks


class PokerFactory(SeqTreeFactory[PokerGame, PokerNature, PokerPlayer], ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    def _get_chance_actions(self, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        game = nature.game
        actions: list[ChanceAction[PokerGame]] = []

        if card_count := game.board_card_target - len(game.board_cards):
            card_sets = list(combinations(game.deck, card_count))

            for cards in card_sets:
                temp_nature = deepcopy(nature)
                temp_nature.deal_board(*cards)

                actions.append(ChanceAction('Deal Board ' + ' '.join(map(str, cards)), temp_nature.game,
                                            1 / len(card_sets)))
        else:
            player = next(player for player in game.players if player.hole_cards is not None and nature.can_deal_player(
                player, *choices(game.deck, k=game.hole_card_target - len(player.hole_cards)),
            ))
            card_sets = list(combinations(game.deck, game.hole_card_target - len(player.hole_cards)))

            for cards in card_sets:
                temp_nature = deepcopy(nature)
                temp_nature.deal_player(player, *cards)

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
        return NLTHEGame(self.settings.ante, self.settings.blinds, self.settings.starting_stacks)
