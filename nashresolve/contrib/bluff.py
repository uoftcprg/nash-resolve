from __future__ import annotations

from gameframe.game.generics import Actor
from gameframe.sequential.generics import SeqGame


class BluffGame(SeqGame[Actor['BluffGame'], 'BluffPlayer']):
    def __init__(self, reward: int, starting_stack: int) -> None:
        nature = Actor(self)
        players = BluffPlayer(self), BluffPlayer(self)
        actor = players[0]

        super().__init__(nature, players, actor)

        self.__reward = reward
        self.__starting_stack = starting_stack

    @property
    def reward(self) -> int:
        return self.__reward

    @property
    def starting_stack(self) -> int:
        return self.__starting_stack


class BluffPlayer(Actor[BluffGame]):
    def __init__(self, game: BluffGame) -> None:
        super().__init__(game)

        self._commitment = 0

    @property
    def commitment(self) -> int:
        return self._commitment

    @property
    def stack(self) -> int:
        return self.game.starting_stack - self.commitment

    def commit(self, amount: int) -> None:
        self._commitment = amount
        self.game._actor = self.game.players[1]

    def accept(self) -> None:
        self._commitment = self.game.players[0].commitment

    def decline(self) -> None:
        pass
