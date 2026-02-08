# Autonomous Development Loop Guide

## Overview
This guide explains how to set up Claude Code to autonomously run the development cycle:
**Run Server → Play → Report Bug → Write Test → Fix Bug → Run Test → Check in → Repeat**

## Prerequisites

### 1. Environment Setup
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Verify GitHub token is configured
cat .env | grep GITHUB_TOKEN

# Ensure git is configured
git config --get user.name
git config --get user.email
```

### 2. Branch Strategy
```bash
# Always work on a feature branch, not main
git checkout -b autonomous-dev-loop
git push -u origin autonomous-dev-loop
```

## Autonomous Loop Configuration

### Step 1: Create CLAUDE.md with Instructions

Create or update `C:\Users\antho\.claude\projects\c--dvlp-signal-server\memory\CLAUDE.md`:

```markdown
# Autonomous Development Instructions

## Your Role
You are an autonomous developer working on the Signal Server Mahjong game. Your goal is to continuously improve the codebase through a structured development loop.

## Development Loop (Run Unsupervised)

### Phase 1: Start Server & Play (Manual Trigger)
When the user says "start autonomous loop":

1. **Start the server**:
   ```bash
   python app.py
   ```
   - Verify it starts on port 8080
   - If port is in use, kill the process or use a different port

2. **Open the game**:
   - Tell user to open: http://localhost:8080/game
   - Wait for user confirmation that they've played a few rounds

### Phase 2: Check for Bugs
1. **Query GitHub for open issues**:
   ```bash
   gh issue list --repo yksi7417/signal_server --label bug --state open --limit 10
   ```

2. **Prioritize issues**:
   - Focus on "auto-reported" bugs first
   - Check issue creation date (newer = higher priority)
   - Read the issue description and action log

3. **Download action log from gist** (if attached):
   - Follow gist link in issue
   - Download actions.parquet.b64
   - Decode: `base64 -d actions.parquet.b64 > actions.parquet`
   - Analyze: `python -m mahjong_engine.action_log actions.parquet`

### Phase 3: Write Test (TDD)
For each bug:

1. **Understand the bug**:
   - Read issue description
   - Analyze action log
   - Identify game state at failure

2. **Write a failing test**:
   - File: `tests/engine/test_<feature>_bug_<issue_number>.py`
   - Test should reproduce the bug
   - Test should FAIL initially

3. **Verify test fails**:
   ```bash
   pytest tests/engine/test_<feature>_bug_<issue_number>.py -v
   ```

### Phase 4: Fix Bug
1. **Implement fix** in `mahjong_engine/` (never in app.py)

2. **Verify fix locally**:
   ```bash
   # Run the specific test
   pytest tests/engine/test_<feature>_bug_<issue_number>.py -v

   # Run all engine tests
   pytest tests/engine/ -v

   # Ensure no regressions
   pytest -m "not integration" -v
   ```

3. **Verify syntax**:
   ```bash
   python -m py_compile mahjong_engine/*.py
   ```

### Phase 5: Commit & Push
1. **Commit with clear message**:
   ```bash
   git add tests/engine/test_<feature>_bug_<issue_number>.py
   git add mahjong_engine/<modified_files>.py
   git commit -m "Fix #<issue_number>: <brief description>

   - Added test to reproduce bug
   - Fixed <root cause>
   - All tests passing

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

2. **Push to branch**:
   ```bash
   git push
   ```

3. **Comment on GitHub issue**:
   ```bash
   gh issue comment <issue_number> --body "Fixed in commit <commit_hash>.

   Test added: tests/engine/test_<feature>_bug_<issue_number>.py
   Root cause: <explanation>
   Solution: <explanation>

   All tests passing ✅"
   ```

4. **Close issue** (only if fix is verified):
   ```bash
   gh issue close <issue_number>
   ```

### Phase 6: Loop Back
1. Check if there are more open bugs
2. If yes, go to Phase 2
3. If no, wait for new bugs or user trigger

## Safety Rules (CRITICAL)

### DO:
- ✅ Always run ALL tests before committing
- ✅ Check syntax with `python -m py_compile`
- ✅ Write clear commit messages
- ✅ Comment on GitHub issues with progress
- ✅ Work on one bug at a time
- ✅ Keep changes small and focused

### DON'T:
- ❌ NEVER push to main directly (use feature branch)
- ❌ NEVER commit if tests are failing
- ❌ NEVER skip writing tests for bugs
- ❌ NEVER force push
- ❌ NEVER commit .env files
- ❌ NEVER make unrelated changes
- ❌ NEVER close issues without verification

## Monitoring & Feedback

### Check Progress
```bash
# See recent commits
git log --oneline -10

# See test coverage
pytest --cov=mahjong_engine tests/engine/

# Check open issues
gh issue list --repo yksi7417/signal_server --label bug
```

### Error Handling
If you encounter:
- **Test failures**: Analyze output, fix code, retry
- **Import errors**: Check dependencies in requirements.txt
- **Git conflicts**: Stop and ask user for help
- **GitHub API errors**: Check GITHUB_TOKEN in .env
- **Server won't start**: Check if port 8080 is in use

## Stopping the Loop

To stop autonomous operation:
- User says "stop autonomous loop"
- Critical error encountered
- All bugs are fixed
- Time limit reached (if specified)
```

