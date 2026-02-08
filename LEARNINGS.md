# Development Learnings - Signal Server Mahjong Project

## 2026-02-07: Bug Reporting System & Action Log Enhancements

### Context
Enhanced the bug reporting system to provide comprehensive debugging information by integrating GitHub issue creation with detailed action logs and game state snapshots.

### What We Learned

#### 1. Git Merge Conflict Resolution
**Problem**: Multiple files had unresolved merge conflicts committed to the repository.
- Files affected: `app.py`, `bug_report.py`, `action_log.py`, `game_state.py`, `test_bug_report.py`
- Conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`) prevented code execution

**Solution**:
- Used `grep -rn "<<<<<<< HEAD"` to find all conflicts
- Manually resolved each conflict by choosing the appropriate version (HEAD for GitHub integration)
- Automated resolution for systematic conflicts using regex replacement

**Key Takeaway**: Always check for merge conflicts before committing. Use `git status` and search for conflict markers.

#### 2. GitHub API Integration with PyGithub
**Implementation**: Automatic GitHub issue creation for bug reports

**Code Pattern**:
```python
from github import Github

gh = Github(github_token)
repo = gh.get_repo("owner/repo")

issue = repo.create_issue(
    title="Bug Report: ...",
    body=markdown_content,
    labels=["bug", "auto-reported"]
)
```

**Lessons**:
- Use try/except for graceful fallback if GitHub API fails
- Check `GITHUB_AVAILABLE` flag before using PyGithub
- Store token in `.env` file, never commit
- Return both `issue_url` and `issue_number` in API response

#### 3. Attaching Files to GitHub Issues via Gists
**Problem**: GitHub Issues API doesn't support direct file attachments

**Solution**: Upload binary files as GitHub Gists
```python
# Encode binary parquet file as base64
parquet_b64 = base64.b64encode(parquet_content).decode('ascii')

# Create gist with base64-encoded file + README
gist_files = {
    "actions.parquet.b64": {"content": parquet_b64},
    "README.md": {"content": "Instructions..."}
}

