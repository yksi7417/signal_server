# Development Learnings - Signal Server Mahjong Game

**Last Updated**: 2026-02-07

## Critical Lessons Learned

### 1. Windows Console Unicode Handling

**Problem**: Windows console (cp1252 encoding) cannot display Mahjong Unicode tiles (U+1F000 range)

**Symptom**:
```python
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f013'
```

**Solution Pattern**:
```python
try:
    print(f"Player {player_id} formed Chow: {chow_object}")
except UnicodeEncodeError:
    print(f"Player {player_id} formed Chow (tile display unavailable)")
```

**Where Applied**:
- `game_state.py:251` - CHOW detection message
- `game_state.py:395-405` - CHOW claim processing (2 locations)
- `game_state.py:318-329` - PUNG claim processing (2 locations)

**Rule**: Wrap ALL print statements containing tile objects in try/except blocks

---

### 2. Claim Implementation Pattern

When adding a new claim type, follow this 3-layer pattern:

#### Backend Layer (`mahjong_engine/hand_validator.py`)
```python
def can_form_TYPE_with_discard(hand, discarded_tile, discarder_pos, claimer_pos):
    # 1. Position validation
    # 2. Tile type validation
    # 3. Pattern matching logic
    return True/False
```

#### Game State Layer (`mahjong_engine/game_state.py`)
```python
def process_TYPE_claim(self, claiming_player_id, claimed_tile):
    # 1. Validate inputs
    # 2. Find tiles in hand
    # 3. Create meld object
    # 4. Update player hand
    # 5. Record action log
    # 6. Update game state
    return True/False
```

#### API Layer (`app.py`)
```python
async def player_claims_TYPE(request):
    # 1. Parse request JSON
    # 2. Call game_state.process_TYPE_claim()
    # 3. Return updated state
```

#### UI Layer (`static/game/js/claimsHandler.js`)
```javascript
async function handleClaimTYPEYes() {
    const response = await fetch('/api/player_claims_TYPE', {
        method: 'POST',
        body: JSON.stringify({ confirm_claim: true })
    });
    // Handle success/failure
}
```

