# Manual Testing Guide

Last updated: 2026-02-07

## Recent Fixes

### ✅ Fix 1: CHOW Claim UI Freeze
**Problem**: CHOW claim buttons (Yes/No) were unresponsive - UI completely frozen
**Root Cause**: Missing CHOW handlers in JavaScript and no `/api/player_claims_chow` endpoint
**Fix**: Implemented complete CHOW claim functionality (validation, API endpoint, UI handlers)

### ✅ Fix 2: GitHub Issue Automation
**Problem**: Bug reports required manual GitHub issue creation
**Solution**: Added automatic GitHub issue creation with PyGithub integration

---

## 🚀 Server Launch

### Option 1: Without GitHub Token
Bug reports will save locally + provide manual GitHub link.

```bash
python app.py
```

### Option 2: With GitHub Token
Bug reports will automatically create GitHub issues.

**Setup:**
```bash
# PowerShell
$env:GITHUB_TOKEN="ghp_your_token_here"
python app.py

# Command Prompt
set GITHUB_TOKEN=ghp_your_token_here
python app.py

# Or use .env file
cp .env.example .env
# Edit .env and add your token
python app.py
```

**Server URL**: http://localhost:8080
**Game URL**: http://localhost:8080/game

---

## 🧪 Test Suite

### Test 1: Bug Report Button Visibility ⭐ HIGH PRIORITY

**Objective**: Verify bug report button is visible and functional

**Steps:**
1. Navigate to http://localhost:8080/game
2. Scroll to bottom of page
3. Look for "Report Bug" button in the button group

