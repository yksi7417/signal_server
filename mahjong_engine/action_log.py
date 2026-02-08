"""Persistent action logging with compact parquet storage.

Records every game action with encoded tile/action IDs for minimal storage.
Provides encode/decode, parquet save/load, and a CLI reader.
"""

import json
import os
import sys
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq

from .constants import (
    SUIT_CHARACTERS, SUIT_BAMBOO, SUIT_DOTS, SUIT_WINDS, SUIT_DRAGONS,
    TILE_VALUES_NUMERIC, WINDS_ALL, DRAGONS_ALL,
)

# --- Action type encoding ---
ACTION_CODES = {
    "game_init": 0,
    "draw": 1,
    "discard": 2,
    "pung": 3,
    "chow": 4,
    "kong": 5,
    "hidden_kong": 6,
    "win": 7,
    "end_hand": 8,
}
ACTION_NAMES = {v: k for k, v in ACTION_CODES.items()}

# --- Tile ID encoding ---
# 0 = no tile
# 1-9 = Characters 1-9
# 10-18 = Bamboo 1-9
# 19-27 = Dots 1-9
# 28-31 = Winds (East, South, West, North)
# 32-34 = Dragons (Red, Green, White)
_TILE_TO_ID = {None: 0}
_ID_TO_TILE = {0: None}

_id = 1
for _suit, _values in [
    (SUIT_CHARACTERS, TILE_VALUES_NUMERIC),
    (SUIT_BAMBOO, TILE_VALUES_NUMERIC),
    (SUIT_DOTS, TILE_VALUES_NUMERIC),
    (SUIT_WINDS, WINDS_ALL),
    (SUIT_DRAGONS, DRAGONS_ALL),
]:
    for _val in _values:
        _TILE_TO_ID[(_suit, _val)] = _id
        _ID_TO_TILE[_id] = (_suit, _val)
        _id += 1


def encode_tile(tile):
    """Encode a Tile object (or None) to a uint8 ID."""
    if tile is None:
        return 0
    return _TILE_TO_ID.get((tile.suit, tile.value), 0)


def decode_tile_id(tid):
    """Decode a uint8 tile ID back to (suit, value) tuple or None."""
    return _ID_TO_TILE.get(tid)


def tile_id_to_unicode(tid):
    """Convert a tile ID to its unicode representation."""
    sv = decode_tile_id(tid)
    if sv is None:
        return None
    from .tile import TileFactory
    tile = TileFactory.get_tile(sv[0], sv[1])
    return tile.unicode


# --- Parquet schema ---
SCHEMA = pa.schema([
    ("seq", pa.uint16()),
    ("ts", pa.int64()),
    ("pid", pa.int8()),
    ("act", pa.uint8()),
    ("tid", pa.uint8()),
    ("extra", pa.string()),
])


