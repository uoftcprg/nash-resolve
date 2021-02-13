from collections import MutableSequence, Sequence
from typing import Any, Collection

from gameframe.poker import PokerGame
from gameframe.poker.stages import HoleCardDealingStage, NLBettingStage, ShowdownStage
from pokertools import Card, CardLike, Evaluator, Hand, Rank, StandardDeck, Suit, parse_card

from nashresolve.contrib.poker import PokerFactory


class OCPDeck(StandardDeck):
    def _create_cards(self) -> MutableSequence[Card]:
        return list(filter(lambda card: card.suit is Suit.SPADE, super()._create_cards()))


class OCPHand(Hand):
    def __init__(self, rank: Rank):
        self.__rank = rank

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, OCPHand):
            ranks = list(Rank)
            return ranks.index(self.__rank) < ranks.index(other.__rank)
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, OCPHand):
            return self.__rank == other.__rank
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__rank)

    def __repr__(self) -> str:
        return self.__rank.value


class OCPEvaluator(Evaluator):
    def hand(self, hole_cards: Collection[CardLike], board_cards: Collection[CardLike]) -> Hand:
        return OCPHand(parse_card(next(iter(hole_cards))).rank)


class OCPGame(PokerGame):
    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds))

        super().__init__([HoleCardDealingStage(self, 1, False), NLBettingStage(self, max_delta), ShowdownStage(self)],
                         OCPDeck(), OCPEvaluator(), ante, blinds, starting_stacks)


class OCPFactory(PokerFactory):
    def _create_game(self) -> OCPGame:
        return OCPGame(self.ante, self.blinds, self.starting_stacks)