**Expected Result:**
- ✅ Button is visible
- ✅ Button has gray background (#f5f5f5)
- ✅ Button positioned next to Reset button

**If not visible:**
- Hard refresh: `Ctrl + Shift + R` (clears cache)
- Check browser console (F12) for JavaScript errors
- Verify file loaded: Check Network tab for `bugReport.js`

---

### Test 2: Bug Report Modal (Without Token)

**Objective**: Test bug reporting without GitHub automation

**Prerequisites**:
- No GITHUB_TOKEN set
- Server running

**Steps:**
1. Click "Report Bug" button
2. Verify modal appears with:
   - Title: "Report a Bug"
   - Text area for description
   - 🎤 Microphone button (voice input)
   - Submit and Cancel buttons

3. **Test voice input** (optional):
   - Click 🎤 button
   - Allow microphone access if prompted
   - Say: "The chow claim button was not responding"
   - Verify text appears in textarea

4. Type or dictate bug description
5. Click "Submit Bug Report"

**Expected Result:**
```
✅ Bug reported! ID: bug_20260207_123456
🔗 Create GitHub Issue Manually
💡 Tip: Set GITHUB_TOKEN environment variable for automatic issue creation

[Preview markdown] (expandable)
```

**Verify:**
- ✅ Bug report saved in `bug_reports/bug_20260207_123456/` folder
- ✅ Folder contains `report.md` and `action_log.parquet`
- ✅ Link opens GitHub new issue page
- ✅ Tip message displayed about setting GITHUB_TOKEN

---

### Test 3: Bug Report with GitHub Token ⭐ HIGH PRIORITY

**Objective**: Test automatic GitHub issue creation

**Prerequisites**:
- GITHUB_TOKEN environment variable set
- Valid token with `repo` scope

**Setup:**
```bash
# Get token from: https://github.com/settings/tokens
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python app.py
```

**Steps:**
1. Click "Report Bug" button
2. Enter description: "Testing automatic GitHub issue creation"
3. Click "Submit Bug Report"

**Expected Result:**
```
✅ Bug reported & GitHub issue created!
Bug ID: bug_20260207_123456
GitHub Issue: #42 (clickable link)

[View report markdown] (expandable)
```

**Verify:**
- ✅ Issue created on GitHub
- ✅ Issue has labels: `bug`, `auto-reported`
- ✅ Issue title starts with "Bug Report:"
- ✅ Issue body contains action log and game state
- ✅ Local report saved in `bug_reports/` folder
- ✅ Link opens the created GitHub issue

**If it fails:**
- Check token is valid (not expired)
- Check token has `repo` scope
- Check repository name: `GITHUB_REPO=yksi7417/signal_server`
- Check server logs for error messages

---

### Test 4: CHOW Claim - Basic Functionality ⭐ CRITICAL

**Objective**: Verify CHOW claim buttons respond correctly

**Prerequisites**:
- Server running
- Game loaded at http://localhost:8080/game

**Steps:**
1. Click "Reset" button to start new game
2. Play several turns (discard tiles, AI takes turns)
3. Wait for CHOW opportunity message:
   ```
   AI Player 3 discarded 🀇 and you can claim it as a CHOW.
   ```
4. Observe:
   - "Yes" and "No" buttons enabled
   - Other buttons (Draw, Discard) disabled
   - 5-second auto-decline timer starts

5. **Test Case A - Accept CHOW:**
   - Click "Yes" button
   - **Expected:**
     - ✅ Buttons respond immediately (not frozen)
     - ✅ Message: "Player 0 claimed Chow. Your turn to discard."
     - ✅ Chow set revealed in "Revealed Sets" area
     - ✅ Hand updated (2 tiles removed, 1 added from discard)
     - ✅ Discard button enabled
     - ✅ Can select and discard a tile

6. **Test Case B - Decline CHOW:**
   - Reset and play until another CHOW opportunity
   - Click "No" button
   - **Expected:**
     - ✅ Message: "Chow claim declined. Game continues."
     - ✅ Turn advances to next player
     - ✅ Hand unchanged

**Common Issues:**
- ❌ Buttons don't respond → FIXED (was missing handlers)
- ❌ Console error about `/api/player_claims_chow` → Check endpoint registered
- ❌ No CHOW opportunities → Play more turns or check hand composition

---

### Test 5: CHOW Position Rule

**Objective**: Verify only left neighbor can claim CHOW

**Game Setup:**
- Player 0: You (human)
- Player 1: AI (right neighbor)
- Player 2: AI (opposite)
- Player 3: AI (left neighbor)

**Test Matrix:**

| Discarder | Can Claim CHOW? | Reason |
|-----------|----------------|---------|
| Player 1  | ❌ No | Not left neighbor |
| Player 2  | ❌ No | Not left neighbor |
| Player 3  | ✅ Yes | Left neighbor ((3+1)%4 = 0) |

**Steps:**
1. Play game and observe discard messages
2. Track which player's discards trigger CHOW prompt
3. Verify ONLY Player 3's discards offer CHOW

**Expected:**
- ✅ Player 3 discards → CHOW prompt appears (if valid sequence)
- ✅ Player 1 discards → NO CHOW prompt (even with valid tiles)
- ✅ Player 2 discards → NO CHOW prompt (even with valid tiles)

---

### Test 6: CHOW Sequence Validation

**Objective**: Verify CHOW only works with sequential numeric tiles

**Valid CHOW Examples:**

| Discarded | Hand Has | Chow Formed |
|-----------|----------|-------------|
| 🀇 (5♦)   | 🀅🀆 (3♦4♦) | 🀅🀆🀇 (3-4-5) |
| 🀇 (5♦)   | 🀆🀈 (4♦6♦) | 🀆🀇🀈 (4-5-6) |
| 🀇 (5♦)   | 🀈🀉 (6♦7♦) | 🀇🀈🀉 (5-6-7) |

**Invalid Cases:**

| Discarded | Hand Has | Why Invalid |
|-----------|----------|-------------|
| 🀀 (East)  | 🀁🀂 | Winds can't form CHOW |
| 🀄 (Red)   | 🀅🀆 | Dragons can't form CHOW |
| 🀇 (5♦)   | 🀇🀇 | Not a sequence (duplicate) |
| 🀇 (5♦)   | 🀃🀆 | Not consecutive (2♦,4♦) |

**Steps:**
1. Play game and note your hand composition
2. When Player 3 discards, check if CHOW prompt appears
3. Verify prompt only appears for valid sequences

---

### Test 7: CHOW Priority (vs PUNG/KONG)

**Objective**: Verify claim priority: WIN > KONG > PUNG > CHOW

**Scenario 1: PUNG takes priority**
- Player 3 discards 🀇 (5♦)
- Your hand: 🀇🀇🀅🀆 (has two 5♦, and 3♦4♦)
- **Expected**: PUNG prompt (not CHOW)

**Scenario 2: WIN takes priority**
- Player 3 discards 🀇 (completes your winning hand)
- Your hand: Almost complete, just needs 🀇
- **Expected**: WIN prompt (not CHOW/PUNG)

**Note**: Creating these scenarios requires specific hand composition - may need multiple game resets.

---

## 📊 Test Results Checklist

Use this checklist to track your testing progress:

- [ ] Test 1: Bug report button visible
- [ ] Test 2: Bug report modal (no token) - saves locally
- [ ] Test 3: Bug report with token - creates GitHub issue
- [ ] Test 4A: CHOW claim - Accept works
- [ ] Test 4B: CHOW claim - Decline works
- [ ] Test 5: CHOW position rule - only Player 3
- [ ] Test 6: CHOW sequences - numeric tiles only
- [ ] Test 7: CHOW priority - lower than PUNG/KONG/WIN

---

## 🐛 Known Issues

None currently identified. Please report any issues found during testing.

---

## 🔧 Troubleshooting

### Server Won't Start

**Error**: `Address already in use: 8080`
```bash
# Windows - Find and kill process
netstat -ano | findstr :8080
taskkill /F /PID <PID>

# Then restart
python app.py
```

### CHOW Not Appearing

**Check:**
1. Hand has sequential tiles (3-4-5, not 3-5-7)
2. Discard is from Player 3 (left neighbor)
3. Tiles are numeric suits (Dots/Bamboo/Characters, not Winds/Dragons)

**Example valid scenario:**
- Your hand includes: 🀃🀄 (3♦ 4♦)
- Player 3 discards: 🀅 (5♦)
- Should trigger: "Player 3 discarded 🀅 and you can claim it as a CHOW"

### Bug Report Button Not Visible

**Try:**
1. Hard refresh: `Ctrl + Shift + R`
2. Check browser console (F12) for errors
3. Verify `static/game/js/bugReport.js` loaded in Network tab
4. Check CSS: Button should have `background: #f5f5f5`

### GitHub Issue Not Created

**Check:**
1. Token set: `echo $env:GITHUB_TOKEN` (PowerShell)
2. Token valid: Not expired, has `repo` scope
3. Repository correct: Default is `yksi7417/signal_server`
4. PyGithub installed: `pip list | grep -i pygithub`
5. Server logs: Look for error messages

---

## 📝 Reporting Test Results

When reporting issues, include:

1. **Test case** (e.g., "Test 4A: CHOW Accept")
2. **Expected result** (from this guide)
3. **Actual result** (what you observed)
4. **Browser console errors** (F12 → Console tab)
5. **Server logs** (terminal output)
6. **Screenshots** (if applicable)

**Example:**
```
Test: 4A - CHOW Accept
Expected: Buttons respond, chow set revealed
Actual: Buttons clicked but nothing happened
Console Error: "POST /api/player_claims_chow 404"
Server Log: [attach screenshot]
```

---

## 🎯 Success Criteria

All tests pass with:
- ✅ No frozen UI
- ✅ All buttons respond immediately
- ✅ CHOW claims work correctly
- ✅ Bug reports save and/or create GitHub issues
- ✅ Position rules enforced
- ✅ Sequence validation working

---

## 🔗 Related Files

- `.env.example` - GitHub token configuration template
- `app.py` - Server with bug report endpoint
- `mahjong_engine/hand_validator.py` - CHOW validation logic
- `mahjong_engine/game_state.py` - CHOW claim processing
- `static/game/js/claimsHandler.js` - CHOW UI handlers
- `static/game/js/bugReport.js` - Bug report modal
