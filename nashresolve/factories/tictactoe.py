from copy import deepcopy

from gameframe.games.tictactoe import TicTacToeGame

from nashresolve.factories.sequential import SequentialTreeFactory
from nashresolve.trees import Action


class TicTacToeTreeFactory(SequentialTreeFactory):
    _cache = {}

    def _create_node(self, game):
        state = str(game.board)

        if state not in self._cache:
            self._cache[state] = super()._create_node(game)

        return self._cache[state]

    def _create_game(self):
        return TicTacToeGame()

    def _create_actions(self, player):
        for r, c in player.game.empty_cell_locations:
            yield Action(self._create_node(deepcopy(player.game).mark((r, c))), f'Mark {r}, {c}')

    def _create_chance_actions(self, nature):
        raise ValueError('The nature has no action in tic tac toe games')

    def _get_payoffs(self, game):
        for player in game.players:
            if player is game.winner:
                yield 1
            elif player is game.loser:
                yield -1
            else:
                yield 0

    def _get_info_set(self, player):
        return str(player.game.board)
