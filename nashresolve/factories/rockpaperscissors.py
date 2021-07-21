from copy import deepcopy

from auxiliary import next_or_none
from gameframe.games.rockpaperscissors import RockPaperScissorsGame, RockPaperScissorsHand, RockPaperScissorsPlayer

from nashresolve.factories.sequential import TreeFactory
from nashresolve.trees import Action


class RockPaperScissorsTreeFactory(TreeFactory):
    def __init__(self, player_count=2):
        self.__player_count = player_count

    @property
    def player_count(self):
        return self.__player_count

    def _create_game(self):
        return RockPaperScissorsGame(self.player_count)

    def _create_actions(self, player):
        for hand in RockPaperScissorsHand:
            yield Action(self._create_node(deepcopy(player.game).throw(hand)), f'Throw {hand.value}')

    def _create_chance_actions(self, nature):
        raise ValueError('The nature has no action in rock paper scissor games')

    def _get_actor(self, game):
        return next_or_none(filter(RockPaperScissorsPlayer.can_throw, game.players))

    def _get_payoffs(self, game):
        for player in game.players:
            if player in tuple(game.winners):
                yield 1
            elif player in tuple(game.losers):
                yield -1
            else:
                yield 0

    def _get_info_set(self, player):
        return player.index
