from abc import ABC
from collections import Hashable, Iterable, Sequence
from copy import deepcopy
from itertools import combinations

from gameframe.poker import KuhnGame, PokerGame, PokerNature, PokerPlayer, parse_poker
from pokertools import HoleCard

from nashresolve.factories import Action, ChanceAction, SequentialTreeFactory


class PokerTreeFactory(SequentialTreeFactory[PokerGame, PokerNature, PokerPlayer], ABC):
    def _get_payoff(self, state: PokerGame, player: PokerPlayer) -> float:
        return player.stack - player.starting_stack

    def _get_chance_actions(self, state: PokerGame, nature: PokerNature) -> Sequence[ChanceAction[PokerGame]]:
        actions: list[ChanceAction[PokerGame]] = []

        if nature.can_deal_board():
            card_sets = tuple(combinations(sorted(state.deck), nature.board_deal_count))

            for cards in card_sets:
                substate = deepcopy(state)
                substate.nature.deal_board(cards)

                actions.append(ChanceAction('Deal Board ' + ' '.join(map(str, cards)), substate, 1 / len(card_sets)))
        else:
            player = next(player for player in state.players if nature.can_deal_hole(player))
            card_sets = tuple(combinations(sorted(state.deck), nature.hole_deal_count))

            for cards in card_sets:
                substate = deepcopy(state)
                substate.nature.deal_hole(substate.players[state.players.index(player)], cards)

                actions.append(ChanceAction(f'Deal Player {state.players.index(player)} ' + ' '.join(map(str, cards)),
                                            substate, 1 / len(card_sets)))

        return actions

    def _get_player_actions(self, state: PokerGame, player: PokerPlayer) -> Sequence[Action[PokerGame]]:
        actions: list[Action[PokerGame]] = []

        if player.can_fold():
            substate = deepcopy(state)
            parse_poker(substate, ['f'])

            actions.append(Action('Fold', substate))

        if player.can_check_call():
            substate = deepcopy(state)
            parse_poker(substate, ['cc'])

            actions.append(Action('Check/Call', substate))

        if player.can_bet_raise():
            for amount in self._get_bet_raise_amounts(player):
                substate = deepcopy(state)
                parse_poker(substate, [f'br {amount}'])

                actions.append(Action(f'Bet/Raise {amount}', substate))

        if player.can_showdown():
            for force in [False, True]:
                substate = deepcopy(state)
                parse_poker(substate, [f's {int(force)}'])

                actions.append(Action('Force showdown' if force else 'Showdown', substate))

        return actions

    def _get_info_set_data(self, state: PokerGame, player: PokerPlayer) -> Hashable:
        return str((
            (state.players.index(state.actor) if isinstance(state.actor, PokerPlayer) else None),
            state.pot, tuple(state.board_cards), tuple(
                self._player_data(other, other is player) for other in state.players
            ),
            state.nature.can_deal_hole(), state.nature.can_deal_board(),
        ))

    def _player_data(self, player: PokerPlayer, private: bool) -> Hashable:
        return (
            player.bet, player.stack, None if player.mucked else tuple(
                HoleCard(hole_card, hole_card.status or private) for hole_card in player.hole_cards
            ),
            player.can_fold(), player.can_check_call(), player.can_bet_raise(), player.can_showdown(),
        )

    def _get_bet_raise_amounts(self, player: PokerPlayer) -> Iterable[int]:
        return range(player.min_bet_raise_amount, player.max_bet_raise_amount + 1)


class KuhnTreeFactory(PokerTreeFactory):
    def _create_game(self) -> KuhnGame:
        return KuhnGame()