**Complete Example**: CHOW implementation (PR #XX)
- Files touched: 4 files (hand_validator.py, game_state.py, app.py, claimsHandler.js)
- Tests added: 13 + 6 = 19 unit tests
- Total changes: ~300 lines of code

---

### 3. Claim Priority Enforcement

**Rule**: WIN > KONG > PUNG > CHOW

**Implementation Location**: `game_state.py:discard_tile_for_current_player()`

**Code Pattern**:
```python
# Check in priority order
if can_win:
    claim_type = "WIN"
elif can_kong:
    claim_type = "KONG"
elif can_pung:
    claim_type = "PUNG"
elif can_chow:
    claim_type = "CHOW"
```

**Testing**: Each claim type should have tests verifying it's blocked by higher-priority claims

---

### 4. CHOW Position Rule

**Critical Rule**: Only the **left neighbor** can claim CHOW

**Math**: `(discarder_position + 1) % 4 == claimer_position`

**Example**:
- Player 3 discards → Player 0 (human) can claim CHOW ✅
- Player 1 discards → Player 0 cannot claim CHOW ❌
- Player 2 discards → Player 0 cannot claim CHOW ❌

**Where Enforced**: `hand_validator.py:can_form_chow_with_discard()`

---

### 5. Tile Value Handling

**Critical**: Tile values are **strings**, not integers

```python
# ❌ WRONG
if tile.value == 5:

# ✅ CORRECT
if int(tile.value) == 5:
```

**Where This Matters**: Sequence validation for CHOWs (need consecutive numeric values)

---

### 6. UI Countdown Timer Pattern

**Implementation** (`claimsHandler.js`):
```javascript
// Store countdown state
store.claimCountdownSeconds = Math.floor(store.CLAIM_TIMEOUT_MS / 1000);

// Update display every second
store.claimCountdownId = setInterval(() => {
    store.claimCountdownSeconds--;
    if (store.claimCountdownSeconds > 0) {
        elements.playerConsoleEl.textContent =
            `Message here (Auto-decline in ${store.claimCountdownSeconds}s)`;
    }
}, 1000);

// Clear interval when done
clearInterval(store.claimCountdownId);
```

**Key Points**:
- Use `setInterval` for display updates
- Use `setTimeout` for actual timeout action
- Always clear both on cleanup
- Store IDs in shared state for cleanup access

---

### 7. Testing Philosophy

**Unit Tests** (`tests/engine/`):
- Pure logic validation
- No HTTP/UI dependencies
- Fast execution (<1s for 215 tests)

**Integration Tests** (`tests/integration/`):
- Server endpoints
- Full request/response cycle
- Slower but comprehensive

**UI Tests** (`tests/ui/`):
- Browser automation (Playwright)
- User interaction flows
- Slowest but catches UI bugs

**Rule**: Write tests in order of speed (unit → integration → UI)

---

### 8. Bug Report System Architecture

**Components**:
1. **ActionLog** (`action_log.py`) - Parquet-based event storage
2. **BugReport** (`bug_report.py`) - Markdown generation + GitHub API
3. **UI Modal** (`bugReport.js`) - User interface with voice input
4. **API Endpoint** (`/api/report_bug`) - Server integration

**Key Feature**: Auto-creates GitHub issues when `GITHUB_TOKEN` is set

**File Structure**:
```
bug_reports/
  bug_20260207_123456/
    report.md
    action_log.parquet
```

---

### 9. Python Version Compatibility

**Project Constraint**: Python 3.8.3 (not 3.9+)

**Impacts**:
- Use `from typing import List` not `list[T]`
- Cannot use union operator `|` for types
- Pattern matching (`match/case`) unavailable

---

### 10. Common Debugging Patterns

#### UnicodeEncodeError in Console
```bash
# Quick test if issue is Unicode-related
python -c "print('🀇')"  # If this fails, wrap in try/except
```

#### Test Claim Detection
```bash
# Check if CHOW opportunity detected
pytest tests/engine/test_hand_validator.py::test_can_form_chow_with_discard -v
```

#### Server Crashes on Claim
```bash
# Check server logs for UnicodeEncodeError
tail -f server.log | grep UnicodeEncode
```

#### UI Not Updating
```bash
# Hard refresh to clear browser cache
Ctrl + Shift + R
```

---

## Architecture Patterns

### Clean Separation of Concerns

```
mahjong_engine/     # Transport-agnostic game logic
├── game_state.py   # Core game mechanics
├── hand_validator.py  # Rule validation
└── action_log.py   # Event recording

app.py              # Web layer (aiohttp)
├── API endpoints
└── HTTP handling

static/game/js/     # UI layer
├── gameStore.js    # State management
├── claimsHandler.js  # User interactions
└── bugReport.js    # Error reporting
```

**Rule**: Game logic should work without web server (pure Python)

---

### Global State Management

**Server-side**: `current_game_state` global in `app.py`
- Single source of truth
- Simplified for demo/testing
- **TODO**: Multi-room support needs refactoring

**Client-side**: `store` object in `gameStore.js`
- Centralized state
- Timeout management
- UI element references

---

## Testing Checklist for New Features

- [ ] Unit tests for validation logic
- [ ] Integration tests for API endpoints
- [ ] UI tests for user interactions
- [ ] Manual testing guide updated
- [ ] Windows Unicode compatibility verified
- [ ] Python 3.8 compatibility checked
- [ ] Action log integration added
- [ ] Error handling with try/except

---

## Future Improvements Needed

### High Priority
1. **Multi-room support**: Refactor global `current_game_state`
2. **Comprehensive UI test suite**: Playwright/Selenium
3. **WIN claim edge cases**: Self-draw vs. discard win
4. **KONG edge cases**: Concealed vs. revealed kong

### Medium Priority
1. **Discard timeout**: Add countdown for discard action (5 seconds)
2. **Scoring system**: Calculate and display points
3. **Game history playback**: Replay from action log
4. **Mobile UI**: Responsive design

### Low Priority
1. **Custom tile themes**: Allow different tile graphics
2. **Sound effects**: Audio feedback for claims
3. **Multiple languages**: i18n support

---

## Quick Reference

### File Locations
- **Claim validation**: `mahjong_engine/hand_validator.py`
- **Claim processing**: `mahjong_engine/game_state.py`
- **API endpoints**: `app.py`
- **UI handlers**: `static/game/js/claimsHandler.js`
- **UI state**: `static/game/js/gameStore.js`
- **Tests**: `tests/engine/test_*.py`

### Test Commands
```bash
# Unit tests only
pytest -m "not integration" -v tests/engine

# Specific test file
pytest tests/engine/test_hand_validator.py -v

# Run all tests
pytest -v

# Syntax check
python -m py_compile app.py

# Lint check
python -m flake8 mahjong_engine/
```

### Server Commands
```bash
# Start server
python app.py

# Start with GitHub token
GITHUB_TOKEN=ghp_xxx python app.py  # Linux/Mac
$env:GITHUB_TOKEN="ghp_xxx"; python app.py  # PowerShell

# Kill server on Windows
tasklist | findstr python
taskkill //F //PID <PID>
```

---

## Known Issues & Workarounds

### Issue: Pre-existing F401 Warnings
**File**: `hand_validator.py`
**Warning**: Unused imports
**Status**: Pre-existing, not our issue
**Action**: Ignore for now

### Issue: Wall Count Confusion
**Question**: "Should there be more tiles?"
**Answer**: Math is correct (136 total - 52 dealt = 84 playable, 36 remaining after 48 draws)

### Issue: CHOW Not Appearing
**Cause**: Usually wrong player discarding (not left neighbor)
**Solution**: Check `(discarder_position + 1) % 4 == claimer_position`

---

## Contact & Resources

- **Project Repository**: https://github.com/yksi7417/signal_server
- **Testing Guide**: `TESTING_GUIDE.md`
- **Python Version**: 3.8.3
- **Framework**: aiohttp
- **Test Framework**: pytest

---

_This document should be updated as new patterns emerge and lessons are learned._
