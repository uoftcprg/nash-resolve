from abc import ABC

from nashresolve.factories.game import TreeFactory


class SequentialTreeFactory(TreeFactory, ABC):
    def _get_actor(self, game):
        return game.actor
