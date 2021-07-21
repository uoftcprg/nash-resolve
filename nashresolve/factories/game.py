from abc import ABC, abstractmethod

from nashresolve.games import TreeGame
from nashresolve.trees import ChanceNode, PlayerNode, TerminalNode


class Factory(ABC):
    @abstractmethod
    def build(self): ...


class TreeFactory(Factory, ABC):
    def build(self):
        return TreeGame(self._create_node(self._create_game()))

    def _create_node(self, game):
        actor = self._get_actor(game)

        if actor is None:
            return TerminalNode(self._get_payoffs(game))
        elif actor.is_nature():
            return ChanceNode(self._create_chance_actions(game))
        elif actor.is_player():
            return PlayerNode(actor.index, self._get_info_set(actor), self._create_actions(actor))
        else:
            raise ValueError('Unknown player type')

    @abstractmethod
    def _create_game(self):
        ...

    @abstractmethod
    def _create_actions(self, player):
        ...

    @abstractmethod
    def _create_chance_actions(self, nature):
        ...

    @abstractmethod
    def _get_actor(self, game):
        ...

    @abstractmethod
    def _get_payoffs(self, game):
        ...

    @abstractmethod
    def _get_info_set(self, player):
        ...
