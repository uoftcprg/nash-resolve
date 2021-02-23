from abc import ABC, abstractmethod
from collections import Hashable, Sequence
from typing import Generic, TypeVar, Union, cast

from gameframe.game import BaseActor
from gameframe.game.bases import BaseGame
from gameframe.sequential.bases import BaseSeqGame

from nashresolve.games import Game, TreeGame
from nashresolve.trees import ChanceNode, Node, PlayerNode, TerminalNode

G = TypeVar('G', bound=BaseGame)
N = TypeVar('N', bound=BaseActor)
P = TypeVar('P', bound=BaseActor)
A = TypeVar('A', bound=BaseActor)

SG = TypeVar('SG', bound=BaseSeqGame)


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
        return TreeGame(self._create_node('Root', self._create_game()))

    def _create_node(self, label: str, state: G) -> Node:
        if state.terminal:
            return self._create_terminal_node(label, state)
        elif self._get_actor(state) is state.nature:
            return self._create_chance_node(label, state)
        else:
            return self._create_player_node(label, state)

    def _create_terminal_node(self, label: str, state: G) -> TerminalNode:
        return TerminalNode(label, (self._get_payoff(cast(P, player)) for player in state.players))

    def _create_chance_node(self, label: str, state: G) -> ChanceNode:
        chance_actions = self._get_chance_actions(cast(N, state.nature))

        return ChanceNode(label, (self._create_node(action.label, action.substate) for action in chance_actions),
                          (action.probability for action in chance_actions))

    def _create_player_node(self, label: str, state: G) -> PlayerNode:
        actions = self._get_player_actions(player := cast(P, self._get_actor(state)))

        return PlayerNode(label, (self._create_node(action.label, action.substate) for action in actions),
                          state.players.index(player), self._get_info_set_data(player))

    @abstractmethod
    def _create_game(self) -> G:
        pass

    @abstractmethod
    def _get_actor(self, state: G) -> Union[N, P]:
        pass

    @abstractmethod
    def _get_payoff(self, player: P) -> float:
        pass

    @abstractmethod
    def _get_chance_actions(self, nature: N) -> Sequence[ChanceAction[G]]:
        pass

    @abstractmethod
    def _get_player_actions(self, player: P) -> Sequence[Action[G]]:
        pass

    @abstractmethod
    def _get_info_set_data(self, player: P) -> Hashable:
        pass


class SeqTreeFactory(TreeFactory[SG, N, P], ABC):
    def _get_actor(self, state: SG) -> Union[N, P]:
        return cast(Union[N, P], state.actor)
