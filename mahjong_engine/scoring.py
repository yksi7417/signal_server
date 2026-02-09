"""Old Hong Kong Mahjong faan scoring.

Implements the faan table from the Wikipedia article on Hong Kong Mahjong scoring.
Minimum 3 faan to win.  Limit (maximum) = 10 faan.
"""

from .constants import (
    SUIT_DRAGONS, SUIT_WINDS, SUITS_NUMERIC,
    DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE,
    DRAGONS_ALL, WINDS_ALL,
)
from .melds import MeldType


class FaanCalculator:
    LIMIT = 10
    MIN_FAAN = 3

    # ---- public API -------------------------------------------------------

    def calculate(self, melds, pair, player_wind, game_wind,
                  is_self_drawn, hand_tiles, revealed_sets):
        """Return ``(total_faan, breakdown)`` where *breakdown* is a list of
        ``{"name": str, "faan": int}`` dicts.

        *melds* and *pair* come from hand decomposition (concealed part).
        *revealed_sets* are the player's already-revealed Meld objects.
        *hand_tiles* is the full list of concealed tiles (used for special hands).
        """
        # Combine concealed melds with revealed sets for pattern checks
        all_melds = list(melds) + list(revealed_sets)

        # 1. Check limit hands first
        limit = self._check_limit_hands(all_melds, pair, hand_tiles, revealed_sets)
        if limit:
            return (self.LIMIT, [limit])

        # 2. Sum regular patterns
        breakdown = []
        for name, faan in self._check_regular(all_melds, pair, player_wind,
                                               game_wind, is_self_drawn,
                                               revealed_sets):
            breakdown.append({"name": name, "faan": faan})

        total = sum(item["faan"] for item in breakdown)
        if total > self.LIMIT:
            total = self.LIMIT
        return (total, breakdown)

    # ---- limit hands (each returns 10) -----------------------------------

    def _check_limit_hands(self, all_melds, pair, hand_tiles, revealed_sets):
        checks = [
            ("Thirteen Orphans", self._check_thirteen_orphans(hand_tiles, revealed_sets)),
            ("Nine Gates", self._check_nine_gates(hand_tiles, revealed_sets)),
            ("All Honors", self._check_all_honors(all_melds, pair)),
            ("Great Dragons", self._check_great_dragons(all_melds)),
            ("Great Winds", self._check_great_winds(all_melds)),
            ("Small Dragons", self._check_small_dragons(all_melds, pair)),
            ("Small Winds", self._check_small_winds(all_melds, pair)),
            ("All Kongs", self._check_all_kongs(all_melds)),
        ]
        for name, hit in checks:
            if hit:
                return {"name": name, "faan": self.LIMIT}
        return None

    def _check_thirteen_orphans(self, hand_tiles, revealed_sets):
        """All 13 unique terminals+honors + 1 duplicate, all concealed."""
        if revealed_sets:
            return False
        if len(hand_tiles) != 14:
            return False
        from .tile import Tile
        required = set()
        for suit in SUITS_NUMERIC:
            required.add((suit, '1'))
            required.add((suit, '9'))
        for w in WINDS_ALL:
            required.add((SUIT_WINDS, w))
        for d in DRAGONS_ALL:
            required.add((SUIT_DRAGONS, d))
        hand_set = {(t.suit, t.value) for t in hand_tiles}
        return required == hand_set and len(hand_tiles) == 14

    def _check_nine_gates(self, hand_tiles, revealed_sets):
        """1112345678999 of one suit + any tile of that suit, all concealed."""
        if revealed_sets:
            return False
        if len(hand_tiles) != 14:
            return False
        suits = {t.suit for t in hand_tiles}
        if len(suits) != 1:
            return False
        suit = suits.pop()
        if suit not in SUITS_NUMERIC:
            return False
        from collections import Counter
        counts = Counter(t.value for t in hand_tiles)
        base = {'1': 3, '2': 1, '3': 1, '4': 1, '5': 1,
                '6': 1, '7': 1, '8': 1, '9': 3}
        # Must have at least the base counts and exactly 14 tiles total
        for val, need in base.items():
            if counts.get(val, 0) < need:
                return False
        return True

    def _check_all_honors(self, all_melds, pair):
        """Every tile is a wind or dragon."""
        if pair is None:
            return False
        all_tiles = []
        for m in all_melds:
            all_tiles.extend(m.raw_tiles)
        all_tiles.extend(pair.raw_tiles)
        return all(t.is_honor() for t in all_tiles)

    def _check_great_dragons(self, all_melds):
        """3 dragon pungs/kongs."""
        dragon_count = sum(
            1 for m in all_melds
            if m.meld_type in (MeldType.PUNG, MeldType.KONG)
            and m.key_tile.is_dragon()
        )
        return dragon_count >= 3

    def _check_great_winds(self, all_melds):
        """4 wind pungs/kongs."""
        wind_count = sum(
            1 for m in all_melds
            if m.meld_type in (MeldType.PUNG, MeldType.KONG)
            and m.key_tile.is_wind()
        )
        return wind_count >= 4

    def _check_small_dragons(self, all_melds, pair):
        """2 dragon pungs/kongs + dragon pair."""
        if pair is None or not pair.key_tile.is_dragon():
            return False
        dragon_meld_count = sum(
            1 for m in all_melds
            if m.meld_type in (MeldType.PUNG, MeldType.KONG)
            and m.key_tile.is_dragon()
        )
        return dragon_meld_count >= 2

    def _check_small_winds(self, all_melds, pair):
        """3 wind pungs/kongs + wind pair."""
        if pair is None or not pair.key_tile.is_wind():
            return False
        wind_meld_count = sum(
            1 for m in all_melds
            if m.meld_type in (MeldType.PUNG, MeldType.KONG)
            and m.key_tile.is_wind()
        )
        return wind_meld_count >= 3

    def _check_all_kongs(self, all_melds):
        """4 kongs."""
        kong_count = sum(1 for m in all_melds if m.meld_type == MeldType.KONG)
        return kong_count >= 4

    # ---- regular patterns (additive) ------------------------------------

    def _check_regular(self, all_melds, pair, player_wind, game_wind,
                       is_self_drawn, revealed_sets):
        """Yield ``(name, faan)`` for every matching regular pattern."""
        # Non-pair melds only (exclude the pair from meld-type checks)
        non_pair = [m for m in all_melds if m.meld_type != MeldType.PAIR]

        # All Chows (4 chows, no pungs/kongs) — 1 faan
        if (len(non_pair) == 4
                and all(m.meld_type == MeldType.CHOW for m in non_pair)):
            yield ("All Chows", 1)

        # All Pungs (4 pungs/kongs, no chows) — 3 faan
        if (len(non_pair) == 4
                and all(m.meld_type in (MeldType.PUNG, MeldType.KONG) for m in non_pair)):
            yield ("All Pungs", 3)

        # Concealed Hand — 1 faan (no revealed sets)
        if not revealed_sets:
            yield ("Concealed Hand", 1)

        # Self-Drawn — 1 faan
        if is_self_drawn:
            yield ("Self-Drawn", 1)

        # Dragon Pung/Kong — 1 faan per dragon
        for m in all_melds:
            if (m.meld_type in (MeldType.PUNG, MeldType.KONG)
                    and m.key_tile.is_dragon()):
                dragon_name = m.key_tile.value
                yield (f"{dragon_name} Dragon", 1)

        # Seat Wind — 1 faan
        if player_wind:
            for m in all_melds:
                if (m.meld_type in (MeldType.PUNG, MeldType.KONG)
                        and m.key_tile.suit == SUIT_WINDS
                        and m.key_tile.value == player_wind):
                    yield ("Seat Wind", 1)
                    break

        # Prevailing (Round) Wind — 1 faan
        if game_wind:
            for m in all_melds:
                if (m.meld_type in (MeldType.PUNG, MeldType.KONG)
                        and m.key_tile.suit == SUIT_WINDS
                        and m.key_tile.value == game_wind):
                    yield ("Prevailing Wind", 1)
                    break

        # Flush checks — use all tiles (melds + pair)
        all_tiles = []
        for m in all_melds:
            all_tiles.extend(m.raw_tiles)
        if pair:
            all_tiles.extend(pair.raw_tiles)

        numeric_suits = {t.suit for t in all_tiles if t.is_numeric_suit()}
        has_honors = any(t.is_honor() for t in all_tiles)

        if len(numeric_suits) == 1 and not has_honors:
            # Full Flush — 6 faan
            yield ("Full Flush", 6)
        elif len(numeric_suits) == 1 and has_honors:
            # Half Flush — 3 faan
            yield ("Half Flush", 3)
