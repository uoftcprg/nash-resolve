from collections.abc import Hashable, Sequence
from copy import deepcopy

from gameframe.tictactoe import TTTGame, TTTPlayer, parse_ttt

from nashresolve.factories import Action, ChanceAction, SequentialTreeFactory


class TTTTreeFactory(SequentialTreeFactory[TTTGame, None, TTTPlayer]):
    def _create_game(self) -> TTTGame:
        return TTTGame()

    def _get_payoff(self, state: TTTGame, player: TTTPlayer) -> float:
        if state.winner is None:
            return 0
        else:
            return 1 if state.winner is player else -1

    def _get_chance_actions(self, state: TTTGame, nature: None) -> Sequence[ChanceAction[TTTGame]]:
        raise NotImplementedError

    def _get_player_actions(self, state: TTTGame, player: TTTPlayer) -> Sequence[Action[TTTGame]]:
        actions: list[Action[TTTGame]] = []

        for r, c in state.empty_coords:
            parse_ttt(substate := deepcopy(state), [(r, c)])

            actions.append(Action(f'Mark ({r}, {c})', substate))

        return actions

    def _get_info_set_data(self, state: TTTGame, player: TTTPlayer) -> Hashable:
        return str(state.board)
