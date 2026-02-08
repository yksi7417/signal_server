"""Tests for ActionLog with parquet persistence and tile/action encoding."""

import json
import os
import tempfile

import pytest

from mahjong_engine.action_log import (
    ACTION_CODES,
    ACTION_NAMES,
    ActionLog,
    decode_tile_id,
    encode_tile,
    tile_id_to_unicode,
    _TILE_TO_ID,
)
from mahjong_engine.tile import TileFactory
from mahjong_engine.constants import (
    SUIT_CHARACTERS, SUIT_BAMBOO, SUIT_DOTS,
    SUIT_WINDS, SUIT_DRAGONS,
    WIND_EAST, WIND_SOUTH, WIND_WEST, WIND_NORTH,
    DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE,
)


class TestTileEncoding:
    """Tests for tile ID encoding/decoding."""

    def test_none_tile_encodes_to_zero(self):
        assert encode_tile(None) == 0

    def test_none_tile_decodes_from_zero(self):
        assert decode_tile_id(0) is None

    def test_all_characters_encode(self):
        for i in range(1, 10):
            tile = TileFactory.get_tile(SUIT_CHARACTERS, str(i))
            tid = encode_tile(tile)
            assert tid == i  # Characters 1-9 map to IDs 1-9

    def test_all_bamboo_encode(self):
        for i in range(1, 10):
            tile = TileFactory.get_tile(SUIT_BAMBOO, str(i))
            tid = encode_tile(tile)
            assert tid == 9 + i  # Bamboo 1-9 map to IDs 10-18

    def test_all_dots_encode(self):
        for i in range(1, 10):
            tile = TileFactory.get_tile(SUIT_DOTS, str(i))
            tid = encode_tile(tile)
            assert tid == 18 + i  # Dots 1-9 map to IDs 19-27

    def test_winds_encode(self):
        winds = [WIND_EAST, WIND_SOUTH, WIND_WEST, WIND_NORTH]
        for j, w in enumerate(winds):
            tile = TileFactory.get_tile(SUIT_WINDS, w)
            tid = encode_tile(tile)
            assert tid == 28 + j

    def test_dragons_encode(self):
        dragons = [DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE]
        for j, d in enumerate(dragons):
            tile = TileFactory.get_tile(SUIT_DRAGONS, d)
            tid = encode_tile(tile)
            assert tid == 32 + j

    def test_encode_decode_roundtrip_all_tiles(self):
        """Every tile encodes to a unique ID and decodes back correctly."""
        seen_ids = set()
        for key, tid in _TILE_TO_ID.items():
            if key is None:
                continue
            suit, value = key
            assert tid not in seen_ids, f"Duplicate ID {tid}"
            seen_ids.add(tid)
            decoded = decode_tile_id(tid)
            assert decoded == (suit, value)

    def test_total_tile_count(self):
        """There should be 34 unique tiles + 1 for None."""
        assert len(_TILE_TO_ID) == 35  # 9+9+9+4+3 = 34, plus None

    def test_tile_id_to_unicode(self):
        tile = TileFactory.get_tile(SUIT_CHARACTERS, "1")
        tid = encode_tile(tile)
        unicode_str = tile_id_to_unicode(tid)
        assert unicode_str == tile.unicode

    def test_tile_id_to_unicode_none(self):
        assert tile_id_to_unicode(0) is None


class TestActionCodes:
    """Tests for action type encoding."""

    def test_all_action_types_have_codes(self):
        expected = ["game_init", "draw", "discard", "pung", "chow",
                    "kong", "hidden_kong", "win", "end_hand"]
        for action in expected:
            assert action in ACTION_CODES

    def test_action_names_reverse_map(self):
        for name, code in ACTION_CODES.items():
            assert ACTION_NAMES[code] == name


