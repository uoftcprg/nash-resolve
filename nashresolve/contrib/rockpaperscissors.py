from collections import Hashable, Sequence
from copy import deepcopy

from gameframe.game import BaseActor
from gameframe.rockpaperscissors import RPSGame, RPSHand, RPSPlayer

from nashresolve.factories import Action, ChanceAction, TreeFactory


class RPSTreeFactory(TreeFactory[RPSGame, BaseActor, RPSPlayer]):
    def _create_game(self) -> RPSGame:
        return RPSGame()

    def _get_actor(self, state: RPSGame) -> RPSPlayer:
        return state.players[0 if state.players[0].hand is None else 1]

    def _get_payoff(self, player: RPSPlayer) -> float:
        if player.game.winner is None:
            return 0
        else:
            return 1 if player.game.winner is player else -1

    def _get_chance_actions(self, nature: BaseActor) -> Sequence[ChanceAction[RPSGame]]:
        raise NotImplementedError

    def _get_player_actions(self, player: RPSPlayer) -> Sequence[Action[RPSGame]]:
        actions: list[Action[RPSGame]] = []

        for hand in RPSHand:
            temp_player = deepcopy(player)
            temp_player.throw(hand)

            actions.append(Action(hand.value, temp_player.game))

        return actions

    def _get_info_set_data(self, player: RPSPlayer) -> Hashable:
        return player.game.players.index(player)
