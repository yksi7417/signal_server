"""Bug report generation with action log capture and GitHub issue formatting."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from .action_log import ActionLog


class BugReport:
    """Captures game state + action log for bug reporting.

    Attributes:
        bug_id: Unique identifier for the report.
        description: User's description of what went wrong.
        action_log: ActionLog instance with the game's action history.
        game_state_snapshot: Dict capturing the current game state.
        created_at: ISO timestamp of when the report was created.
    """

    def __init__(self, description, action_log, game_state_snapshot=None):
        """Create a bug report.

        Args:
            description: User description of the bug.
            action_log: ActionLog instance.
            game_state_snapshot: Dict from GameState.get_state_snapshot().
        """
        self.bug_id = str(uuid.uuid4())[:8]
        self.description = description
        self.action_log = action_log
        self.game_state_snapshot = game_state_snapshot or {}
        self.created_at = datetime.now(timezone.utc).isoformat()

    def save(self, base_dir="bug_reports"):
        """Save bug report to a directory.

        Creates: <base_dir>/bug_<id>/report.json + actions.parquet

        Args:
            base_dir: Parent directory for bug reports.

        Returns:
            str: Path to the created bug report directory.
        """
        report_dir = os.path.join(base_dir, f"bug_{self.bug_id}")
        os.makedirs(report_dir, exist_ok=True)

        # Save action log as parquet
        parquet_path = os.path.join(report_dir, "actions.parquet")
        self.action_log.save(parquet_path)

        # Save metadata as JSON
        metadata = {
            "bug_id": self.bug_id,
            "description": self.description,
            "created_at": self.created_at,
            "game_state": self.game_state_snapshot,
            "action_count": self.action_log.count,
        }
        json_path = os.path.join(report_dir, "report.json")
        with open(json_path, "w", encoding="utf-8") as f:
<<<<<<< HEAD
=======
            json.dumps(metadata, ensure_ascii=False, indent=2)
>>>>>>> 45e16b8178c4ff0a18775514e95795d458c77023
            f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

        return report_dir

<<<<<<< HEAD
    def to_github_markdown(self, max_actions=None):
=======
    def to_github_markdown(self, max_actions=50):
>>>>>>> 45e16b8178c4ff0a18775514e95795d458c77023
        """Generate markdown suitable for a GitHub issue body.

        Args:
            max_actions: Maximum number of recent actions to include.
<<<<<<< HEAD
                        None or 0 = show all actions (default).
=======
>>>>>>> 45e16b8178c4ff0a18775514e95795d458c77023

        Returns:
            str: Markdown-formatted bug report.
        """
        lines = []
        lines.append("## Bug Report")
        lines.append("")
        lines.append("### Description")
        lines.append(self.description)
        lines.append("")

        # Game state summary
        snap = self.game_state_snapshot
        if snap:
            lines.append("### Game State at Time of Report")
            lines.append("")
            lines.append(f"- **Turn**: {snap.get('turn_number', '?')}")
            lines.append(f"- **Current Player**: {snap.get('current_player_index', '?')}")
            lines.append(f"- **Wall Remaining**: {snap.get('wall_size', '?')}")
            lines.append(f"- **Winner Found**: {snap.get('winner_found', False)}")

            pending = snap.get("pending_claim")
            if pending:
                lines.append(f"- **Pending Claim**: Player {pending.get('player_id')} "
                             f"— {pending.get('claim_type')} on {pending.get('tile')}")

            lines.append("")

            players = snap.get("players", [])
            if players:
                lines.append("#### Player Hands")
                lines.append("")
                for p in players:
                    hand_str = " ".join(p.get("hand", []))
                    melds_str = ""
                    if p.get("revealed_sets"):
                        meld_parts = []
                        for m in p["revealed_sets"]:
                            meld_parts.append(
                                f"{m['type']}[{' '.join(m['tiles'])}]"
                            )
                        melds_str = f"  Melds: {', '.join(meld_parts)}"
                    lines.append(
                        f"- **P{p['player_id']}** ({p.get('wind', '?')}): "
                        f"`{hand_str}`{melds_str}"
                    )
                lines.append("")

<<<<<<< HEAD
        # Action log
=======
        # Recent actions
>>>>>>> 45e16b8178c4ff0a18775514e95795d458c77023
        decoded = self.action_log.decode()
        total = len(decoded)
        if total > 0:
            lines.append("### Action Log")
            lines.append("")
<<<<<<< HEAD

            # Show all actions by default, or limit if max_actions is specified
            if max_actions and max_actions > 0 and total > max_actions:
                lines.append(f"_Showing last {max_actions} of {total} actions_")
                decoded = decoded[-max_actions:]
            else:
                lines.append(f"_Showing all {total} actions_")

=======
            if total > max_actions:
                lines.append(f"_Showing last {max_actions} of {total} actions_")
                decoded = decoded[-max_actions:]
>>>>>>> 45e16b8178c4ff0a18775514e95795d458c77023
            lines.append("")
            lines.append("| # | Player | Action | Tile |")
            lines.append("|---|--------|--------|------|")
            for d in decoded:
                pid = d["player_id"] if d["player_id"] is not None else "sys"
                tile = d["tile"] or ""
                lines.append(f"| {d['seq']} | {pid} | {d['action']} | {tile} |")
            lines.append("")

        lines.append("---")
        lines.append(f"_Bug ID: `{self.bug_id}` | "
                     f"Reported: {self.created_at} | "
                     f"Total actions: {total}_")

        return "\n".join(lines)

    def to_dict(self):
        """Serialize report metadata to dict."""
        return {
            "bug_id": self.bug_id,
            "description": self.description,
            "created_at": self.created_at,
            "action_count": self.action_log.count,
            "game_state": self.game_state_snapshot,
        }
