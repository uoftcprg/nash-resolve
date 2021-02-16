from collections import Iterable, Sequence
from copy import deepcopy

from gameframe.poker import PokerGame, PokerNature, PokerPlayer

from nashresolve.factories import Action, ChanceAction
from nashresolve.utils import limit
from nashresolve.contrib.poker import PokerTreeFactory


class ReducedPokerTreeFactory(PokerTreeFactory):
    def __init__(self, initial_state: PokerGame, bet_raise_scalars: Sequence[float]):
        self.__initial_state = deepcopy(initial_state)
        self.__bet_raise_scalars = tuple(bet_raise_scalars)

    def _get_chance_actions(self, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        return list(map(
            lambda action: ChanceAction(action.label, self.__skip_showdown(action.substate), action.probability),
            super()._get_chance_actions(nature),
        ))

    def _get_player_actions(self, player: PokerPlayer) -> Sequence[Action[PokerGame]]:
        return list(map(lambda action: Action(action.label, self.__skip_showdown(action.substate)),
                        super()._get_player_actions(player)))

    def _create_game(self) -> PokerGame:
        return self.__initial_state

    def _get_bet_raise_amounts(self, player: PokerPlayer) -> Iterable[int]:
        bets = [player.bet for player in player.game.players]
        pot_bet = player.game.pot + sum(bets) + max(bets) - player.bet
        amounts = set()

        for scalar in self.__bet_raise_scalars:
            amount = limit(int(max(bets) + pot_bet * scalar), player.min_bet_raise_amount, player.max_bet_raise_amount)
            amounts.add(amount)

        return sorted(amounts)

    @staticmethod
    def __skip_showdown(game: PokerGame) -> PokerGame:
        while any(player.can_showdown() for player in game.players):
            next(player for player in game.players if player.can_showdown()).showdown(True)

        return game
