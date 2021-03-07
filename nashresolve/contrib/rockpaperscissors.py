from collections import Hashable, Sequence
from copy import deepcopy

from gameframe.rockpaperscissors import RPSGame, RPSHand, RPSPlayer

from nashresolve.factories import Action, ChanceAction, TreeFactory


class RPSTreeFactory(TreeFactory[RPSGame, None, RPSPlayer]):
    def _create_game(self) -> RPSGame:
        return RPSGame()

    def _get_actor(self, state: RPSGame) -> RPSPlayer:
        return state.players[0 if state.players[0].hand is None else 1]

    def _get_payoff(self, state: RPSGame, player: RPSPlayer) -> float:
        if state.winner is None:
            return 0
        else:
            return 1 if state.winner is player else -1

    def _get_chance_actions(self, state: RPSGame, nature: None) -> Sequence[ChanceAction[RPSGame]]:
        raise NotImplementedError

    def _get_player_actions(self, state: RPSGame, player: RPSPlayer) -> Sequence[Action[RPSGame]]:
        actions: list[Action[RPSGame]] = []

        for hand in RPSHand:
            substate = deepcopy(state)
            substate.players[state.players.index(player)].throw(hand)

            actions.append(Action(str(hand.value), substate))

        return actions

    def _get_info_set_data(self, state: RPSGame, player: RPSPlayer) -> Hashable:
        return state.players.index(player)
