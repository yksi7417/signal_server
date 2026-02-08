# Autonomous Development Prompt Templates

## Quick Start - Single Bug Fix

```
Fix the most recent auto-reported bug:

1. Check GitHub for the newest bug with label "auto-reported"
2. Download and analyze the action log from the gist
3. Write a failing test that reproduces the bug
4. Implement the fix in mahjong_engine/
5. Run all tests and ensure they pass
6. Commit with clear message
7. Comment on the GitHub issue with fix details

Stop after completing this one bug and report back to me.
```

## Autonomous Loop - Multiple Bugs

```
Start autonomous bug fix loop:

Work through open bugs one at a time:
1. Get list of open bugs (prioritize "auto-reported" label)
2. For each bug:
   - Download action log from gist
   - Analyze game state at failure
   - Write failing test
   - Implement fix
   - Verify ALL tests pass
   - Commit and push
   - Comment on issue
3. Continue until no bugs remain or ask me to stop

After each bug, summarize what you fixed and ask if I want to continue.
```

## Supervised Mode (Recommended First Time)

```
Let's fix bugs together. For the next open bug:

1. Show me the bug details from GitHub
2. Show me the action log analysis
3. Propose a test case
4. Wait for my approval
5. Implement the fix
6. Run tests
7. Show me the diff
8. Wait for my approval to commit

We'll do this step-by-step so I can learn the process.
```

## Full Autonomous Mode (Advanced)

```
Run fully autonomous development loop with these parameters:
- Max iterations: 10
- Stop conditions: All bugs fixed OR critical error
- Auto-commit: Yes
- Auto-push: Yes
- Require confirmation: No

For each bug:
1. Analyze (download gist, read action log)
2. Write test (must fail initially)
3. Fix (in mahjong_engine/ only)
4. Verify (ALL tests must pass)
5. Commit (with Co-Authored-By line)
6. Push
7. Comment on issue

Report summary after completion or if stuck.

SAFETY: Stop immediately if:
- Any test fails after fix
- Git conflict detected
- GitHub API error
- Unable to understand bug
```

## Debug Investigation Only (No Fixes)

```
Investigate all open bugs and create a report:

For each open bug:
1. Read GitHub issue
2. Download action log from gist
3. Analyze game state snapshots
4. Identify likely root cause
5. Propose fix approach

Create a markdown report with:
- Bug priority ranking
- Root cause analysis for each
- Proposed solution for each
- Time estimate for each

Don't implement fixes yet, just investigate and report.
```

## Quick Commands

### Check Status
```
Check autonomous dev status:
- How many open bugs?
- What's the newest auto-reported bug?
- Show me the last 3 commits
- Are all tests passing?
```

### Resume Loop
```
Continue the autonomous bug fix loop from where we left off.
Start with the next open bug.
```

### Stop Loop
```
Stop autonomous operations. Show me:
- What bug you were working on
- What you've completed
- What's left to do
```

## Example Session

**User**:
```
Start autonomous loop. Fix 3 bugs then stop and report.
```

**Expected Claude Response**:
```
Starting autonomous bug fix loop (max 3 bugs)

🔍 Checking for open bugs...
Found 9 open bugs

🐛 Bug #1: Issue #28 - "the game caught into a backstage when AI don't know what to do"
- Downloading gist...
- Analyzing action log (87 actions, 22 snapshots)...
- Root cause: AI gets stuck when Player 0 has pending CHOW claim
- Writing test: tests/engine/test_ai_turn_bug_28.py
- Implementing fix in mahjong_engine/player_agent.py
- Running tests... ✅ All 216 tests pass
- Committing...
- Commenting on issue #28
✅ Bug #28 fixed

[Continues for 2 more bugs...]

📊 Summary:
Fixed 3 bugs:
- #28: AI stuck on pending claim
- #17: Self-claim winning logic
- #15: Multi-player support

Next open bug: #14 (Multi-table mode)
Continue? [yes/no]
```

---

## Tips for Successful Autonomous Operation

1. **Start Small**: Try 1-2 bugs manually first
2. **Monitor**: Watch the first autonomous run closely
3. **Trust but Verify**: Review commits periodically
4. **Set Limits**: Use max_iterations to prevent runaway
5. **Check Tests**: Ensure tests are meaningful
6. **Review Code**: Check code quality after autonomous runs

## Emergency Stop

If things go wrong:
```
STOP! Emergency stop autonomous loop.
Show me what you were doing and git status.
```
