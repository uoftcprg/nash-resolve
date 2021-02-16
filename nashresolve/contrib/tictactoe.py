from collections import Hashable, Sequence
from copy import deepcopy

from gameframe.game import BaseActor
from gameframe.tictactoe import TTTGame, TTTPlayer

from nashresolve.factories import Action, ChanceAction, SeqTreeFactory


class TTTTreeFactory(SeqTreeFactory[TTTGame, BaseActor, TTTPlayer]):
    def _create_game(self) -> TTTGame:
        return TTTGame()

    def _get_payoff(self, player: TTTPlayer) -> float:
        if player.game.winner is None:
            return 0
        else:
            return 1 if player.game.winner is player else -1

    def _get_chance_actions(self, nature: BaseActor) -> Sequence[ChanceAction[TTTGame]]:
        raise NotImplementedError

    def _get_player_actions(self, player: TTTPlayer) -> Sequence[Action[TTTGame]]:
        actions: list[Action[TTTGame]] = []

        for r, c in player.game.empty_coords:
            temp_player = deepcopy(player)
            temp_player.mark(r, c)

            actions.append(Action(f'Mark ({r}, {c})', temp_player.game))

        return actions

    def _get_info_set_data(self, player: TTTPlayer) -> Hashable:
        return str(player.game.board)