class ActionLog:
    """Accumulates game actions and persists them to parquet.

    Unlike GameHistory, this does NOT clear on end_hand — it accumulates
    across the entire session for debugging and replay purposes.

    Thread-safe via a lock.
    """

    def __init__(self):
        self._entries = []  # type: List[Dict]
        self._seq = 0
        self._lock = threading.Lock()

    def record(self, action_type, player_id=None, tile=None, extra=None):
        """Record a game action.

        Args:
            action_type: String action name (e.g. 'draw', 'discard').
            player_id: Player ID (0-3) or None for system events.
            tile: Tile object or None.
            extra: Optional string/dict for additional data.
        """
        act_code = ACTION_CODES.get(action_type, 255)
        tid_code = encode_tile(tile)
        extra_str = None
        if extra is not None:
            extra_str = json.dumps(extra) if not isinstance(extra, str) else extra

        entry = {
            "seq": self._seq,
            "ts": int(datetime.now(timezone.utc).timestamp() * 1_000_000),
            "pid": player_id if player_id is not None else -1,
            "act": act_code,
            "tid": tid_code,
            "extra": extra_str,
        }
        with self._lock:
            self._entries.append(entry)
            self._seq += 1

    @property
    def count(self):
        """Number of recorded actions."""
        with self._lock:
            return len(self._entries)

    def get_entries(self):
        """Return a copy of raw entries."""
        with self._lock:
            return list(self._entries)

    def decode(self, player_filter=None):
        """Decode entries into human-readable dicts.

        Args:
            player_filter: Optional player_id to filter by.

        Returns:
            List of dicts with human-readable action/tile names.
        """
        with self._lock:
            entries = list(self._entries)

        result = []
        for e in entries:
            pid = e["pid"]
            if pid == -1:
                pid = None
            if player_filter is not None and pid != player_filter:
                continue

            tile_sv = decode_tile_id(e["tid"])
            tile_str = None
            if tile_sv is not None:
                try:
                    tile_str = tile_id_to_unicode(e["tid"])
                except Exception:
                    tile_str = f"{tile_sv[0]}:{tile_sv[1]}"

            ts_dt = datetime.fromtimestamp(
                e["ts"] / 1_000_000, tz=timezone.utc
            )

            decoded = {
                "seq": e["seq"],
                "timestamp": ts_dt.isoformat(),
                "player_id": pid,
                "action": ACTION_NAMES.get(e["act"], f"unknown({e['act']})"),
                "tile": tile_str,
            }
            if e["extra"] is not None:
                decoded["extra"] = e["extra"]
            result.append(decoded)
        return result

    def to_json(self, player_filter=None):
        """Return decoded actions as a JSON string."""
        return json.dumps(self.decode(player_filter=player_filter),
                          ensure_ascii=False)

    def save(self, filepath):
        """Write action log to a parquet file.

        Args:
            filepath: Path to write the .parquet file.
        """
        with self._lock:
            entries = list(self._entries)

        if not entries:
            # Write empty table with correct schema
            table = pa.table({
                "seq": pa.array([], type=pa.uint16()),
                "ts": pa.array([], type=pa.int64()),
                "pid": pa.array([], type=pa.int8()),
                "act": pa.array([], type=pa.uint8()),
                "tid": pa.array([], type=pa.uint8()),
                "extra": pa.array([], type=pa.string()),
            }, schema=SCHEMA)
        else:
            table = pa.table({
                "seq": pa.array([e["seq"] for e in entries], type=pa.uint16()),
                "ts": pa.array([e["ts"] for e in entries], type=pa.int64()),
                "pid": pa.array([e["pid"] for e in entries], type=pa.int8()),
                "act": pa.array([e["act"] for e in entries], type=pa.uint8()),
                "tid": pa.array([e["tid"] for e in entries], type=pa.uint8()),
                "extra": pa.array([e["extra"] for e in entries], type=pa.string()),
            }, schema=SCHEMA)

        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        pq.write_table(table, filepath, compression="snappy")

    @classmethod
    def load(cls, filepath):
        """Load an ActionLog from a parquet file.

        Args:
            filepath: Path to the .parquet file.

        Returns:
            ActionLog instance with loaded entries.
        """
        table = pq.read_table(filepath)
        log = cls()

        seqs = table.column("seq").to_pylist()
        tss = table.column("ts").to_pylist()
        pids = table.column("pid").to_pylist()
        acts = table.column("act").to_pylist()
        tids = table.column("tid").to_pylist()
        extras = table.column("extra").to_pylist()

        for i in range(len(seqs)):
            entry = {
                "seq": seqs[i],
                "ts": tss[i],
                "pid": pids[i],
                "act": acts[i],
                "tid": tids[i],
                "extra": extras[i],
            }
            log._entries.append(entry)

        if seqs:
            log._seq = max(seqs) + 1
        return log

    def clear(self):
        """Remove all entries."""
        with self._lock:
            self._entries.clear()
            self._seq = 0


def _cli_main():
    """CLI entry point for reading parquet action logs."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Read and display mahjong action log parquet files."
    )
    parser.add_argument("file", help="Path to .parquet action log file")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of table")
    parser.add_argument("--player", type=int, default=None,
                        help="Filter by player ID")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    log = ActionLog.load(args.file)
    decoded = log.decode(player_filter=args.player)

    if args.json:
        print(json.dumps(decoded, indent=2, ensure_ascii=False))
    else:
        if not decoded:
            print("(empty action log)")
            return

        print(f"{'SEQ':>4}  {'TIME':>12}  {'PID':>3}  {'ACTION':<12}  TILE")
        print("-" * 55)
        for d in decoded:
            ts_short = d["timestamp"].split("T")[1][:12]
            pid_str = str(d["player_id"]) if d["player_id"] is not None else " - "
            tile_str = d["tile"] or ""
            extra_str = ""
            if "extra" in d:
                extra_val = d["extra"]
                if len(extra_val) > 40:
                    extra_str = f"  [{extra_val[:40]}...]"
                else:
                    extra_str = f"  [{extra_val}]"
            print(f"{d['seq']:>4}  {ts_short:>12}  {pid_str:>3}  "
                  f"{d['action']:<12}  {tile_str}{extra_str}")
        print(f"\nTotal: {len(decoded)} actions")


if __name__ == "__main__":
    _cli_main()
