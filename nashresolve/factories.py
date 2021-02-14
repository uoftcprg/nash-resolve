from abc import ABC, abstractmethod
from collections import Hashable, Sequence
from typing import Generic, Union, cast

from gameframe.game.generics import G, N, P
from gameframe.sequential.generics import G as SG

from nashresolve.games import Game, TreeGame
from nashresolve.trees import ChanceNode, Node, PlayerNode, TerminalNode


class Action(Generic[G]):
    def __init__(self, label: str, substate: G):
        self.__label = label
        self.__substate = substate

    @property
    def label(self) -> str:
        return self.__label

    @property
    def substate(self) -> G:
        return self.__substate


class ChanceAction(Action[G]):
    def __init__(self, label: str, substate: G, probability: float):
        super().__init__(label, substate)

        self.__probability = probability

    @property
    def probability(self) -> float:
        return self.__probability


class GameFactory(Generic[G, N, P], ABC):
    @abstractmethod
    def build(self) -> Game:
        pass


class TreeFactory(GameFactory[G, N, P], ABC):
    def build(self) -> TreeGame:
        return TreeGame(self._build_tree('Root', self._create_game()))

    def _build_tree(self, label: str, state: G) -> Node:
        if state.terminal:
            return TerminalNode(label, [self._get_payoff(cast(P, player)) for player in state.players])
        else:
            actor = self._get_actor(state)

            if actor is state.nature:
                chance_actions = self._get_chance_actions(cast(N, state.nature))

                return ChanceNode(label, [self._build_tree(action.label, action.substate) for action in chance_actions],
                                  [action.probability for action in chance_actions])
            else:
                player = cast(P, self._get_actor(state))
                actions = self._get_player_actions(player)

                return PlayerNode(label, [self._build_tree(action.label, action.substate) for action in actions],
                                  state.players.index(player), self._get_info_set_data(player))

    @abstractmethod
    def _get_chance_actions(self, nature: N) -> Sequence[ChanceAction[G]]:
        pass

    @abstractmethod
    def _get_player_actions(self, player: P) -> Sequence[Action[G]]:
        pass

    @abstractmethod
    def _get_payoff(self, player: P) -> float:
        pass

    @abstractmethod
    def _get_actor(self, state: G) -> Union[N, P]:
        pass

    @abstractmethod
    def _get_info_set_data(self, player: P) -> Hashable:
        pass

    @abstractmethod
    def _create_game(self) -> G:
        pass


class SeqTreeFactory(TreeFactory[SG, N, P], ABC):
    def _get_actor(self, state: SG) -> Union[N, P]:
        return cast(Union[N, P], state.actor)
