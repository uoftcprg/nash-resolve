from copy import deepcopy
from functools import partial

from gameframe.games.tictactoe import TicTacToeGame

from nashresolve.factories.sequential import SequentialTreeFactory
from nashresolve.trees import Action


class TicTacToeTreeFactory(SequentialTreeFactory):
    _cache = {}

    def _create_action(self, game, coordinates):
        return Action(self._create_node(deepcopy(game).mark(coordinates)), f'Mark {coordinates[0]}, {coordinates[1]}')

    def _create_node(self, game):
        state = str(game.board)

        if state in self._cache:
            return self._cache[state]
        else:
            self._cache[state] = super()._create_node(game)

            return self._cache[state]

    def _create_game(self):
        return TicTacToeGame()

    def _create_actions(self, player):
        return map(partial(self._create_action, player.game), player.game.empty_cell_locations)

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
