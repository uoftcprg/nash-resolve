from collections import Sequence
from copy import deepcopy

from gameframe.game import BaseActor
from gameframe.rockpaperscissors import Hand, RPSGame, RPSPlayer

from nashresolve.factories import Action, ChanceAction, TreeFactory
from nashresolve.trees import InfoSet


class RPSTreeFactory(TreeFactory[RPSGame, BaseActor, RPSPlayer]):
    def __init__(self) -> None:
        super().__init__(2)

        self.__info_sets = [InfoSet(3, 0), InfoSet(3, 1)]

    def _get_chance_actions(self, nature: BaseActor) -> Sequence[ChanceAction[RPSGame]]:
        raise NotImplementedError

    def _get_player_actions(self, player: RPSPlayer) -> Sequence[Action[RPSGame]]:
        actions: list[Action[RPSGame]] = []

        for hand in Hand:
            temp_player = deepcopy(player)
            temp_player.throw(hand)

            actions.append(Action(hand.value, temp_player.game))

        return actions

    def _get_payoff(self, player: RPSPlayer) -> float:
        if player.game.winner is None:
            return 0
        else:
            return 1 if player.game.winner is player else -1

    def _get_actor(self, state: RPSGame) -> RPSPlayer:
        return state.players[0 if state.players[0].hand is None else 1]

    def _get_info_set(self, player: RPSPlayer) -> InfoSet:
        return self.__info_sets[player.game.players.index(player)]

    def _create_game(self) -> RPSGame:
        return RPSGame()
