from abc import ABC, abstractmethod
from collections import Sequence
from typing import Generic, TypeVar, Union, cast

from gameframe.game import BaseActor, BaseGame
from gameframe.sequential import BaseSeqGame

from nashresolve.games import Game, TreeGame
from nashresolve.trees import ChanceNode, InfoSet, Node, PlayerNode, TerminalNode

G = TypeVar('G', bound=BaseGame)
SG = TypeVar('SG', bound=BaseSeqGame)
N = TypeVar('N', bound=BaseActor)
P = TypeVar('P', bound=BaseActor)


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
    def __init__(self, player_count: int):
        self.__player_count = player_count

    @property
    def player_count(self) -> int:
        return self.__player_count

    @abstractmethod
    def build(self) -> Game:
        pass


class TreeFactory(GameFactory[G, N, P], ABC):
    def build(self) -> TreeGame:
        return TreeGame(self.player_count, self._build('Root', self._create_game()))

    def _build(self, label: str, state: G) -> Node:
        if state.terminal:
            return TerminalNode(label, [self._get_payoff(cast(P, player)) for player in state.players])
        else:
            actor = self._get_actor(state)

            if actor is state.nature:
                chance_actions = self._get_chance_actions(cast(N, state.nature))
                children = [self._build(action.label, action.substate) for action in chance_actions]
                probabilities = [action.probability for action in chance_actions]

                return ChanceNode(label, children, probabilities)
            else:
                player = cast(P, self._get_actor(state))
                actions = self._get_player_actions(player)
                children = [self._build(action.label, action.substate) for action in actions]

                return PlayerNode(label, children, self._get_info_set(player))

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
    def _get_actor(self, state: G) -> Union[N, P]:
        pass

    @abstractmethod
    def _get_info_set(self, player: P) -> InfoSet:
        pass

    @abstractmethod
    def _create_game(self) -> G:
        pass


class SeqTreeFactory(TreeFactory[SG, N, P], ABC):
    def _get_actor(self, state: SG) -> Union[N, P]:
        return cast(Union[N, P], state.actor)