class TestActionLog:
    """Tests for the ActionLog class."""

    def test_record_and_count(self):
        log = ActionLog()
        assert log.count == 0
        log.record("draw", player_id=0)
        assert log.count == 1

    def test_record_with_tile(self):
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_CHARACTERS, "1")
        log.record("discard", player_id=0, tile=tile)
        entries = log.get_entries()
        assert entries[0]["tid"] == encode_tile(tile)

    def test_record_with_extra(self):
        log = ActionLog()
        log.record("game_init", extra={"wall": ["a", "b"]})
        entries = log.get_entries()
        assert json.loads(entries[0]["extra"]) == {"wall": ["a", "b"]}

    def test_record_system_event(self):
        """System events have player_id=-1 in storage."""
        log = ActionLog()
        log.record("game_init")
        entries = log.get_entries()
        assert entries[0]["pid"] == -1

    def test_sequence_numbers_increment(self):
        log = ActionLog()
        log.record("draw", player_id=0)
        log.record("discard", player_id=0)
        log.record("pung", player_id=1)
        entries = log.get_entries()
        assert [e["seq"] for e in entries] == [0, 1, 2]

    def test_decode_returns_readable_actions(self):
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_BAMBOO, "5")
        log.record("draw", player_id=2, tile=tile)
        decoded = log.decode()
        assert len(decoded) == 1
        assert decoded[0]["action"] == "draw"
        assert decoded[0]["player_id"] == 2
        assert decoded[0]["tile"] == tile.unicode
        assert "timestamp" in decoded[0]

    def test_decode_system_event_has_none_player(self):
        log = ActionLog()
        log.record("game_init")
        decoded = log.decode()
        assert decoded[0]["player_id"] is None

    def test_decode_player_filter(self):
        log = ActionLog()
        log.record("draw", player_id=0)
        log.record("draw", player_id=1)
        log.record("discard", player_id=0)
        decoded = log.decode(player_filter=0)
        assert len(decoded) == 2
        assert all(d["player_id"] == 0 for d in decoded)

    def test_to_json(self):
        log = ActionLog()
        log.record("draw", player_id=0)
        result = json.loads(log.to_json())
        assert isinstance(result, list)
        assert len(result) == 1

    def test_clear(self):
        log = ActionLog()
        log.record("draw", player_id=0)
        log.record("discard", player_id=0)
        log.clear()
        assert log.count == 0
        assert log.get_entries() == []

    def test_save_and_load_roundtrip(self):
        """Save to parquet and load back preserves all data."""
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_DOTS, "7")
        log.record("game_init", extra={"wall": ["x"]})
        log.record("draw", player_id=0, tile=tile)
        log.record("discard", player_id=0, tile=tile)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.parquet")
            log.save(path)
            assert os.path.exists(path)

            loaded = ActionLog.load(path)
            assert loaded.count == 3

            orig_entries = log.get_entries()
            loaded_entries = loaded.get_entries()
            for orig, loaded_e in zip(orig_entries, loaded_entries):
                assert orig["seq"] == loaded_e["seq"]
                assert orig["pid"] == loaded_e["pid"]
                assert orig["act"] == loaded_e["act"]
                assert orig["tid"] == loaded_e["tid"]
                assert orig["extra"] == loaded_e["extra"]

    def test_save_empty_log(self):
        """Saving an empty log creates a valid parquet file."""
        log = ActionLog()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "empty.parquet")
            log.save(path)
            loaded = ActionLog.load(path)
            assert loaded.count == 0

    def test_load_decode_roundtrip(self):
        """Loaded log decodes to same readable output as original."""
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_WINDS, WIND_EAST)
        log.record("draw", player_id=1, tile=tile)
        log.record("win", player_id=1, tile=tile)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.parquet")
            log.save(path)
            loaded = ActionLog.load(path)

            orig_decoded = log.decode()
            loaded_decoded = loaded.decode()
            assert len(orig_decoded) == len(loaded_decoded)
            for o, l in zip(orig_decoded, loaded_decoded):
                assert o["action"] == l["action"]
                assert o["player_id"] == l["player_id"]
                assert o["tile"] == l["tile"]

    def test_parquet_file_is_compact(self):
        """Parquet file with 100 actions should be small."""
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_CHARACTERS, "5")
        for i in range(100):
            log.record("draw", player_id=i % 4, tile=tile)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "compact.parquet")
            log.save(path)
            size = os.path.getsize(path)
            # Should be well under 10KB for 100 simple rows
            assert size < 10000