### Step 2: Create Automation Script

Create `scripts/autonomous_loop.sh`:

```bash
#!/bin/bash
# Autonomous Development Loop Runner

set -e  # Exit on error

echo "🤖 Starting Autonomous Development Loop"
echo "========================================"

# Configuration
REPO="yksi7417/signal_server"
MAX_ITERATIONS=${1:-10}  # Default: 10 iterations
ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "🔄 Iteration $ITERATION/$MAX_ITERATIONS"
    echo "========================================"

    # Check for open bugs
    echo "📋 Checking for open bugs..."
    OPEN_BUGS=$(gh issue list --repo $REPO --label bug --state open --json number --jq '. | length')

    if [ "$OPEN_BUGS" -eq 0 ]; then
        echo "✅ No open bugs! Loop complete."
        break
    fi

    echo "Found $OPEN_BUGS open bug(s)"

    # Get the oldest bug
    BUG_NUMBER=$(gh issue list --repo $REPO --label bug --state open --json number --jq '.[0].number')

    if [ -z "$BUG_NUMBER" ]; then
        echo "⚠️  Could not get bug number. Stopping."
        break
    fi

    echo "🐛 Working on bug #$BUG_NUMBER"

    # Let Claude Code handle it
    echo ""
    echo "Waiting for Claude Code to:"
    echo "  1. Analyze bug #$BUG_NUMBER"
    echo "  2. Write test"
    echo "  3. Fix bug"
    echo "  4. Commit changes"
    echo ""
    echo "Press ENTER when Claude Code completes this bug..."
    read -r

    # Verify tests pass
    echo "🧪 Running tests..."
    if pytest -m "not integration" -v; then
        echo "✅ Tests passed!"
    else
        echo "❌ Tests failed. Stopping loop."
        exit 1
    fi

    echo "Iteration $ITERATION complete ✅"
done

echo ""
echo "🎉 Autonomous Development Loop Complete!"
echo "Total iterations: $ITERATION"
```

### Step 3: Configure Claude Code Settings

Create `.claude/config.json`:

```json
{
  "autonomous_mode": {
    "enabled": true,
    "max_iterations": 10,
    "require_user_confirmation": false,
    "auto_commit": true,
    "auto_push": true,
    "branch_strategy": "feature_per_bug"
  },
  "testing": {
    "run_before_commit": true,
    "fail_on_test_failure": true,
    "coverage_threshold": 80
  },
  "github": {
    "auto_comment_issues": true,
    "auto_close_on_fix": false,
    "require_manual_verification": true
  }
}
```

## How to Use

### Manual Mode (Recommended for First Time)
```bash
# 1. Start Claude Code
claude-code

# 2. In Claude Code chat:
"Start autonomous development loop. Work on one bug at a time."

# 3. Claude will:
#    - Check for open bugs
#    - Pick the oldest/highest priority
#    - Write test
#    - Fix bug
#    - Run tests
#    - Commit
#    - Ask if you want to continue

# 4. Review and approve each step
```

### Semi-Autonomous Mode
```bash
# Use the script to manage iterations
chmod +x scripts/autonomous_loop.sh
./scripts/autonomous_loop.sh 5  # Run 5 iterations max
```

### Fully Autonomous Mode (Advanced)
**⚠️  Use with caution! Requires trust in Claude Code.**

```bash
# Set up git hooks to prevent bad commits
# Create .git/hooks/pre-commit
#!/bin/bash
pytest -m "not integration" -v || exit 1

# Make executable
chmod +x .git/hooks/pre-commit

# Then let Claude Code run unsupervised
claude-code --autonomous --max-iterations=10
```

## Monitoring Autonomous Operation

### Real-time Logs
```bash
# Watch test output
tail -f test-output.log

# Watch git commits
watch -n 5 'git log --oneline -5'

# Watch GitHub issues
watch -n 30 'gh issue list --repo yksi7417/signal_server --label bug'
```

### Dashboard (Optional)
Create a simple dashboard to monitor:
- Open bugs count
- Tests passing/failing
- Last commit time
- Current iteration

## Troubleshooting

### Loop Gets Stuck
- Check if tests are failing
- Check if GitHub API rate limit hit
- Check if git has conflicts

### Tests Keep Failing
- Review test output
- Check if environment is correct
- Verify dependencies are installed

### No Progress
- Ensure GitHub token is valid
- Check if bugs are properly labeled
- Verify Claude Code has necessary context

## Best Practices

1. **Start Small**: Run 1-2 iterations manually first
2. **Monitor Closely**: Watch the first few autonomous runs
3. **Set Limits**: Use max_iterations to prevent runaway loops
4. **Review Commits**: Check code quality periodically
5. **Test Coverage**: Ensure tests are meaningful, not just passing

---

**Remember**: Autonomous operation is powerful but requires trust. Start supervised, then gradually increase autonomy as confidence builds.
