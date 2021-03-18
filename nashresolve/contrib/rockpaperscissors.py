from collections.abc import Hashable, Sequence
from copy import deepcopy

from gameframe.rockpaperscissors import RockPaperScissors, RockPaperScissorsHand, RockPaperScissorsPlayer

from nashresolve.factories import Action, ChanceAction, TreeFactory


class RockPaperScissorsTreeFactory(TreeFactory[RockPaperScissors, None, RockPaperScissorsPlayer]):
    def _create_game(self) -> RockPaperScissors:
        return RockPaperScissors()

    def _get_actor(self, state: RockPaperScissors) -> RockPaperScissorsPlayer:
        return state.players[0 if state.players[0].hand is None else 1]

    def _get_payoff(self, state: RockPaperScissors, player: RockPaperScissorsPlayer) -> float:
        if state.winner is None:
            return 0
        else:
            return 1 if state.winner is player else -1

    def _get_chance_actions(self, state: RockPaperScissors, nature: None) -> Sequence[ChanceAction[RockPaperScissors]]:
        raise NotImplementedError

    def _get_player_actions(self, state: RockPaperScissors,
                            player: RockPaperScissorsPlayer) -> Sequence[Action[RockPaperScissors]]:
        actions: list[Action[RockPaperScissors]] = []

        for hand in RockPaperScissorsHand:
            substate = deepcopy(state)
            substate.players[state.players.index(player)].throw(hand)

            actions.append(Action(str(hand.value), substate))

        return actions

    def _get_info_set_data(self, state: RockPaperScissors, player: RockPaperScissorsPlayer) -> Hashable:
        return state.players.index(player)
