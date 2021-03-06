from abc import ABC, abstractmethod
from collections import Hashable, Sequence
from typing import Any, Generic, TypeVar, Union, cast

from gameframe.game import Game as GFGame
from gameframe.sequential import SequentialGame

from nashresolve.games import Game, TreeGame
from nashresolve.trees import ChanceNode, Node, PlayerNode, TerminalNode

_G = TypeVar('_G', bound=GFGame[Any, Any])
_N = TypeVar('_N')
_P = TypeVar('_P')
_A = TypeVar('_A')

_SG = TypeVar('_SG', bound=SequentialGame[Any, Any])


class Action(Generic[_G]):
    def __init__(self, label: str, substate: _G):
        self.__label = label
        self.__substate = substate

    @property
    def label(self) -> str:
        return self.__label

    @property
    def substate(self) -> _G:
        return self.__substate


class ChanceAction(Action[_G]):
    def __init__(self, label: str, substate: _G, probability: float):
        super().__init__(label, substate)

        self.__probability = probability

    @property
    def probability(self) -> float:
        return self.__probability


class GameFactory(Generic[_G, _N, _P], ABC):
    @abstractmethod
    def build(self) -> Game:
        pass


class TreeFactory(GameFactory[_G, _N, _P], ABC):
    def build(self) -> TreeGame:
        return TreeGame(self._create_node('ROOT', self._create_game()))

    def _create_node(self, label: str, state: _G) -> Node:
        if state.terminal:
            return self._create_terminal_node(label, state)
        elif self._get_actor(state) is state.nature:
            return self._create_chance_node(label, state)
        else:
            return self._create_player_node(label, state)

    def _create_terminal_node(self, label: str, state: _G) -> TerminalNode:
        return TerminalNode(label, (self._get_payoff(state, cast(_P, player)) for player in state.players))

    def _create_chance_node(self, label: str, state: _G) -> ChanceNode:
        chance_actions = self._get_chance_actions(state, cast(_N, state.nature))

        return ChanceNode(label, (self._create_node(action.label, action.substate) for action in chance_actions),
                          (action.probability for action in chance_actions))

    def _create_player_node(self, label: str, state: _G) -> PlayerNode:
        player = cast(_P, self._get_actor(state))
        actions = self._get_player_actions(state, player)

        return PlayerNode(label, (self._create_node(action.label, action.substate) for action in actions),
                          state.players.index(player), self._get_info_set_data(state, player))

    @abstractmethod
    def _create_game(self) -> _G:
        pass

    @abstractmethod
    def _get_actor(self, state: _G) -> Union[_N, _P]:
        pass

    @abstractmethod
    def _get_payoff(self, state: _G, player: _P) -> float:
        pass

    @abstractmethod
    def _get_chance_actions(self, state: _G, nature: _N) -> Sequence[ChanceAction[_G]]:
        pass

    @abstractmethod
    def _get_player_actions(self, state: _G, player: _P) -> Sequence[Action[_G]]:
        pass

    @abstractmethod
    def _get_info_set_data(self, state: _G, player: _P) -> Hashable:
        pass


class SequentialTreeFactory(TreeFactory[_SG, _N, _P], ABC):
    def _get_actor(self, state: _SG) -> Union[_N, _P]:
        return cast(Union[_N, _P], state.actor)
