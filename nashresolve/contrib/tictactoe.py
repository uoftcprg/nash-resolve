from collections.abc import Hashable, Sequence
from copy import deepcopy

from gameframe.tictactoe import TicTacToe, TicTacToePlayer, parse_tic_tac_toe

from nashresolve.factories import Action, ChanceAction, SequentialTreeFactory


class TicTacToeTreeFactory(SequentialTreeFactory[TicTacToe, None, TicTacToePlayer]):
    def _create_game(self) -> TicTacToe:
        return TicTacToe()

    def _get_payoff(self, state: TicTacToe, player: TicTacToePlayer) -> float:
        if state.winner is None:
            return 0
        else:
            return 1 if state.winner is player else -1

    def _get_chance_actions(self, state: TicTacToe, nature: None) -> Sequence[ChanceAction[TicTacToe]]:
        raise NotImplementedError

    def _get_player_actions(self, state: TicTacToe, player: TicTacToePlayer) -> Sequence[Action[TicTacToe]]:
        actions: list[Action[TicTacToe]] = []

        for r, c in state.empty_coords:
            parse_tic_tac_toe(substate := deepcopy(state), [(r, c)])

            actions.append(Action(f'Mark ({r}, {c})', substate))

        return actions

    def _get_info_set_data(self, state: TicTacToe, player: TicTacToePlayer) -> Hashable:
        return str(state.board)