user = gh.get_user()
gist = user.create_gist(
    public=False,
    files=gist_files,
    description=f"Action log for bug {bug_id}"
)
```

**Lessons**:
- Binary files must be base64-encoded for gist storage
- Include a README with decoding instructions
- Use private gists for sensitive data
- Append gist link to issue markdown for easy access
- Typical 8KB parquet → 11KB base64 (acceptable overhead)

#### 4. Action Log Enhancement with State Snapshots
**Problem**: Action logs only recorded individual actions (draw, discard), making debugging difficult without full game context.

**Solution**: Added periodic state snapshots at key decision points

**Implementation**:
1. Added `"snapshot"` action type (code 9) to ACTION_CODES
2. Created `record_state_snapshot()` method in ActionLog
3. Automatically record snapshots after:
   - Every discard (end of turn)
   - Every claim (pung, chow, kong)
   - Every win
   - Game end

**Snapshot Contents**:
```json
{
  "turn_number": 0,
  "wall_size": 83,
  "current_player_index": 0,
  "players": [
    {
      "player_id": 0,
      "hand": [...],
      "discards": [...],
      "revealed_sets": [...]
    }
  ]
}
```

**Benefits**:
- Complete game state at each decision point
- Easy to replay and understand bugs
- Minimal storage overhead (~4KB for typical game)

#### 5. ActionLog.load() Pattern - Class Method Gotcha
**Problem**: `ActionLog.load()` returned empty logs when used incorrectly

**Root Cause**: `load()` is a **classmethod** that returns a NEW instance

**Wrong Usage**:
```python
log = ActionLog()
log.load("file.parquet")  # log remains empty!
```

**Correct Usage**:
```python
log = ActionLog.load("file.parquet")  # Returns loaded instance
```

**Lesson**: Always check if methods are classmethods or instance methods. Classmethods return new instances.

#### 6. Parquet File Storage and Retrieval
**Schema**:
```python
{
    "seq": uint16,      # Sequence number
    "ts": int64,        # Timestamp (microseconds)
    "pid": int8,        # Player ID (-1 for system)
    "act": uint8,       # Action code
    "tid": uint8,       # Tile ID (encoded)
    "extra": string     # JSON extra data
}
```

**Best Practices**:
- Use PyArrow for efficient columnar storage
- Compress with Snappy (good balance of speed/size)
- Store extra data as JSON strings
- Define schema explicitly for empty tables
- Thread-safe with locks when recording

#### 7. Unicode Handling in Windows Console
**Problem**: Mahjong tile emojis (🀇🀈🀉) caused `UnicodeEncodeError` in Windows console

**Workaround**:
- Use JSON output mode when possible
- Catch `UnicodeEncodeError` and provide fallback messages
- Open files with `encoding='utf-8'` explicitly

**Not a bug**: This is a Windows console limitation, not a code issue.

### Architecture Patterns

#### Separation of Concerns
- **`mahjong_engine/`**: Transport-agnostic game logic
- **`app.py`**: Web/HTTP layer
- **`action_log.py`**: Persistence and replay
- **`bug_report.py`**: Debugging and GitHub integration

#### Testing Strategy
- Unit tests for engine logic: `pytest tests/engine/`
- 215+ unit tests ensuring correctness
- TDD approach: Write tests → Implement → Verify

### Development Workflow Improvements

#### Bug Report Workflow
1. User encounters issue → clicks "Report Bug"
2. Frontend calls `POST /api/report_bug` with description
3. Backend:
   - Creates bug report with action log
   - Uploads parquet file to GitHub Gist
   - Creates GitHub issue with markdown + gist link
   - Returns issue URL to user
4. Developer:
   - Opens GitHub issue
   - Downloads gist
   - Decodes parquet: `base64 -d actions.parquet.b64 > actions.parquet`
   - Analyzes: `python -m mahjong_engine.action_log actions.parquet`

### Environment Setup
- Python 3.8.3 (not 3.9+)
- Use `from typing import List` not `list[T]`
- PyGithub 2.8.1 for GitHub API
- PyArrow for parquet files

### Git Best Practices
- Check for merge conflicts before committing
- Use `git status` to see modified files
- Never commit `.env` files
- Use descriptive commit messages
- Test code before pushing

### Next Steps
- Implement session management API endpoints (Priority 2.3.2)
- Add game room management (Priority 3.1.x)
- Continue TDD approach for new features

## 2026-02-08: Integration Tests & Docker Deployment Fixes

### Summary
Fixed all 33 integration tests and resolved Docker dependency conflicts for fly.io deployment.

### Key Learnings

**1. Integration Test Fixtures**: Created conftest.py for shared session-scoped server fixtures

**2. API Endpoint Patterns**: aiohttp uses `/api/endpoint_name` (underscore, not hyphen)

**3. Docker Dependencies**: Removed unused legacy deps (gevent, bottle), separated dev deps (playwright) into requirements-dev.txt

**4. UTF-8 Encoding**: Always use `encoding='utf-8'` when opening files with Unicode characters on Windows

**5. Test Results**: 249 total passing tests (216 unit + 33 integration)

## 2026-02-08 (PM): Bug #30 - Parquet File Gist Attachment Fix

### Issue
GitHub issues created successfully but parquet files not attached as gists.

### Root Cause
Silent failures: missing file checks, generic exceptions, no logging, empty action logs not detected.

### Solution
- Added file existence and size logging
- Specific exception handling (FileNotFoundError, PermissionError)
- Empty action log detection
- Cross-platform base64 decode instructions (PowerShell + Linux)
- exc_info=True for stack traces

### Cross-Platform Tools
Created `autonomous_loop.py` - Python script works on Windows PowerShell AND Linux:
```bash
python autonomous_loop.py --dry-run    # Test mode
python autonomous_loop.py --max-bugs 5 # Fix bugs
```

Created `POWERSHELL_SETUP.md` - Complete Windows development guide

### Key Learnings
1. Check file existence before operations
2. Use specific exceptions, not generic Exception
3. Add detailed logging with file sizes
4. Python scripts > Shell scripts for cross-platform
5. Provide platform-specific instructions

---

**Key Principle**: "Capture everything for debugging" - The more context we save during gameplay, the easier it is to reproduce and fix bugs.
