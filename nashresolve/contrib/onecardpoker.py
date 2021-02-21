from collections import Sequence
from typing import Iterable

from gameframe.poker import PokerGame
from gameframe.poker._stages import HoleCardDealingStage, NLBettingStage, ShowdownStage
from pokertools import Card, Deck, Evaluator, Hand, Rank, Suit

from nashresolve.contrib.poker import PokerTreeFactory


class OCPDeck(Deck):
    def __init__(self) -> None:
        super().__init__(Card(rank, Suit.SPADE) for rank in Rank)


class OCPHand(Hand):
    def __init__(self, rank: Rank):
        super().__init__(-rank.index)

        self.__rank = rank

    def __repr__(self) -> str:
        return self.__rank.value


class OCPEvaluator(Evaluator):
    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        return OCPHand(next(iter(hole_cards)).rank)


class OCPGame(PokerGame):
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds))

        super().__init__([HoleCardDealingStage(self, 1, False), NLBettingStage(self, max_delta), ShowdownStage(self)],
                         OCPDeck(), OCPEvaluator(), ante, blinds, starting_stacks)


class OCPTreeFactory(PokerTreeFactory):
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        self.ante = ante
        self.blinds = blinds
        self.starting_stacks = starting_stacks

    def _create_game(self) -> OCPGame:
        return OCPGame(self.ante, self.blinds, self.starting_stacks)
